"""Tracker: records bets, follows closing lines, settles results."""
from __future__ import annotations

from ..models import Game
from .base import Agent, Desk
from .market import has_started, line_key


def grade(bet, home: str, away: str, scores: dict[str, float]) -> str:
    """Return won / lost / push for a bet given final scores."""
    sel, market, point = bet["selection"], bet["market"], bet["point"]
    hs, as_ = scores[home], scores[away]
    if market == "h2h":
        if hs == as_:
            if sel == "Draw":
                return "won"
            return "lost" if _is_three_way(bet) else "push"
        if sel == "Draw":
            return "lost"
        winner = home if hs > as_ else away
        return "won" if sel == winner else "lost"
    if market == "spreads":
        mine, theirs = (hs, as_) if sel == home else (as_, hs)
        diff = mine + point - theirs
    elif market == "totals":
        total = hs + as_
        diff = (total - point) if sel == "Over" else (point - total)
    else:
        return "void"
    return "won" if diff > 0 else "lost" if diff < 0 else "push"


def _is_three_way(bet) -> bool:
    return bet["sport"].startswith("soccer")


class Tracker(Agent):
    name = "Tracker"
    role = "Logs every bet, captures closing line value, and settles results."

    def __init__(self, mode: str = "paper", place: bool = True):
        self.mode = mode
        self.place = place

    def run(self, desk: Desk) -> None:
        self._update_closing(desk)
        if not self.place:
            return
        new = 0
        for o in desk.approved:
            if desk.ledger.record(o, mode=self.mode):
                new += 1
        self.say(desk, f"logged {new} new {self.mode} bets "
                       f"({len(desk.approved) - new} already on the books)")

    def _update_closing(self, desk: Desk) -> None:
        games: dict[str, Game] = {g.id: g for g in desk.games if not has_started(g)}
        updated = 0
        for bet in desk.ledger.open_bets():
            g = games.get(bet["game_id"])
            if not g:
                continue
            for q in g.quotes:
                if (q.book == bet["book"] and q.market == bet["market"] and q.outcome == bet["selection"]
                        and line_key(g, q.market, q.outcome, q.point) == bet["line_key"]):
                    desk.ledger.update_closing(bet["id"], q.price)
                    updated += 1
                    break
        if updated:
            self.say(desk, f"refreshed closing prices on {updated} open bets")

    def settle(self, desk: Desk, results: list[dict]) -> int:
        finals = {r["id"]: r for r in results if r.get("completed") and r.get("scores")}
        settled = 0
        for bet in desk.ledger.open_bets():
            r = finals.get(bet["game_id"])
            if not r:
                continue
            scores = {s["name"]: float(s["score"]) for s in r["scores"]}
            status = grade(bet, r["home_team"], r["away_team"], scores)
            desk.ledger.settle(bet["id"], status)
            settled += 1
        self.say(desk, f"settled {settled} bets")
        return settled
