"""Turn raw season stat lines into per-PA / per-match model inputs.

Small samples are regressed toward league average (``rate = (x + k*lg) / (n + k)``),
so a hot 60-PA stretch can't masquerade as true talent.
"""
from __future__ import annotations

from .baseball import EVENTS, LEAGUE

BATTER_K = 220   # PA of league-average "ballast"
PITCHER_K = 300  # BF of ballast


def _shrink(count: float, n: float, lg: float, k: float) -> float:
    return (count + k * lg) / (n + k)


def batter_rates(season: dict) -> dict:
    """season: pa, h, 2b, 3b, hr, bb, (hbp), so  -> per-PA event rates."""
    pa = season["pa"]
    singles = season["h"] - season.get("2b", 0) - season.get("3b", 0) - season["hr"]
    counts = {"k": season["so"], "bb": season["bb"] + season.get("hbp", 0), "1b": singles,
              "2b": season.get("2b", 0), "3b": season.get("3b", 0), "hr": season["hr"]}
    return {e: round(_shrink(counts[e], pa, LEAGUE[e], BATTER_K), 4) for e in EVENTS}


def pitcher_rates(season: dict) -> tuple[dict, float]:
    """season: ip, h, hr, bb, (hbp), so, gs  -> (per-BF rates, batters faced per start)."""
    ip = season["ip"]
    outs = int(ip) * 3 + round((ip - int(ip)) * 10)
    bb = season["bb"] + season.get("hbp", 0)
    bf = season.get("bf") or outs + season["h"] + bb
    hits_non_hr = season["h"] - season["hr"]
    counts = {"k": season["so"], "bb": bb, "1b": hits_non_hr * 0.73, "2b": hits_non_hr * 0.25,
              "3b": hits_non_hr * 0.02, "hr": season["hr"]}
    rates = {e: round(_shrink(counts[e], bf, LEAGUE[e], PITCHER_K), 4) for e in EVENTS}
    per_start = bf / season["gs"] if season.get("gs") else 23
    return rates, round(per_start, 1)


def soccer_base_xg(team: dict, opp: dict, league_avg: float = 1.3, home: bool = True,
                   home_adv: float = 1.07) -> float:
    """Expected goals for ``team`` vs ``opp`` from attack/defence per-90 numbers (xG preferred)."""
    att = team.get("xg_for", team.get("goals_for"))
    dfn = opp.get("xg_against", opp.get("goals_against"))
    mult = home_adv if home else 1 / home_adv
    return round(att * dfn / league_avg * mult, 3)
