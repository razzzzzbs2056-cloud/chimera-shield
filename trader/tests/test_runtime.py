import json

import pytest

from tests.conftest import StubReflex, good_decision, make_candles
from trader.alerts import Alerts
from trader.config import LIVE_APPROVAL_PHRASE, Config, live_trading_allowed, load_config
from trader.exec.broker import MarketView, PaperBroker
from trader.exec.ccxt_broker import CcxtBroker
from trader.policy import Policy
from trader.runtime.loop import Runner, heartbeat_ok
from trader.types import Book, OrderIntent, Side

TF = 3600
CFG = dict(
    costs={"spot": {"taker_fee": 0.001}, "swap": {"taker_fee": 0.0005}},
    setups=[dict(id="aaa-long", base="AAA", symbol="AAA/USDT", market="spot", bias="long")],
    context_symbol="BTC/USDT",
)


class FakeData:
    def __init__(self, candles, now):
        self.c, self.now, self.fail, self.book_age = candles, now, set(), 0

    def exchange_time(self):
        if "time" in self.fail:
            raise ConnectionError("down")
        return self.now

    def candles(self, symbol, limit=300):
        if symbol in self.fail:
            raise ConnectionError("down")
        return self.c

    def book(self, symbol, depth=20):
        px = self.c[-1].close
        return Book(int(self.now) - self.book_age, ((px * 0.9999, 5000.0),), ((px * 1.0001, 5000.0),))

    def funding_pct(self, symbol):
        return None

    def contract_size(self, symbol):
        return 1.0


def make_runner(tmp_path, reflex=None, now_offset=5.0, cfg=None):
    candles = make_candles(n=300)
    now = candles[-1].ts_close + now_offset
    cfg = Config(**{**CFG, "data_dir": str(tmp_path), **(cfg or {})})
    data = FakeData(candles, now)
    broker = PaperBroker({}, None)
    broker.cost = cfg.cost_of
    r = Runner(cfg, Policy(version="t1"), data, broker, reflex or StubReflex(good_decision()),
               Alerts(min_gap_s=0), tmp_path, clock=lambda: data.now)
    return r, data


def test_one_pass_trades_saves_state_and_heartbeat(tmp_path):
    r, data = make_runner(tmp_path)
    recs = r.run_once()
    assert recs[0]["action"] == "enter" and "AAA/USDT" in r.core.account.positions
    assert r.run_once() == []  # the same candle is never processed twice
    state = json.loads((tmp_path / "state.json").read_text())
    assert state["last_asof"] == data.c[-1].ts_close and state["account"]["positions"]
    assert heartbeat_ok(tmp_path, 60, now=data.now)[0]
    assert not heartbeat_ok(tmp_path, 60, now=data.now + 600)[0]
    assert not heartbeat_ok(tmp_path / "nope", 60)[0]


def test_restart_restores_positions_pauses_and_reconciles(tmp_path):
    r, _ = make_runner(tmp_path)
    r.run_once()
    r.core.global_pause = True
    r.save()
    r2, _ = make_runner(tmp_path)
    assert r2.core.account.positions.keys() == r.core.account.positions.keys()
    assert r2.core.global_pause and r2.last_asof == r.last_asof
    r2.core.begin_bar(r2.last_asof, r2.marks)
    assert not r2.core.halt_reason  # the reseeded paper broker agrees with the ledger


def test_exchange_errors_and_stale_book_block_orders(tmp_path):
    r, data = make_runner(tmp_path)
    data.fail.add("AAA/USDT")
    assert r.run_once() == [] and not r.core.account.positions  # no data at all: nothing happens
    r, data = make_runner(tmp_path / "b")
    data.fail.add("BTC/USDT")
    rec = r.run_once()[0]
    assert rec["status"] == "fault" and rec["reasons"] == ["exchange_error"] and not r.core.account.positions
    r, data = make_runner(tmp_path / "c")
    data.book_age = 120
    rec = r.run_once()[0]
    assert rec["status"] == "fault" and rec["reasons"] == ["stale_data"]
    r, data = make_runner(tmp_path / "d")
    data.fail.add("time")
    assert r.run_once() == []


def test_clock_skew_and_late_start_block_entries(tmp_path):
    r, data = make_runner(tmp_path)
    r.clock = lambda: data.now + 30
    assert r.run_once()[0]["reasons"] == ["clock_skew"]
    r, data = make_runner(tmp_path / "b", now_offset=900.0)
    assert r.run_once()[0]["reasons"] == ["late_start"]


def test_denylisted_coin_cannot_be_configured():
    bad = {**CFG, "denylist": {"memecoins": ["AAA"]}}
    with pytest.raises(ValueError, match="off-limits"):
        Config(**bad)
    with pytest.raises(ValueError):
        Config(**{**CFG, "limits": {"max_leverage": 20}})
    with pytest.raises(ValueError):
        Config(**{**CFG, "setups": [dict(id="x", base="AAA", symbol="BBB/USDT", market="spot", bias="long")]})
    with pytest.raises(ValueError):
        Config(**{**CFG, "setups": [dict(id="x", base="AAA", symbol="AAA/USDT", market="spot", bias="short")]})


def test_shipped_config_is_valid_and_matches_the_brief():
    cfg = load_config("config/default.yaml")
    assert cfg.mode == "paper" and cfg.paper_balance == 1000 and cfg.exchange == "okx"
    L = cfg.limits
    assert (L.risk_per_trade, L.max_daily_loss, L.max_open_positions, L.max_leverage, L.kill_drawdown) == \
        (0.02, 0.05, 3, 2.0, 0.15)
    bases = {s.base for s in cfg.setups}
    denied = {b for v in cfg.denylist.values() for b in v}
    assert not bases & denied and {"DOGE", "XMR", "ZEC"} <= denied


def test_live_needs_mode_phrase_and_keys():
    paper = Config(**CFG)
    env = {"TRADER_LIVE_APPROVED": LIVE_APPROVAL_PHRASE, "EXCHANGE_API_KEY": "k", "EXCHANGE_API_SECRET": "s",
           "EXCHANGE_API_PASSPHRASE": "p"}
    assert not live_trading_allowed(paper, env)[0]
    live = Config(**{**CFG, "mode": "live"})
    assert live_trading_allowed(live, env)[0]
    assert not live_trading_allowed(live, {**env, "TRADER_LIVE_APPROVED": "yes"})[0]
    assert not live_trading_allowed(live, {k: v for k, v in env.items() if k != "EXCHANGE_API_SECRET"})[0]
    with pytest.raises(PermissionError):
        CcxtBroker(object(), sandbox=False, live_allowed=False)


class FakeExchange:
    def __init__(self, fail=False):
        self.orders, self.fail = [], fail

    def market(self, symbol):
        return {"contract": ":" in symbol, "contractSize": 100.0 if ":" in symbol else None}

    def amount_to_precision(self, symbol, qty):
        return f"{qty:.4f}"

    def price_to_precision(self, symbol, px):
        return f"{px:.4f}"

    def create_order(self, symbol, type_, side, amount, price, params):
        if self.fail:
            raise RuntimeError("secret-looking exchange message")
        self.orders.append((symbol, type_, side, amount, params))
        return {"id": "1", "status": "closed", "filled": amount, "average": 1.1, "fee": {"cost": 0.01}}


def test_ccxt_broker_order_shape_idempotency_and_failure():
    ex = FakeExchange()
    b = CcxtBroker(ex, sandbox=True, live_allowed=False)
    v = MarketView("XRP/USDT:USDT", 1.09, 1.1, 1e6, 0)
    short = OrderIntent("XRP/USDT:USDT", Side.SELL, 500.0, 1.1, 1.2, 0.9, False, "xrp-short", "xrp-short-1-e")
    f = b.place(short, v)
    sym, typ, side, amount, params = ex.orders[0]
    assert (typ, side, amount) == ("market", "sell", 5.0)  # 500 XRP = 5 contracts of 100
    assert params["clOrdId"] == "xrpshort1e" and params["tdMode"] == "cross" and "reduceOnly" not in params
    assert params["stopLoss"]["triggerPrice"] == 1.2  # exchange-side stop travels with the entry
    assert f.status == "filled" and f.qty == 500.0
    assert b.place(short, v) is f and len(ex.orders) == 1
    close = OrderIntent("XRP/USDT:USDT", Side.BUY, 500.0, 1.1, None, None, True, "xrp-short", "x2")
    b.place(close, v)
    assert ex.orders[1][4]["reduceOnly"] is True and "stopLoss" not in ex.orders[1][4]
    spot = OrderIntent("AAVE/USDT", Side.BUY, 2.0, 100.0, 95.0, 110.0, False, "a", "a1")
    b.place(spot, MarketView("AAVE/USDT", 99.9, 100.1, 1e5, 0))
    assert ex.orders[2][4]["tdMode"] == "cash" and ex.orders[2][4]["tgtCcy"] == "base_ccy"
    bad = CcxtBroker(FakeExchange(fail=True), sandbox=True, live_allowed=False).place(short, v)
    assert bad.status == "failed" and bad.reason == "RuntimeError"  # only the error type, never its text


def test_paper_funding_is_charged_on_eight_hour_boundaries(tmp_path):
    from trader.types import Position
    cfg = {"setups": [dict(id="x-short", base="AAA", symbol="AAA/USDT:USDT", market="swap", bias="short")]}
    r, data = make_runner(tmp_path, reflex=StubReflex(good_decision(direction="neutral")), cfg=cfg)
    data.funding_pct = lambda symbol: 0.01  # 0.01% per interval
    px = data.c[-1].close
    r.core.account.positions["AAA/USDT:USDT"] = Position("AAA/USDT:USDT", -10.0, px, px * 2, px / 2,
                                                         data.c[-1].ts_open, "x-short")
    r.core.broker._pos = {"AAA/USDT:USDT": -10.0}
    asof = data.c[-1].ts_close
    r.run_once()
    events = [e for e in r.core.journal.read("events") if e["type"] == "funding"]
    if asof % 28800 == 0:
        assert events and r.core.account.balance == pytest.approx(1000 + 10 * px * 0.0001, rel=1e-3)
    else:
        assert not events and r.core.account.balance == 1000.0
    r._apply_funding(28800 * 60000, {"AAA/USDT:USDT": (data.c, None, 0.01)}, {"AAA/USDT:USDT": px})
    assert [e for e in r.core.journal.read("events") if e["type"] == "funding"]  # a short receives positive funding
    assert r.core.account.balance > 1000.0
