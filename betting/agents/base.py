from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ..ledger import Ledger
from ..models import Game, Line, Opportunity


@dataclass
class Desk:
    """Shared blackboard every agent reads from and writes to during a run."""
    ledger: Ledger
    sports: list[str]
    games: list[Game] = field(default_factory=list)
    lines: list[Line] = field(default_factory=list)
    opportunities: list[Opportunity] = field(default_factory=list)
    approved: list[Opportunity] = field(default_factory=list)
    recorded: list[int] = field(default_factory=list)
    scores: list[dict] = field(default_factory=list)
    briefing: Optional[str] = None
    log: list[str] = field(default_factory=list)


class Agent:
    name = "agent"
    role = ""

    def run(self, desk: Desk) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    def say(self, desk: Desk, msg: str) -> None:
        desk.log.append(f"[{self.name}] {msg}")
