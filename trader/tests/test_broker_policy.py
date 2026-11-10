import pytest

from tests.conftest import view
from trader.exec.broker import CostModel, Ledger, PaperBroker, reconcile
from trader.journal import load_state, save_state
from trader.policy import Policy, PolicyStore
from trader.risk.calibration import Calibrator
from trader.risk.engine import Account
from trader.types import OrderIntent, Position, Side


def buy(qty=1.0, cid="c1", sym="AAA/USDT", stop=95.0, tgt=110.0):
    return OrderIntent(sym, Side.BUY, qty, 100.0, stop, tgt, False, "s", cid)


def sell(qty=1.0, cid="c2", sym="AAA/USDT"):
    return OrderIntent(sym, Side.SELL, qty, 100.0, None, None, True, "s", cid, "stop")


def acct(b=1000.0):
    return Account(balance=b, peak_equity=b, day="d", day_start_equity=b)


def test_fill_pays_spread_slippage_and_fee():
    b = PaperBroker({}, CostModel(taker_fee=0.001, slippage_bps=2, impact_bps_full_depth=0))
    f = b.place(buy(), view(spread_bps=10))
    assert f.status == "filled" and f.price == pytest.approx(100.05 * 1.0002)
    assert f.fee == pytest.approx(f.price * 0.001)
    s = b.place(sell(), view(spread_bps=10))
    assert s.price == pytest.approx(99.95 * 0.9998) and s.price < f.price


def test_round_trip_at_flat_price_loses_exactly_costs():
    b = PaperBroker({}, CostModel(taker_fee=0.001, slippage_bps=2, impact_bps_full_depth=0))
    led = Ledger(acct())
    i1, i2 = buy(), sell()
    led.apply(b.place(i1, view(spread_bps=10)), i1)
    trade = led.apply(b.place(i2, view(spread_bps=10)), i2)
    assert not led.account.positions and trade["pnl"] < 0
    lost = 1000.0 - led.account.balance
    assert lost == pytest.approx(100 * CostModel(0.001, 2, 0).round_trip_frac(10), rel=0.01)


def test_impact_grows_with_order_size_and_thin_books_fill_partially():
    b = PaperBroker({}, CostModel(impact_bps_full_depth=20, max_depth_frac=0.25))
    small = b.place(buy(qty=1, cid="a"), view(depth=1_000_000))
    big = b.place(buy(qty=1000, cid="b"), view(depth=1_000_000))
    assert big.price > small.price
    part = b.place(buy(qty=100, cid="c"), view(depth=10_000))
    assert part.status == "partial" and part.qty == pytest.approx(2500 / view().ask)


def test_failures_rejections_and_idempotency():
    b = PaperBroker({}, CostModel())
    b.fail_next()
    f = b.place(buy(cid="x"), view())
    assert f.status == "failed" and not f.done and b.positions() == {}
    assert b.place(buy(cid="x"), view()) is f  # same id returns the same result, never a second order
    assert b.place(buy(qty=0.01, cid="y"), view()).reason == "below_min_notional"
    ok = b.place(buy(cid="z"), view())
    assert b.place(buy(cid="z"), view()) is ok and b.positions() == {"AAA/USDT": 1.0}
    flaky = PaperBroker({}, CostModel(), fail_prob=1.0)
    assert flaky.place(buy(cid="q"), view()).status == "failed"


def test_ledger_short_pnl_partial_close_and_funding():
    led = Ledger(acct())
    b = PaperBroker({}, CostModel(taker_fee=0, slippage_bps=0, impact_bps_full_depth=0))
    o = OrderIntent("X/USDT:USDT", Side.SELL, 2.0, 100.0, 105.0, 90.0, False, "s", "o")
    led.apply(b.place(o, view("X/USDT:USDT", spread_bps=0)), o)
    assert led.account.positions["X/USDT:USDT"].qty == -2.0
    assert led.apply_funding("X/USDT:USDT", 0.0001, 100.0) == pytest.approx(-0.02)  # shorts receive
    c = OrderIntent("X/USDT:USDT", Side.BUY, 1.0, 90.0, None, None, True, "s", "c", "target")
    t = led.apply(b.place(c, view("X/USDT:USDT", px=90.0, spread_bps=0)), c)
    assert t["pnl"] == pytest.approx(10.0) and led.account.positions["X/USDT:USDT"].qty == -1.0
    assert led.account.balance == pytest.approx(1010.02)
    assert led.account.equity({"X/USDT:USDT": 90.0}) == pytest.approx(1020.02)


def test_reconcile_detects_drift():
    mine = {"A": Position("A", 1.0, 100, 90, 120, 0, "s")}
    assert reconcile(mine, {"A": 1.0}) == []
    assert reconcile(mine, {"A": 0.5})
    assert reconcile(mine, {})
    assert reconcile({}, {"B": -2.0})


def test_state_round_trips_atomically(tmp_path):
    a = acct()
    a.positions["A"] = Position("A", 1.5, 100, 90, 120, 7, "s")
    a.kill_latched, a.kill_reason = True, "test"
    p = tmp_path / "state.json"
    save_state(p, a, {"global_pause": True})
    b, extra = load_state(p)
    assert b == a and extra == {"global_pause": True}
    assert not p.with_suffix(".tmp").exists() and load_state(tmp_path / "none.json") is None


def test_policy_validation_and_round_trip():
    with pytest.raises(ValueError):
        Policy(version="x", kelly_mult=0.5)
    with pytest.raises(ValueError):
        Policy(version="x", min_setup_quality=4)
    p = Policy(version="v1", calibrator=Calibrator(knots=((0.6, 0.4), (0.9, 0.6))))
    assert Policy.from_dict(p.to_dict()) == p


def test_policy_promotion_needs_approval_and_paper_first(tmp_path):
    st = PolicyStore(tmp_path)
    st.save(Policy(version="v1"))
    st.save(Policy(version="v2", parent="v1"), candidate=True)
    with pytest.raises(FileExistsError):
        st.save(Policy(version="v1"))
    with pytest.raises(PermissionError):
        st.promote("v1", "paper", approved_by=" ")
    st.promote("v1", "paper", approved_by="owner")
    assert st.active("paper").version == "v1"
    with pytest.raises(PermissionError):
        st.promote("v1", "live", approved_by="owner")  # no explicit live approval
    with pytest.raises(PermissionError):
        st.promote("v2", "live", approved_by="owner", live_approved=True)  # not in paper yet
    st.promote("v2", "paper", approved_by="owner")
    assert st.active_version("paper") == "v2"
    assert st.rollback("paper", approved_by="owner") == "v1" and st.active_version("paper") == "v1"
    with pytest.raises(FileNotFoundError):
        st.active("live")
    with pytest.raises(FileNotFoundError):
        st.promote("nope", "paper", approved_by="owner")
    assert len((tmp_path / "history.jsonl").read_text().splitlines()) == 3
