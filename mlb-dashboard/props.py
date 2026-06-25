"""Prop projection math.

Projections use a player's season per-game (or per-start) rate as the mean of a
Poisson distribution, then derive over/under probabilities for a betting line
and convert those to fair American odds. This is a simple, transparent baseline
model -- not a market-beating one -- meant to make the mechanics legible.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


# --- prop catalogues -------------------------------------------------------
# Each prop maps a friendly label to the Stats API stat key it sums, the group
# it belongs to, and a sensible default betting line.

HITTING_PROPS: dict[str, dict] = {
    "Hits": {"key": "hits", "line": 0.5},
    "Total Bases": {"key": "totalBases", "line": 1.5},
    "Home Runs": {"key": "homeRuns", "line": 0.5},
    "RBIs": {"key": "rbi", "line": 0.5},
    "Runs": {"key": "runs", "line": 0.5},
    "Stolen Bases": {"key": "stolenBases", "line": 0.5},
    "Walks": {"key": "baseOnBalls", "line": 0.5},
    "Strikeouts": {"key": "strikeOuts", "line": 0.5},
}

PITCHING_PROPS: dict[str, dict] = {
    "Strikeouts": {"key": "strikeOuts", "line": 5.5},
    "Hits Allowed": {"key": "hits", "line": 5.5},
    "Walks": {"key": "baseOnBalls", "line": 1.5},
    "Earned Runs": {"key": "earnedRuns", "line": 2.5},
}


# --- distribution helpers --------------------------------------------------


def poisson_pmf(k: int, lam: float) -> float:
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-lam) * lam**k / math.factorial(k)


def poisson_cdf(k: int, lam: float) -> float:
    return sum(poisson_pmf(i, lam) for i in range(0, max(k, 0) + 1))


def prob_over(line: float, lam: float) -> float:
    """P(X strictly greater than the line) for a Poisson(lam) count.

    For a half-line like 1.5, 'over' means X >= 2, i.e. 1 - CDF(1).
    """
    threshold = math.floor(line)  # need at least threshold+1 to clear the line
    return 1.0 - poisson_cdf(threshold, lam)


def american_odds(p: float) -> str:
    """Fair American moneyline odds implied by probability p (no vig)."""
    if p <= 0:
        return "+∞"
    if p >= 1:
        return "-∞"
    if p >= 0.5:
        return f"-{round(100 * p / (1 - p))}"
    return f"+{round(100 * (1 - p) / p)}"


# --- projection ------------------------------------------------------------


@dataclass
class Projection:
    label: str
    stat_key: str
    line: float
    lam: float          # projected mean (expected value) for the game/start
    season_total: int
    games: int
    p_over: float = field(init=False)
    p_under: float = field(init=False)
    odds_over: str = field(init=False)
    odds_under: str = field(init=False)

    def __post_init__(self) -> None:
        self.p_over = prob_over(self.line, self.lam)
        self.p_under = 1.0 - self.p_over
        self.odds_over = american_odds(self.p_over)
        self.odds_under = american_odds(self.p_under)

    def distribution(self, max_k: Optional[int] = None) -> list[tuple[int, float]]:
        if max_k is None:
            max_k = max(6, math.ceil(self.lam * 2) + 1)
        return [(k, poisson_pmf(k, self.lam)) for k in range(0, max_k + 1)]


def _to_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def project_hitting(stat: dict, label: str, line: float,
                    projected_pa: Optional[float] = None) -> Optional[Projection]:
    games = int(_to_float(stat.get("gamesPlayed")))
    if games <= 0:
        return None
    spec = HITTING_PROPS[label]
    total = int(_to_float(stat.get(spec["key"])))
    lam = total / games

    # Optional playing-time lever: scale the rate by projected plate
    # appearances relative to the player's season PA/G.
    season_pa = _to_float(stat.get("plateAppearances"))
    if projected_pa and season_pa > 0:
        pa_per_game = season_pa / games
        if pa_per_game > 0:
            lam *= projected_pa / pa_per_game

    return Projection(label, spec["key"], line, lam, total, games)


def project_pitching(stat: dict, label: str, line: float) -> Optional[Projection]:
    starts = int(_to_float(stat.get("gamesStarted")))
    appearances = int(_to_float(stat.get("gamesPlayed")))
    denom = starts if starts > 0 else appearances
    if denom <= 0:
        return None
    spec = PITCHING_PROPS[label]
    total = int(_to_float(stat.get(spec["key"])))
    lam = total / denom
    return Projection(label, spec["key"], line, lam, total, denom)


def season_pa_per_game(stat: dict) -> Optional[float]:
    games = _to_float(stat.get("gamesPlayed"))
    pa = _to_float(stat.get("plateAppearances"))
    if games > 0 and pa > 0:
        return pa / games
    return None
