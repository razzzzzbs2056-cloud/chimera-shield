"""Email delivery with guard rails.

Every email is written to ``<workspace>/outbox/*.eml`` so there is always a
record. It is only handed to an SMTP server when ``AGENCY_SEND_EMAILS=true``
and SMTP is configured; otherwise the run is a dry run.
"""

from __future__ import annotations

import re
import smtplib
from email.message import EmailMessage
from pathlib import Path

from agency.config import Config

_ADDRESS = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class EmailError(Exception):
    pass


class Mailer:
    def __init__(self, config: Config):
        self.config = config
        self.outbox = config.workspace / "outbox"
        self.sent_count = 0

    def _check(self, to: str) -> None:
        if not _ADDRESS.match(to):
            raise EmailError(f"invalid recipient address: {to!r}")
        allow = self.config.email_allowlist
        if allow and to.lower() not in allow and "@" + to.lower().split("@")[1] not in allow:
            raise EmailError(f"{to} is not on AGENCY_EMAIL_ALLOWLIST")
        if self.sent_count >= self.config.max_emails_per_run:
            raise EmailError(f"per-run email limit ({self.config.max_emails_per_run}) reached")

    def send(self, to: str, subject: str, body: str) -> str:
        self._check(to)
        msg = EmailMessage()
        msg["From"] = self.config.email_from or f"{self.config.company_name} <no-reply@example.com>"
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        self.outbox.mkdir(parents=True, exist_ok=True)
        self.sent_count += 1
        path: Path = self.outbox / f"{self.sent_count:03d}-{_slug(subject)}.eml"
        path.write_bytes(bytes(msg))

        if not (self.config.send_emails and self.config.smtp_host):
            return f"DRY RUN: email to {to} saved to {path} (set AGENCY_SEND_EMAILS=true and SMTP_* to deliver)"

        with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port, timeout=30) as smtp:
            smtp.starttls()
            if self.config.smtp_user:
                smtp.login(self.config.smtp_user, self.config.smtp_password)
            smtp.send_message(msg)
        return f"SENT: email to {to} delivered via {self.config.smtp_host} (copy at {path})"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "email"
