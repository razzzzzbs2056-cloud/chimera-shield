"""Analyst: optional Claude-powered desk briefing on the approved card."""
from __future__ import annotations

import os

from ..books import book_name
from ..odds import decimal_to_american
from .base import Agent, Desk

MODEL = os.getenv("BETTING_ANALYST_MODEL", "claude-opus-5")

SYSTEM = """You are the lead analyst on a quantitative sports-betting desk.
The quant agents have already priced every line against sharp/consensus fair odds
and sized stakes with fractional Kelly. Your job is a short, skeptical briefing:
- For each bet, name what could make the edge fake (stale line, injury/lineup news,
  weather, rest/travel, limits, palpable-error risk) and what to verify before placing.
- Flag correlated bets and anything that looks too good to be true.
- Finish with a one-line overall read of the card.
Be concise and concrete. Never promise profit; betting outcomes are uncertain."""


class Analyst(Agent):
    name = "Analyst"
    role = "Claude reviews the card for news, correlation and too-good-to-be-true risks."

    def __init__(self, enabled: bool | None = None, max_bets: int = 15):
        self.enabled = bool(os.getenv("ANTHROPIC_API_KEY")) if enabled is None else enabled
        self.max_bets = max_bets

    def run(self, desk: Desk) -> None:
        if not self.enabled or not desk.approved:
            return
        try:
            import anthropic
        except ImportError:
            self.say(desk, "anthropic SDK not installed; skipping briefing")
            return

        rows = []
        for o in desk.approved[: self.max_bets]:
            pt = f" {o.point:+g}" if o.point is not None and o.market == "spreads" else (
                f" {o.point:g}" if o.point is not None else "")
            rows.append(f"- [{o.kind}] {o.game.label} ({o.game.sport}, {o.game.commence_time}): "
                        f"{o.selection}{pt} {o.market} @ {o.price:.2f} ({decimal_to_american(o.price):+d}) "
                        f"at {book_name(o.book)}, fair p={o.fair_prob:.3f}, edge={o.edge:.2%}, "
                        f"stake=${o.stake:.2f}")
        client = anthropic.Anthropic()
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=4000,
                system=SYSTEM,
                messages=[{"role": "user", "content": "Today's card:\n" + "\n".join(rows)}],
            )
        except anthropic.APIConnectionError:
            self.say(desk, "could not reach the Claude API; skipping briefing")
            return
        except anthropic.APIStatusError as e:
            self.say(desk, f"Claude API error {e.status_code}; skipping briefing")
            return
        if resp.stop_reason == "refusal":
            self.say(desk, "Claude declined to brief this card")
            return
        desk.briefing = "".join(b.text for b in resp.content if b.type == "text")
        self.say(desk, "briefing ready")
