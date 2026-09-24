"""The company board: one shared record of everything the agents produce.

Every campaign, piece of content, email and code file lands here, so any
agent (and the CEO in particular) can see the whole marketing picture.
The board is persisted as JSON in the run's workspace directory.
"""

from __future__ import annotations

import json
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

KINDS = ("campaign", "content", "email", "code", "note")


@dataclass
class Entry:
    id: int
    kind: str
    author: str
    title: str
    body: str
    meta: dict = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )


class Board:
    def __init__(self, path: Path | None = None):
        self.path = path
        self._lock = threading.Lock()
        self.entries: list[Entry] = []
        if path and path.exists():
            self.entries = [Entry(**e) for e in json.loads(path.read_text())]

    def post(self, kind: str, author: str, title: str, body: str, **meta) -> Entry:
        if kind not in KINDS:
            raise ValueError(f"unknown kind {kind!r}; expected one of {KINDS}")
        with self._lock:
            entry = Entry(len(self.entries) + 1, kind, author, title, body, meta)
            self.entries.append(entry)
            self._save()
        return entry

    def list(self, kind: str | None = None) -> list[Entry]:
        return [e for e in self.entries if kind in (None, e.kind)]

    def summary(self, kind: str | None = None, max_body: int = 400) -> str:
        """Plain-text view of the board that agents read as a tool result."""
        entries = self.list(kind)
        if not entries:
            return "The board is empty."
        lines = []
        for e in entries:
            body = e.body if len(e.body) <= max_body else e.body[:max_body] + "…"
            meta = f" {e.meta}" if e.meta else ""
            lines.append(f"#{e.id} [{e.kind}] {e.title} — by {e.author}{meta}\n{body}")
        return "\n\n".join(lines)

    def _save(self) -> None:
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps([asdict(e) for e in self.entries], indent=2))
