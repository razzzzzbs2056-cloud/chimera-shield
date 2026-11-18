"""ffmpeg / ffprobe helpers."""
import json
import re
import subprocess
from pathlib import Path

from . import config


class MediaError(RuntimeError):
    pass


def _run(cmd: list[str], timeout: int = 900) -> subprocess.CompletedProcess:
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise MediaError(f"{cmd[0]} failed: {p.stderr.strip()[-600:]}")
    return p


def probe(path: str | Path) -> dict:
    out = _run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)]).stdout
    data = json.loads(out)
    video = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    audio = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
    if not video:
        raise MediaError("No video stream found")
    return {
        "duration": float(data["format"].get("duration", 0)),
        "width": int(video["width"]),
        "height": int(video["height"]),
        "has_audio": audio is not None,
        "size_bytes": int(data["format"].get("size", 0)),
    }


def cut_vertical(src: str, start: float, end: float, dst: str) -> None:
    """Cut [start, end] and reframe to 9:16: centre crop for wide sources, with a
    blurred fill behind the full frame so nothing important is cropped away."""
    w, h = config.OUT_W, config.OUT_H
    vf = (
        f"[0:v]split[a][b];"
        f"[a]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=20:2[bg];"
        f"[b]scale={w}:-2[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[v]"
    )
    _run([
        "ffmpeg", "-y", "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", src,
        "-filter_complex", vf, "-map", "[v]", "-map", "0:a?",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", dst,
    ])


def burn_subtitles(src: str, ass_path: str, dst: str) -> None:
    esc = str(ass_path).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
    _run([
        "ffmpeg", "-y", "-i", src, "-vf", f"ass='{esc}'",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
        "-c:a", "copy", "-movflags", "+faststart", dst,
    ])


def thumbnail(src: str, dst: str, at: float = 1.0) -> None:
    _run(["ffmpeg", "-y", "-ss", f"{at:.2f}", "-i", src, "-frames:v", "1", "-vf", "scale=360:-2", dst])


def mean_volume_db(src: str) -> float | None:
    p = subprocess.run(["ffmpeg", "-i", src, "-af", "volumedetect", "-vn", "-f", "null", "-"],
                       capture_output=True, text=True, timeout=300)
    m = re.search(r"mean_volume:\s*(-?[\d.]+) dB", p.stderr)
    return float(m.group(1)) if m else None
