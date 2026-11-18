"""The editing department: three AI editors that each make one pass on every clip.

    clipper -> [pacing editor] -> [motion editor] -> [audio engineer] -> captioner

Each editor reads `clip.edit_path` (the latest render) and the clip's edit map,
writes a new render, and appends to `edit_log` so you can see what changed.
Pausing an editor on the dashboard *bypasses* it: clips pass straight through.
"""
import json
import re
import zlib
from pathlib import Path

from .. import config, db, editing, media, transcript
from .base import Agent

MUSIC_DIR = config.ROOT / "music"
MUSIC_DIR.mkdir(parents=True, exist_ok=True)


def load_map(clip: dict) -> dict:
    em = json.loads(clip["edit_map"]) if clip.get("edit_map") else {}
    em.setdefault("keeps", editing.identity(clip["end"] - clip["start"]))
    em.setdefault("zooms", [])
    return em


def add_log(clip: dict, line: str) -> list[str]:
    return (json.loads(clip["edit_log"]) if clip.get("edit_log") else []) + [line]


class EditorAgent(Agent):
    """An agent that works on one pipeline stage and can be bypassed."""

    takes, busy, gives = "", "", ""
    always_tick = True

    def step(self) -> bool:
        clip = db.claim("clips", self.takes, self.busy)
        if not clip:
            return False
        if not self.enabled():
            db.update("clips", clip["id"], status=self.gives,
                      edit_log=add_log(clip, f"{self.name}: bypassed"))
            self.log(f"Clip #{clip['id']}: bypassed (you paused {self.name})", entity=("clip", clip["id"]))
            return True
        self.working(f"{self.verb} clip #{clip['id']}")
        try:
            self.edit(clip)
            self.done()
        except Exception as e:  # an editing pass is an enhancement: never block the clip on it
            db.update("clips", clip["id"], status=self.gives, edit_log=add_log(clip, f"{self.name}: skipped ({e})"))
            db.execute("UPDATE agents SET errors = errors + 1 WHERE name = ?", (self.name,))
            self.log(f"Clip #{clip['id']}: pass failed, sent on unedited: {str(e)[:200]}", "warn", ("clip", clip["id"]))
        return True

    verb = "Editing"

    def edit(self, clip: dict) -> None:  # pragma: no cover
        raise NotImplementedError

    def out_path(self, clip: dict, tag: str) -> str:
        return str(Path(config.WORK) / f"clip_{clip['id']}_{tag}.mp4")


class PacingEditor(EditorAgent):
    """Removes dead air with jump cuts so the clip never drags."""
    name, role = "pacing", "Cuts silences and dead air"
    takes, busy, gives = "cut", "trimming", "paced"
    verb = "Tightening"

    def edit(self, clip):
        cid, src = clip["id"], clip["edit_path"] or clip["raw_path"]
        dur = media.probe(src)["duration"]
        sil = media.silences(src, noise_db=-35, min_dur=0.6)
        keeps = editing.keeps_from_silences(dur, sil)
        removed = dur - editing.kept_duration(keeps)
        em = load_map(clip)
        if removed < 0.3 or editing.kept_duration(keeps) < config.MIN_CLIP_S:
            db.update("clips", cid, status=self.gives, edit_map=em,
                      edit_log=add_log(clip, "pacing: no dead air worth cutting"))
            self.log(f"Clip #{cid}: pacing already tight", entity=("clip", cid))
            return
        out = self.out_path(clip, "paced")
        media.keep_segments(src, keeps, out)
        em["keeps"] = keeps
        cuts = len(keeps) - 1 + (keeps[0][0] > 0)
        line = f"pacing: removed {removed:.1f}s of silence ({cuts} jump cut{'s' * (cuts != 1)})"
        db.update("clips", cid, status=self.gives, edit_path=out, edit_map=em, edit_log=add_log(clip, line))
        self.log(f"Clip #{cid}: {line.split(": ", 1)[1]}", entity=("clip", cid))


def plan_zooms(sentence_starts: list[float], duration: float, push_in: float = 2.5,
               level: float = 1.12, min_hold: float = 1.5, max_hold: float = 6.0) -> list[list[float]]:
    """Punch in on every other sentence after the hook; hold until the next sentence."""
    starts = sorted(t for t in sentence_starts if push_in <= t < duration - min_hold)
    if len(starts) < 2:  # long monologue: fall back to a steady rhythm
        starts = [push_in + 4 * i for i in range(int((duration - push_in) // 4))]
    zooms = []
    for i, a in enumerate(starts):
        if i % 2:
            continue
        b = starts[i + 1] if i + 1 < len(starts) else duration
        b = min(b, a + max_hold, duration)
        if b - a >= min_hold:
            zooms.append([round(a, 3), round(b, 3), level])
    return zooms


def zoom_expr(zooms: list[list[float]], push_in: float = 2.5, push: float = 0.06) -> str:
    """zoompan `z` expression: slow push-in under the hook, then hard punch-ins."""
    expr = f"1+{push}*min(it,{push_in})/{push_in}*lt(it,{push_in})"
    for a, b, z in zooms:
        expr += f"+{z - 1:.3f}*between(it,{a},{b})"
    return expr


class MotionEditor(EditorAgent):
    """Adds camera movement: a push-in under the hook and punch-ins on sentence changes."""
    name, role = "motion", "Punch-in zooms and movement"
    takes, busy, gives = "paced", "zooming", "zoomed"
    verb = "Adding motion to"

    def edit(self, clip):
        cid, src = clip["id"], clip["edit_path"] or clip["raw_path"]
        order = db.row("SELECT transcript_path FROM orders WHERE id = ?", (clip["order_id"],))
        segs = transcript.load(order["transcript_path"])
        em = load_map(clip)
        dur = media.probe(src)["duration"]
        starts = []
        for s in segs:
            if clip["start"] < s["start"] < clip["end"]:
                t = editing.remap(s["start"] - clip["start"], em["keeps"])
                if t is not None:
                    starts.append(t)
        zooms = plan_zooms(starts, dur)
        out = self.out_path(clip, "motion")
        media.zoom(src, zoom_expr(zooms), out)
        em["zooms"] = zooms
        line = f"motion: hook push-in + {len(zooms)} punch-in{'s' * (len(zooms) != 1)}"
        db.update("clips", cid, status=self.gives, edit_path=out, edit_map=em, edit_log=add_log(clip, line))
        self.log(f"Clip #{cid}: {line.split(": ", 1)[1]}", entity=("clip", cid))


def pick_track(seed: str) -> Path | None:
    tracks = sorted(p for p in MUSIC_DIR.iterdir() if p.suffix.lower() in (".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"))
    if not tracks:
        return None
    return tracks[zlib.crc32(seed.encode()) % len(tracks)]  # same client -> same sound


class AudioEngineer(EditorAgent):
    """Masters the sound: -14 LUFS for social platforms, plus a ducked music bed."""
    name, role = "audio", "Loudness and music bed"
    takes, busy, gives = "zoomed", "mixing", "edited"
    verb = "Mixing"

    def edit(self, clip):
        cid, src = clip["id"], clip["edit_path"] or clip["raw_path"]
        if not media.probe(src)["has_audio"]:
            db.update("clips", cid, status=self.gives, edit_log=add_log(clip, "audio: no audio track"))
            return
        order = db.row("SELECT client_id FROM orders WHERE id = ?", (clip["order_id"],))
        track = pick_track(f"client-{order['client_id']}")
        out = self.out_path(clip, "mixed")
        media.master_audio(src, out, music=str(track) if track else None)
        lufs = media.integrated_loudness(out)
        em = load_map(clip)
        em["music"] = track.name if track else None
        line = f"audio: {lufs:.1f} LUFS" if lufs is not None else "audio: normalised"
        line += f", music '{re.sub(r'[_-]+', ' ', track.stem)}' ducked under voice" if track else ", no music (add tracks to data/music/)"
        db.update("clips", cid, status=self.gives, edit_path=out, edit_map=em, edit_log=add_log(clip, line))
        self.log(f"Clip #{cid}: {line.split(": ", 1)[1]}", entity=("clip", cid))
