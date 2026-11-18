"""Transcript loading and transcription.

Canonical form: list of {"start": float, "end": float, "text": str}.
Accepted inputs: our JSON, Whisper JSON ({"segments": [...]}), SRT, WebVTT.
If none is supplied, faster-whisper is used when installed."""
import json
import re
from pathlib import Path

_TS = re.compile(r"(?:(\d+):)?(\d+):(\d+)[.,](\d+)")


def _ts(s: str) -> float:
    m = _TS.search(s)
    if not m:
        raise ValueError(f"Bad timestamp: {s}")
    h, mi, se, ms = m.groups()
    return int(h or 0) * 3600 + int(mi) * 60 + int(se) + int(ms.ljust(3, "0")[:3]) / 1000


def parse(text: str, filename: str = "") -> list[dict]:
    stripped = text.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        data = json.loads(text)
        segs = data.get("segments", data) if isinstance(data, dict) else data
        out = [{"start": float(s["start"]), "end": float(s["end"]), "text": str(s["text"]).strip()} for s in segs]
    else:
        out = []
        for block in re.split(r"\n\s*\n", text.replace("\r", "")):
            lines = [l for l in block.strip().split("\n") if l.strip()]
            arrow = next((i for i, l in enumerate(lines) if "-->" in l), None)
            if arrow is None:
                continue
            a, b = lines[arrow].split("-->")
            body = " ".join(lines[arrow + 1:])
            body = re.sub(r"<[^>]+>", "", body).strip()
            if body:
                out.append({"start": _ts(a), "end": _ts(b.split()[0]), "text": body})
    out = [s for s in out if s["text"] and s["end"] > s["start"]]
    if not out:
        raise ValueError("Transcript contained no usable segments")
    return sorted(out, key=lambda s: s["start"])


def transcribe(video_path: str) -> list[dict]:
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except ImportError as e:
        raise RuntimeError(
            "No transcript supplied and faster-whisper is not installed. "
            "Upload an SRT/VTT/JSON transcript or `pip install faster-whisper`."
        ) from e
    model = WhisperModel("small", compute_type="int8")
    segments, _ = model.transcribe(video_path, vad_filter=True)
    return [{"start": s.start, "end": s.end, "text": s.text.strip()} for s in segments if s.text.strip()]


def save(segments: list[dict], path: Path) -> None:
    path.write_text(json.dumps(segments, indent=1))


def load(path: str) -> list[dict]:
    return json.loads(Path(path).read_text())


def words_between(segments: list[dict], start: float, end: float) -> list[dict]:
    """Approximate per-word timings (relative to `start`) by spreading each
    segment's words evenly across its duration."""
    words = []
    for s in segments:
        if s["end"] <= start or s["start"] >= end:
            continue
        toks = s["text"].split()
        if not toks:
            continue
        step = (s["end"] - s["start"]) / len(toks)
        for i, w in enumerate(toks):
            ws = s["start"] + i * step
            we = ws + step
            if we <= start or ws >= end:
                continue
            words.append({"word": w, "start": max(ws, start) - start, "end": min(we, end) - start})
    return words


def text_between(segments: list[dict], start: float, end: float) -> str:
    return " ".join(s["text"] for s in segments if s["end"] > start and s["start"] < end)
