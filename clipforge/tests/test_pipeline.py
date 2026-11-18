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


def test_full_pipeline(agency):
    demo, db = agency
    from agency.orchestrator import Orchestrator

    oid = demo.seed()
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
        assert all(ch["ok"] for ch in report if ch["severity"] == "error")
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
