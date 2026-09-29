"""Game simulator CLI.

    python -m betting.sim list
    python -m betting.sim run mlb_bos_nyy_2026-09-29 [--n 20000]
    python -m betting.sim run soccer_esp_cro_2026-09-29 --scenario "Yamal out"
    python -m betting.sim run mlb_bos_nyy_2026-09-29 --scenarios        # every what-if side by side
    python -m betting.sim run soccer_esp_cro_2026-09-29 --actual 2-0     # grade the model vs reality
    python -m betting.sim desk mlb_bos_nyy_2026-09-29 [--research]        # full agent team
    python -m betting.sim agents                                          # who's on the team
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from . import baseball, soccer
from .common import GAMES_DIR, american, devig2, load_game, pct, scenario


def _edge(model_p: float, price: float | None) -> str:
    if not price:
        return ""
    ev = model_p * price - 1
    return f"  @ {price:.2f} -> EV {ev:+.1%}"


# ------------------------------------------------------------------ baseball
def print_baseball(game: dict, rep: baseball.BaseballReport) -> None:
    away, home = rep.away, rep.home
    mk = game.get("market", {})
    ml = mk.get("moneyline", {})
    print(f"{game['title']} - {rep.n:,} simulated games\n")
    print(f"Projected runs: {away} {rep.mean_runs[0]:.2f}  {home} {rep.mean_runs[1]:.2f}  "
          f"(total {sum(rep.mean_runs):.2f})")
    print("\nMONEYLINE              model    fair     market (no-vig)")
    if ml:
        mkt = devig2([ml["away"], ml["home"]])
    else:
        mkt = [None, None]
    for i, (name, key) in enumerate(((away, "away"), (home, "home"))):
        m = f"{pct(mkt[i])}" if mkt[i] else "   -  "
        print(f"  {name:20} {pct(rep.win[i])}  {american(rep.win[i]):>6}   {m}{_edge(rep.win[i], ml.get(key))}")
    print("\nRUN LINE")
    for k, v in rep.runline.items():
        print(f"  {k:20} {pct(v)}  {american(v):>6}")
    print("\nTOTAL RUNS             over    under")
    for ln, v in rep.totals.items():
        flag = "  <- market line" if mk.get("total", {}).get("line") == ln else ""
        print(f"  {ln:<20} {pct(v)}  {pct(1 - v)}{flag}")
    print("\nFIRST 5 INNINGS")
    for k in ("away", "home", "tie"):
        label = {"away": away, "home": home, "tie": "Tied after 5"}[k]
        print(f"  {label:20} {pct(rep.f5.get(k, 0))}")
    print(f"\nNo run in 1st inning (NRFI): {pct(rep.nrfi)}   Extra innings: {pct(rep.extras)}")
    print("\nMOST LIKELY FINAL SCORES (away-home)")
    print("  " + "   ".join(f"{s} {pct(p).strip()}" for s, p in rep.scores[:8]))
    print("\nGAME SCRIPTS")
    for k, v in rep.scripts.items():
        print(f"  {k:40} {pct(v)}")
    print("\nSTARTING PITCHERS      avg K  avg outs  5+ inn  6+ inn  <=2 ER   K>=4   K>=5   K>=6   K>=7   K>=8")
    for name, s in rep.starters.items():
        print(f"  {name:20} {s['k']:5.2f}  {s['outs']:7.1f}  {pct(s['outs15'])} {pct(s['outs18'])} "
              f"{pct(s['er2'])} {pct(s['k4'])} {pct(s['k5'])} {pct(s['k6'])} {pct(s['k7'])} {pct(s['k8'])}")
    for side in ("away", "home"):
        print(f"\n{game[side]['name'].upper()} BATTERS    PA   1+ hit  2+ hits  HR     2+ TB   1+ RBI  1+ run  H+R+RBI 2+")
        for p in game[side]["lineup"]:
            b = rep.batters[p["name"]]
            print(f"  {p['name']:20} {b['pa']:4.2f} {pct(b['h1'])} {pct(b['h2'])} {pct(b['hr1'])} "
                  f"{pct(b['tb2'])} {pct(b['rbi1'])} {pct(b['r1'])} {pct(b['hrr2'])}")


# ------------------------------------------------------------------ soccer
def print_soccer(game: dict, rep: soccer.SoccerReport) -> None:
    home, away = rep.home, rep.away
    mk = game.get("market", {})
    x = mk.get("1x2", {})
    print(f"{game['title']} - {rep.n:,} simulated matches\n")
    print(f"Expected goals: {home} {rep.mean_goals[0]:.2f}  {away} {rep.mean_goals[1]:.2f}")
    mkt = None
    if x:
        mk_p = [1 / x["home"], 1 / x["draw"], 1 / x["away"]]
        s = sum(mk_p)
        mkt = [p / s for p in mk_p]
    print("\nMATCH RESULT           model   fair odds   market (no-vig)")
    for i, (label, key) in enumerate(((home, "home"), ("Draw", "draw"), (away, "away"))):
        p = rep.result[key]
        m = pct(mkt[i]) if mkt else "  -  "
        print(f"  {label:20} {pct(p)}  {1 / p:8.2f}    {m}{_edge(p, x.get(key))}")
    print("\nGOALS                  over    under")
    for ln, v in rep.totals.items():
        extra = _edge(v, mk.get("over_2_5")) if ln == 2.5 else ""
        print(f"  {ln:<20} {pct(v)}  {pct(1 - v)}{extra}")
    print(f"\nBoth teams score: yes {pct(rep.btts)} / no {pct(1 - rep.btts)}{_edge(1 - rep.btts, mk.get('btts_no'))}")
    for k, v in rep.win_to_nil.items():
        print(f"{k} win to nil: {pct(v)}")
    print("\nHANDICAP")
    for k, v in rep.handicap.items():
        print(f"  {k:20} {pct(v)}  fair {1 / v:.2f}")
    print("\nHALF-TIME RESULT")
    print("  " + "   ".join(f"{ {'home': home, 'away': away}.get(k, 'Draw')} {pct(v).strip()}" for k, v in rep.ht.items()))
    print("\nMOST LIKELY SCORES (home-away)")
    print("  " + "   ".join(f"{s} {pct(p).strip()}" for s, p in rep.scores[:10]))
    print("\nFIRST GOAL")
    print("  " + "   ".join(f"{k} {pct(v).strip()}" for k, v in rep.first_goal.items()))
    print("  timing: " + "   ".join(f"{k}' {pct(v).strip()}" for k, v in rep.first_goal_time.items()))
    print("\nGOALSCORERS            anytime  first    2+ goals  fair anytime odds")
    anyt = mk.get("anytime", {})
    for name, s in list(rep.scorers.items())[:16]:
        a = s.get("any", 0)
        print(f"  {name:20} {pct(a)}  {pct(s.get('first', 0))}  {pct(s.get('two', 0))}   "
              f"{1 / a:6.2f}{_edge(a, anyt.get(name))}")
    print("\nCARDS (yellow)         over")
    for ln, v in rep.cards.items():
        print(f"  {ln:<20} {pct(v)}")
    print(f"  Any red card: {pct(rep.reds)}")
    print("\nMATCH SCRIPTS")
    for k, v in rep.scripts.items():
        print(f"  {k:45} {pct(v)}")


def run(game: dict, n: int, seed: int):
    if game["sport"] == "baseball":
        return baseball.simulate(game, n, seed)
    return soccer.simulate(game, n, seed)


def headline(game: dict, rep) -> str:
    if game["sport"] == "baseball":
        return (f"{rep.away} {pct(rep.win[0])} / {rep.home} {pct(rep.win[1])} | "
                f"runs {rep.mean_runs[0]:.2f}-{rep.mean_runs[1]:.2f} | "
                f"over {game.get('market', {}).get('total', {}).get('line', 7.5)} "
                f"{pct(rep.totals.get(game.get('market', {}).get('total', {}).get('line', 7.5), 0))}")
    return (f"{rep.home} {pct(rep.result['home'])} / draw {pct(rep.result['draw'])} / "
            f"{rep.away} {pct(rep.result['away'])} | goals {rep.mean_goals[0]:.2f}-{rep.mean_goals[1]:.2f} | "
            f"over 2.5 {pct(rep.totals[2.5])} | BTTS {pct(rep.btts)}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="betting.sim", description="Monte Carlo game simulator")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    sub.add_parser("agents")
    d = sub.add_parser("desk", help="run the full agent team on a game")
    d.add_argument("game")
    d.add_argument("--n", type=int, default=20000)
    d.add_argument("--research", action="store_true", help="Claude + web search refresh first")
    d.add_argument("--min-edge", type=float, default=0.03)
    d.add_argument("--bankroll", type=float)
    d.add_argument("--actual", help="real final score, to grade the model")
    r = sub.add_parser("run")
    r.add_argument("game")
    r.add_argument("--n", type=int, default=20000)
    r.add_argument("--seed", type=int, default=7)
    r.add_argument("--scenario", help="apply one named what-if scenario")
    r.add_argument("--scenarios", action="store_true", help="compare every scenario to the base case")
    r.add_argument("--actual", help="real final score (away-home for baseball, home-away for soccer)")
    r.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    if args.cmd == "list":
        for f in sorted(GAMES_DIR.glob("*.json")):
            g = json.loads(f.read_text())
            print(f"{f.stem:34} {g['title']}")
            for s in g.get("scenarios", []):
                print(f"    - {s['name']}: {s['about']}")
        return

    if args.cmd == "agents":
        from .agents import SimDirector
        for a in SimDirector(research=False).roster():
            print(f"{a['name']:12} {a['role']}")
        return

    if args.cmd == "desk":
        from ..ledger import DEFAULT_DB, Ledger
        from .agents import SimDirector
        import os
        director = SimDirector(research=True if args.research else None, min_edge=args.min_edge,
                               actual=args.actual, bankroll=args.bankroll)
        desk = director.run(load_game(args.game), n=args.n,
                            ledger=Ledger(os.getenv("BETTING_DB", str(DEFAULT_DB))))
        print("\n".join(desk.log), "\n")
        print(desk.briefing)
        if desk.review:
            rv = desk.review
            print(f"\nREVIEW vs actual {rv['actual']}: Brier {rv['brier']:.3f}"
                  + (f" | season Brier {rv['season_brier']:.3f} over {rv['season_predictions']} predictions"
                     if "season_brier" in rv else ""))
            for m, p, o in rv["predictions"]:
                print(f"  {m:14} model {pct(p)}  happened: {'yes' if o else 'no'}")
        return

    game = load_game(args.game)
    if args.scenarios:
        print(f"{game['title']} - scenario comparison ({args.n:,} sims each)\n")
        print(f"  {'Base case':28} {headline(game, run(game, args.n, args.seed))}")
        for s in game.get("scenarios", []):
            g = scenario(game, s["name"])
            print(f"  {s['name'][:28]:28} {headline(g, run(g, args.n, args.seed))}")
        return

    if args.scenario:
        game = scenario(game, args.scenario)
    rep = run(game, args.n, args.seed)
    if args.json:
        print(json.dumps(asdict(rep), indent=2, default=str))
        return
    if args.scenario:
        print(f"SCENARIO: {args.scenario}\n")
    if game.get("context"):
        print("CONTEXT")
        for c in game["context"]:
            print(f"  - {c}")
        print()
    (print_baseball if game["sport"] == "baseball" else print_soccer)(game, rep)
    if args.actual:
        a, b = (int(v) for v in args.actual.split("-"))
        mod = baseball if game["sport"] == "baseball" else soccer
        chk = mod.check_actual(rep, a, b)
        print("\nREALITY CHECK vs actual result " + args.actual)
        for k, v in chk.items():
            print(f"  {k:22} {pct(v) if v is not None else 'n/a'}")


if __name__ == "__main__":
    sys.exit(main())
