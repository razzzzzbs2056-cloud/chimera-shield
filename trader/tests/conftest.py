import math
import random

import pytest

from trader.alerts import Alerts
from trader.core import CoreConfig, Setup, TraderCore
from trader.exec.broker import CostModel, MarketView, PaperBroker
from trader.journal import Journal
from trader.policy import Policy
from trader.risk.engine import Account, RiskEngine, RiskLimits
from trader.state.engine import AccountView, EngineConfig, build_snapshot
from trader.types import Candle, Direction, ReflexDecision, Regime, RiskState

TF = 3600
T0 = 1_750_000_000 - (1_750_000_000 % TF)


def make_candles(n=260, start=100.0, drift=0.0, vol=0.004, seed=1, t0=T0):
    rng = random.Random(seed)
    out, px = [], start
    for i in range(n):
        o = px
        c = o * math.exp(drift + rng.gauss(0, vol))
        h = max(o, c) * (1 + abs(rng.gauss(0, vol / 2)))
        lo = min(o, c) * (1 - abs(rng.gauss(0, vol / 2)))
        out.append(Candle(t0 + i * TF, t0 + (i + 1) * TF, o, h, lo, c, 1000 + rng.random() * 500))
        px = c
    return out


SAFE_VIEW = AccountView(0.0, 0.0, 0.0, 0.0, 0, RiskState.SAFE)


@pytest.fixture
def candles():
    return make_candles()


@pytest.fixture
def cfg():
    return EngineConfig(require_book=False)


def snap_for(candles, bias=Direction.LONG, cfg=None, account=SAFE_VIEW, **kw):
    cfg = cfg or EngineConfig(require_book=False)
    return build_snapshot(asof=candles[-1].ts_close, symbol="AAA/USDT", cfg=cfg, bias=bias, candles=candles,
                          btc_candles=kw.pop("btc", candles), book=kw.pop("book", None),
                          funding_pct=kw.pop("funding", None), invalidation_price=kw.pop("inval", None),
                          account=account, **kw)


class StubReflex:
    """Returns a fixed decision; can sleep-by-clock, raise, or return garbage."""

    name = "stub"
    uses_model = False

    def __init__(self, decision=None, raises=None):
        self.decision = decision
        self.raises = raises
        self.calls = 0

    def decide(self, snap, timeout_s):
        self.calls += 1
        if self.raises:
            raise self.raises
        return self.decision


def good_decision(**kw):
    base = dict(regime=Regime.TRENDING, direction=Direction.LONG, direction_confidence=0.93,
                toxic_flow=False, setup_quality=3, risk_state=RiskState.SAFE)
    base.update(kw)
    return ReflexDecision(**base)


def view(symbol="AAA/USDT", px=100.0, spread_bps=2.0, depth=1_000_000.0, ts=T0):
    half = px * spread_bps / 2e4
    return MarketView(symbol, px - half, px + half, depth, ts)


def make_core(reflex=None, balance=1000.0, limits=None, policy=None, defer=False, setups=None, broker=None):
    limits = limits or RiskLimits()
    account = Account(balance=balance, peak_equity=balance, day="1970-01-01", day_start_equity=balance)
    setups = setups or [Setup("aaa-long", "AAA/USDT", "AAA", Direction.LONG, "spot")]
    broker = broker or PaperBroker({}, CostModel())
    core = TraderCore(setups=setups, policy=policy or Policy(version="t1"),
                      reflex=reflex or StubReflex(good_decision()), broker=broker, risk=RiskEngine(limits),
                      account=account, journal=Journal(None), alerts=Alerts(min_gap_s=0),
                      cfg=CoreConfig(tf_seconds=TF, defer_entries=defer), cost_of=broker.cost)
    return core
