"""Caption agent: writes the on-screen hook and burns punchy word-chunk subtitles."""
import json
import re
from pathlib import Path

from pydantic import BaseModel

from .. import config, db, editing, handoff, llm, media, transcript
from .editors import load_map
from .strategist import EMOTION_WORDS, HOOK_WORDS
from .base import Agent

HOOK_SECONDS = 3.0
ASS_HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {config.OUT_W}
PlayResY: {config.OUT_H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,DejaVu Sans,86,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,7,2,2,80,80,560,1
Style: Hook,DejaVu Sans,68,&H00000000,&H00000000,&H0000E5FF,&H0000E5FF,1,0,0,0,100,100,0,0,3,18,0,8,90,90,240,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


class Hook(BaseModel):
    hook: str


def _t(sec: float, srt: bool = False) -> str:
    sec = max(0.0, sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    if srt:
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def chunk_words(words: list[dict], size: int) -> list[dict]:
    chunks = []
    for i in range(0, len(words), size):
        group = words[i:i + size]
        chunks.append({"start": group[0]["start"], "end": group[-1]["end"],
                       "text": " ".join(w["word"] for w in group)})
    for a, b in zip(chunks, chunks[1:]):  # no gaps/flicker between chunks
        if 0 < b["start"] - a["end"] < 0.4:
            a["end"] = b["start"]
    return chunks


def _esc(t: str) -> str:
    return t.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", " ")


HIGHLIGHT = r"{\c&H00E5FF&}"  # ASS colours are BGR: this is the hook-box yellow


def keyword(words: list[str]) -> int | None:
    """Index of the word in a caption chunk worth colouring, if any."""
    best, best_score = None, 0
    for i, w in enumerate(words):
        lw = re.sub(r"[^a-z0-9']", "", w.lower())
        score = (3 if re.search(r"\d", lw) else 0) + (2 if lw in EMOTION_WORDS else 0) \
            + (1 if lw in HOOK_WORDS and lw not in ("you", "people", "most") else 0) + (1 if len(lw) >= 8 else 0)
        if score > best_score:
            best, best_score = i, score
    return best


def caption_text(text: str, highlight: bool = True) -> str:
    words = _esc(text).upper().split()
    k = keyword(words) if highlight else None
    if k is not None:
        words[k] = HIGHLIGHT + words[k] + r"{\r}"
    return " ".join(words)


def build_ass(hook: str, chunks: list[dict], highlight: bool = True) -> str:
    lines = [f"Dialogue: 1,{_t(0)},{_t(HOOK_SECONDS)},Hook,,0,0,0,,{_esc(hook).upper()}"]
    for c in chunks:
        lines.append(f"Dialogue: 0,{_t(c['start'])},{_t(c['end'])},Caption,,0,0,0,,{caption_text(c['text'], highlight)}")
    return ASS_HEADER + "\n".join(lines) + "\n"


def build_srt(chunks: list[dict]) -> str:
    return "\n".join(f"{i}\n{_t(c['start'], True)} --> {_t(c['end'], True)}\n{c['text']}\n"
                     for i, c in enumerate(chunks, 1))


class CaptionAgent(Agent):
    name = "captioner"
    role = "Subtitles and hooks"

    def step(self) -> bool:
        clip = db.claim("clips", "edited", "captioning") or db.claim("clips", "needs_recaption", "captioning")
        if not clip:
            return False
        cid = clip["id"]
        notes = json.loads(clip["fix_notes"] or "[]")
        order = db.row("SELECT * FROM orders WHERE id = ?", (clip["order_id"],))
        segs = transcript.load(order["transcript_path"])
        self.working(f"Captioning clip #{cid}")

        hook = clip["hook"] or ""
        if "hook_too_long" in notes or "weak_hook" in notes or not hook:
            text = transcript.text_between(segs, clip["start"], clip["end"])
            ai = llm.structured(
                "Write the on-screen hook for a vertical short video: max 8 words, curiosity-driven, "
                "true to what is said, no emojis, no hashtags, no clickbait lies.",
                f"Clip transcript: {text}\nCurrent hook: {hook}", Hook, effort="low")
            if ai and ai.hook.strip():
                hook = ai.hook.strip()
            else:
                from .strategist import make_hook
                hook = make_hook(text, 8)
        em = load_map(clip)
        words = editing.remap_words(transcript.words_between(segs, clip["start"], clip["end"]), em["keeps"])
        chunks = chunk_words(words, 2 if "caption_density" in notes else 3)

        ass = Path(config.WORK) / f"clip_{cid}.ass"
        srt = Path(config.OUTPUT) / f"clip_{cid}.srt"
        ass.write_text(build_ass(hook, chunks))
        srt.write_text(build_srt(chunks))
        final = Path(config.OUTPUT) / f"clip_{cid}.mp4"
        src = clip["edit_path"] or clip["raw_path"]
        info = media.probe(src)
        media.burn_subtitles(src, str(ass), str(final), duration=info["duration"])
        otio = handoff.write_otio({**clip, "hook": hook}, order, em, media.probe(order["source_path"]), str(srt))
        thumb = Path(config.OUTPUT) / f"clip_{cid}.jpg"
        media.thumbnail(str(final), str(thumb), at=1.0)
        db.update("clips", cid, status="captioned", hook=hook, final_path=str(final),
                  srt_path=str(srt), thumb_path=str(thumb))
        self.log(f"Clip #{cid}: {len(chunks)} caption cues, keyword highlights, progress bar + hook \"{hook}\". "
                 f"Editable timeline: {Path(otio).name}", entity=("clip", cid))
        self.done()
        return True
