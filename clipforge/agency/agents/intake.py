"""Intake agent: validates uploaded footage and prepares a transcript."""
from pathlib import Path

from .. import config, db, media, transcript
from .base import Agent


class IntakeAgent(Agent):
    name = "intake"
    role = "Receives videos and briefs"

    def step(self) -> bool:
        order = db.claim("orders", "received", "intake")
        if not order:
            return False
        oid = order["id"]
        self.working(f"Checking footage for order #{oid}: {order['title']}")
        try:
            info = media.probe(order["source_path"])
        except Exception as e:
            db.update("orders", oid, status="failed", error=f"Unreadable video: {e}")
            self.log(f"Order #{oid} rejected: unreadable video", "error", ("order", oid))
            return True
        if info["duration"] < 2 * config.MIN_CLIP_S:
            db.update("orders", oid, status="failed", error="Video too short to clip")
            self.log(f"Order #{oid} rejected: only {info['duration']:.0f}s long", "error", ("order", oid))
            return True
        if not info["has_audio"]:
            self.log(f"Order #{oid}: video has no audio track", "warn", ("order", oid))

        tpath = Path(config.WORK) / f"order_{oid}_transcript.json"
        try:
            raw = order.get("transcript_path")
            if raw and Path(raw).exists():
                segs = transcript.parse(Path(raw).read_text(errors="replace"), raw)
                self.log(f"Order #{oid}: loaded supplied transcript ({len(segs)} segments)", entity=("order", oid))
            else:
                self.working(f"Transcribing order #{oid}")
                segs = transcript.transcribe(order["source_path"])
                self.log(f"Order #{oid}: transcribed {len(segs)} segments", entity=("order", oid))
        except Exception as e:
            db.update("orders", oid, status="failed", error=str(e))
            self.log(f"Order #{oid}: transcript failed: {e}", "error", ("order", oid))
            return True
        transcript.save(segs, tpath)
        db.update("orders", oid, status="transcribed", transcript_path=str(tpath),
                  duration=info["duration"], width=info["width"], height=info["height"])
        self.log(f"Order #{oid} accepted: {info['duration'] / 60:.1f} min, {info['width']}x{info['height']}",
                 entity=("order", oid))
        self.done()
        return True
