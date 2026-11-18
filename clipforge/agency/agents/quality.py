"""Quality agent: reviews every finished clip before it reaches the CEO.

Fixable problems are routed back to the clipper (timing) or captioner (text);
clips that still fail after MAX_QC_ATTEMPTS are parked as `qc_failed`."""
import json
import re

from pydantic import BaseModel

from .. import config, db, editing, llm, media, transcript
from .editors import load_map
from .base import Agent
from .captioner import HOOK_SECONDS

RECUT = {"too_long", "too_short", "start_mid_sentence"}
RECAPTION = {"hook_too_long", "caption_density", "weak_hook"}


class Review(BaseModel):
    hook_score: int
    standalone: bool
    notes: str


def _srt_cues(path: str) -> list[tuple[float, float, str]]:
    cues = []
    for block in open(path).read().strip().split("\n\n"):
        lines = block.split("\n")
        if len(lines) >= 3 and "-->" in lines[1]:
            a, b = (transcript._ts(x) for x in lines[1].split("-->"))
            cues.append((a, b, " ".join(lines[2:])))
    return cues


def run_checks(clip: dict, segs: list[dict]) -> list[dict]:
    checks = []

    def add(name, ok, detail, fix=None, severity="error"):
        checks.append({"check": name, "ok": bool(ok), "detail": detail, "fix": None if ok else fix,
                       "severity": severity})

    info = media.probe(clip["final_path"])
    dur = info["duration"]
    add("format", (info["width"], info["height"]) == (config.OUT_W, config.OUT_H),
        f"{info['width']}x{info['height']} (need {config.OUT_W}x{config.OUT_H})")
    add("duration", config.MIN_CLIP_S - 0.5 <= dur <= config.MAX_CLIP_S + 0.5,
        f"{dur:.1f}s (target {config.MIN_CLIP_S:.0f}-{config.MAX_CLIP_S:.0f}s)",
        "too_long" if dur > config.MAX_CLIP_S else "too_short")
    add("audio", info["has_audio"], "audio track present" if info["has_audio"] else "no audio", severity="warn")
    if info["has_audio"]:
        vol = media.mean_volume_db(clip["final_path"])
        add("loudness", vol is None or vol > -35, f"mean volume {vol} dB", severity="warn")
        lufs = media.integrated_loudness(clip["final_path"])
        add("loudness_target", lufs is None or -17 <= lufs <= -11,
            f"{lufs} LUFS (platform target -14)", severity="warn")

    starts = [s["start"] for s in segs]
    on_boundary = any(abs(clip["start"] - s) < 0.25 for s in starts)
    add("clean_start", on_boundary, "starts at a sentence boundary" if on_boundary else "starts mid-sentence",
        "start_mid_sentence")

    hook = clip.get("hook") or ""
    hw = len(hook.split())
    add("hook", 2 <= hw <= 10, f"\"{hook}\" ({hw} words, shown first {HOOK_SECONDS:.0f}s)", "hook_too_long")

    cues = _srt_cues(clip["srt_path"]) if clip.get("srt_path") else []
    covered = sum(min(b, dur) - max(a, 0) for a, b, _ in cues if b > a)
    keeps = load_map(clip)["keeps"]
    speech = sum(b - a for s in segs if s["end"] > clip["start"] and s["start"] < clip["end"]
                 for a, b in editing.remap_span(max(s["start"], clip["start"]) - clip["start"],
                                               min(s["end"], clip["end"]) - clip["start"], keeps))
    coverage = covered / speech if speech > 0 else 1.0
    add("subtitles", cues and coverage >= 0.8, f"{len(cues)} cues covering {coverage:.0%} of speech", "caption_density")
    longest = max((len(t.split()) for *_, t in cues), default=0)
    add("subtitle_readability", longest <= 4, f"max {longest} words on screen at once", "caption_density")

    words = len(re.findall(r"\w+", transcript.text_between(segs, clip["start"], clip["end"])))
    wps = words / max(dur, 1)
    add("pacing", 1.5 <= wps <= 4.5, f"{wps:.1f} words/sec", severity="warn")
    return checks


class QualityAgent(Agent):
    name = "quality"
    role = "Reviews finished clips"

    def step(self) -> bool:
        clip = db.claim("clips", "captioned", "qc")
        if not clip:
            return False
        cid = clip["id"]
        self.working(f"Reviewing clip #{cid}")
        order = db.row("SELECT * FROM orders WHERE id = ?", (clip["order_id"],))
        segs = transcript.load(order["transcript_path"])
        checks = run_checks(clip, segs)

        review = llm.structured(
            "You are the QC editor at a short-form clipping agency. Judge the clip's on-screen hook (0-100) "
            "and whether the clip makes sense without the rest of the video.",
            f"Hook: {clip['hook']}\nTranscript of clip: {transcript.text_between(segs, clip['start'], clip['end'])}",
            Review, effort="low")
        if review:
            checks.append({"check": "editor_review", "ok": review.hook_score >= 50 and review.standalone,
                           "detail": f"hook {review.hook_score}/100; {'stands alone' if review.standalone else 'needs context'}. {review.notes}",
                           "fix": "weak_hook" if review.hook_score < 50 else None, "severity": "warn"})

        errors = [c for c in checks if not c["ok"] and c["severity"] == "error"]
        warns = [c for c in checks if not c["ok"] and c["severity"] == "warn"]
        qc_score = max(0, 100 - 25 * len(errors) - 8 * len(warns))
        attempts = clip["attempts"] + 1
        fixes = sorted({c["fix"] for c in errors if c["fix"]})

        if not errors:
            status = "awaiting_approval"
            msg = f"Clip #{cid} passed QC ({qc_score}/100), waiting for your approval"
        elif attempts >= config.MAX_QC_ATTEMPTS or not fixes:
            status = "qc_failed"
            msg = f"Clip #{cid} failed QC after {attempts} attempt(s): {', '.join(c['check'] for c in errors)}"
        else:
            status = "needs_recut" if RECUT & set(fixes) else "needs_recaption"
            msg = f"Clip #{cid} sent back ({status}): {', '.join(fixes)}"
        db.update("clips", cid, status=status, qc_report=checks, qc_score=qc_score, attempts=attempts,
                  fix_notes=fixes if status.startswith("needs_") else [])
        self.log(msg, "warn" if errors else "info", ("clip", cid))
        self.done()
        return True
