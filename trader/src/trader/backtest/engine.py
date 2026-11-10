"""Event-driven backtest that drives the SAME TraderCore used for paper and live.

Timing, per bar k: entries decided at the close of bar k-1 fill at the OPEN of bar k;
stops and targets are then checked against bar k's high/low (stop first if both hit);
a new decision is made at the close of bar k from features that use bars <= k only.
There is no historical order book, so spread and depth are stated assumptions and
order-book fields in the snapshot are null. Perp funding is not simulated.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from trader.alerts import Alerts
from trader.core import CoreConfig, Setup, TraderCore
from trader.exec.broker import CostModel, MarketView, PaperBroker
from trader.journal import Journal
from trader.policy import Policy
from trader.reflex.base import Reflex
from trader.reflex.rule import RuleReflex
from trader.risk.engine import Account, RiskEngine, RiskLimits
from trader.state.engine import DataFault, EngineConfig, assemble
from trader.state.features import FEATURE_COLS, WARMUP, compute_features
from trader.types import Candle


@dataclass
class Series:
    """One instrument's bars plus causal features, as plain arrays for a fast loop."""

    symbol: str
    ts: np.ndarray  # bar open times
    o: np.ndarray
    h: np.ndarray
    lo: np.ndarray
    c: np.ndarray
    v: np.ndarray
    feats: list[dict]  # feats[k] uses bars <= k
    btc: list[dict]  # BTC context at the same bar
    valid: np.ndarray  # True when the last WARMUP bars are contiguous and features are finite
    index: dict[int, int] = field(default_factory=dict)


def load_frame(cache_dir: Path, exchange: str, symbol: str, tf: str) -> pd.DataFrame:
    path = Path(cache_dir) / f"{exchange}_{symbol.replace('/', '-').replace(':', '_')}_{tf}.csv"
    return pd.read_csv(path).drop_duplicates("ts").sort_values("ts").reset_index(drop=True)


def prepare(frames: dict[str, pd.DataFrame], context_symbol: str, tf_seconds: int) -> dict[str, Series]:
    bars_per_year = 365 * 86400 / tf_seconds
    feats = {s: compute_features(df, bars_per_year) for s, df in frames.items()}
    ctx = feats[context_symbol][["r24", "ma_s", "volr"]].copy()
    ctx["ts"] = frames[context_symbol]["ts"].values
    ctx_valid = _contiguous(frames[context_symbol]["ts"].values, tf_seconds)
    ctx = ctx[ctx_valid].set_index("ts")
    out = {}
    for s, df in frames.items():
        ts = df["ts"].values.astype("int64")
        f = feats[s]
        b = ctx.reindex(ts)
        finite = np.isfinite(f[list(FEATURE_COLS)].values).all(axis=1) & np.isfinite(b.values).all(axis=1)
        out[s] = Series(
            symbol=s, ts=ts, o=df["open"].values, h=df["high"].values, lo=df["low"].values,
            c=df["close"].values, v=df["volume"].values, feats=f.to_dict("records"),
            btc=b.to_dict("records"), valid=finite & _contiguous(ts, tf_seconds),
            index={int(t): i for i, t in enumerate(ts)},
        )
    return out


def _contiguous(ts: np.ndarray, step: int) -> np.ndarray:
    """ok[k] is True when bars k-WARMUP..k have no gaps."""
    gap = np.ones(len(ts), dtype=int)
    gap[1:] = (np.diff(ts) != step).astype(int)
    run = pd.Series(gap).rolling(WARMUP + 1).sum().values
    return run == 0


@dataclass
class BacktestResult:
    equity: pd.Series  # indexed by bar close time
    trades: list[dict]
    decisions: list[dict]
    fills: list[dict]
    stats: dict
    killed: bool
    final_positions: int


def run_backtest(
    series: dict[str, Series], setups: list[Setup], *, policy_at: Callable[[int], Policy],
    limits: RiskLimits, cost_of: Callable[[str], CostModel], spread_bps: dict[str, float],
    depth_usd: dict[str, float], t_start: int, t_end: int, tf: str = "1h", tf_seconds: int = 3600,
    start_balance: float = 1000.0, reflex_for: Callable[[Policy], Reflex] | None = None,
    journal_all: bool = False, fail_prob: float = 0.0,
) -> BacktestResult:
    """Run over bars with open time in [t_start, t_end). Open positions are closed at the end."""
    reflex_for = reflex_for or (lambda p: RuleReflex(p.rule))
    policy = policy_at(t_start)
    account = Account(balance=start_balance, peak_equity=start_balance, day="", day_start_equity=start_balance)
    broker = PaperBroker({}, CostModel(), fail_prob=fail_prob)
    broker.cost = cost_of  # type: ignore[method-assign]
    journal = Journal(None)
    core = TraderCore(setups=setups, policy=policy, reflex=reflex_for(policy), broker=broker,
                      risk=RiskEngine(limits), account=account, journal=journal, alerts=_Quiet(),
                      cfg=CoreConfig(tf_seconds=tf_seconds, latency_budget_s=60.0, defer_entries=True,
                                     journal_all_decisions=journal_all), cost_of=cost_of)
    ecfg = EngineConfig(tf=tf, tf_seconds=tf_seconds, require_book=False)
    syms = [s.symbol for s in setups if s.enabled and s.symbol in series]
    marks: dict[str, float] = {}
    eq_ts, eq_val = [], []

    def synth(sym: str, px: float, ts: int) -> MarketView:
        half = px * spread_bps.get(sym, 3.0) / 2e4
        return MarketView(sym, px - half, px + half, depth_usd.get(sym, 100_000.0), ts)

    for t in range(t_start, t_end, tf_seconds):
        asof = t + tf_seconds
        new_policy = policy_at(t)
        if new_policy.version != core.policy.version:
            core.policy, core.reflex = new_policy, reflex_for(new_policy)
        live = [(s, series[s].index[t]) for s in syms if t in series[s].index]
        for s, k in live:  # 1. fills at the open
            S = series[s]
            marks.setdefault(s, float(S.o[k]))
            if s in core.pending:
                core.execute_pending(s, synth(s, float(S.o[k]), t), marks)
        for s, k in live:  # 2. exits against this bar's range
            if s in account.positions:
                S = series[s]
                bar = Candle(t, asof, float(S.o[k]), float(S.h[k]), float(S.lo[k]), float(S.c[k]), float(S.v[k]))
                forced = s in core.exit_pending
                core.process_exits(
                    s, asof, bar,
                    lambda ref, s=s, bar=bar, forced=forced: synth(
                        s, ref if ref is not None else (bar.open if forced else bar.close), asof), marks)
        for s, k in live:
            marks[s] = float(series[s].c[k])
        if not marks:
            continue
        reading = core.begin_bar(asof, marks)  # 3. risk, then decisions at the close
        for s, k in live:
            S = series[s]
            setup = core.setups[s]
            px = float(S.c[k])
            view = synth(s, px, asof)
            if not S.valid[k]:
                if k >= WARMUP:  # before warm-up there is simply no signal; after it, a gap is a fault
                    core.decide(s, asof, DataFault("missing_data", "gap or non-finite feature"), view,
                                marks, reading)
                continue
            try:
                snap = assemble(asof=asof, symbol=s, cfg=ecfg, bias=setup.bias, feat=S.feats[k],
                                btc=S.btc[k], px=px, spread_bps=None, imbalance=None, funding_pct=None,
                                invalidation_price=setup.invalidation_price,
                                account=core.account_view(s, marks, reading))
            except DataFault as e:
                snap = e
            core.decide(s, asof, snap, view, marks, reading)
        eq_ts.append(asof)
        eq_val.append(reading.equity)

    # close whatever is still open at the last known price, paying costs
    last = t_end
    for s in list(account.positions):
        core.exit_pending[s] = "end_of_test"
        px = marks[s]
        bar = Candle(last - tf_seconds, last, px, px, px, px, 0.0)
        core.process_exits(s, last, bar, lambda ref, s=s, px=px: synth(s, px, last), marks)
    if eq_ts:
        eq_val[-1] = account.equity(marks)
    return BacktestResult(pd.Series(eq_val, index=eq_ts, dtype=float), journal.read("trades"),
                          journal.read("decisions"), journal.read("fills"), dict(core.stats),
                          account.kill_latched, len(account.positions))


class _Quiet(Alerts):
    def notify(self, level: str, text: str, key: str | None = None) -> bool:  # no logging in backtests
        self.sent.append((level, text))
        return True


def metrics(equity: pd.Series, trades: list[dict], tf_seconds: int, start_balance: float) -> dict:
    if len(equity) < 2:
        return {"total_return": 0.0, "cagr": 0.0, "max_drawdown": 0.0, "sharpe": 0.0, "trades": 0,
                "win_rate": 0.0, "profit_factor": 0.0, "final_equity": start_balance}
    eq = pd.concat([pd.Series([start_balance], index=[equity.index[0] - tf_seconds]), equity])
    rets = eq.pct_change().dropna()
    years = (eq.index[-1] - eq.index[0]) / (365 * 86400)
    total = eq.iloc[-1] / eq.iloc[0] - 1
    dd = (eq / eq.cummax() - 1).min()
    sd = rets.std(ddof=0)
    wins = [t["pnl"] for t in trades if t["pnl"] > 0]
    losses = [-t["pnl"] for t in trades if t["pnl"] <= 0]
    return {
        "total_return": float(total),
        "cagr": float((1 + total) ** (1 / years) - 1) if years > 0 and total > -1 else float("nan"),
        "max_drawdown": float(dd),
        "sharpe": float(rets.mean() / sd * math.sqrt(365 * 86400 / tf_seconds)) if sd > 0 else 0.0,
        "trades": len(trades),
        "win_rate": len(wins) / len(trades) if trades else 0.0,
        "profit_factor": sum(wins) / sum(losses) if losses and sum(losses) > 0 else float("inf") if wins else 0.0,
        "final_equity": float(eq.iloc[-1]),
    }


def buy_and_hold(S: Series, t_start: int, t_end: int, tf_seconds: int, start_balance: float,
                 cost: CostModel, spread_bps: float) -> pd.Series:
    """Benchmark: spend the whole balance on the asset at the first open, pay entry costs once, hold."""
    ks = [S.index[t] for t in range(t_start, t_end, tf_seconds) if t in S.index]
    entry = float(S.o[ks[0]]) * (1 + (cost.slippage_bps + spread_bps / 2) / 1e4)
    qty = start_balance / (entry * (1 + cost.taker_fee))
    return pd.Series([qty * float(S.c[k]) for k in ks], index=[int(S.ts[k]) + tf_seconds for k in ks])
