import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(os.getenv("CLIPFORGE_HOME", Path(__file__).resolve().parent.parent / "data"))
UPLOADS = ROOT / "uploads"
WORK = ROOT / "work"
OUTPUT = ROOT / "output"
DB_PATH = ROOT / "clipforge.db"
for p in (UPLOADS, WORK, OUTPUT):
    p.mkdir(parents=True, exist_ok=True)

ANTHROPIC_MODEL = os.getenv("CLIPFORGE_MODEL", "claude-opus-5-5")
# AI features turn on automatically when an Anthropic credential is present.
USE_LLM = os.getenv("CLIPFORGE_USE_LLM", "auto")

TICK_SECONDS = float(os.getenv("CLIPFORGE_TICK", "1.0"))
OUT_W, OUT_H = 1080, 1920
MIN_CLIP_S, MAX_CLIP_S = 15.0, 60.0
MAX_QC_ATTEMPTS = 2

# Packages: name -> (clips per video, price in cents)
PACKAGES = {
    "starter": (3, 9900),
    "growth": (6, 17900),
    "pro": (10, 27900),
}
