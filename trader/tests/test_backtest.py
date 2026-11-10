import math
import random

import pandas as pd
import pytest

from trader.backtest import walkforward as wf
from trader.backtest.engine import buy_and_hold, metrics, prepare, run_backtest
from trader.core import Setup
from trader.exec.broker import CostModel
from trader.policy import Policy
from trader.risk.engine import RiskLimits
from trader.state.features import WARMUP
from trader.types import Direction

TF = 3600
T0 = 1_700_000_000 - (1_700_000_000 % TF)
N = 1500


def frame(seed, drift, vol=0.004, n=N, start=100.0):
    rng = random.Random(seed)
    rows, px = [], start
    for i in range(n):
        o = px
        c = o * math.exp(drift + rng.gauss(0, vol))
        rows.append([T0 + i * TF, o, max(o, c) * 1.001, min(o, c) * 0.999, c, 1000.0 + rng.random()])
        px = c
    return pd.DataFrame(rows, columns=["ts", "open", "high", "low", "close", "volume"])


def world(drift=0.0012, seed=1):
    frames = {"BTC/USDT": frame(seed, 0.0008), "AAA/USDT": frame(seed + 1, drift)}
    return prepare(frames, "BTC/USDT", TF), frames


SETUPS = [Setup("aaa-long", "AAA/USDT", "AAA", Direction.LONG, "spot")]
POL = Policy(version="bt")
KW = dict(limits=RiskLimits(), spread_bps={"AAA/USDT": 4.0}, depth_usd={"AAA/USDT": 500_000.0},
          t_start=T0, t_end=T0 + N * TF, tf_seconds=TF, start_balance=1000.0)


def run(series, cost=CostModel(), **kw):
    return run_backtest(series, SETUPS, policy_at=lambda t: POL, cost_of=lambda s: cost, **{**KW, **kw})


def test_backtest_trades_and_is_deterministic():
    series, _ = world()
    a, b = run(series), run(series)
    assert len(a.trades) > 3 and a.final_positions == 0
    assert a.equity.equals(b.equity) and a.trades == b.trades


def test_no_lookahead_future_bars_do_not_change_the_past():
    series, frames = world()
    base = run(series)
    cut = T0 + 900 * TF
    f2 = {k: v.copy() for k, v in frames.items()}
    for df in f2.values():
        m = df["ts"] >= cut
        df.loc[m, ["open", "high", "low", "close"]] = df.loc[m, ["open", "high", "low", "close"]] * 0.5
    alt = run(prepare(f2, "BTC/USDT", TF))
    before = base.equity.index < cut
    assert before.sum() > 500
    pd.testing.assert_series_equal(base.equity[before], alt.equity[alt.equity.index < cut])
    assert not base.equity.equals(alt.equity)


def test_entries_fill_at_the_next_open_with_costs():
    series, frames = world()
    res = run(series, journal_all=True)
    S = series["AAA/USDT"]
    entries = [f for f in res.fills if f.get("kind") == "entry" and f.get("status") == "filled"]
    assert entries
    for f in entries:
        k = S.index[f["ts"]]  # the fill is stamped with a bar's open time
        assert f["price"] > S.o[k]  # paid more than the open: half-spread + slippage
        assert f["fee"] == pytest.approx(f["qty"] * f["price"] * 0.001)
    dec_ts = {d["ts"] for d in res.decisions if d["action"] == "enter_pending"}
    assert {f["ts"] for f in entries} <= dec_ts  # decided at a close, filled at that same instant's next open


def test_no_decisions_before_warmup():
    series, _ = world()
    res = run(series, journal_all=True)
    assert min(d["ts"] for d in res.decisions) >= T0 + (WARMUP + 1) * TF


def test_costs_reduce_results_and_prohibitive_costs_stop_trading():
    series, _ = world()
    cheap = run(series, CostModel(taker_fee=0.0))
    normal = run(series, CostModel(taker_fee=0.001))
    assert cheap.equity.iloc[-1] > normal.equity.iloc[-1]
    assert len(run(series, CostModel(taker_fee=0.05)).trades) == 0


def test_failed_orders_do_not_corrupt_the_account():
    series, _ = world()
    res = run(series, fail_prob=0.3)
    assert res.final_positions <= 1 and res.stats["order_failures"] > 0
    assert math.isfinite(res.equity.iloc[-1]) and res.equity.min() > 0


def test_downtrend_long_setup_stays_mostly_flat():
    series, _ = world(drift=-0.0015)
    res = run(series)
    assert res.equity.iloc[-1] > 900  # a long-only setup in a falling market must not bleed out


def test_gap_in_data_is_a_fault_not_a_trade():
    _, frames = world()
    f2 = {k: v.copy() for k, v in frames.items()}
    f2["AAA/USDT"] = f2["AAA/USDT"].drop(index=range(600, 640)).reset_index(drop=True)
    res = run(prepare(f2, "BTC/USDT", TF), journal_all=True)
    assert res.stats["fault"] > 0
    gap_start, gap_end = T0 + 600 * TF, T0 + (640 + WARMUP) * TF
    assert not [d for d in res.decisions if gap_start < d["ts"] <= gap_end and d["action"] != "hold"]


def test_metrics_and_buy_and_hold():
    eq = pd.Series([1100.0, 990.0, 1210.0], index=[T0 + TF, T0 + 2 * TF, T0 + 3 * TF])
    m = metrics(eq, [{"pnl": 10.0}, {"pnl": -5.0}], TF, 1000.0)
    assert m["total_return"] == pytest.approx(0.21) and m["max_drawdown"] == pytest.approx(-0.1)
    assert m["win_rate"] == 0.5 and m["profit_factor"] == 2.0
    series, _ = world()
    S = series["BTC/USDT"]
    bh = buy_and_hold(S, T0, T0 + N * TF, TF, 1000.0, CostModel(taker_fee=0.001, slippage_bps=2), 2.0)
    gross = S.c[-1] / S.o[0]
    assert bh.iloc[-1] == pytest.approx(1000 * gross / (1.001 * 1.0003), rel=1e-9) and len(bh) == N


def test_walk_forward_only_scores_unseen_windows():
    series, _ = world()
    out = wf.run(series, SETUPS, POL, limits=RiskLimits(), cost_of=lambda s: CostModel(),
                 spread={"AAA/USDT": 4.0}, depth={"AAA/USDT": 500_000.0}, t_start=T0, t_end=T0 + N * TF,
                 tf="1h", tf_seconds=TF, balance=1000.0, benchmark="BTC/USDT", train_days=25, test_days=12,
                 workers=1, min_trades=2)
    assert len(out["folds"]) == 4
    for f in out["folds"]:
        assert f["train"][1] == f["test"][0]  # the test window starts where training ends
    assert out["oos_span"][0] == out["folds"][0]["test"][0]
    assert isinstance(out["beats_btc_hold"], bool) and "btc_hold" in out


def test_model_reflex_cannot_be_backtested_before_its_cutoff():
    class M:
        uses_model = True
    with pytest.raises(ValueError):
        wf.check_model_cutoff(M(), T0, "2026-06-30")
    with pytest.raises(ValueError):
        wf.check_model_cutoff(M(), T0, None)
    wf.check_model_cutoff(M(), 1_790_000_000, "2026-06-30")
    wf.check_model_cutoff(type("R", (), {"uses_model": False})(), T0, None)


def test_train_score_distrusts_thin_samples():
    assert wf.train_score({"trades": 2, "total_return": 5.0, "max_drawdown": -0.01}) == float("-inf")
    assert wf.train_score({"trades": 20, "total_return": 0.2, "max_drawdown": -0.1}) == pytest.approx(2.0)
    assert len({p.version for p in wf.default_grid(POL)}) == 8
