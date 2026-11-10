"""Alerts: always logged; sent to Telegram when a bot token and chat id are configured."""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.parse
import urllib.request

log = logging.getLogger("trader.alerts")


class Alerts:
    def __init__(self, token: str | None = None, chat_id: str | None = None, min_gap_s: float = 300.0):
        self.token = token or os.environ.get("TELEGRAM_BOT_TOKEN") or None
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID") or None
        self.min_gap_s = min_gap_s
        self._last: dict[str, float] = {}
        self.sent: list[tuple[str, str]] = []  # (level, text) kept for tests and the nightly report

    @property
    def telegram_enabled(self) -> bool:
        return bool(self.token and self.chat_id)

    def notify(self, level: str, text: str, key: str | None = None) -> bool:
        """Returns True if the alert was emitted (not rate-limited). Never raises."""
        now = time.monotonic()
        if key is not None and now - self._last.get(key, -1e18) < self.min_gap_s:
            return False
        if key is not None:
            self._last[key] = now
        self.sent.append((level, text))
        log.log(logging.ERROR if level in ("critical", "error") else logging.WARNING, "[%s] %s", level, text)
        if self.telegram_enabled:
            try:
                body = urllib.parse.urlencode({"chat_id": self.chat_id, "text": f"[{level.upper()}] {text}"})
                req = urllib.request.Request(
                    f"https://api.telegram.org/bot{self.token}/sendMessage", data=body.encode())
                with urllib.request.urlopen(req, timeout=10) as r:
                    json.load(r)
            except Exception as e:  # an alert failure must never stop trading logic
                log.error("telegram send failed: %s", type(e).__name__)
        return True
