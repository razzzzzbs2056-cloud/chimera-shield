"""End-to-end: footage in -> clips through QC -> CEO approval -> publish -> invoice.
Runs in heuristic mode (no API calls) against a temporary data directory."""
import importlib
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture()
def agency(tmp_path, monkeypatch):
    monkeypatch.setenv("CLIPFORGE_HOME", str(tmp_path))
    monkeypatch.setenv("CLIPFORGE_USE_LLM", "off")
    for m in [m for m in sys.modules if m == "agency" or m.startswith("agency.") or m.startswith("scripts")]:
        del sys.modules[m]
    import agency.config  # noqa: F401
    from agency import db
    db.init()
    return importlib.import_module("scripts.demo"), db


def test_full_pipeline(agency, monkeypatch):
    demo, db = agency
    monkeypatch.delenv("FILMCRAFT_CLI", raising=False)  # this test covers the ffmpeg-only path
    from agency.orchestrator import Orchestrator

    oid = demo.seed()
    # one music track in the library so the audio engineer lays a bed
    from agency.agents.editors import MUSIC_DIR
    import subprocess
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=frequency=440:duration=8",
                    str(MUSIC_DIR / "calm_pad.wav")], check=True)
    orch = Orchestrator()
    orch.run_until_idle()

    order = db.row("SELECT * FROM orders WHERE id = ?", (oid,))
    assert order["status"] == "in_production", order
    clips = db.rows("SELECT * FROM clips WHERE order_id = ?", (oid,))
    assert len(clips) == 3
    for c in clips:
        assert c["status"] == "awaiting_approval", (c["status"], c["qc_report"])
        assert 15 <= c["end"] - c["start"] <= 60
        assert Path(c["final_path"]).exists() and Path(c["srt_path"]).exists()
        report = json.loads(c["qc_report"])
        assert all(ch["ok"] for ch in report if ch["severity"] == "error"), report
        log = " | ".join(json.loads(c["edit_log"]))
        assert "pacing: removed" in log and "punch-in" in log and "LUFS" in log and "calm pad" in log, log
        em = json.loads(c["edit_map"])
        assert len(em["keeps"]) >= 2 and em["zooms"]
        lufs = next(ch for ch in report if ch["check"] == "loudness_target")
        assert lufs["ok"], lufs
        otio_path = Path(c["final_path"]).with_suffix(".otio")
        assert otio_path.exists()
    # no overlapping moments
    spans = sorted((c["start"], c["end"]) for c in clips)
    assert all(a[1] <= b[0] for a, b in zip(spans, spans[1:]))

    # leads were qualified and the best one got an outreach draft
    leads = {l["name"]: l for l in db.rows("SELECT * FROM leads")}
    assert leads["Maya Chen"]["stage"] == "outreach_drafted"
    assert leads["Lena Ruiz"]["stage"] == "disqualified"
    assert db.row("SELECT * FROM outreach WHERE lead_id = ?", (leads["Maya Chen"]["id"],))

    # CEO approves two, rejects one
    db.update("clips", clips[0]["id"], status="approved")
    db.update("clips", clips[1]["id"], status="approved")
    db.update("clips", clips[2]["id"], status="rejected")
    orch.run_until_idle()

    for c in clips[:2]:
        c = db.row("SELECT * FROM clips WHERE id = ?", (c["id"],))
        assert c["status"] == "scheduled"
        pub = json.loads(c["publish"])
        assert set(pub) == {"tiktok", "instagram_reels", "youtube_shorts"}
        assert len(pub["youtube_shorts"]["caption"]) <= 100
    order = db.row("SELECT * FROM orders WHERE id = ?", (oid,))
    assert order["status"] == "delivered"
    inv = db.row("SELECT * FROM invoices WHERE order_id = ?", (oid,))
    assert inv and inv["amount_cents"] == order["price_cents"]

    # winning a lead creates a client
    db.update("leads", leads["Maya Chen"]["id"], stage="won")
    orch.run_until_idle()
    assert db.row("SELECT * FROM clients WHERE lead_id = ?", (leads["Maya Chen"]["id"],))


def test_caption_chunking(agency):
    _, db = agency
    from agency.agents.quality import run_checks
    from agency.agents.captioner import chunk_words, build_srt
    from agency import transcript
    segs = [{"start": 0, "end": 5, "text": "one two three four five six seven eight"}]
    words = transcript.words_between(segs, 0, 5)
    assert len(chunk_words(words, 3)) == 3
    assert "-->" in build_srt(chunk_words(words, 3))


def test_transcript_formats():
    sys.path.insert(0, str(ROOT))
    from agency import transcript
    srt = "1\n00:00:01,000 --> 00:00:03,500\nHello there\n\n2\n00:00:04,000 --> 00:00:06,000\nGeneral <i>Kenobi</i>\n"
    segs = transcript.parse(srt)
    assert segs == [{"start": 1.0, "end": 3.5, "text": "Hello there"}, {"start": 4.0, "end": 6.0, "text": "General Kenobi"}]
    vtt = "WEBVTT\n\n00:01.000 --> 00:02.000\nhi\n"
    assert transcript.parse(vtt)[0]["text"] == "hi"
    assert transcript.parse('{"segments":[{"start":0,"end":1,"text":"x"}]}')[0]["text"] == "x"


def test_edit_map_math():
    sys.path.insert(0, str(ROOT))
    from agency import editing
    keeps = editing.keeps_from_silences(20.0, [(0.0, 1.0), (5.0, 7.0), (19.5, 20.0)], pad=0.1)
    assert keeps == [[0.9, 5.1], [6.9, 19.6]]  # a 0.1s breath is kept around speech
    assert editing.remap(0.5, keeps) is None            # inside the cut leading silence
    assert abs(editing.remap(7.0, keeps) - 4.3) < 1e-9  # 4.2s kept before, +0.1 into the 2nd span
    assert editing.remap(6.0, keeps) is None
    words = [{"word": "a", "start": 4.8, "end": 5.4}, {"word": "b", "start": 5.5, "end": 6.5}]
    out = editing.remap_words(words, keeps)
    assert [w["word"] for w in out] == ["a"]           # 'b' sat entirely in removed silence


def test_zoom_plan():
    sys.path.insert(0, str(ROOT))
    from agency.agents.editors import plan_zooms, zoom_expr
    z = plan_zooms([0.0, 3.0, 6.0, 9.0, 12.0], 20.0)
    assert z == [[3.0, 6.0, 1.12], [9.0, 12.0, 1.12]]
    assert "between(it,3.0,6.0)" in zoom_expr(z)


def test_otio_is_valid_and_matches_edit(tmp_path):
    otio = pytest.importorskip("opentimelineio")
    sys.path.insert(0, str(ROOT))
    from agency import handoff
    clip = {"id": 7, "order_id": 1, "start": 10.0, "end": 40.0, "hook": "Why prices matter", "title": "t"}
    order = {"source_path": str(tmp_path / "ep.mp4")}
    em = {"keeps": [[0.0, 12.0], [13.5, 30.0]], "zooms": [[4.0, 7.0, 1.12]]}
    doc = handoff.build_otio(clip, order, em, {"duration": 600.0, "fps": 30.0}, "clip_7.srt")
    p = tmp_path / "c.otio"
    p.write_text(json.dumps(doc))
    tl = otio.adapters.read_from_file(str(p))
    v, a = tl.tracks
    assert v.kind == "Video" and a.kind == "Audio"
    ranges = [(c.source_range.start_time.to_seconds(), c.source_range.duration.to_seconds()) for c in v]
    assert ranges == [(10.0, 12.0), (23.5, 16.5)]        # source time = clip start + kept span
    assert abs(tl.duration().to_seconds() - 28.5) < 1e-6
    names = [m.name for m in tl.tracks.markers]
    assert names[0].startswith("HOOK") and "Jump cut" in names and "Punch-in 112%" in names
    assert v[0].media_reference.target_url.startswith("file://")


def test_filmcraft_zoom_keys():
    sys.path.insert(0, str(ROOT))
    from agency.agents.filmcraft_agents import zoom_at, zoom_keys, heuristic_look
    keys = zoom_keys([[4.0, 7.0, 1.12]], 30)
    assert keys[0] == (0.0, 1.0, "linear") and (4.0, 1.12, "hold") in keys and (7.0, 1.0, "hold") in keys
    assert zoom_at(1.25, []) == pytest.approx(1.03) and zoom_at(5.0, [[4.0, 7.0, 1.12]]) == 1.12
    assert heuristic_look({"luma": 40, "sat": 20})[0] == "Lift Shadows"
    assert heuristic_look({"luma": 120, "sat": 20})[0] == "Boost Vibrance"


@pytest.mark.skipif(not os.getenv("FILMCRAFT_CLI"), reason="set FILMCRAFT_CLI to run the FilmCraft agents for real")
def test_filmcraft_agents_end_to_end(agency):
    """Slow (FilmCraft renders ~7x real time on CPU): one clip through all three FilmCraft agents."""
    demo, db = agency
    from agency.orchestrator import Orchestrator
    from agency import filmcraft
    demo.seed()
    db.update("orders", 1, clips_requested=1)
    Orchestrator().run_until_idle()
    c = db.row("SELECT * FROM clips WHERE order_id = 1")
    assert c["status"] == "awaiting_approval", c["status"]
    log = json.loads(c["edit_log"])
    assert any(l.startswith("assembler: FilmCraft project") for l in log), log
    assert any(l.startswith("colorist: '") for l in log), log
    assert any(l.startswith("finisher: rendered by FilmCraft") for l in log), log
    proj = json.loads(c["edit_map"])["filmcraft"]["project"]
    seq = filmcraft.inspect(proj)["sequence"]
    assert (seq["settings"]["width"], seq["settings"]["height"]) == (1080, 1920)
    fg = seq["video"][1]["items"]
    assert fg and all(any(e["effect"] == "lumetri" for e in it["effects"]) for it in fg)
    tracks = filmcraft.run([{"id": "captions.list", "params": {}}], project=proj)[0]["tracks"]
    assert {t["name"] for t in tracks} == {"Captions", "Hook"}
    lufs = next(r for r in json.loads(c["qc_report"]) if r["check"] == "loudness_target")
    assert lufs["ok"], lufs
