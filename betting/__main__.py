"""CLI for the betting desk.

    python -m betting scan --sample          # run every agent on bundled data
    python -m betting scan --sports basketball_nba americanfootball_nfl
    python -m betting settle --sample        # grade open bets, update Elo
    python -m betting train --sample         # warm up the Elo model on past results
    python -m betting report                 # P&L, ROI, CLV, breakdowns
    python -m betting bets [--status open]
    python -m betting bankroll --set 1000
    python -m betting books | agents | sports
    python -m betting convert -110           # odds converter
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from .agents import DeskConfig, HeadTrader
from .books import ALL_BOOKS, SHARP_BOOKS, SPORTS, book_name
from .feeds import DATA_DIR, OddsAPIFeed, SampleFeed
from .ledger import DEFAULT_DB, Ledger
from .odds import american_to_decimal, decimal_to_american, implied_prob


def _feed(args):
    if args.sample or not os.getenv("ODDS_API_KEY"):
        if not args.sample:
            print("ODDS_API_KEY not set - using bundled sample data (pass --sample to hide this).\n")
        return SampleFeed()
    return OddsAPIFeed()


def _fmt_point(market, point):
    if point is None:
        return ""
    return f" {point:+g}" if market == "spreads" else f" {point:g}"


def _print_card(desk) -> None:
    if not desk.approved:
        print("No bets pass the desk's filters right now. No edge = no bet.")
        return
    print(f"{'type':5} {'game':44} {'bet':34} {'book':13} {'price':>12} {'fair%':>6} "
          f"{'edge':>6} {'stake':>9}")
    for o in desk.approved:
        bet = f"{o.selection}{_fmt_point(o.market, o.point)} ({o.market})"
        price = f"{o.price:.2f}/{decimal_to_american(o.price):+d}"
        print(f"{o.kind:5} {o.game.label[:44]:44} {bet[:34]:34} {book_name(o.book)[:13]:13} "
              f"{price:>12} {o.fair_prob:6.1%} {o.edge:6.2%} {o.stake:9.2f}")
    exp = sum(o.stake * o.edge for o in desk.approved if o.kind == "value")
    exp += sum(o.stake * o.edge / (1 + o.edge) for o in desk.approved if o.kind == "arb")
    print(f"\nTotal at risk ${sum(o.stake for o in desk.approved):,.2f} | "
          f"expected profit ${exp:,.2f} (long-run average, not a guarantee)")


def cmd_scan(args, ledger):
    cfg = DeskConfig(place=not args.dry_run, mode=args.mode, min_edge=args.min_edge,
                     analyst=False if args.no_analyst else None, devig_method=args.devig)
    if args.sports:
        cfg.sports = args.sports
    elif args.sample:
        cfg.sports = []  # everything in the sample file
    trader = HeadTrader(_feed(args), ledger, cfg)
    desk = trader.scan()
    if args.json:
        print(json.dumps({"log": desk.log, "bets": [o.to_dict() for o in desk.approved],
                          "briefing": desk.briefing}, indent=2, default=str))
        return
    print("\n".join(desk.log), "\n")
    _print_card(desk)
    if desk.briefing:
        print("\n=== Analyst briefing ===\n" + desk.briefing)


def cmd_settle(args, ledger):
    cfg = DeskConfig(sports=args.sports or ([] if args.sample else DeskConfig().sports))
    desk = HeadTrader(_feed(args), ledger, cfg).settle()
    print("\n".join(desk.log))
    cmd_report(args, ledger)


def cmd_train(args, ledger):
    path = args.file or (DATA_DIR / "sample_history.json")
    with open(path) as f:
        results = json.load(f)
    desk = HeadTrader(SampleFeed(), ledger).train(results)
    print("\n".join(desk.log) or "nothing new to learn")


def cmd_report(args, ledger):
    r = ledger.report()
    if getattr(args, "json", False):
        print(json.dumps(r, indent=2))
        return
    clv = f"{r['avg_clv']:+.2%}" if r["avg_clv"] is not None else "n/a"
    print(f"\nBankroll ${r['bankroll']:,.2f} (start ${r['starting_bankroll']:,.2f})")
    print(f"Open: {r['open_bets']} bets, ${r['open_stake']:,.2f} staked, "
          f"+${r['expected_profit_open']:,.2f} expected")
    print(f"Settled: {r['settled_bets']} bets | staked ${r['staked']:,.2f} | "
          f"profit ${r['profit']:+,.2f} | ROI {r['roi']:+.2%} | win {r['win_rate']:.1%} | CLV {clv}")
    for title in ("by_kind", "by_sport", "by_market", "by_book"):
        if r[title]:
            print(f"\n{title.replace('_', ' ')}:")
            for k, d in sorted(r[title].items(), key=lambda kv: -kv[1]["profit"]):
                print(f"  {book_name(k):28} {d['bets']:4} bets  ${d['profit']:+9.2f}  ROI {d['roi']:+.2%}")


def cmd_bets(args, ledger):
    rows = ledger.bets(status=args.status)
    if not rows:
        print("No bets yet. Run: python -m betting scan --sample")
        return
    for b in rows:
        res = f"{b['status']:5}" + (f" ${b['payout'] - b['stake']:+.2f}" if b["payout"] is not None else "")
        print(f"#{b['id']:<4} {b['event'][:40]:40} {b['selection']}{_fmt_point(b['market'], b['point'])} "
              f"{b['market']} @ {b['price']:.2f} {book_name(b['book'])} ${b['stake']:.2f} [{res}]")


def cmd_bankroll(args, ledger):
    if args.set is not None:
        ledger.set_setting("bankroll", args.set)
    print(f"Starting bankroll ${ledger.starting_bankroll:,.2f}; available ${ledger.bankroll():,.2f}")


def cmd_convert(args, ledger):
    v = args.odds
    dec = american_to_decimal(v) if abs(v) >= 100 else v
    print(f"decimal {dec:.3f} | american {decimal_to_american(dec):+d} | implied {implied_prob(dec):.2%}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="betting", description="Multi-agent sports betting desk")
    p.add_argument("--db", default=os.getenv("BETTING_DB", str(DEFAULT_DB)))
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan", help="run all agents and log a card of bets")
    s.add_argument("--sample", action="store_true")
    s.add_argument("--sports", nargs="*")
    s.add_argument("--min-edge", type=float, default=0.02)
    s.add_argument("--devig", choices=["power", "multiplicative"], default="power")
    s.add_argument("--mode", choices=["paper", "live"], default="paper",
                   help="'live' just labels bets you placed yourself; nothing is auto-wagered")
    s.add_argument("--dry-run", action="store_true", help="don't record bets")
    s.add_argument("--no-analyst", action="store_true")
    s.add_argument("--json", action="store_true")

    st = sub.add_parser("settle", help="grade open bets from final scores")
    st.add_argument("--sample", action="store_true")
    st.add_argument("--sports", nargs="*")

    t = sub.add_parser("train", help="warm up Elo ratings from past results")
    t.add_argument("--sample", action="store_true")
    t.add_argument("--file")

    r = sub.add_parser("report")
    r.add_argument("--json", action="store_true")

    b = sub.add_parser("bets")
    b.add_argument("--status", choices=["open", "won", "lost", "push", "void"])

    br = sub.add_parser("bankroll")
    br.add_argument("--set", type=float)

    c = sub.add_parser("convert", help="convert American/decimal odds")
    c.add_argument("odds", type=float)

    sub.add_parser("books")
    sub.add_parser("sports")
    sub.add_parser("agents")

    args = p.parse_args(argv)

    if args.cmd == "books":
        for k, v in ALL_BOOKS.items():
            print(f"{k:16} {v:24} {'SHARP' if k in SHARP_BOOKS else ''}")
        return
    if args.cmd == "sports":
        for k, v in SPORTS.items():
            print(f"{k:30} {v}")
        return

    ledger = Ledger(args.db)
    if args.cmd == "agents":
        for a in HeadTrader(SampleFeed(), ledger).roster():
            print(f"{a['name']:15} {a['role']}")
        return
    {"scan": cmd_scan, "settle": cmd_settle, "train": cmd_train, "report": cmd_report,
     "bets": cmd_bets, "bankroll": cmd_bankroll, "convert": cmd_convert}[args.cmd](args, ledger)


if __name__ == "__main__":
    sys.exit(main())
