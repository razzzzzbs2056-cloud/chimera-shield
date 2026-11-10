
import pytest

from tests.conftest import T0, TF, StubReflex, good_decision, make_candles, make_core, snap_for, view
from trader.core import Setup
from trader.exec.broker import CostModel, PaperBroker
from trader.risk.engine import RiskLimits
from trader.state.engine import DataFault
from trader.types import Candle, Direction, Regime

SYM = "AAA/USDT"
CANDLES = make_candles()
SNAP = snap_for(CANDLES)
M = {SYM: 100.0}


def bar(o=100.0, h=100.5, lo=99.5, c=100.0, t=T0):
    return Candle(t, t + TF, o, h, lo, c, 1000.0)


def enter(core, asof=T0):
    r = core.begin_bar(asof, M)
    return core.decide(SYM, asof, SNAP, view(ts=asof), M, r)


def test_clean_decision_becomes_a_sized_order_with_stop_and_target():
    core = make_core()
    rec = enter(core)
    pos = core.account.positions[SYM]
    assert rec["action"] == "enter" and pos.qty > 0
    assert pos.stop_price < pos.entry_price < pos.target_price
    risk = pos.qty * (pos.entry_price - pos.stop_price)
    assert risk <= 0.02 * 1000 + 1e-6
    assert core.journal.read("decisions")[0]["snapshot"]["sym"] == SYM


def test_gate_failure_places_no_order():
    core = make_core(StubReflex(good_decision(direction_confidence=0.80)))
    rec = enter(core)
    assert rec["action"] == "hold" and not core.account.positions and not core.journal.read("fills")


def test_late_or_broken_reflex_skips_the_candle():
    core = make_core(StubReflex(raises=TimeoutError("deadline")))
    rec = enter(core)
    assert rec["status"] == "error" and not core.account.positions and core.stats["error"] == 1
    core = make_core(StubReflex(None))  # returns garbage (no decision)
    rec = enter(core)
    assert rec["status"] == "error" and not core.account.positions


def test_data_fault_blocks_orders_without_calling_the_reflex():
    reflex = StubReflex(good_decision())
    core = make_core(reflex)
    r = core.begin_bar(T0, M)
    rec = core.decide(SYM, T0, DataFault("stale_data", "old"), view(), M, r)
    assert rec["status"] == "fault" and reflex.calls == 0 and not core.account.positions
    rec = core.decide(SYM, T0, SNAP, None, M, r)
    assert rec["status"] == "fault" and reflex.calls == 0


def test_stop_exits_without_the_reflex_even_when_it_is_down():
    reflex = StubReflex(good_decision())
    core = make_core(reflex)
    enter(core)
    pos = core.account.positions[SYM]
    reflex.raises = RuntimeError("model down")
    b = bar(lo=pos.stop_price * 0.99, c=pos.stop_price * 0.995, t=T0 + TF)
    core.begin_bar(T0 + 2 * TF, M)
    f = core.process_exits(SYM, T0 + 2 * TF, b, lambda ref: view(px=ref or b.close, ts=T0 + 2 * TF), M)
    assert f.done and SYM not in core.account.positions
    t = core.journal.read("trades")[0]
    assert t["reason"] == "stop" and t["pnl"] < 0
    assert 1000 - core.account.balance <= 0.02 * 1000 * 1.25  # loss ~ the 2% budget plus costs


def test_gap_through_stop_fills_at_the_open_not_the_stop():
    core = make_core()
    enter(core)
    pos = core.account.positions[SYM]
    gap_open = pos.stop_price * 0.97
    b = bar(o=gap_open, h=gap_open * 1.001, lo=gap_open * 0.99, c=gap_open, t=T0 + TF)
    f = core.process_exits(SYM, T0 + 2 * TF, b, lambda ref: view(px=ref, ts=T0 + 2 * TF), M)
    assert f.price < pos.stop_price * 0.975


def test_target_time_stop_and_invalidation_exits():
    core = make_core()
    enter(core)
    pos = core.account.positions[SYM]
    b = bar(h=pos.target_price * 1.01, t=T0 + TF)
    core.process_exits(SYM, T0 + 2 * TF, b, lambda ref: view(px=ref or 100, ts=T0 + 2 * TF), M)
    assert core.journal.read("trades")[0]["reason"] == "target"

    core = make_core()
    enter(core)
    late = T0 + (core.policy.time_stop_bars + 1) * TF
    core.process_exits(SYM, late, bar(t=late - TF), lambda ref: view(ts=late), M)
    assert core.journal.read("trades")[0]["reason"] == "time_stop"

    core = make_core(setups=[Setup("aaa-long", SYM, "AAA", Direction.LONG, "spot", invalidation_price=99.9)])
    enter(core)
    core.process_exits(SYM, T0 + 2 * TF, bar(c=99.8, lo=99.7, t=T0 + TF), lambda ref: view(px=99.8), M)
    assert core.journal.read("trades")[0]["reason"] == "thesis_invalidated"


def test_stop_checked_before_target_when_both_hit_in_one_bar():
    core = make_core()
    enter(core)
    pos = core.account.positions[SYM]
    b = bar(h=pos.target_price * 1.01, lo=pos.stop_price * 0.99, t=T0 + TF)
    core.process_exits(SYM, T0 + 2 * TF, b, lambda ref: view(px=ref), M)
    assert core.journal.read("trades")[0]["reason"] == "stop"


def test_failed_exit_is_retried_until_it_fills_and_alerts():
    core = make_core()
    enter(core)
    pos = core.account.positions[SYM]
    core.broker.fail_next()
    b = bar(lo=pos.stop_price * 0.99, t=T0 + TF)
    f = core.process_exits(SYM, T0 + 2 * TF, b, lambda ref: view(px=ref or 100), M)
    assert not f.done and SYM in core.account.positions and core.exit_pending[SYM] == "stop"
    assert any("EXIT ORDER FAILED" in t for _, t in core.alerts.sent)
    calm = bar(t=T0 + 2 * TF)  # price recovered: the exit must still go through
    f = core.process_exits(SYM, T0 + 3 * TF, calm, lambda ref: view(px=ref or 100), M)
    assert f.done and SYM not in core.account.positions


def test_failed_entry_is_not_retried_and_leaves_no_position():
    core = make_core()
    core.broker.fail_next()
    rec = enter(core)
    assert rec["action"] == "enter_failed" and not core.account.positions
    assert core.stats["order_failures"] == 1 and any("ENTRY ORDER" in t for _, t in core.alerts.sent)


def test_low_confidence_pauses_symbol_and_crisis_pauses_everything():
    reflex = StubReflex(good_decision(direction_confidence=0.5))
    core = make_core(reflex)
    assert enter(core)["action"] == "pause"
    reflex.decision = good_decision()
    assert "paused" in enter(core, T0 + TF)["reasons"]
    assert enter(core, T0 + (core.policy.pause_bars + 1) * TF)["action"] == "enter"

    reflex = StubReflex(good_decision(regime=Regime.CRISIS))
    core = make_core(reflex)  # default: cooldown that renews on every crisis reading
    assert enter(core)["action"] == "pause" and not core.account.positions
    assert enter(core, T0 + 10 * TF)["action"] == "pause"
    reflex.decision = good_decision()
    cool = core.policy.crisis_cooldown_bars
    assert "paused" in enter(core, T0 + (10 + cool - 1) * TF)["reasons"]
    assert enter(core, T0 + (10 + cool + 1) * TF)["action"] == "enter"
    assert any(lvl == "critical" for lvl, _ in core.alerts.sent)

    from trader.policy import Policy
    reflex = StubReflex(good_decision(regime=Regime.CRISIS))
    core = make_core(reflex, policy=Policy(version="m", crisis_cooldown_bars=0))  # manual resume only
    assert enter(core)["action"] == "pause" and core.global_pause
    reflex.decision = good_decision()
    assert "paused" in enter(core, T0 + 5000 * TF)["reasons"]


def test_kill_switch_flattens_and_blocks_new_orders():
    core = make_core()
    enter(core)
    crash = {SYM: 100.0}
    core.account.balance -= 200  # simulate a 20% loss from elsewhere
    r = core.begin_bar(T0 + TF, crash)
    assert r.kill and core.exit_pending[SYM] == "kill_switch"
    core.process_exits(SYM, T0 + TF, bar(t=T0), lambda ref: view(ts=T0 + TF), crash)
    assert not core.account.positions
    rec = core.decide(SYM, T0 + TF, SNAP, view(ts=T0 + TF), crash, core.begin_bar(T0 + TF, crash))
    assert rec["action"] == "hold" and "risk_state_not_safe" in rec["reasons"] and not core.account.positions


def test_reconciliation_mismatch_halts_entries():
    core = make_core()
    core.broker._pos["GHOST/USDT"] = 3.0
    r = core.begin_bar(T0, M)
    assert core.halt_reason
    assert "paused" in core.decide(SYM, T0, SNAP, view(), M, r)["reasons"]


def test_deferred_entry_fills_next_bar_and_is_rechecked():
    core = make_core(defer=True)
    rec = enter(core)
    assert rec["action"] == "enter_pending" and not core.account.positions
    f = core.execute_pending(SYM, view(px=101.0, ts=T0 + TF), M)
    assert f.done and core.account.positions[SYM].entry_price > 101.0
    pos = core.account.positions[SYM]
    assert pos.qty * (pos.entry_price - pos.stop_price) <= 20.0 + 1e-6  # still within 2% after the gap

    core = make_core(defer=True)
    rec = enter(core)
    below_stop = rec["stop"] * 0.99
    assert core.execute_pending(SYM, view(px=below_stop, ts=T0 + TF), M) is None  # gapped through the stop
    assert not core.account.positions


def test_position_cap_counts_pending_orders():
    syms = ["A/USDT", "B/USDT", "C/USDT", "D/USDT"]
    setups = [Setup(s[0].lower(), s, s[0], Direction.LONG, "spot") for s in syms]
    core = make_core(defer=True, setups=setups, limits=RiskLimits(risk_per_trade=0.002))
    marks = {s: 100.0 for s in syms}
    r = core.begin_bar(T0, marks)
    acts = [core.decide(s, T0, SNAP, view(s), marks, r)["action"] for s in syms]
    assert acts[:3] == ["enter_pending"] * 3 and acts[3] == "hold"


def test_expensive_market_is_not_traded():
    broker = PaperBroker({}, CostModel(taker_fee=0.02))  # 4% round trip
    core = make_core(broker=broker)
    rec = enter(core)
    assert rec["action"] == "hold" and rec["reasons"][0].startswith("size:") and not core.account.positions


def test_short_setup_must_use_a_swap_market():
    with pytest.raises(ValueError):
        Setup("x", "X/USDT", "X", Direction.SHORT, "spot")
    core = make_core(StubReflex(good_decision(direction=Direction.SHORT)),
                     setups=[Setup("x-short", SYM, "AAA", Direction.SHORT, "swap")])
    snap = snap_for(CANDLES, bias=Direction.SHORT)
    r = core.begin_bar(T0, M)
    rec = core.decide(SYM, T0, snap, view(), M, r)
    pos = core.account.positions[SYM]
    assert rec["action"] == "enter" and pos.qty < 0 and pos.target_price < pos.entry_price < pos.stop_price


def test_spot_cannot_spend_more_than_cash_and_one_position_is_capped_at_equity():
    syms = ["A/USDT", "B/USDT"]
    setups = [Setup(s[0].lower(), s, s[0], Direction.LONG, "spot") for s in syms]
    core = make_core(setups=setups)  # default 2% risk with a tight stop wants > 1x equity
    marks = {s: 100.0 for s in syms}
    r = core.begin_bar(T0, marks)
    assert core.decide("A/USDT", T0, SNAP, view("A/USDT"), marks, r)["action"] == "enter"
    assert core.account.positions["A/USDT"].notional(100.0) <= 1000.0 * 1.001
    r = core.begin_bar(T0, marks)
    rec = core.decide("B/USDT", T0, SNAP, view("B/USDT"), marks, r)
    assert rec["action"] == "hold" and "B/USDT" not in core.account.positions


def test_risk_layer_rejects_an_oversized_position():
    from trader.risk.engine import Account, RiskEngine
    from trader.types import OrderIntent, Side
    a = Account(balance=1000.0, peak_equity=1000.0, day="d", day_start_equity=1000.0)
    big = OrderIntent("A", Side.BUY, 15.0, 100.0, 99.9, None, False, "s", "c")
    assert "position_too_large" in RiskEngine(RiskLimits()).check_order(big, a, {"A": 100.0}).reasons


def test_size_shrinks_in_drawdown():
    full = make_core(limits=RiskLimits(risk_per_trade=0.002))
    enter(full)
    hurt = make_core(limits=RiskLimits(risk_per_trade=0.002))
    hurt.account.peak_equity = 1000 / 0.925  # 7.5% below the peak
    rec = enter(hurt)
    assert rec["risk_scale"] == pytest.approx(0.5, abs=0.01)
    ratio = hurt.account.positions[SYM].qty / full.account.positions[SYM].qty
    assert ratio == pytest.approx(0.5, abs=0.02)
