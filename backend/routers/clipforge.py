"""
ClipForge Studio — optional AI assist endpoints.

These power the *optional* hosted-AI features of the ClipForge Studio frontend
(`clipforge-studio/`). The app works fully offline without them; these endpoints
only add:

  * POST /api/clipforge/caption-ideas  — generate caption / hook ideas with Claude
  * POST /api/clipforge/transcribe     — speech-to-text for auto-captions (Whisper)

Both degrade gracefully when their API key is missing, so the frontend never
hard-fails: caption ideas fall back to a built-in list, and transcription
returns a clear 501 the UI explains to the user.
"""

import os
import json

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

router = APIRouter(prefix="/api/clipforge", tags=["clipforge"])

# Built-in fallback ideas, returned when no ANTHROPIC_API_KEY is configured so
# the UI still works offline.
FALLBACK_IDEAS = [
    "Wait for it…",
    "POV: you finally get it",
    "The part nobody talks about",
    "Save this for later",
    "Watch till the end 👀",
    "This changed everything",
]


class CaptionIdeasRequest(BaseModel):
    topic: str = ""
    transcript: str = ""
    platform: str = "TikTok / Reels / Shorts"


class CaptionIdeasResponse(BaseModel):
    ideas: list[str]
    source: str  # "ai" | "fallback"
    note: str = ""


def _anthropic_client():
    """Create an Anthropic client only if a key is present (avoids import-time crash)."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key or key.startswith("your_"):
        return None
    import anthropic

    return anthropic.Anthropic(api_key=key)


@router.post("/caption-ideas", response_model=CaptionIdeasResponse)
def caption_ideas(request: CaptionIdeasRequest):
    client = _anthropic_client()
    if client is None:
        return CaptionIdeasResponse(
            ideas=FALLBACK_IDEAS,
            source="fallback",
            note="Set ANTHROPIC_API_KEY on the backend to generate custom, on-topic hooks with Claude.",
        )

    context_bits = []
    if request.topic.strip():
        context_bits.append(f"Topic / working title: {request.topic.strip()}")
    if request.transcript.strip():
        # Keep the transcript bounded — we only need the gist for hooks.
        context_bits.append(f"Transcript excerpt: {request.transcript.strip()[:1500]}")
    context = "\n".join(context_bits) or "A short-form social video for a creator."

    prompt = f"""You are a short-form social video strategist who writes scroll-stopping hook captions.

Write 6 punchy caption / hook ideas for this clip, optimised for {request.platform}.

Context:
{context}

Rules:
- Each idea is a single line, max ~60 characters, no hashtags.
- Make them curiosity-driven, bold, and varied in angle.
- Return JSON ONLY, no extra text, in exactly this shape:
{{"ideas": ["idea 1", "idea 2", "idea 3", "idea 4", "idea 5", "idea 6"]}}"""

    try:
        message = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in message.content if getattr(b, "type", "") == "text")
        data = json.loads(text)
        ideas = [str(i).strip() for i in data.get("ideas", []) if str(i).strip()]
        if not ideas:
            raise ValueError("no ideas returned")
        return CaptionIdeasResponse(ideas=ideas[:8], source="ai")
    except (json.JSONDecodeError, ValueError, KeyError):
        return CaptionIdeasResponse(
            ideas=FALLBACK_IDEAS,
            source="fallback",
            note="Claude returned an unexpected format — showing built-in ideas.",
        )
    except Exception as exc:  # network / auth / rate-limit, etc.
        raise HTTPException(status_code=502, detail=f"AI request failed: {exc}")


class TranscribeResponse(BaseModel):
    text: str


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(file: UploadFile = File(...)):
    key = os.getenv("OPENAI_API_KEY")
    if not key or key.startswith("your_"):
        raise HTTPException(
            status_code=501,
            detail=(
                "Transcription is not configured. Set OPENAI_API_KEY on the backend to enable "
                "speech-to-text, or add an in-browser Whisper model (transformers.js) for a "
                "fully local option."
            ),
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    try:
        from openai import OpenAI

        oai = OpenAI(api_key=key)
        result = oai.audio.transcriptions.create(
            model="whisper-1",
            file=(file.filename or "clip.mp4", contents),
        )
        return TranscribeResponse(text=getattr(result, "text", "") or "")
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Transcription failed. The browser-playable file may have an audio codec the "
                f"transcription service can't read. ({exc})"
            ),
        )
