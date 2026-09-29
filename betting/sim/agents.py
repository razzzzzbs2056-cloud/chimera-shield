"""Match desk: a lead agent (SimDirector) coordinating simulation sub-agents.

    ResearchAgent  (optional, Claude + web search) -> fresh lineups, injuries, prices
    StatsAgent     season lines -> model rates (with regression to the mean)
    ScoutAgent     styles, matchups, history -> what matters in this game
    ScenarioAgent  auto-builds what-ifs and live game states
    SimAgent       Monte Carlo: base case + every scenario
    MarketAgent    model vs market prices -> edges
    RiskManager    fractional-Kelly stakes with caps
    ReportAgent    the briefing
    ReviewAgent    after the game: grades the model on the real result (Brier score)
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from ..agents.base import Agent
from ..ledger import Ledger
from ..odds import kelly_fraction
from . import baseball, soccer
from .baseball import LEAGUE
from .common import apply_ops, american, devig2, pct
from .stats import batter_rates, pitcher_rates, soccer_base_xg


@dataclass
class MatchDesk:
    """Blackboard shared by the sim sub-agents."""
    game: dict
    n: int = 20000
    seed: int = 7
    ledger: Ledger | None = None
    base: object = None
    scenarios: dict = field(default_factory=dict)       # name -> (about, report)
    notes: list[str] = field(default_factory=list)      # scouting notes
    edges: list[dict] = field(default_factory=list)
    stakes: list[dict] = field(default_factory=list)
    briefing: str = ""
    review: dict | None = None
    log: list[str] = field(default_factory=list)

    @property
    def sport(self) -> str:
        return self.game["sport"]


# --------------------------------------------------------------------------- research
class ResearchAgent(Agent):
    """Uses Claude with live web search to refresh the game file before simulating.

    Claude returns scenario-style ops (same language as game files), which are applied
    only if they validate. Needs ANTHROPIC_API_KEY; skipped otherwise.
    """
    name = "Research"
    role = "Claude + web search: confirmed lineups, injuries, weather, latest prices."
    MODEL = os.getenv("BETTING_RESEARCH_MODEL", "claude-opus-5")

    SYSTEM = """You are the research analyst on a sports modelling desk. Use web search to find
the latest confirmed information for the game described, then return ONLY a JSON object in a
```json fenced block with keys:
  "context": [short factual strings with the most decision-relevant news, each with its source site],
  "ops": [edits to the game file, using ops {"op":"set"|"mul"|"replace"|"remove", "path":..., ...}],
  "market": {optional updated prices in the same shape as the game file's "market"}
Paths walk dicts by key and lists by a player's "name", e.g. "home.lineup.Aaron Judge.hr".
Only propose an op when a source confirms it (official lineup, confirmed injury, scratch).
Use decimal odds. Never invent statistics; if something is unconfirmed, put it in context instead."""

    def __init__(self, enabled: bool | None = None, max_searches: int = 8):
        self.enabled = bool(os.getenv("ANTHROPIC_API_KEY")) if enabled is None else enabled
        self.max_searches = max_searches

    def run(self, desk: MatchDesk) -> None:
        if not self.enabled:
            self.say(desk, "skipped (set ANTHROPIC_API_KEY to enable live research)")
            return
        import anthropic

        g = desk.game
        brief = {k: g[k] for k in ("sport", "title", "date", "venue") if k in g}
        brief["current_market"] = g.get("market")
        brief["lineups"] = {s: [p["name"] for p in g[s].get("lineup", g[s].get("players", []))]
                            for s in ("home", "away")}
        messages = [{"role": "user", "content": "Game file summary:\n" + json.dumps(brief, indent=1)}]
        tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": self.max_searches}]
        client = anthropic.Anthropic()
        try:
            for _ in range(5):  # resume pause_turn up to 5 times
                resp = client.beta.messages.create(
                    model=self.MODEL, max_tokens=16000, system=self.SYSTEM, messages=messages,
                    tools=tools, betas=["server-side-fallback-2026-07-01"], fallbacks="default")
                if resp.stop_reason != "pause_turn":
                    break
                messages = messages[:1] + [{"role": "assistant", "content": resp.content}]
        except anthropic.APIConnectionError:
            self.say(desk, "could not reach the Claude API; using the game file as is")
            return
        except anthropic.APIStatusError as e:
            self.say(desk, f"Claude API error {e.status_code}; using the game file as is")
            return
        if resp.stop_reason == "refusal":
            self.say(desk, "research request was declined; using the game file as is")
            return
        text = "".join(b.text for b in resp.content if b.type == "text")
        m = re.search(r"```json\s*(\{.*\})\s*```", text, re.S)
        try:
            found = json.loads(m.group(1) if m else text)
        except (json.JSONDecodeError, AttributeError):
            self.say(desk, "could not parse research output; using the game file as is")
            return
        applied = 0
        for op in found.get("ops", []):
            try:
                desk.game = apply_ops(desk.game, [op])
                applied += 1
            except (KeyError, ValueError, StopIteration, IndexError, TypeError):
                desk.game.setdefault("context", []).append(f"(unapplied research op: {json.dumps(op)})")
        desk.game.setdefault("context", []).extend(found.get("context", []))
        if found.get("market"):
            desk.game.setdefault("market", {}).update(found["market"])
        self.say(desk, f"added {len(found.get('context', []))} news items, applied {applied} updates")


# --------------------------------------------------------------------------- stats
class StatsAgent(Agent):
    name = "Stats"
    role = "Converts season stat lines into model rates, regressed to the mean."

    def run(self, desk: MatchDesk) -> None:
        g = desk.game
        built = filled = 0
        if desk.sport == "baseball":
            for side in ("home", "away"):
                sp = g[side]["starter"]
                if "season" in sp:
                    rates, per_start = pitcher_rates(sp["season"])
                    sp["rates"] = rates
                    if not sp.get("bf_mean"):
                        sp["bf_mean"] = min(per_start, 26)
                    built += 1
                for p in g[side]["lineup"]:
                    if "season" in p:
                        p.update(batter_rates(p["season"]))
                        built += 1
                    elif not all(e in p for e in LEAGUE):
                        for e, v in LEAGUE.items():
                            p.setdefault(e, v)
                        p["source"] = p.get("source", "") + " [league-average fill]"
                        filled += 1
        else:
            for side, opp, home in (("home", "away", True), ("away", "home", False)):
                t, o = g[side], g[opp]
                if "base_xg" not in t and "profile" in t and "profile" in o:
                    t["base_xg"] = soccer_base_xg(t["profile"], o["profile"], home=home)
                    built += 1
        self.say(desk, f"built {built} stat profiles from season lines, filled {filled} gaps with league average")


# --------------------------------------------------------------------------- scouting
class ScoutAgent(Agent):
    name = "Scout"
    role = "Reads styles, matchups and history to flag what should decide the game."

    def run(self, desk: MatchDesk) -> None:
        g = desk.game
        notes = desk.notes
        if desk.sport == "baseball":
            for side, opp in (("away", "home"), ("home", "away")):
                sp = g[opp]["starter"]
                hand = sp.get("throws", "R")
                lineup = g[side]["lineup"]
                adv = sum(1 for p in lineup if p.get("bats") == "S" or p.get("bats") != hand)
                pw = sorted(lineup, key=lambda p: -p["hr"])[:3]
                notes.append(f"{g[side]['name']}: {adv}/9 hitters have the platoon edge vs "
                             f"{'LHP' if hand == 'L' else 'RHP'} {sp['name']}; top power "
                             + ", ".join(f"{p['name']} ({p['hr']:.1%} HR/PA)" for p in pw))
                r = sp["rates"]
                notes.append(f"{sp['name']}: K {r['k']:.1%} vs lg {LEAGUE['k']:.1%}, BB {r['bb']:.1%}, "
                             f"HR {r['hr']:.1%} per batter; leash ~{sp['bf_mean']} batters")
            park = g.get("park", {})
            if park:
                notes.append(f"Park HR factor: LHB x{park.get('hr_L', 1):.2f}, RHB x{park.get('hr_R', 1):.2f}"
                             + (f" ({park['note']})" if park.get("note") else ""))
        else:
            h, a = g["home"], g["away"]
            gap = h["base_xg"] - a["base_xg"]
            notes.append(f"Expected-goals gap {gap:+.2f} in {h['name']}'s favour; "
                         f"{h['name']} {h['base_xg']:.2f} vs {a['name']} {a['base_xg']:.2f}")
            for side in ("home", "away"):
                t = g[side]
                top = sorted(t["players"], key=lambda p: -p["share"])[:3]
                notes.append(f"{t['name']} goal threats: " + ", ".join(
                    f"{p['name']} ({p['share']:.0%} of goals{'' if p.get('starter', True) else ', off the bench'})"
                    for p in top))
            for side, text in g.get("style", {}).items():
                notes.append(f"{g[side]['name']} style: {text}")
        for c in g.get("context", []):
            notes.append(c)
        self.say(desk, f"{len(notes)} scouting notes")


# --------------------------------------------------------------------------- scenarios
class ScenarioAgent(Agent):
    """Adds standard what-ifs on top of the hand-written ones in the game file."""
    name = "Scenarios"
    role = "Builds what-if and live-state scenarios automatically."

    def run(self, desk: MatchDesk) -> None:
        g = desk.game
        existing = {s["name"] for s in g.get("scenarios", [])}
        auto = []
        if desk.sport == "baseball":
            for side in ("home", "away"):
                star = max(g[side]["lineup"], key=lambda p: p["hr"] + p["bb"] * 0.5 + p["1b"] * 0.6)
                repl = {"name": "Replacement bat", "bats": "R", **{e: v * 0.9 if e != "k" else v * 1.1
                                                                   for e, v in LEAGUE.items()}}
                auto.append({"name": f"{star['name']} out", "about": f"{g[side]['name']}'s best hitter scratched",
                             "ops": [{"op": "replace", "path": f"{side}.lineup", "out": star["name"], "in": repl}]})
                sp = g[side]["starter"]
                auto.append({"name": f"{sp['name']} early exit", "about": "Starter lasts ~2 times through",
                             "ops": [{"op": "set", "path": f"{side}.starter.bf_mean", "value": 14}]})
            auto.append({"name": "Cold night, ball dies", "about": "-12% home runs",
                         "ops": [{"op": "set", "path": "weather.hr_mult", "value": 0.88}]})
        else:
            for side in ("home", "away"):
                t = g[side]
                star = max((p for p in t["players"] if p.get("starter", True)), key=lambda p: p["share"])
                auto.append({"name": f"{star['name']} out", "about": f"{t['name']}'s top scorer misses out",
                             "ops": [{"op": "remove", "path": f"{side}.players", "name": star["name"]},
                                     {"op": "mul", "path": f"{side}.base_xg", "value": 1 - star["share"] * 0.35}]})
            auto.append({"name": "Home side score early", "about": "Live: 1-0 at 15'",
                         "ops": [{"op": "state", "value": {"minute": 15, "score": [1, 0], "reds": [0, 0]}}]})
            auto.append({"name": "Away side score early", "about": "Live: 0-1 at 15'",
                         "ops": [{"op": "state", "value": {"minute": 15, "score": [0, 1], "reds": [0, 0]}}]})
        added = [s for s in auto if s["name"] not in existing]
        g.setdefault("scenarios", []).extend(added)
        self.say(desk, f"{len(existing)} scenarios from the file + {len(added)} auto-generated")


# --------------------------------------------------------------------------- simulation
class SimAgent(Agent):
    name = "Simulator"
    role = "Plays the game thousands of times: base case plus every scenario."

    def run(self, desk: MatchDesk) -> None:
        engine = baseball if desk.sport == "baseball" else soccer
        desk.base = engine.simulate(desk.game, desk.n, desk.seed)
        for s in desk.game.get("scenarios", []):
            g = apply_ops(desk.game, s["ops"])
            desk.scenarios[s["name"]] = (s["about"], engine.simulate(g, max(desk.n // 2, 2000), desk.seed))
        self.say(desk, f"ran {desk.n:,} base simulations and {len(desk.scenarios)} scenarios")


# --------------------------------------------------------------------------- market
class MarketAgent(Agent):
    name = "Market"
    role = "Compares model probabilities with bookmaker prices and flags edges."

    def __init__(self, min_edge: float = 0.03):
        self.min_edge = min_edge

    def _add(self, desk, market, selection, prob, price):
        if not price:
            return
        ev = prob * price - 1
        desk.edges.append({"market": market, "selection": selection, "prob": prob, "price": price,
                           "fair": 1 / prob if prob else None, "ev": ev, "bet": ev >= self.min_edge})

    def run(self, desk: MatchDesk) -> None:
        g, r, mk = desk.game, desk.base, desk.game.get("market", {})
        if desk.sport == "baseball":
            ml = mk.get("moneyline", {})
            self._add(desk, "moneyline", g["away"]["name"], r.win[0], ml.get("away"))
            self._add(desk, "moneyline", g["home"]["name"], r.win[1], ml.get("home"))
            t = mk.get("total", {})
            if t.get("line") in r.totals:
                self._add(desk, f"total {t['line']}", "Over", r.totals[t["line"]], t.get("over"))
                self._add(desk, f"total {t['line']}", "Under", 1 - r.totals[t["line"]], t.get("under"))
            for name, price in mk.get("hr", {}).items():
                if name in r.batters:
                    self._add(desk, "to hit a HR", name, r.batters[name]["hr1"], price)
            for name, price in mk.get("hits", {}).items():
                if name in r.batters:
                    self._add(desk, "1+ hit", name, r.batters[name]["h1"], price)
        else:
            x = mk.get("1x2", {})
            for key, label in (("home", g["home"]["name"]), ("draw", "Draw"), ("away", g["away"]["name"])):
                self._add(desk, "1X2", label, r.result[key], x.get(key))
            self._add(desk, "over 2.5", "Over", r.totals[2.5], mk.get("over_2_5"))
            self._add(desk, "under 2.5", "Under", 1 - r.totals[2.5], mk.get("under_2_5"))
            self._add(desk, "BTTS", "Yes", r.btts, mk.get("btts_yes"))
            self._add(desk, "BTTS", "No", 1 - r.btts, mk.get("btts_no"))
            for name, price in mk.get("anytime", {}).items():
                self._add(desk, "anytime scorer", name, r.scorers.get(name, {}).get("any", 0.0), price)
        desk.edges.sort(key=lambda e: -e["ev"])
        n_bets = sum(e["bet"] for e in desk.edges)
        self.say(desk, f"priced {len(desk.edges)} markets; {n_bets} beat the {self.min_edge:.0%} edge bar")


class RiskManager(Agent):
    name = "RiskManager"
    role = "Quarter-Kelly stakes, 2% cap per bet, 5% per game."

    def __init__(self, bankroll: float | None = None, kelly: float = 0.25,
                 max_bet: float = 0.02, max_game: float = 0.05):
        self.bankroll = bankroll
        self.kelly = kelly
        self.max_bet = max_bet
        self.max_game = max_game

    def run(self, desk: MatchDesk) -> None:
        bank = self.bankroll or (desk.ledger.bankroll() if desk.ledger else 1000.0)
        room = self.max_game * bank
        for e in (e for e in desk.edges if e["bet"]):
            stake = min(kelly_fraction(e["prob"], e["price"]) * self.kelly, self.max_bet) * bank
            stake = round(min(stake, room), 2)
            if stake < 1:
                continue
            room -= stake
            desk.stakes.append({**e, "stake": stake})
        self.say(desk, f"sized {len(desk.stakes)} bets, ${sum(s['stake'] for s in desk.stakes):.2f} "
                       f"total on a ${bank:,.0f} bankroll")


# --------------------------------------------------------------------------- report
class ReportAgent(Agent):
    name = "Reporter"
    role = "Writes the briefing: outlook, scenarios, edges, stakes."

    def run(self, desk: MatchDesk) -> None:
        g, r = desk.game, desk.base
        out = [f"{g['title']} ({g.get('date', '')}) - {desk.n:,} simulations", ""]
        if desk.sport == "baseball":
            a, h = g["away"]["name"], g["home"]["name"]
            out.append(f"OUTLOOK  {a} {pct(r.win[0])} ({american(r.win[0])})  |  {h} {pct(r.win[1])} "
                       f"({american(r.win[1])})  |  runs {r.mean_runs[0]:.2f}-{r.mean_runs[1]:.2f}")
            top = sorted(((n, b) for n, b in r.batters.items()), key=lambda kv: -kv[1]["hr1"])[:5]
            out.append("Top HR chances: " + ", ".join(f"{n} {pct(b['hr1']).strip()}" for n, b in top))
            for n, s in r.starters.items():
                out.append(f"{n}: avg {s['k']:.1f} K, 6+ K {pct(s['k6']).strip()}, 6+ inn {pct(s['outs18']).strip()}")
        else:
            h, a = g["home"]["name"], g["away"]["name"]
            out.append(f"OUTLOOK  {h} {pct(r.result['home'])}  |  draw {pct(r.result['draw'])}  |  "
                       f"{a} {pct(r.result['away'])}  |  xG {r.mean_goals[0]:.2f}-{r.mean_goals[1]:.2f}")
            out.append("Likely scores: " + ", ".join(f"{s} {pct(p).strip()}" for s, p in r.scores[:5]))
            named = [(n, s) for n, s in r.scorers.items() if n not in ("Other player", "Own goal")][:5]
            out.append("Top scorer chances: " + ", ".join(f"{n} {pct(s['any']).strip()}" for n, s in named))
        out += ["", "SCOUTING"] + [f"  - {n}" for n in desk.notes]
        out += ["", "SCENARIOS (what-ifs and live states)"]
        for name, (about, rep) in desk.scenarios.items():
            if desk.sport == "baseball":
                line = f"{g['home']['name']} {pct(rep.win[1])}, runs {sum(rep.mean_runs):.2f}"
            else:
                line = (f"{g['home']['name']} {pct(rep.result['home'])} / draw {pct(rep.result['draw'])} / "
                        f"{g['away']['name']} {pct(rep.result['away'])}, over 2.5 {pct(rep.totals[2.5])}")
            out.append(f"  {name[:30]:30} {line}   ({about})")
        out += ["", "MARKET CHECK"]
        for e in desk.edges:
            flag = "BET" if e["bet"] else "pass"
            out.append(f"  [{flag:4}] {e['market']:16} {e['selection'][:22]:22} model {pct(e['prob'])} "
                       f"fair {e['fair']:.2f} vs {e['price']:.2f}  EV {e['ev']:+.1%}")
        if not desk.edges:
            out.append("  no prices in the game file to compare")
        out += ["", "STAKES"]
        out += [f"  ${s['stake']:.2f} on {s['selection']} ({s['market']}) @ {s['price']:.2f}" for s in desk.stakes] \
            or ["  none - no price beats the model by enough. No edge, no bet."]
        desk.briefing = "\n".join(out)
        self.say(desk, "briefing written")


# --------------------------------------------------------------------------- review
class ReviewAgent(Agent):
    """After the game: how good were the probabilities? Tracks Brier score over time."""
    name = "Reviewer"
    role = "Grades the model against the real result and keeps a running accuracy record."

    def __init__(self, actual: str | None = None):
        self.actual = actual

    def run(self, desk: MatchDesk) -> None:
        if not self.actual:
            return
        a, b = (int(x) for x in self.actual.split("-"))
        g, r = desk.game, desk.base
        if desk.sport == "baseball":
            chk = baseball.check_actual(r, a, b)
            preds = [("home win", r.win[1], int(b > a)),
                     (f"over {g.get('market', {}).get('total', {}).get('line', 7.5)}",
                      r.totals.get(g.get("market", {}).get("total", {}).get("line", 7.5), 0.5),
                      int(a + b > g.get("market", {}).get("total", {}).get("line", 7.5)))]
        else:
            chk = soccer.check_actual(r, a, b)
            preds = [("home win", r.result["home"], int(a > b)), ("draw", r.result["draw"], int(a == b)),
                     ("over 2.5", r.totals[2.5], int(a + b > 2.5)), ("btts", r.btts, int(a > 0 and b > 0))]
        brier = sum((p - o) ** 2 for _, p, o in preds) / len(preds)
        desk.review = {"actual": self.actual, **chk, "brier": brier, "predictions": preds}
        if desk.ledger:
            db = desk.ledger.db
            db.execute("CREATE TABLE IF NOT EXISTS sim_reviews (game TEXT, reviewed_at TEXT, actual TEXT, "
                       "market TEXT, prob REAL, outcome INTEGER, PRIMARY KEY (game, market))")
            gid = g.get("id", g["title"])
            for m, p, o in preds:
                db.execute("INSERT OR REPLACE INTO sim_reviews VALUES (?,?,?,?,?,?)",
                           (gid, datetime.now(timezone.utc).isoformat(timespec="seconds"), self.actual, m, p, o))
            db.commit()
            rows = db.execute("SELECT prob, outcome FROM sim_reviews").fetchall()
            desk.review["season_brier"] = sum((p - o) ** 2 for p, o in rows) / len(rows)
            desk.review["season_predictions"] = len(rows)
        self.say(desk, f"graded vs {self.actual}: Brier {brier:.3f} (0 = perfect, 0.25 = coin flip)")


# --------------------------------------------------------------------------- director
class SimDirector:
    """Lead agent: runs the sub-agents in order on one game."""

    def __init__(self, research: bool | None = None, min_edge: float = 0.03, actual: str | None = None,
                 bankroll: float | None = None):
        self.pipeline: list[Agent] = [
            ResearchAgent(enabled=research), StatsAgent(), ScoutAgent(), ScenarioAgent(), SimAgent(),
            MarketAgent(min_edge=min_edge), RiskManager(bankroll=bankroll), ReportAgent(),
            ReviewAgent(actual=actual),
        ]

    def run(self, game: dict, n: int = 20000, ledger: Ledger | None = None, seed: int = 7) -> MatchDesk:
        desk = MatchDesk(game=json.loads(json.dumps(game)), n=n, ledger=ledger, seed=seed)
        for agent in self.pipeline:
            agent.run(desk)
        return desk

    def roster(self) -> list[dict]:
        return [{"name": a.name, "role": a.role} for a in self.pipeline]
