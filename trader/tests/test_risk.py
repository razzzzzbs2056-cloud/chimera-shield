import math

import pytest

from trader.risk.calibration import Calibrator, brier_score, fit_isotonic, reliability_table
from trader.risk.engine import Account, RiskEngine, RiskLimits
from trader.risk.sizing import MAX_KELLY_MULT, kelly_fraction, size_position
from trader.types import OrderIntent, Position, RiskState, Side


def acct(balance=1000.0, **kw):
    return Account(balance=balance, peak_equity=kw.pop("peak", balance), day="d",
                   day_start_equity=kw.pop("day_start", balance), **kw)


def intent(qty=1.0, px=100.0, stop=95.0, side=Side.BUY, sym="A", reduce=False):
    return OrderIntent(sym, side, qty, px, stop, None, reduce, "s", "cid")


def pos(sym="A", qty=1.0, entry=100.0):
    return Position(sym, qty, entry, 90.0, 120.0, 0, "s")


ENG = RiskEngine(RiskLimits())
M = {"A": 100.0, "B": 100.0, "C": 100.0, "D": 100.0}


def test_default_limits_match_the_brief():
    L = RiskLimits()
    assert (L.risk_per_trade, L.max_daily_loss, L.max_open_positions, L.max_leverage, L.kill_drawdown) == \
        (0.02, 0.05, 3, 2.0, 0.15)


def test_limits_cannot_be_configured_recklessly():
    for bad in (dict(risk_per_trade=0.5), dict(max_leverage=10), dict(kill_drawdown=0.9),
                dict(max_daily_loss=0.5), dict(max_open_positions=50)):
        with pytest.raises(ValueError):
            RiskLimits(**bad)


def test_per_trade_risk_limit():
    assert ENG.check_order(intent(qty=4.0), acct(), M).ok  # risks 20 = 2%
    v = ENG.check_order(intent(qty=4.1), acct(), M)
    assert not v.ok and "trade_risk_exceeds_limit" in v.reasons
    v = ENG.check_order(intent(qty=4.0), acct(), M, est_cost=1.0)  # costs count toward risk
    assert not v.ok


def test_stop_is_mandatory_and_on_the_right_side():
    assert "stop_required" in ENG.check_order(intent(stop=None), acct(), M).reasons
    assert "stop_on_wrong_side" in ENG.check_order(intent(stop=105.0), acct(), M).reasons
    assert "stop_on_wrong_side" in ENG.check_order(intent(stop=95.0, side=Side.SELL), acct(), M).reasons


def test_max_open_positions():
    a = acct(positions={s: pos(s, 0.1) for s in "ABC"})
    v = ENG.check_order(intent(sym="D", qty=0.1), a, M)
    assert not v.ok and "max_open_positions" in v.reasons


def test_leverage_limit():
    a = acct(positions={"B": pos("B", 19.0)})  # 1900 gross on 1000 equity
    v = ENG.check_order(intent(qty=1.5, stop=99.0), a, M)
    assert not v.ok and "leverage_limit" in v.reasons
    assert ENG.check_order(intent(qty=1.0, stop=99.0), a, M).ok


def test_daily_loss_blocks_new_risk():
    a = acct(balance=949.0, peak=1000.0, day_start=1000.0)
    v = ENG.check_order(intent(qty=0.1), a, M)
    assert not v.ok and "daily_loss_limit" in v.reasons
    assert ENG.read(a, M).state is RiskState.REDUCE


def test_kill_switch_latches_and_survives_recovery():
    a = acct(balance=850.0, peak=1000.0, day_start=850.0)
    r = ENG.read(a, M)
    assert r.kill and a.kill_latched
    a.balance = 2000.0  # even a full recovery does not clear it
    assert ENG.read(a, M).kill
    assert "kill_switch" in ENG.check_order(intent(qty=0.1), a, M).reasons


def test_reduce_only_always_allowed_but_never_grows_or_flips():
    a = acct(balance=500.0, peak=1000.0, positions={"A": pos("A", 2.0)})
    ENG.read(a, M)
    assert a.kill_latched
    assert ENG.check_order(intent(qty=2.0, side=Side.SELL, stop=None, reduce=True), a, M).ok
    assert not ENG.check_order(intent(qty=2.5, side=Side.SELL, stop=None, reduce=True), a, M).ok
    assert not ENG.check_order(intent(qty=1.0, side=Side.BUY, stop=None, reduce=True), a, M).ok
    assert not ENG.check_order(intent(sym="B", qty=1.0, side=Side.SELL, stop=None, reduce=True), a, M).ok


def test_bad_numbers_are_rejected():
    for q in (0, -1, float("nan"), float("inf")):
        assert not ENG.check_order(intent(qty=q), acct(), M).ok
    assert not ENG.check_order(intent(px=float("nan")), acct(), M).ok
    assert not ENG.check_order(intent(sym="ZZZ"), acct(), M).ok


def test_non_finite_equity_trips_the_kill():
    a = acct(positions={"A": pos("A", 1.0)})
    assert ENG.read(a, {"A": float("nan")}).kill


def test_near_limit_state_and_drawdown_scaling():
    a = acct(balance=962.0, peak=1000.0, day_start=1000.0)  # 3.8% daily loss >= 70% of 5%
    assert ENG.read(a, M).state is RiskState.NEAR_LIMIT
    assert ENG.read(acct(), M).state is RiskState.SAFE
    # drawdown below the kill level must not deadlock trading; it shrinks size instead
    deep = acct(balance=890.0, peak=1000.0, day_start=890.0)
    assert ENG.read(deep, M).state is RiskState.SAFE
    assert ENG.risk_scale(0.0) == 1.0 and ENG.risk_scale(0.075) == pytest.approx(0.5)
    assert ENG.risk_scale(0.14) == 0.25 and ENG.risk_scale(0.5) == 0.25


def test_kelly_math():
    assert kelly_fraction(0.6, 2.0) == pytest.approx(0.4)
    assert kelly_fraction(0.3, 2.0) < 0
    assert kelly_fraction(0.6, 0) == 0


SZ = dict(equity=1000.0, price=100.0, stop=95.0, rr=2.0, risk_per_trade=0.02, kelly_mult=0.25,
          cost_frac=0.0, gross_exposure=0.0, max_leverage=2.0)


def test_sizing_caps_at_risk_limit_and_quarter_kelly():
    r = size_position(p_win=0.7, **SZ)
    assert r.risk_frac == pytest.approx(0.02) and r.qty == pytest.approx(4.0)
    r = size_position(p_win=0.36, **SZ)  # full kelly 0.04 -> quarter = 0.01
    assert r.risk_frac == pytest.approx(0.01)
    r = size_position(p_win=0.36, **{**SZ, "kelly_mult": 1.0})  # asking for full Kelly is clamped
    assert r.risk_frac == pytest.approx(MAX_KELLY_MULT * 0.04)


def test_sizing_refuses_without_edge_or_when_costs_eat_reward():
    assert size_position(p_win=0.30, **SZ).reason == "no_edge"
    assert size_position(p_win=0.9, **{**SZ, "cost_frac": 0.2}).reason == "costs_exceed_reward"
    assert size_position(p_win=0.9, **{**SZ, "stop": 100.0}).reason == "zero_stop_distance"
    assert size_position(p_win=float("nan"), **SZ).reason == "bad_inputs"


def test_sizing_costs_reduce_size():
    assert size_position(p_win=0.7, **{**SZ, "cost_frac": 0.004}).qty < 4.0


def test_sizing_leverage_liquidity_and_minimums():
    r = size_position(p_win=0.7, **{**SZ, "stop": 99.9, "gross_exposure": 1900.0})
    assert r.reason == "ok_capped_by_leverage" and r.qty * 100 == pytest.approx(100.0)
    r = size_position(p_win=0.7, depth_usd=1000.0, max_depth_frac=0.05, **SZ)
    assert r.reason == "ok_capped_by_liquidity" and r.qty * 100 == pytest.approx(50.0)
    assert size_position(p_win=0.7, **{**SZ, "equity": 10.0}).reason == "below_min_notional"
    assert size_position(p_win=0.7, lot=1.0, **{**SZ, "stop": 94.0}).qty == 3.0


def test_calibrator_shrinks_and_caps():
    c = Calibrator()
    assert c.p_win(0.9) == pytest.approx(0.7)
    assert c.p_win(1.0) <= c.max_p
    k = Calibrator(knots=((0.6, 0.4), (0.9, 0.6)))
    assert k.p_win(0.5) == 0.4 and k.p_win(0.75) == pytest.approx(0.5) and k.p_win(0.99) == 0.6
    assert Calibrator.from_dict(k.to_dict()) == k


def test_brier_and_reliability():
    assert brier_score([1.0, 0.0], [1, 0]) == 0
    assert brier_score([0.5, 0.5], [1, 0]) == 0.25
    with pytest.raises(ValueError):
        brier_score([], [])
    t = reliability_table([0.1, 0.15, 0.9, 1.0], [0, 0, 1, 1])
    assert sum(r["n"] for r in t) == 4


def test_isotonic_fit_is_monotone_and_needs_data():
    assert fit_isotonic([0.9] * 10, [1] * 10) is None
    confs = [0.5 + 0.4 * (i % 100) / 100 for i in range(600)]
    outs = [1 if (i * 7919) % 100 < 30 + 40 * (c - 0.5) / 0.4 else 0 for i, c in enumerate(confs)]
    cal = fit_isotonic(confs, outs)
    ps = [p for _, p in cal.knots]
    assert ps == sorted(ps) and all(0 <= p <= 1 for p in ps)
    assert cal.p_win(0.9) > cal.p_win(0.5) and math.isfinite(cal.p_win(0.7))
