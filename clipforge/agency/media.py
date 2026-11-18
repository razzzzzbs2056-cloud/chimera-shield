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
        "fps": _fps(video.get("avg_frame_rate") or video.get("r_frame_rate") or "30/1"),
    }


def _fps(r: str) -> float:
    n, _, d = r.partition("/")
    try:
        v = float(n) / float(d or 1)
    except (ValueError, ZeroDivisionError):
        v = 0
    return round(v, 3) if 1 <= v <= 240 else 30.0


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


def burn_subtitles(src: str, ass_path: str, dst: str, duration: float | None = None,
                   bar_color: str = "0xFF5A36", bar_h: int = 14) -> None:
    """Burn ASS captions; with `duration`, add a progress bar that fills along the bottom."""
    esc = str(ass_path).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
    if duration:
        graph = (f"[0:v]ass='{esc}'[s];color=c={bar_color}:s={config.OUT_W}x{bar_h}:r=30[bar];"
                 f"[s][bar]overlay=x='-w+w*t/{duration:.3f}':y=H-{bar_h}:shortest=1[v]")
        vargs = ["-filter_complex", graph, "-map", "[v]", "-map", "0:a?"]
    else:
        vargs = ["-vf", f"ass='{esc}'"]
    _run(["ffmpeg", "-y", "-i", src, *vargs,
          "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
          "-c:a", "copy", "-movflags", "+faststart", dst])


def thumbnail(src: str, dst: str, at: float = 1.0) -> None:
    _run(["ffmpeg", "-y", "-ss", f"{at:.2f}", "-i", src, "-frames:v", "1", "-vf", "scale=360:-2", dst])


def mean_volume_db(src: str) -> float | None:
    p = subprocess.run(["ffmpeg", "-i", src, "-af", "volumedetect", "-vn", "-f", "null", "-"],
                       capture_output=True, text=True, timeout=300)
    m = re.search(r"mean_volume:\s*(-?[\d.]+) dB", p.stderr)
    return float(m.group(1)) if m else None


ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p"]


def silences(src: str, noise_db: float = -35, min_dur: float = 0.6) -> list[tuple[float, float]]:
    """Return [(start, end)] spans where the audio stays below `noise_db` for `min_dur`+ seconds."""
    p = subprocess.run(["ffmpeg", "-i", src, "-af", f"silencedetect=noise={noise_db}dB:d={min_dur}", "-vn", "-f", "null", "-"],
                       capture_output=True, text=True, timeout=300)
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", p.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", p.stderr)]
    if len(ends) < len(starts):  # silence runs to the end of the file
        ends.append(probe(src)["duration"])
    return [(max(0.0, a), b) for a, b in zip(starts, ends)]


def keep_segments(src: str, keeps: list[tuple[float, float]], dst: str) -> None:
    """Concatenate only the `keeps` spans of `src` (video and audio stay in sync)."""
    expr = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in keeps)
    _run(["ffmpeg", "-y", "-i", src,
          "-vf", f"select='{expr}',setpts=N/FRAME_RATE/TB",
          "-af", f"aselect='{expr}',asetpts=N/SR/TB",
          *ENC, "-c:a", "aac", "-b:a", "192k", "-ar", "48000", dst])


def zoom(src: str, z_expr: str, dst: str, fps: int = 30) -> None:
    """Centre zoom driven by a per-frame expression of `it` (seconds)."""
    w, h = config.OUT_W, config.OUT_H
    _run(["ffmpeg", "-y", "-i", src,
          "-vf", f"zoompan=z='{z_expr}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={w}x{h}:fps={fps},setsar=1",
          "-map", "0:v", "-map", "0:a?", *ENC, "-c:a", "copy", "-movflags", "+faststart", dst])


def master_audio(src: str, dst: str, music: str | None = None, music_db: float = -20) -> None:
    """Normalise to -14 LUFS (TikTok/Reels/Shorts target). With `music`, lay a looped
    bed under the voice that ducks automatically whenever someone speaks."""
    if music:
        graph = (f"[1:a]volume={music_db}dB,aformat=channel_layouts=stereo[m];"
                 f"[0:a]aformat=channel_layouts=stereo,asplit[v][sc];"
                 f"[m][sc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400[duck];"
                 f"[v][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
        cmd = ["ffmpeg", "-y", "-i", src, "-stream_loop", "-1", "-i", music, "-filter_complex", graph,
               "-map", "0:v", "-map", "[a]"]
    else:
        cmd = ["ffmpeg", "-y", "-i", src, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-map", "0:v", "-map", "0:a"]
    _run(cmd + ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", dst])


def integrated_loudness(src: str) -> float | None:
    p = subprocess.run(["ffmpeg", "-i", src, "-af", "ebur128", "-vn", "-f", "null", "-"],
                       capture_output=True, text=True, timeout=300)
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", p.stderr)
    return float(m[-1]) if m else None
