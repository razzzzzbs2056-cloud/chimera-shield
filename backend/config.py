"""Runtime settings for the ChimeraShield API.

`.env` is loaded once, before anything reads configuration, and every setting
is read from the environment lazily (at call time), so nothing captures a
value at import time. See codebase-audit.md B1.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

DEFAULT_TRIAGE_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_ALLOWED_ORIGINS = "http://localhost:3000"
DEFAULT_SCAN_RATE_LIMIT = "10/minute"
DEFAULT_MAX_EMAIL_BYTES = 50 * 1024


def load_environment(dotenv_path: str | None = None) -> None:
    """Load `.env` into the process environment. Real env vars win over `.env`."""
    load_dotenv(dotenv_path=dotenv_path, override=False)


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str | None
    triage_model: str
    allowed_origins: list[str]
    scan_rate_limit: str
    max_email_bytes: int
    environment: str

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value > 0 else default


def get_settings() -> Settings:
    key = (os.getenv("ANTHROPIC_API_KEY") or "").strip() or None
    origins = os.getenv("ALLOWED_ORIGINS", DEFAULT_ALLOWED_ORIGINS)
    return Settings(
        anthropic_api_key=key,
        triage_model=(os.getenv("TRIAGE_MODEL") or "").strip() or DEFAULT_TRIAGE_MODEL,
        allowed_origins=[o.strip() for o in origins.split(",") if o.strip()],
        scan_rate_limit=(os.getenv("SCAN_RATE_LIMIT") or "").strip() or DEFAULT_SCAN_RATE_LIMIT,
        max_email_bytes=_int_env("MAX_EMAIL_BYTES", DEFAULT_MAX_EMAIL_BYTES),
        environment=(os.getenv("ENV") or "development").strip().lower(),
    )
