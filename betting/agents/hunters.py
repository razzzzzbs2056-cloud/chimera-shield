"""Opportunity hunters: +EV value bets and cross-book arbitrage."""
from __future__ import annotations

from ..books import is_sharp
from ..models import Opportunity
from ..odds import arbitrage, expected_value
from .base import Agent, Desk


class ValueHunter(Agent):
    """Finds prices that beat the fair line by at least ``min_edge``.

    Edges above ``max_edge`` are usually stale lines or data errors, so they are
    skipped rather than trusted.
    """
    name = "ValueHunter"
    role = "Finds +EV prices at soft books versus the fair line."

    def __init__(self, min_edge: float = 0.02, max_edge: float = 0.15,
                 min_price: float = 1.25, max_price: float = 6.0, bet_sharp_books: bool = False):
        self.min_edge = min_edge
        self.max_edge = max_edge
        self.min_price = min_price
        self.max_price = max_price
        self.bet_sharp_books = bet_sharp_books

    def run(self, desk: Desk) -> None:
        found = 0
        for line in desk.lines:
            for outcome, prob in line.fair.items():
                candidates = [q for q in line.offers[outcome].values()
                              if self.bet_sharp_books or not is_sharp(q.book)]
                if not candidates:
                    continue
                best = max(candidates, key=lambda q: q.price)
                ev = expected_value(prob, best.price)
                if not (self.min_edge <= ev <= self.max_edge):
                    continue
                if not (self.min_price <= best.price <= self.max_price):
                    continue
                desk.opportunities.append(Opportunity(
                    kind="value", game=line.game, line_key=line.key, market=line.market,
                    selection=outcome, point=best.point, book=best.book, price=best.price,
                    fair_prob=prob, edge=ev, notes=line.fair_source))
                found += 1
        self.say(desk, f"found {found} +EV bets (edge >= {self.min_edge:.1%})")


class ArbHunter(Agent):
    """Finds lines where the best price on every outcome guarantees a profit."""
    name = "ArbHunter"
    role = "Locks risk-free margin when books disagree enough."

    def __init__(self, min_margin: float = 0.005, max_margin: float = 0.10):
        self.min_margin = min_margin
        self.max_margin = max_margin

    def run(self, desk: Desk) -> None:
        found = 0
        for line in desk.lines:
            outcomes = line.outcomes
            if len(outcomes) < 2:
                continue
            if line.market == "h2h" and line.game.sport.startswith("soccer") and "Draw" not in outcomes:
                continue  # incomplete 3-way market
            best = [line.best(o) for o in outcomes]
            margin = arbitrage([q.price for q in best])
            if margin is None or not (self.min_margin <= margin <= self.max_margin):
                continue
            group = f"arb:{line.game.id}:{line.key}"
            for o, q in zip(outcomes, best):
                desk.opportunities.append(Opportunity(
                    kind="arb", game=line.game, line_key=line.key, market=line.market,
                    selection=o, point=q.point, book=q.book, price=q.price,
                    fair_prob=line.fair.get(o, 1 / q.price), edge=margin, group=group,
                    notes=f"{len(best)}-leg arb"))
            found += 1
        self.say(desk, f"found {found} arbitrage lines (margin >= {self.min_margin:.1%})")
