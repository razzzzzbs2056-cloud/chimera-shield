"""Market sub-agents: collect odds, shop lines, and price the true probability."""
from __future__ import annotations

from datetime import datetime, timezone
from statistics import mean

from ..books import is_sharp
from ..feeds import Feed
from ..models import Game, Line
from ..odds import devig, median
from .base import Agent, Desk


def line_key(game: Game, market: str, outcome: str, point) -> str:
    if market == "totals":
        return f"totals {point}"
    if market == "spreads":
        home_point = point if outcome == game.home else -point
        return f"spreads {game.home} {home_point:+g}"
    return market


def has_started(game: Game, now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    try:
        start = datetime.fromisoformat(game.commence_time.replace("Z", "+00:00"))
    except ValueError:
        return False
    return start <= now


class OddsScout(Agent):
    name = "OddsScout"
    role = "Pulls every game and every price from every book."

    def __init__(self, feed: Feed, include_live: bool = False):
        self.feed = feed
        self.include_live = include_live

    def run(self, desk: Desk) -> None:
        games = self.feed.games(desk.sports)
        if not self.include_live:
            games = [g for g in games if not has_started(g)]
        desk.games = games
        books = {q.book for g in games for q in g.quotes}
        self.say(desk, f"tracked {len(games)} games, {sum(len(g.quotes) for g in games)} "
                       f"prices across {len(books)} books")


class LineShopper(Agent):
    name = "LineShopper"
    role = "Groups identical lines across books so prices can be compared."

    def run(self, desk: Desk) -> None:
        lines: list[Line] = []
        for game in desk.games:
            by_key: dict[str, Line] = {}
            for q in game.quotes:
                key = line_key(game, q.market, q.outcome, q.point)
                line = by_key.setdefault(key, Line(game=game, market=q.market, key=key))
                line.offers.setdefault(q.outcome, {})[q.book] = q
            lines.extend(by_key.values())
        desk.lines = lines
        self.say(desk, f"built {len(lines)} comparable lines")


class FairValueAgent(Agent):
    """Estimates true probabilities by removing the bookmaker margin.

    Sharp books (Pinnacle, Circa, exchanges) are trusted first; otherwise the
    median de-vigged price across the whole market is used as consensus.
    """
    name = "FairValue"
    role = "De-vigs sharp/consensus prices into true probabilities."

    def __init__(self, method: str = "power", min_books: int = 3):
        self.method = method
        self.min_books = min_books

    def run(self, desk: Desk) -> None:
        priced = 0
        for line in desk.lines:
            outcomes = line.outcomes
            if len(outcomes) < 2:
                continue
            per_book: dict[str, list[float]] = {}
            for book in line.books_with_full_market():
                prices = [line.offers[o][book].price for o in outcomes]
                per_book[book] = devig(prices, self.method)
            if not per_book:
                continue
            sharp = [b for b in per_book if is_sharp(b)]
            if sharp:
                line.fair = {o: mean(per_book[b][i] for b in sharp) for i, o in enumerate(outcomes)}
                line.fair_source = "sharp:" + ",".join(sharp)
            elif len(per_book) >= self.min_books:
                raw = {o: median(per_book[b][i] for b in per_book) for i, o in enumerate(outcomes)}
                total = sum(raw.values())
                line.fair = {o: p / total for o, p in raw.items()}
                line.fair_source = f"consensus:{len(per_book)} books"
            else:
                continue
            priced += 1
        self.say(desk, f"priced {priced}/{len(desk.lines)} lines ({self.method} de-vig)")
