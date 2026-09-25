"""EloModel: our own ratings-based opinion, blended with the market."""
from __future__ import annotations

from .base import Agent, Desk

# Home advantage in Elo points and K-factor per sport family.
HOME_ADV = {"americanfootball": 48, "basketball": 70, "baseball": 24, "icehockey": 33, "soccer": 60}
K_FACTOR = {"americanfootball": 20, "basketball": 18, "baseball": 6, "icehockey": 8, "soccer": 20}


def family(sport: str) -> str:
    return sport.split("_", 1)[0]


def elo_home_prob(r_home: float, r_away: float, hfa: float) -> float:
    return 1 / (1 + 10 ** (-(r_home + hfa - r_away) / 400))


class EloModel(Agent):
    """Learns team strength from final scores and nudges 2-way moneyline fair prices.

    ``weight`` is how much we trust our model vs. the sharp market (default 25%).
    It only speaks up once both teams have ``min_games`` results behind them.
    """
    name = "EloModel"
    role = "Rates every team from results and blends its view with the market."

    def __init__(self, weight: float = 0.25, min_games: int = 5, base: float = 1500.0):
        self.weight = weight
        self.min_games = min_games
        self.base = base

    # ---------------------------------------------------------------- learning
    def learn(self, desk: Desk, results: list[dict]) -> int:
        ledger = desk.ledger
        learned = 0
        for r in results:
            if not r.get("completed") or not r.get("scores") or ledger.result_processed(r["id"]):
                continue
            scores = {s["name"]: float(s["score"]) for s in r["scores"]}
            home, away, sport = r["home_team"], r["away_team"], r["sport_key"]
            ratings = ledger.ratings(sport)
            rh, ra = ratings.get(home, self.base), ratings.get(away, self.base)
            fam = family(sport)
            exp_home = elo_home_prob(rh, ra, HOME_ADV.get(fam, 40))
            actual = 1.0 if scores[home] > scores[away] else 0.5 if scores[home] == scores[away] else 0.0
            k = K_FACTOR.get(fam, 20)
            ledger.set_rating(sport, home, rh + k * (actual - exp_home))
            ledger.set_rating(sport, away, ra - k * (actual - exp_home))
            ledger.mark_result_processed(r["id"])
            learned += 1
        if learned:
            self.say(desk, f"learned from {learned} final scores")
        return learned

    # ---------------------------------------------------------------- opinion
    def run(self, desk: Desk) -> None:
        adjusted = 0
        for line in desk.lines:
            if line.market != "h2h" or len(line.fair) != 2:
                continue
            g = line.game
            if min(desk.ledger.rating_games(g.sport, g.home),
                   desk.ledger.rating_games(g.sport, g.away)) < self.min_games:
                continue
            ratings = desk.ledger.ratings(g.sport)
            p_home = elo_home_prob(ratings[g.home], ratings[g.away], HOME_ADV.get(family(g.sport), 40))
            market_home = line.fair[g.home]
            blended = (1 - self.weight) * market_home + self.weight * p_home
            line.fair = {g.home: blended, g.away: 1 - blended}
            line.fair_source += f"+elo({self.weight:.0%})"
            adjusted += 1
        self.say(desk, f"blended model view into {adjusted} moneylines")
