"""Command line: trader <run|once|status|health|backtest|nightly|resume|clear-kill|policy>."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

from trader.alerts import Alerts
from trader.config import Config, live_trading_allowed, load_config
from trader.policy import Policy, PolicyStore


def _store(args) -> PolicyStore:
    return PolicyStore(Path(args.policies))


def _build_runner(cfg: Config, args):
    from trader.data.market import CcxtData, make_exchange
    from trader.exec.broker import PaperBroker
    from trader.reflex.rule import RuleReflex
    from trader.runtime.loop import Runner

    stage = "live" if cfg.mode == "live" else "paper"
    policy = _store(args).active(stage)
    alerts = Alerts()
    data = CcxtData(make_exchange(cfg.exchange), cfg.timeframe)  # public market data, no keys
    if cfg.mode == "paper":
        broker = PaperBroker({}, None)
        broker.cost = cfg.cost_of  # type: ignore[method-assign]
    else:
        from trader.exec.ccxt_broker import CcxtBroker

        allowed, why = live_trading_allowed(cfg)
        if cfg.mode == "live" and not allowed:
            raise SystemExit(f"refusing to start live: {why}")
        keys = [os.environ.get(k) for k in ("EXCHANGE_API_KEY", "EXCHANGE_API_SECRET", "EXCHANGE_API_PASSPHRASE")]
        if not all(keys):
            raise SystemExit("exchange keys are not set in the environment (see .env.example)")
        ex = make_exchange(cfg.exchange, sandbox=cfg.mode == "testnet", api_key=keys[0], secret=keys[1],
                           password=keys[2])
        broker = CcxtBroker(ex, sandbox=cfg.mode == "testnet", live_allowed=allowed)
    if cfg.reflex.kind == "haiku":
        if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
            raise SystemExit("reflex.kind is haiku but no Anthropic credential is set; "
                             "set ANTHROPIC_API_KEY or use reflex.kind: rule")
        from trader.reflex.haiku import HaikuReflex

        reflex = HaikuReflex()
    else:
        reflex = RuleReflex(policy.rule)
    return Runner(cfg, policy, data, broker, reflex, alerts, Path(cfg.data_dir))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="trader")
    ap.add_argument("--config", default=os.environ.get("TRADER_CONFIG", "config/default.yaml"))
    ap.add_argument("--policies", default=os.environ.get("TRADER_POLICIES", "policies"))
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run", help="run forever, one pass per closed candle")
    sub.add_parser("once", help="process the latest closed candle once and exit")
    sub.add_parser("status", help="print saved account and pause state")
    sub.add_parser("health", help="exit 0 if the heartbeat is fresh (container health check)")
    b = sub.add_parser("backtest", help="walk-forward on cached history versus holding BTC")
    b.add_argument("--cache", default="data_cache")
    b.add_argument("--out", default=None)
    b.add_argument("--workers", type=int, default=4)
    b.add_argument("--download", action="store_true", help="refresh the history cache first")
    n = sub.add_parser("nightly", help="nightly review: calibration, misses, candidate policies")
    n.add_argument("--cache", default="data_cache")
    n.add_argument("--loop", action="store_true", help="stay up and run once per UTC day at 00:10")
    sub.add_parser("resume", help="clear pauses and halts set by escalations (human decision)")
    k = sub.add_parser("clear-kill", help="clear the latched kill switch (human decision)")
    k.add_argument("--i-have-reviewed-the-drawdown", action="store_true", required=True)
    p = sub.add_parser("policy", help="list, promote or roll back policy versions")
    p.add_argument("action", choices=["list", "init", "promote", "rollback"])
    p.add_argument("version", nargs="?")
    p.add_argument("--stage", choices=["paper", "live"], default="paper")
    p.add_argument("--approved-by", default="")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    cfg = load_config(args.config)
    root = Path(cfg.data_dir)

    if args.cmd in ("run", "once"):
        runner = _build_runner(cfg, args)
        if args.cmd == "run":
            runner.run_forever()
        for r in runner.run_once():
            print(json.dumps({k: r.get(k) for k in ("symbol", "status", "action", "reasons", "latency_ms")}))
        return 0
    if args.cmd == "health":
        from trader.runtime.loop import heartbeat_ok

        ok, msg = heartbeat_ok(root, 180.0)
        print(msg)
        return 0 if ok else 1
    if args.cmd in ("status", "resume", "clear-kill"):
        from trader.journal import load_state, save_state

        loaded = load_state(root / "state.json")
        if not loaded:
            print("no saved state yet")
            return 0 if args.cmd == "status" else 1
        account, extra = loaded
        if args.cmd == "resume":
            extra.update(global_pause=False, global_pause_until=0, paused_until={}, halt_reason="")
            save_state(root / "state.json", account, extra)
            print("pauses and halts cleared; restart the trader service to apply")
        elif args.cmd == "clear-kill":
            account.kill_latched, account.kill_reason = False, ""
            marks = extra.get("marks", {})
            account.peak_equity = account.balance + sum(
                p.unrealized(marks.get(s, p.entry_price)) for s, p in account.positions.items())
            save_state(root / "state.json", account, extra)
            print("kill switch cleared and equity peak reset; restart the trader service to apply")
        else:
            print(json.dumps({"balance": account.balance, "peak_equity": account.peak_equity,
                              "kill_latched": account.kill_latched,
                              "positions": {s: p.qty for s, p in account.positions.items()}, **extra},
                             indent=2))
        return 0
    if args.cmd == "policy":
        st = _store(args)
        if args.action == "init":
            if not (st.root / "v001.json").exists():
                st.save(Policy(version="v001", note="baseline: thresholds from the brief; hypotheses"))
            st.promote("v001", "paper", approved_by=args.approved_by or "bootstrap", note="initial paper policy")
            print("v001 active for paper")
        elif args.action == "list":
            ptr = json.loads((st.root / "ACTIVE.json").read_text()) if (st.root / "ACTIVE.json").exists() else {}
            print("active:", ptr)
            print("versions:", sorted(x.stem for x in st.root.glob("*.json") if x.name != "ACTIVE.json"))
            print("candidates:", sorted(x.stem for x in (st.root / "candidates").glob("*.json")))
        elif args.action == "promote":
            live_ok = args.stage == "live" and live_trading_allowed(cfg)[0]
            st.promote(args.version, args.stage, approved_by=args.approved_by, live_approved=live_ok)
            print(f"{args.version} active for {args.stage}")
        else:
            print("rolled back to", st.rollback(args.stage, approved_by=args.approved_by))
        return 0
    if args.cmd == "backtest":
        from trader.backtest.walkforward import run_from_config

        if args.download:
            _download(cfg, Path(args.cache))
        out = run_from_config(cfg, args.cache, _store(args).active("paper"), workers=args.workers)
        s, bh = out["strategy"], out["btc_hold"]
        verdict = "BEATS" if out["beats_btc_hold"] else "DOES NOT BEAT"
        print(f"Out-of-sample {out['oos_span'][0]} to {out['oos_span'][1]}: strategy {verdict} holding BTC "
              f"after costs ({s['total_return']:+.1%} vs {bh['total_return']:+.1%}; max drawdown "
              f"{s['max_drawdown']:.1%} vs {bh['max_drawdown']:.1%}; {s['trades']} trades).")
        if args.out:
            Path(args.out).write_text(json.dumps(out, indent=2, default=str))
        return 0
    if args.cmd == "nightly":
        while True:
            rep = _nightly(cfg, args)
            print(json.dumps({k: rep[k] for k in ("generated_utc", "active_policy", "notes")}, default=str))
            if not args.loop:
                return 0
            now = time.time()
            time.sleep(max(60.0, (int(now // 86400) + 1) * 86400 + 600 - now))
    return 2


def _download(cfg: Config, cache: Path) -> None:
    from trader.data.market import download_history, make_exchange

    ex = make_exchange(cfg.exchange)
    end = int(time.time())
    for sym in sorted({s.symbol for s in cfg.setups if s.enabled} | {cfg.context_symbol}):
        df = download_history(ex, sym, cfg.timeframe, 1672531200, end, cache)  # from 2023-01-01
        print(sym, len(df), "bars")


def _nightly(cfg: Config, args) -> dict:
    from trader.backtest.engine import load_frame, prepare
    from trader.data.market import TF_SECONDS
    from trader.journal import Journal
    from trader.review.nightly import review, run_regression_tests

    cache, root = Path(args.cache), Path(cfg.data_dir)
    _download(cfg, cache)
    scfgs = [s for s in cfg.setups if s.enabled]
    frames = {s: load_frame(cache, cfg.exchange, s, cfg.timeframe)
              for s in sorted({x.symbol for x in scfgs} | {cfg.context_symbol})}
    tf_s = TF_SECONDS[cfg.timeframe]
    j = Journal(root / "journal")
    project = Path.cwd()  # the regression suite lives next to the config (repo checkout or /app in Docker)
    has_tests = (project / "tests").exists() and (project / "pyproject.toml").exists()
    return review(
        decisions=j.read("decisions"), trades=j.read("trades"), fills=j.read("fills"), events=j.read("events"),
        series=prepare(frames, cfg.context_symbol, tf_s), setups=[s.build() for s in scfgs],
        store=_store(args), stage="live" if cfg.mode == "live" else "paper", limits=cfg.limits.build(),
        cost_of=cfg.cost_of, spread={s.symbol: s.bt_spread_bps for s in scfgs},
        depth={s.symbol: s.bt_depth_usd for s in scfgs}, tf=cfg.timeframe, tf_seconds=tf_s,
        balance=cfg.paper_balance, now=int(time.time()), out_dir=root / "reports",
        run_tests=(lambda: run_regression_tests(project)) if has_tests else (lambda: (False, "tests not shipped")))


if __name__ == "__main__":
    sys.exit(main())
