"""Clipping agent: cuts each planned moment and reframes it to vertical 9:16."""
import json
from pathlib import Path

from .. import config, db, media, transcript
from .base import Agent


def fix_boundaries(clip: dict, segs: list[dict], notes: list[str]) -> tuple[float, float]:
    a, b = clip["start"], clip["end"]
    starts = sorted(s["start"] for s in segs)
    ends = sorted(s["end"] for s in segs)
    if "start_mid_sentence" in notes:
        a = max((t for t in starts if t <= a + 0.05), default=a)
    if "too_long" in notes:
        b = max((e for e in ends if a + config.MIN_CLIP_S <= e <= a + config.MAX_CLIP_S), default=a + config.MAX_CLIP_S)
    if "too_short" in notes:
        b = min((e for e in ends if e >= a + config.MIN_CLIP_S), default=b)
    return a, b


class ClipperAgent(Agent):
    name = "clipper"
    role = "Cuts and reframes video"

    def step(self) -> bool:
        clip = db.claim("clips", "planned", "cutting") or db.claim("clips", "needs_recut", "cutting")
        if not clip:
            return False
        cid = clip["id"]
        order = db.row("SELECT * FROM orders WHERE id = ?", (clip["order_id"],))
        notes = json.loads(clip["fix_notes"] or "[]")
        a, b = clip["start"], clip["end"]
        if notes:
            a, b = fix_boundaries(clip, transcript.load(order["transcript_path"]), notes)
            self.log(f"Clip #{cid}: re-cutting to fix {', '.join(notes)} -> {a:.1f}s-{b:.1f}s", entity=("clip", cid))
        self.working(f"Cutting clip #{cid} ({b - a:.0f}s) to 9:16")
        out = Path(config.WORK) / f"clip_{cid}_raw.mp4"
        media.cut_vertical(order["source_path"], a, b, str(out))
        db.update("clips", cid, status="cut", start=a, end=b, raw_path=str(out))
        self.log(f"Clip #{cid} cut and reframed to {config.OUT_W}x{config.OUT_H}", entity=("clip", cid))
        self.done()
        return True
