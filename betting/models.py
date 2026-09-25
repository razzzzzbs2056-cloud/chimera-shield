"""Core data structures shared by every agent."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass(frozen=True)
class Quote:
    """One price offered by one book on one outcome."""
    book: str
    market: str            # h2h | spreads | totals
    outcome: str           # team name, "Draw", "Over", "Under"
    price: float           # decimal odds
    point: Optional[float] = None


@dataclass
class Game:
    id: str
    sport: str
    commence_time: str
    home: str
    away: str
    quotes: list[Quote] = field(default_factory=list)

    @property
    def label(self) -> str:
        return f"{self.away} @ {self.home}"


@dataclass
class Line:
    """A comparable market across books, e.g. 'spreads -3.5' or 'totals 47.5'."""
    game: Game
    market: str
    key: str                                   # stable identifier for this line
    # outcome name -> {book -> Quote}
    offers: dict[str, dict[str, Quote]] = field(default_factory=dict)
    fair: dict[str, float] = field(default_factory=dict)   # outcome -> true probability
    fair_source: str = ""

    @property
    def outcomes(self) -> list[str]:
        return sorted(self.offers)

    def best(self, outcome: str) -> Quote:
        return max(self.offers[outcome].values(), key=lambda q: q.price)

    def books_with_full_market(self) -> list[str]:
        books = None
        for per_book in self.offers.values():
            books = set(per_book) if books is None else books & set(per_book)
        return sorted(books or [])


@dataclass
class Opportunity:
    kind: str               # value | arb
    game: Game
    line_key: str
    market: str
    selection: str
    point: Optional[float]
    book: str
    price: float
    fair_prob: float
    edge: float             # EV per unit (value) or locked margin (arb)
    stake: float = 0.0
    group: Optional[str] = None   # arb legs share a group id
    notes: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["game"] = {"id": self.game.id, "sport": self.game.sport,
                     "label": self.game.label, "commence_time": self.game.commence_time}
        return d
