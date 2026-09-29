"""Minute-by-minute Monte Carlo football (soccer) simulator.

Each minute, each team scores with a probability driven by:

* its base expected goals (attack strength x opponent defence, home advantage built in)
* the in-match time profile (goal rate climbs through the match; stoppage time added)
* game state: a trailing team pushes (more goals for AND against), a leading team
  sits deeper; the effect grows after the hour mark
* red cards: 10 men attack less and concede more
* who is on the pitch: starters' expected minutes and substitutes' entry times

Every goal is credited to a player on the pitch, weighted by their share of the team's
goals, so anytime / first / 2+ scorer probabilities come straight from the simulation.
"""
from __future__ import annotations

import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field

RED_OWN = 0.72    # attack multiplier for a side down to 10
RED_OPP = 1.30    # opponent's attack multiplier vs 10 men
OWN_GOAL = 0.03


def time_weight(minute: int) -> float:
    """Relative goal intensity: ~0.85 early, ~1.25 at full time (empirical shape)."""
    return 0.85 + 0.40 * min(minute, 95) / 95


@dataclass
class Player:
    name: str
    share: float          # share of team goals while on the pitch
    on: int               # minute entering (0 = starter)
    off: int              # minute leaving (95+ = full match)


class SoccerSim:
    def __init__(self, game: dict, seed: int | None = None):
        self.g = game
        self.rng = random.Random(seed)
        self.teams = [game["home"], game["away"]]
        # normalise so base_xg is the expected goals for a full match incl. average stoppage
        # (first half ~2.5 min added, second half ~5.3 min added)
        typical = list(range(1, 48)) + list(range(46, 96))
        self.norm = sum(time_weight(m) for m in typical) / 90

    def _lineup(self, team: dict) -> list[Player]:
        rng = self.rng
        out = []
        for p in team["players"]:
            if p.get("starter", True):
                mins = p.get("minutes", 90)
                off = 99 if mins >= 90 else int(max(46, min(95, rng.gauss(mins, 8))))
                out.append(Player(p["name"], p["share"], 0, off))
            else:
                if rng.random() > p.get("sub_prob", 0.7):
                    continue
                on = int(max(46, min(88, rng.gauss(p.get("on_minute", 65), 8))))
                out.append(Player(p["name"], p["share"], on, 99))
        return out

    def play(self) -> dict:
        rng = self.rng
        st = self.g.get("state") or {}
        minute0 = st.get("minute", 0)
        score = list(st.get("score", [0, 0]))
        reds = list(st.get("reds", [0, 0]))
        yellows = [0, 0]
        lineups = [self._lineup(t) for t in self.teams]
        goals = []  # (minute, team, scorer, half)
        ht = None
        stoppage1 = rng.choice([1, 2, 2, 3, 3, 4])
        stoppage2 = rng.choice([3, 4, 5, 5, 6, 7, 8])
        timeline = [(m, 1) for m in range(1, 46 + stoppage1)] + [(m, 2) for m in range(46, 91 + stoppage2)]
        for m, half in timeline:
            if half == 2 and ht is None:
                ht = tuple(st.get("ht", score)) if minute0 >= 45 else tuple(score)
            if (half == 1 and minute0 >= 45) or m <= minute0:
                continue
            tw = time_weight(m) / self.norm / 90
            late = 1.0 if m < 60 else 1.0 + (m - 60) / 35
            for i in (0, 1):
                t, o = self.teams[i], self.teams[1 - i]
                lam = t["base_xg"] * tw
                diff = score[i] - score[1 - i]
                if diff < 0:
                    lam *= 1 + t.get("chase", 0.12) * late
                elif diff > 0:
                    lam *= 1 - (1 - t.get("protect", 0.93)) * late
                # opponent pushing leaves space behind
                if diff > 0:
                    lam *= 1 + 0.06 * late
                lam *= RED_OWN ** reds[i] * RED_OPP ** reds[1 - i]
                if rng.random() < lam:
                    score[i] += 1
                    goals.append((m, i, self._scorer(lineups[i], m), half))
            # discipline
            for i in (0, 1):
                t = self.teams[i]
                y_rate = t.get("yellows", 2.0) / 95
                if score[i] < score[1 - i]:
                    y_rate *= 1.25
                if rng.random() < y_rate:
                    yellows[i] += 1
                if rng.random() < t.get("reds_rate", 0.06) / 95:
                    reds[i] += 1
        if ht is None:
            ht = tuple(score)
        return {"score": score, "ht": ht, "goals": goals, "yellows": yellows, "reds": reds}

    def _scorer(self, lineup: list[Player], minute: int) -> str:
        rng = self.rng
        if rng.random() < OWN_GOAL:
            return "Own goal"
        on = [p for p in lineup if p.on <= minute < p.off]
        weights = [p.share for p in on]
        other = max(0.0, 1 - sum(weights)) * 0.3 + 0.02
        x = rng.random() * (sum(weights) + other)
        acc = 0.0
        for p, w in zip(on, weights):
            acc += w
            if x < acc:
                return p.name
        return "Other player"


@dataclass
class SoccerReport:
    n: int
    home: str
    away: str
    result: dict[str, float]
    mean_goals: list[float]
    totals: dict[float, float]
    btts: float
    scores: list[tuple[str, float]]
    ht: dict[str, float]
    first_goal: dict[str, float]
    first_goal_time: dict[str, float]
    scorers: dict[str, dict]
    cards: dict[float, float]
    reds: float
    scripts: dict[str, float]
    win_to_nil: dict[str, float]
    handicap: dict[str, float] = field(default_factory=dict)


def simulate(game: dict, n: int = 20000, seed: int | None = 7) -> SoccerReport:
    sim = SoccerSim(game, seed)
    home, away = game["home"]["name"], game["away"]["name"]
    res = Counter()
    goals_sum = [0, 0]
    totals = Counter()
    scores = Counter()
    ht = Counter()
    fg = Counter()
    fgt = Counter()
    btts = 0
    cards = Counter()
    reds = 0
    scor = defaultdict(Counter)
    scripts = Counter()
    wtn = Counter()
    margins = Counter()
    for _ in range(n):
        r = sim.play()
        h, a = r["score"]
        res["home" if h > a else "away" if a > h else "draw"] += 1
        goals_sum[0] += h
        goals_sum[1] += a
        totals[h + a] += 1
        margins[h - a] += 1
        scores[f"{h}-{a}"] += 1
        hh, ha = r["ht"]
        ht["home" if hh > ha else "away" if ha > hh else "draw"] += 1
        btts += h > 0 and a > 0
        wtn["home"] += h > a and a == 0
        wtn["away"] += a > h and h == 0
        if r["goals"]:
            m, team, who, half = r["goals"][0]
            fg[home if team == 0 else away] += 1
            if half == 1:
                bucket = "0-15" if m <= 15 else "16-30" if m <= 30 else "31-45+"
            else:
                bucket = "46-60" if m <= 60 else "61-75" if m <= 75 else "76-90+"
            fgt[bucket] += 1
            scor[who]["first"] += 1
        else:
            fg["no goal"] += 1
        per = Counter(g[2] for g in r["goals"])
        for who, c in per.items():
            scor[who]["any"] += 1
            scor[who]["two"] += c >= 2
            scor[who]["hat"] += c >= 3
        cards[sum(r["yellows"])] += 1
        reds += sum(r["reds"]) > 0
        if (hh > ha and a > h) or (ha > hh and h > a):
            scripts["half-time leader loses"] += 1
        if (hh < ha and h >= a) or (ha < hh and a >= h):
            scripts["comeback from half-time deficit (draw or win)"] += 1
        if h + a == 0:
            scripts["0-0"] += 1
        if abs(h - a) >= 3:
            scripts["rout (3+ goal margin)"] += 1
        late = [g for g in r["goals"] if g[0] >= 80]
        if late:
            scripts["goal after 80'"] += 1

    def f(x):
        return x / n

    return SoccerReport(
        n=n, home=home, away=away,
        result={"home": f(res["home"]), "draw": f(res["draw"]), "away": f(res["away"])},
        mean_goals=[goals_sum[0] / n, goals_sum[1] / n],
        totals={ln: f(sum(v for t, v in totals.items() if t > ln)) for ln in (0.5, 1.5, 2.5, 3.5, 4.5)},
        btts=f(btts),
        scores=[(s, f(v)) for s, v in scores.most_common(12)],
        ht={k: f(v) for k, v in ht.items()},
        first_goal={k: f(v) for k, v in fg.most_common()},
        first_goal_time={k: f(v) for k, v in sorted(fgt.items())},
        scorers={k: {kk: f(vv) for kk, vv in v.items()} for k, v in
                 sorted(scor.items(), key=lambda kv: -kv[1]["any"])},
        cards={ln: f(sum(v for t, v in cards.items() if t > ln)) for ln in (2.5, 3.5, 4.5, 5.5)},
        reds=f(reds),
        scripts={k: f(v) for k, v in scripts.most_common()},
        win_to_nil={home: f(wtn["home"]), away: f(wtn["away"])},
        handicap={f"{home} -1.5": f(sum(v for m, v in margins.items() if m >= 2)),
                  f"{home} -2.5": f(sum(v for m, v in margins.items() if m >= 3)),
                  f"{away} +1.5": f(sum(v for m, v in margins.items() if m <= 1))},
    )


def check_actual(rep: SoccerReport, home_goals: int, away_goals: int) -> dict:
    res = "home" if home_goals > away_goals else "away" if away_goals > home_goals else "draw"
    return {
        "result_prob": rep.result[res],
        "exact_score_prob": dict(rep.scores).get(f"{home_goals}-{away_goals}", 0.0),
        "total_over_prob": rep.totals.get(home_goals + away_goals - 0.5, 0.0),
    }
