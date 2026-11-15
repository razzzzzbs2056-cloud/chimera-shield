"""Tests for the pure decision and risk functions in user_data/strategies/ChimeraRule.py.

Run with either environment:  pytest tests   (freqtrade is optional for these tests).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ChimeraRule", ROOT / "user_data/strategies/ChimeraRule.py")
cr = importlib.util.module_from_spec(spec)
sys.modules["ChimeraRule"] = cr
spec.loader.exec_module(cr)

UTC = timezone.utc


def candles(n: int = 700, seed: int = 1, drift: float = 0.0006) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(drift, 0.01, n)))
    high = close * (1 + rng.uniform(0, 0.006, n))
    low = close * (1 - rng.uniform(0, 0.006, n))
    return pd.DataFrame({
        "date": pd.date_range("2025-01-01", periods=n, freq="1h", tz="UTC"),
        "open": np.roll(close, 1), "high": high, "low": low, "close": close,
        "volume": rng.uniform(100, 1000, n),
    })


def scored(bias: str, seed: int = 1, drift: float = 0.0006) -> pd.DataFrame:
    df = cr.add_features(candles(seed=seed, drift=drift))
    btc = cr.add_features(candles(seed=seed + 100, drift=drift))
    df["btc_r24"], df["btc_volr"], df["btc_ma_s"] = btc["f_r24"], btc["f_volr"], btc["f_ma_s"]
    return cr.add_rule(df, bias)


# ---------------------------------- signal ----------------------------------

@pytest.mark.parametrize("bias", ["long", "short"])
def test_no_lookahead(bias):
    """A row computed on truncated history equals the same row computed on full history."""
    full = scored(bias, drift=0.0006 if bias == "long" else -0.0006)
    cols = ["f_atr", "f_ma_s", "f_er", "f_rsi", "conf", "quality", "gate_ok"]
    for cut in (300, 450, 699):
        raw, braw = candles().iloc[: cut + 1].copy(), candles(seed=101).iloc[: cut + 1].copy()
        if bias == "short":
            raw = candles(drift=-0.0006).iloc[: cut + 1].copy()
            braw = candles(seed=101, drift=-0.0006).iloc[: cut + 1].copy()
        part, btc = cr.add_features(raw), cr.add_features(braw)
        part["btc_r24"], part["btc_volr"], part["btc_ma_s"] = btc["f_r24"], btc["f_volr"], btc["f_ma_s"]
        part = cr.add_rule(part, bias)
        for c in cols:
            assert part[c].iloc[-1] == pytest.approx(full[c].iloc[cut], nan_ok=True), (c, cut)


def test_gate_thresholds_hold_on_every_entry_bar():
    for bias, drift in (("long", 0.0012), ("short", -0.0012)):
        df = scored(bias, drift=drift)
        ok = df[df["gate_ok"]]
        assert len(ok) > 0, "test data should produce some entries"
        assert (ok["conf"] > cr.MIN_CONFIDENCE).all()
        assert (ok["quality"] >= cr.MIN_QUALITY).all()
        assert ok["directional"].all()
        assert not ok["crisis"].any()


def test_crisis_blocks_entries_for_the_cooldown():
    df = cr.add_features(candles(drift=0.0012))
    btc = cr.add_features(candles(seed=101, drift=0.0012))
    df["btc_r24"], df["btc_volr"], df["btc_ma_s"] = btc["f_r24"], btc["f_volr"], btc["f_ma_s"]
    df.loc[400, "btc_r24"] = -9.0  # one crisis bar
    df = cr.add_rule(df, "long")
    window = df.iloc[400: 400 + cr.CRISIS_COOLDOWN_BARS + 1]
    assert not window["gate_ok"].any()


def test_matches_the_original_rule_reflex():
    """Bar by bar, the port gives the same confidence and quality as trader/'s RuleReflex."""
    sys.path.insert(0, str(ROOT.parent / "trader" / "src"))
    try:
        from trader.policy import RuleParams
        from trader.reflex.rule import RuleReflex
        from trader.types import Direction, RiskState
    except ImportError:
        pytest.skip("original trader package (and pydantic) not importable here")
    reflex = RuleReflex(RuleParams())
    for bias, drift in (("long", 0.0008), ("short", -0.0008)):
        df = scored(bias, drift=drift).iloc[200:]
        for _, r in df.iterrows():
            snap = SimpleNamespace(
                btc_r24=r.btc_r24, btc_volr=r.btc_volr, btc_ma_s=r.btc_ma_s, volr=r.f_volr, er=r.f_er,
                ma_s=r.f_ma_s, ma_f=r.f_ma_f, hi=r.f_hi, lo=r.f_lo, r24=r.f_r24, rsi=r.f_rsi, imb=None,
                bias=Direction.LONG if bias == "long" else Direction.SHORT, rs=RiskState.SAFE,
            )
            d = reflex.decide(snap)
            assert d.direction_confidence == pytest.approx(r.conf, abs=1e-9)
            assert d.setup_quality == r.quality
            assert (d.regime.value == "crisis") == bool(r.crisis)


# ---------------------------------- sizing ----------------------------------

def test_p_win_is_shrunk_and_capped():
    assert cr.p_win(0.5) == 0.5
    assert cr.p_win(0.9) == pytest.approx(0.7)
    assert cr.p_win(1.0) <= cr.CAL_MAX_P
    assert cr.p_win(5.0) <= cr.CAL_MAX_P


@pytest.mark.parametrize("conf", [0.89, 0.92, 0.95])
@pytest.mark.parametrize("stop", [0.004, 0.02, 0.08])
@pytest.mark.parametrize("dd", [0.0, 0.07, 0.149])
def test_stake_never_risks_more_than_two_percent_or_one_times_equity(conf, stop, dd):
    equity = 1000.0
    notional, reason = cr.stake_for(equity, conf, stop, dd, gross_open=0.0)
    loss_if_stopped = notional * (stop + cr.ROUND_TRIP_COST)
    assert loss_if_stopped <= cr.RISK_PER_TRADE * equity + 1e-9
    assert notional <= cr.MAX_POSITION_FRAC * equity + 1e-9
    if notional > 0:
        assert reason == "ok"


def test_stake_shrinks_in_drawdown():
    at_peak, _ = cr.stake_for(1000, 0.95, 0.05, 0.0, 0.0)
    deep, _ = cr.stake_for(1000, 0.95, 0.05, 0.14, 0.0)
    assert 0 < deep < at_peak
    assert cr.risk_scale(0.5) == cr.MIN_RISK_SCALE


def test_stake_is_zero_without_edge_or_headroom():
    assert cr.stake_for(1000, 0.0, 0.02, 0.0, 0.0) == (0.0, "no_edge")
    assert cr.stake_for(1000, 0.95, 0.0005, 0.0, 0.0)[1] == "costs_exceed_reward"
    assert cr.stake_for(1000, 0.95, 0.02, 0.0, gross_open=2000.0) == (0.0, "no_leverage_headroom")
    assert cr.stake_for(float("nan"), 0.95, 0.02, 0.0, 0.0)[0] == 0.0
    assert cr.stake_for(-5, 0.95, 0.02, 0.0, 0.0)[0] == 0.0


def test_gross_exposure_capped_at_two_times_equity():
    notional, _ = cr.stake_for(1000, 0.95, 0.004, 0.0, gross_open=1900.0)
    assert notional <= 100.0 + 1e-9


def test_stop_fraction_bounds():
    assert cr.stop_fraction(1.0) == pytest.approx(0.025)
    assert cr.stop_fraction(0.0) == 0.003
    assert cr.stop_fraction(500.0) == 0.25


# ------------------------------ account limits ------------------------------

T0 = datetime(2026, 1, 10, 12, tzinfo=UTC)


def test_kill_switch_trips_at_fifteen_percent_and_stays_latched():
    trades = [(T0, -100.0), (T0 + timedelta(days=1), -50.0)]
    st = cr.equity_state(trades, 1000, T0 + timedelta(days=2))
    assert st["killed"] and st["drawdown"] == pytest.approx(0.15)
    # A later recovery does not un-kill it.
    trades.append((T0 + timedelta(days=3), 400.0))
    assert cr.equity_state(trades, 1000, T0 + timedelta(days=4))["killed"]


def test_kill_switch_not_tripped_below_the_limit():
    st = cr.equity_state([(T0, -149.0)], 1000, T0 + timedelta(days=1))
    assert not st["killed"]


def test_kill_switch_measures_from_the_peak():
    trades = [(T0, 500.0), (T0 + timedelta(days=1), -225.0)]  # 1500 -> 1275 is exactly -15%
    assert cr.equity_state(trades, 1000, T0 + timedelta(days=2))["killed"]


def test_only_a_dated_human_clear_releases_the_kill_switch():
    trades = [(T0, -200.0)]
    now = T0 + timedelta(days=5)
    assert cr.equity_state(trades, 1000, now)["killed"]
    assert not cr.equity_state(trades, 1000, now, cleared_at=T0 + timedelta(days=1))["killed"]
    # A clear dated before the loss, or in the future, changes nothing.
    assert cr.equity_state(trades, 1000, now, cleared_at=T0 - timedelta(days=1))["killed"]
    assert cr.equity_state(trades, 1000, now, cleared_at=now + timedelta(days=1))["killed"]
    # After a clear the peak restarts: a fresh 15% loss trips it again.
    more = trades + [(T0 + timedelta(days=2), -120.0)]
    assert cr.equity_state(more, 1000, now, cleared_at=T0 + timedelta(days=1))["killed"]


def test_daily_loss_stop_is_for_the_current_utc_day_only():
    now = T0 + timedelta(hours=3)
    assert cr.equity_state([(T0, -50.0)], 1000, now)["daily_stop"]
    assert not cr.equity_state([(T0, -49.0)], 1000, now)["daily_stop"]
    assert not cr.equity_state([(T0, -50.0)], 1000, now + timedelta(days=1))["daily_stop"]


def test_zero_equity_counts_as_killed():
    assert cr.equity_state([(T0, -1000.0)], 1000, T0)["killed"]


# -------------------------------- order book --------------------------------

def test_book_imbalance():
    book = {"bids": [[99, 9.0], [98, 1.0]], "asks": [[100, 1.0], [101, 1.0]]}
    assert cr.book_imbalance(book) == pytest.approx(8 / 12)
    for bad in ({}, {"bids": [], "asks": [[1, 1]]}, {"bids": [[101, 1]], "asks": [[100, 1]]},
                {"bids": [[99, 0]], "asks": [[100, 0]]}):
        with pytest.raises(ValueError):
            cr.book_imbalance(bad)


# ---------------------------------- config ----------------------------------

def test_committed_config_is_paper_only_and_has_no_secrets():
    cfg = json.loads((ROOT / "config.json").read_text())
    assert cfg["dry_run"] is True
    ex = cfg["exchange"]
    assert ex["key"] == "" and ex["secret"] == "" and ex.get("password", "") == ""
    assert cfg["max_open_trades"] == 3
    assert cfg["dry_run_wallet"] == 1000
    assert sorted(ex["pair_whitelist"]) == sorted(cr.SETUPS)
    assert cfg.get("force_entry_enable", False) is False
    assert "api_server" not in cfg and "telegram" not in cfg  # those need secrets: config-private.json


def test_denylisted_coins_are_not_configured():
    banned = {"DOGE", "SHIB", "PEPE", "WIF", "BONK", "FLOKI", "TRUMP", "PUMP", "XMR", "ZEC", "DASH"}
    assert not {p.split("/")[0] for p in cr.SETUPS} & banned


def test_hard_limits_are_the_agreed_numbers():
    assert (cr.RISK_PER_TRADE, cr.MAX_DAILY_LOSS, cr.KILL_DRAWDOWN, cr.MAX_LEVERAGE) == (0.02, 0.05, 0.15, 2.0)
    assert cr.KELLY_MULT <= 0.25 and cr.POSITION_LEVERAGE <= cr.MAX_LEVERAGE


def test_strategy_class_loads_under_freqtrade():
    pytest.importorskip("freqtrade")
    s = cr.ChimeraRule
    assert s.can_short and s.use_custom_stoploss and s.use_custom_roi and s.timeframe == "1h"
    assert s.startup_candle_count >= cr.SLOW + cr.CRISIS_COOLDOWN_BARS
