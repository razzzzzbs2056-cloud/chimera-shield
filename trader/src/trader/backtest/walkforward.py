"""Walk-forward evaluation. Parameters are chosen on a training window and judged ONLY on
the window that follows it; the out-of-sample (OOS) windows are stitched into one
continuous account and compared with buying and holding BTC over the same span, after costs.

Rule: a REFLEX that uses a model may only be tested on data after the model's training
cutoff (the model may remember earlier prices). run() refuses otherwise.
"""

from __future__ import annotations

import datetime as dt
import itertools
import multiprocessing as mp
from dataclasses import replace
from typing import Callable

from trader.backtest.engine import Series, buy_and_hold, metrics, run_backtest
from trader.core import Setup
from trader.exec.broker import CostModel
from trader.policy import Policy
from trader.reflex.base import Reflex
from trader.risk.engine import RiskLimits

DAY = 86400
_G: dict = {}  # shared with forked workers (avoids pickling the price data per task)


def default_grid(base: Policy) -> list[Policy]:
    """Deliberately small (8 variants) to limit overfitting."""
    out = []
    for stop, rr, er in itertools.product((2.0, 3.5), (1.5, 3.0), (0.35, 0.55)):
        out.append(replace(base, version=f"{base.version}+s{stop}r{rr}e{er}", stop_atr_mult=stop, rr=rr,
                           rule=replace(base.rule, er_full=er), parent=base.version))
    return out


def train_score(m: dict, min_trades: int = 8) -> float:
    """Return per unit of drawdown; variants with too few trades are not trusted."""
    if m["trades"] < min_trades:
        return float("-inf")
    return m["total_return"] / max(abs(m["max_drawdown"]), 0.01)


def _train_task(args: tuple) -> tuple[int, int, dict]:
    fold, gi, t0, t1 = args
    g = _G
    res = run_backtest(g["series"], g["setups"], policy_at=lambda t, p=g["grid"][gi]: p, limits=g["limits"],
                       cost_of=g["cost_of"], spread_bps=g["spread"], depth_usd=g["depth"], t_start=t0,
                       t_end=t1, tf=g["tf"], tf_seconds=g["tf_s"], start_balance=g["balance"])
    return fold, gi, metrics(res.equity, res.trades, g["tf_s"], g["balance"])


def check_model_cutoff(reflex: Reflex, first_test_ts: int, cutoff_iso: str | None) -> None:
    if getattr(reflex, "uses_model", False):
        if not cutoff_iso:
            raise ValueError("a model REFLEX needs its training cutoff to be backtested")
        cutoff = int(dt.datetime.fromisoformat(cutoff_iso).replace(tzinfo=dt.timezone.utc).timestamp())
        if first_test_ts <= cutoff:
            raise ValueError(f"model-driven backtest must start after the training cutoff {cutoff_iso}: "
                             "the model may remember what happened before it")


def run(series: dict[str, Series], setups: list[Setup], base: Policy, *, limits: RiskLimits,
        cost_of: Callable[[str], CostModel], spread: dict[str, float], depth: dict[str, float],
        t_start: int, t_end: int, tf: str, tf_seconds: int, balance: float, benchmark: str,
        train_days: int = 365, test_days: int = 91, grid: list[Policy] | None = None, workers: int = 4,
        min_trades: int = 8) -> dict:
    grid = grid or default_grid(base)
    folds = []
    t = t_start + train_days * DAY
    while t < t_end:
        folds.append((t - train_days * DAY, t, min(t + test_days * DAY, t_end)))
        t += test_days * DAY
    if not folds:
        raise ValueError("not enough history for one train + test window")

    _G.update(series=series, setups=setups, grid=grid, limits=limits, cost_of=cost_of, spread=spread,
              depth=depth, tf=tf, tf_s=tf_seconds, balance=balance)
    tasks = [(fi, gi, f[0], f[1]) for fi, f in enumerate(folds) for gi in range(len(grid))]
    if workers > 1:
        with mp.get_context("fork").Pool(workers) as pool:
            results = pool.map(_train_task, tasks, chunksize=1)
    else:
        results = [_train_task(x) for x in tasks]

    chosen: list[Policy] = []
    fold_rows = []
    for fi, (tr0, te0, te1) in enumerate(folds):
        scored = sorted(((train_score(m, min_trades), gi, m) for f, gi, m in results if f == fi),
                        key=lambda x: (-x[0], x[1]))
        best_score, gi, m = scored[0]
        pick = grid[gi] if best_score > float("-inf") else base  # no trustworthy variant: keep the base
        chosen.append(pick)
        fold_rows.append({"fold": fi, "train": [_d(tr0), _d(te0)], "test": [_d(te0), _d(te1)],
                          "picked": pick.version, "train_return": m["total_return"],
                          "train_trades": m["trades"], "train_score": best_score})

    oos0, oos1 = folds[0][1], folds[-1][2]

    def policy_at(ts: int) -> Policy:
        for (_, te0, te1), p in zip(folds, chosen):
            if te0 <= ts < te1:
                return p
        return chosen[-1]

    oos = run_backtest(series, setups, policy_at=policy_at, limits=limits, cost_of=cost_of, spread_bps=spread,
                       depth_usd=depth, t_start=oos0, t_end=oos1, tf=tf, tf_seconds=tf_seconds,
                       start_balance=balance)
    strat = metrics(oos.equity, oos.trades, tf_seconds, balance)
    bh_eq = buy_and_hold(series[benchmark], oos0, oos1, tf_seconds, balance, cost_of(benchmark),
                         spread.get(benchmark, 1.0))
    bench = metrics(bh_eq, [], tf_seconds, balance)
    for row, (_, te0, te1) in zip(fold_rows, folds):
        e = oos.equity[(oos.equity.index > te0) & (oos.equity.index <= te1)]
        b = bh_eq[(bh_eq.index > te0) & (bh_eq.index <= te1)]
        prev_e = oos.equity[oos.equity.index <= te0]
        prev_b = bh_eq[bh_eq.index <= te0]
        e0 = prev_e.iloc[-1] if len(prev_e) else balance
        b0 = prev_b.iloc[-1] if len(prev_b) else balance
        row["test_return"] = float(e.iloc[-1] / e0 - 1) if len(e) else 0.0
        row["btc_return"] = float(b.iloc[-1] / b0 - 1) if len(b) else 0.0
        row["test_trades"] = sum(1 for t in oos.trades if te0 < t["closed_ts"] <= te1)
        # Diagnostic only: the same window with a fresh account (as if a human had cleared the
        # kill switch and reset the balance). Still out-of-sample for the picked parameters.
        fr = run_backtest(series, setups, policy_at=lambda t, p=policy_at(te0): p, limits=limits,
                          cost_of=cost_of, spread_bps=spread, depth_usd=depth, t_start=te0, t_end=te1, tf=tf,
                          tf_seconds=tf_seconds, start_balance=balance)
        fm = metrics(fr.equity, fr.trades, tf_seconds, balance)
        row["fresh_return"], row["fresh_trades"], row["fresh_max_drawdown"] = (
            fm["total_return"], fm["trades"], fm["max_drawdown"])
    by_setup: dict[str, dict] = {}
    for tr in oos.trades:
        d = by_setup.setdefault(tr["setup_id"], {"trades": 0, "pnl": 0.0, "wins": 0})
        d["trades"] += 1
        d["pnl"] += tr["pnl"]
        d["wins"] += tr["pnl"] > 0
    return {
        "oos_span": [_d(oos0), _d(oos1)], "strategy": strat, "btc_hold": bench,
        "beats_btc_hold": strat["total_return"] > bench["total_return"],
        "fresh_folds_summary": {
            "note": "diagnostic: each test window with a fresh account; not a tradable track record",
            "windows_beating_btc": sum(r["fresh_return"] > r["btc_return"] for r in fold_rows),
            "windows_positive": sum(r["fresh_return"] > 0 for r in fold_rows), "windows": len(fold_rows),
            "mean_return": sum(r["fresh_return"] for r in fold_rows) / len(fold_rows),
            "mean_btc_return": sum(r["btc_return"] for r in fold_rows) / len(fold_rows)},
        "folds": fold_rows, "by_setup": by_setup, "stats": oos.stats, "killed": oos.killed,
        "exit_reasons": _count(t["reason"] for t in oos.trades),
        "assumptions": {"spread_bps": spread, "depth_usd": depth, "funding": "not simulated",
                        "order_book": "none in history; snapshot spr/imb are null",
                        "fills": "next bar open plus spread, slippage, impact and taker fee"},
    }


def _d(ts: int) -> str:
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%d")


def _count(items) -> dict:
    out: dict = {}
    for i in items:
        out[i] = out.get(i, 0) + 1
    return out


def run_from_config(cfg, cache_dir, base: Policy, workers: int = 4, train_days: int = 365,
                    test_days: int = 91, only: list[str] | None = None) -> dict:
    """Load cached history for every enabled setup and run the walk-forward."""
    from pathlib import Path

    from trader.backtest.engine import load_frame, prepare
    from trader.data.market import TF_SECONDS

    tf_s = TF_SECONDS[cfg.timeframe]
    scfgs = [s for s in cfg.setups if s.enabled and (not only or s.id in only)]
    symbols = {s.symbol for s in scfgs} | {cfg.context_symbol}
    frames = {s: load_frame(Path(cache_dir), cfg.exchange, s, cfg.timeframe) for s in sorted(symbols)}
    series = prepare(frames, cfg.context_symbol, tf_s)
    ctx = frames[cfg.context_symbol]["ts"]
    out = run(series, [s.build() for s in scfgs], base, limits=cfg.limits.build(), cost_of=cfg.cost_of,
              spread={**{s.symbol: s.bt_spread_bps for s in scfgs}, cfg.context_symbol: 1.0},
              depth={s.symbol: s.bt_depth_usd for s in scfgs}, t_start=int(ctx.min()),
              t_end=int(ctx.max()) + tf_s, tf=cfg.timeframe, tf_seconds=tf_s, balance=cfg.paper_balance,
              benchmark=cfg.context_symbol, train_days=train_days, test_days=test_days, workers=workers)
    out["history"] = {s: [_d(int(f["ts"].min())), _d(int(f["ts"].max())), len(f)] for s, f in frames.items()}
    out["setups"] = [s.id for s in scfgs]
    out["base_policy"] = base.version
    return out
