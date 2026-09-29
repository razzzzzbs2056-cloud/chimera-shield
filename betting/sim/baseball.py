"""Plate-appearance Monte Carlo baseball simulator.

Every PA is resolved from the batter's and pitcher's per-PA event rates, combined
with the odds-ratio (log5) method against league average, then adjusted for:

* platoon (batter hand vs pitcher hand, switch hitters take the favourable side)
* park HR factor by batter hand, plus a weather multiplier
* times-through-the-order penalty for starters
* starter hook (batters-faced leash + early hook when getting hit)
* bullpen roles: high-leverage arms in close late games, the rest otherwise
* realistic baserunning (extra bases on hits, double plays, sac flies)
* postseason rules (no automatic runner in extras) or regular-season ghost runner

Outputs are frequencies over N simulated games, so every number is a probability.
"""
from __future__ import annotations

import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field

EVENTS = ("k", "bb", "1b", "2b", "3b", "hr")

# 2025-26 MLB per-PA averages (bb includes HBP).
LEAGUE = {"k": 0.222, "bb": 0.093, "1b": 0.140, "2b": 0.043, "3b": 0.0035, "hr": 0.030}

PLATOON_SAME = {"k": 1.07, "bb": 0.93, "1b": 0.97, "2b": 0.95, "3b": 0.95, "hr": 0.88}
PLATOON_OPP = {"k": 0.97, "bb": 1.03, "1b": 1.01, "2b": 1.02, "3b": 1.02, "hr": 1.05}
HOME_BOOST = 1.035  # home batters' non-strikeout event multiplier
ROE = 0.020          # share of would-be outs where the batter reaches on an error
ADVANCE = 0.045      # per PA with runners on: steal / wild pitch / passed ball moves them up
TTO3 = {"k": 0.93, "bb": 1.06, "1b": 1.06, "2b": 1.08, "3b": 1.08, "hr": 1.15}


def out_rate(r: dict) -> float:
    return max(0.0, 1 - sum(r[e] for e in EVENTS))


def log5(bat: dict, pit: dict) -> dict:
    """Combine batter and pitcher event rates relative to league (odds-ratio)."""
    raw = {e: bat[e] * pit[e] / LEAGUE[e] for e in EVENTS}
    lo = out_rate(LEAGUE)
    raw["out"] = out_rate(bat) * out_rate(pit) / lo
    s = sum(raw.values())
    return {e: v / s for e, v in raw.items()}


@dataclass
class Line:
    """Box-score line for one batter in one sim game."""
    pa: int = 0
    h: int = 0
    hr: int = 0
    tb: int = 0
    bb: int = 0
    k: int = 0
    r: int = 0
    rbi: int = 0


@dataclass
class PitchLine:
    bf: int = 0
    outs: int = 0
    k: int = 0
    er: int = 0
    h: int = 0
    bb: int = 0


@dataclass
class GameResult:
    runs: list[int]
    by_inning: list[list[int]]
    batters: dict[str, Line]
    starters: dict[str, PitchLine]
    innings: int


class Team:
    def __init__(self, cfg: dict, rng: random.Random):
        self.cfg = cfg
        self.name = cfg["name"]
        self.lineup = cfg["lineup"]
        self.starter = cfg["starter"]
        self.pen = cfg["bullpen"]
        self.rng = rng


class BaseballSim:
    def __init__(self, game: dict, seed: int | None = None):
        self.game = game
        self.rng = random.Random(seed)
        self.park = game.get("park", {"hr_L": 1.0, "hr_R": 1.0})
        self.weather_hr = game.get("weather", {}).get("hr_mult", 1.0)
        self.postseason = game.get("postseason", True)
        self._cache: dict = {}

    # ------------------------------------------------------------------ rates
    def _rates(self, bat: dict, pit: dict, tto3: bool, home: bool = False) -> dict:
        key = (bat["name"], pit["name"], tto3, home)
        if key in self._cache:
            return self._cache[key]
        b_hand = bat.get("bats", "R")
        p_hand = pit.get("throws", "R")
        if b_hand == "S":
            b_hand = "L" if p_hand == "R" else "R"
        plat = PLATOON_SAME if b_hand == p_hand else PLATOON_OPP
        b = {e: bat[e] * plat[e] for e in EVENTS}
        b["hr"] *= self.park.get(f"hr_{b_hand}", 1.0) * self.weather_hr
        if home:  # home-field edge: ~53.5% home win rate league-wide
            b = {e: v * (0.98 if e == "k" else HOME_BOOST) for e, v in b.items()}
        p = dict(pit["rates"])
        if tto3:
            p = {e: p[e] * TTO3[e] for e in EVENTS}
        r = log5(b, p)
        self._cache[key] = r
        return r

    def _outcome(self, r: dict) -> str:
        x = self.rng.random()
        acc = 0.0
        for e, v in r.items():
            acc += v
            if x < acc:
                return e
        return "out"

    # ------------------------------------------------------------------ bases
    def _advance(self, ev: str, bases: list, outs: int, batter: str):
        """Return (new_bases, runners_scored_names, outs_added)."""
        rng = self.rng
        b1, b2, b3 = bases
        scored = []
        if ev == "hr":
            scored = [r for r in (b3, b2, b1) if r] + [batter]
            return [None, None, None], scored, 0
        if ev == "3b":
            scored = [r for r in (b3, b2, b1) if r]
            return [None, None, batter], scored, 0
        if ev == "2b":
            scored = [r for r in (b3, b2) if r]
            n3 = None
            if b1:
                if rng.random() < 0.42:
                    scored.append(b1)
                else:
                    n3 = b1
            return [None, batter, n3], scored, 0
        if ev == "1b":
            if b3:
                scored.append(b3)
            n2 = n3 = None
            if b2:
                if rng.random() < 0.62:
                    scored.append(b2)
                else:
                    n3 = b2
            if b1:
                if n3 is None and rng.random() < 0.28:
                    n3 = b1
                else:
                    n2 = b1
            return [batter, n2, n3], scored, 0
        if ev == "bb":
            if b1 and b2 and b3:
                scored.append(b3)
                return [batter, b1, b2], scored, 0
            if b1 and b2:
                return [batter, b1, b2], scored, 0
            if b1:
                return [batter, b1, b3], scored, 0
            return [batter, b2, b3], scored, 0
        if ev == "k":
            return bases, [], 1
        # ball in play out: 45% grounder, 35% fly, 20% liner
        kind = rng.random()
        if kind < 0.45:
            if b1 and outs < 2 and rng.random() < 0.40:  # double play
                nb = [None, b2, b3]
                if b3 and outs == 0 and rng.random() < 0.5:
                    scored.append(b3)
                    nb[2] = None
                return nb, scored, 2
            nb = [None, b2, b3]
            if b1:
                nb[1] = b1 if not b2 else b2
            if b3 and outs < 2 and rng.random() < 0.5:
                scored.append(b3)
                nb[2] = None
            if b2 and nb[2] is None and rng.random() < 0.5:
                nb[2] = b2
                nb[1] = b1 if b1 else None
            return nb, scored, 1
        if kind < 0.80:
            nb = [b1, b2, b3]
            if b3 and outs < 2 and rng.random() < 0.55:
                scored.append(b3)
                nb[2] = None
            if b2 and nb[2] is None and outs < 2 and rng.random() < 0.25:
                nb[2], nb[1] = b2, None
            return nb, scored, 1
        return bases, [], 1

    # ------------------------------------------------------------------ game
    def play(self) -> GameResult:
        g = self.game
        rng = self.rng
        teams = [Team(g["away"], rng), Team(g["home"], rng)]
        state = g.get("state") or {}
        runs = list(state.get("score", [0, 0]))
        by_inning = [[], []]
        lines = {p["name"]: Line() for t in teams for p in t.lineup}
        spot = list(state.get("spot", [0, 0]))
        # pitcher currently facing team i is the other team's staff
        leash = []
        for t in teams:
            s = t.starter
            leash.append(max(9, int(rng.gauss(s["bf_mean"], s.get("bf_sd", 3)))))
        pstate = []
        for i, t in enumerate(teams):
            ps = state.get("pitching", [{}, {}])[i]
            pstate.append({"pitcher": ps.get("pitcher", "starter"), "bf": ps.get("bf", 0),
                           "runs": ps.get("runs", 0), "role": "starter"})
            if pstate[-1]["pitcher"] != "starter":
                pstate[-1]["role"] = pstate[-1]["pitcher"]
        starters = {teams[0].starter["name"]: PitchLine(), teams[1].starter["name"]: PitchLine()}

        inning = state.get("inning", 1)
        half = state.get("half", 0)
        first = True
        while True:
            bat_i, pit_i = half, 1 - half
            bat_team, pit_team = teams[bat_i], teams[pit_i]
            ps = pstate[pit_i]
            if first and state:
                outs = state.get("outs", 0)
                bases = [("ghost" if b else None) for b in state.get("bases", [0, 0, 0])]
            else:
                outs = 0
                bases = [None, None, None]
                if inning > 9 and not self.postseason:
                    prev = bat_team.lineup[(spot[bat_i] - 1) % 9]["name"]
                    bases = [None, prev, None]
            first = False
            inning_runs = 0
            while outs < 3:
                # --- bullpen decision before each PA
                diff = runs[pit_i] - runs[bat_i]
                if ps["role"] == "starter":
                    s = pit_team.starter
                    early_hook = ps["runs"] >= s.get("hook_runs", 5) or (
                        ps["bf"] >= 18 and ps["runs"] >= s.get("hook_runs", 5) - 1)
                    if ps["bf"] >= leash[pit_i] or early_hook:
                        ps["role"] = "setup"
                if ps["role"] != "starter":
                    close_late = inning >= 7 and abs(diff) <= 3
                    want = "high" if close_late else "rest"
                    if inning >= 9 and 0 < diff <= 3:
                        want = "closer"
                    ps["role"] = want
                if ps["role"] == "starter":
                    pit = {"name": pit_team.starter["name"], "throws": pit_team.starter["throws"],
                           "rates": pit_team.starter["rates"]}
                    tto3 = ps["bf"] >= 18
                else:
                    group = pit_team.pen.get(ps["role"], pit_team.pen.get("high" if ps["role"] == "closer" else "rest"))
                    pit = {"name": f"{pit_team.name} {ps['role']}", "throws": group.get("throws", "R"),
                           "rates": group["rates"]}
                    tto3 = False

                batter = bat_team.lineup[spot[bat_i] % 9]
                spot[bat_i] += 1
                # free bases between pitches: steals, wild pitches, passed balls
                if any(bases) and rng.random() < ADVANCE:
                    b1, b2, b3 = bases
                    if b3 and rng.random() < 0.35:
                        runs[bat_i] += 1
                        inning_runs += 1
                        if ps["role"] == "starter":
                            ps["runs"] += 1
                            starters[pit_team.starter["name"]].er += 1
                        if b3 in lines:
                            lines[b3].r += 1
                        b3 = None
                    if b2 and not b3:
                        b3, b2 = b2, None
                    if b1 and not b2:
                        b2, b1 = b1, None
                    bases = [b1, b2, b3]
                    if bat_i == 1 and inning >= 9 and runs[1] > runs[0]:
                        break
                ev = self._outcome(self._rates(batter, pit, tto3, bat_i == 1))
                roe = ev == "out" and rng.random() < ROE
                ln = lines[batter["name"]]
                ln.pa += 1
                if ev in ("1b", "2b", "3b", "hr"):
                    ln.h += 1
                    ln.tb += {"1b": 1, "2b": 2, "3b": 3, "hr": 4}[ev]
                    ln.hr += ev == "hr"
                ln.bb += ev == "bb"
                ln.k += ev == "k"
                bases, scored, add_outs = self._advance("1b" if roe else ev, bases, outs, batter["name"])
                outs += add_outs
                ps["bf"] += 1
                if ps["role"] == "starter":
                    sl = starters[pit_team.starter["name"]]
                    sl.bf += 1
                    sl.outs += add_outs
                    sl.k += ev == "k"
                    sl.h += ev in ("1b", "2b", "3b", "hr")
                    sl.bb += ev == "bb"
                n = len(scored)
                if n:
                    if ev != "out" or add_outs < 2:
                        ln.rbi += n
                    for r in scored:
                        if r in lines:
                            lines[r].r += 1
                    runs[bat_i] += n
                    inning_runs += n
                    if ps["role"] == "starter":
                        ps["runs"] += n
                        starters[pit_team.starter["name"]].er += n
                    # walk-off
                    if bat_i == 1 and inning >= 9 and runs[1] > runs[0]:
                        break
            by_inning[bat_i].append(inning_runs)
            # end of half-inning
            if half == 0:
                if inning >= 9 and runs[1] > runs[0]:
                    break
                half = 1
            else:
                if inning >= 9 and runs[0] != runs[1]:
                    break
                half = 0
                inning += 1
            if inning > 20:
                break
        return GameResult(runs, by_inning, lines, starters, inning)


# ---------------------------------------------------------------------- analysis

@dataclass
class BaseballReport:
    n: int
    away: str
    home: str
    win: list[float]
    mean_runs: list[float]
    totals: dict[float, float]            # line -> P(over)
    runline: dict[str, float]
    f5: dict[str, float]
    nrfi: float
    scores: list[tuple[str, float]]
    extras: float
    batters: dict[str, dict]
    starters: dict[str, dict]
    scripts: dict[str, float]
    total_dist: dict[int, float] = field(default_factory=dict)
    margin_dist: dict[int, float] = field(default_factory=dict)


def simulate(game: dict, n: int = 20000, seed: int | None = 7) -> BaseballReport:
    sim = BaseballSim(game, seed)
    wins = [0, 0]
    tot_runs = [0, 0]
    totals = Counter()
    margins = Counter()
    scores = Counter()
    f5 = Counter()
    nrfi = extras = 0
    bat = defaultdict(lambda: Counter())
    pit = defaultdict(lambda: Counter())
    scripts = Counter()
    for _ in range(n):
        r = sim.play()
        a, h = r.runs
        wins[0 if a > h else 1] += 1
        tot_runs[0] += a
        tot_runs[1] += h
        totals[a + h] += 1
        margins[h - a] += 1
        scores[f"{a}-{h}"] += 1
        a5 = sum(r.by_inning[0][:5])
        h5 = sum(r.by_inning[1][:5])
        f5["away" if a5 > h5 else "home" if h5 > a5 else "tie"] += 1
        if r.by_inning[0][:1] == [0] and r.by_inning[1][:1] == [0]:
            nrfi += 1
        extras += r.innings > 9
        for name, ln in r.batters.items():
            c = bat[name]
            c["h1"] += ln.h >= 1
            c["h2"] += ln.h >= 2
            c["hr1"] += ln.hr >= 1
            c["tb2"] += ln.tb >= 2
            c["rbi1"] += ln.rbi >= 1
            c["r1"] += ln.r >= 1
            c["hrr2"] += (ln.h + ln.r + ln.rbi) >= 2
            c["pa"] += ln.pa
            c["k1"] += ln.k >= 1
        for name, pl in r.starters.items():
            c = pit[name]
            for k in range(2, 12):
                c[f"k{k}"] += pl.k >= k
            c["k"] += pl.k
            c["outs"] += pl.outs
            c["er"] += pl.er
            c["outs15"] += pl.outs >= 15
            c["outs18"] += pl.outs >= 18
            c["er2"] += pl.er <= 2
        tot = a + h
        if tot <= 4:
            scripts["pitchers' duel (4 or fewer total runs)"] += 1
        if abs(h - a) >= 5:
            scripts["blowout (won by 5+)"] += 1
        if abs(h - a) == 1:
            scripts["one-run game"] += 1
        if r.innings > 9:
            scripts["extra innings"] += 1
        if (a5 > h5 and h > a) or (h5 > a5 and a > h):
            scripts["comeback (F5 leader loses)"] += 1

    def f(x):
        return x / n

    lines = [x + 0.5 for x in range(4, 12)]
    return BaseballReport(
        n=n, away=game["away"]["name"], home=game["home"]["name"],
        win=[f(wins[0]), f(wins[1])],
        mean_runs=[tot_runs[0] / n, tot_runs[1] / n],
        totals={ln: f(sum(v for t, v in totals.items() if t > ln)) for ln in lines},
        runline={"home -1.5": f(sum(v for m, v in margins.items() if m >= 2)),
                 "away +1.5": f(sum(v for m, v in margins.items() if m <= 1)),
                 "away -1.5": f(sum(v for m, v in margins.items() if m <= -2)),
                 "home +1.5": f(sum(v for m, v in margins.items() if m >= -1))},
        f5={k: f(v) for k, v in f5.items()},
        nrfi=f(nrfi),
        scores=[(s, f(v)) for s, v in scores.most_common(10)],
        extras=f(extras),
        batters={name: {k: (v / n if k != "pa" else v / n) for k, v in c.items()} for name, c in bat.items()},
        starters={name: {k: v / n for k, v in c.items()} for name, c in pit.items()},
        scripts={k: f(v) for k, v in scripts.most_common()},
        total_dist={t: f(v) for t, v in sorted(totals.items())},
        margin_dist={m: f(v) for m, v in sorted(margins.items())},
    )


def check_actual(rep: BaseballReport, away_runs: int, home_runs: int) -> dict:
    """How likely was the real result under the model?"""
    exact = dict(rep.scores).get(f"{away_runs}-{home_runs}")
    tot = away_runs + home_runs
    return {
        "winner_prob": rep.win[1] if home_runs > away_runs else rep.win[0],
        "exact_score_prob": exact,
        "total_percentile": sum(v for t, v in rep.total_dist.items() if t <= tot),
        "margin_prob": rep.margin_dist.get(home_runs - away_runs, 0.0),
    }
