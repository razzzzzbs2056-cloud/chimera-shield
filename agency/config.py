"""Runtime configuration, read from environment variables (see .env.example)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _flag(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def _list(name: str) -> list[str]:
    return [x.strip().lower() for x in os.getenv(name, "").split(",") if x.strip()]


@dataclass
class Config:
    company_name: str = field(default_factory=lambda: os.getenv("AGENCY_COMPANY_NAME", "Chimera Content Co."))
    model: str = field(default_factory=lambda: os.getenv("AGENCY_MODEL", "claude-opus-5"))
    effort: str = field(default_factory=lambda: os.getenv("AGENCY_EFFORT", "high"))
    # Server-side refusal fallbacks (re-runs a declined request on another model).
    fallbacks: bool = field(default_factory=lambda: _flag("AGENCY_FALLBACKS", True))
    # "mock" runs the whole company offline with scripted agents — no API key needed.
    mock: bool = field(default_factory=lambda: _flag("AGENCY_MOCK"))
    workspace: Path = field(default_factory=lambda: Path(os.getenv("AGENCY_WORKSPACE", "agency_output")))
    max_turns: int = field(default_factory=lambda: int(os.getenv("AGENCY_MAX_TURNS", "12")))

    # Email: dry-run by default. Real sends need AGENCY_SEND_EMAILS=true + SMTP settings.
    send_emails: bool = field(default_factory=lambda: _flag("AGENCY_SEND_EMAILS"))
    max_emails_per_run: int = field(default_factory=lambda: int(os.getenv("AGENCY_MAX_EMAILS", "10")))
    # Optional allowlist of recipient addresses or @domains. Empty = any recipient.
    email_allowlist: list[str] = field(default_factory=lambda: _list("AGENCY_EMAIL_ALLOWLIST"))
    smtp_host: str = field(default_factory=lambda: os.getenv("SMTP_HOST", ""))
    smtp_port: int = field(default_factory=lambda: int(os.getenv("SMTP_PORT", "587")))
    smtp_user: str = field(default_factory=lambda: os.getenv("SMTP_USER", ""))
    smtp_password: str = field(default_factory=lambda: os.getenv("SMTP_PASSWORD", ""))
    email_from: str = field(default_factory=lambda: os.getenv("EMAIL_FROM", ""))
