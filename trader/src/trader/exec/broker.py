"""Order execution contracts, the ledger, and the paper broker.

The Ledger is the system's own record of balance and positions; it is updated only from
fills. PaperBroker plays the exchange: it prices fills with fees, spread, slippage and
depth impact, can reject, fail or partially fill, and keeps its own position book so
reconciliation against the ledger is a real check.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Protocol

from trader.risk.engine import Account
from trader.types import OrderIntent, Position, Side


@dataclass(frozen=True)
class MarketView:
    symbol: str
    bid: float
    ask: float
    depth_usd: float  # resting size per side near the touch
    ts: int

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2


@dataclass(frozen=True)
class Fill:
    client_id: str
    symbol: str
    side: Side
    qty: float  # filled quantity (0 when rejected/failed)
    price: float
    fee: float
    ts: int
    status: str  # "filled" | "partial" | "rejected" | "failed"
    reason: str = ""

    @property
    def done(self) -> bool:
        return self.status in ("filled", "partial") and self.qty > 0


class Broker(Protocol):
    def place(self, intent: OrderIntent, view: MarketView) -> Fill: ...

    def positions(self) -> dict[str, float]: ...


@dataclass(frozen=True)
class CostModel:
    taker_fee: float = 0.001  # fraction of notional per side
    slippage_bps: float = 2.0  # fixed adverse slippage per side, on top of the spread
    impact_bps_full_depth: float = 20.0  # extra slippage when an order equals the visible depth
    max_depth_frac: float = 0.25  # an order larger than this share of depth is partially filled
    min_notional: float = 5.0

    def round_trip_frac(self, spread_bps: float) -> float:
        return 2 * (self.taker_fee + self.slippage_bps / 1e4 + spread_bps / 2e4)


class PaperBroker:
    def __init__(self, costs: dict[str, CostModel], default: CostModel | None = None,
                 fail_prob: float = 0.0, seed: int = 7):
        self.costs = costs
        self.default = default or CostModel()
        self.fail_prob = fail_prob
        self._rng = random.Random(seed)
        self._fail_next = 0
        self._seen: dict[str, Fill] = {}
        self._pos: dict[str, float] = {}

    def cost(self, symbol: str) -> CostModel:
        return self.costs.get(symbol, self.default)

    def fail_next(self, n: int = 1) -> None:
        self._fail_next += n

    def positions(self) -> dict[str, float]:
        return {s: q for s, q in self._pos.items() if abs(q) > 1e-12}

    def place(self, intent: OrderIntent, view: MarketView) -> Fill:
        if intent.client_id in self._seen:  # idempotent: a retried id never double-fills
            return self._seen[intent.client_id]
        fill = self._simulate(intent, view)
        self._seen[intent.client_id] = fill
        if fill.done:
            signed = fill.qty if fill.side is Side.BUY else -fill.qty
            self._pos[fill.symbol] = self._pos.get(fill.symbol, 0.0) + signed
        return fill

    def _simulate(self, intent: OrderIntent, view: MarketView) -> Fill:
        def no(status: str, reason: str) -> Fill:
            return Fill(intent.client_id, intent.symbol, intent.side, 0.0, 0.0, 0.0, view.ts, status, reason)

        c = self.cost(intent.symbol)
        if self._fail_next > 0:
            self._fail_next -= 1
            return no("failed", "injected_failure")
        if self.fail_prob > 0 and self._rng.random() < self.fail_prob:
            return no("failed", "simulated_exchange_error")
        if not (view.bid > 0 and view.ask >= view.bid and math.isfinite(view.ask)):
            return no("rejected", "bad_market")
        if intent.qty <= 0 or not math.isfinite(intent.qty):
            return no("rejected", "bad_qty")
        touch = view.ask if intent.side is Side.BUY else view.bid
        notional = intent.qty * touch
        if notional < c.min_notional and not intent.reduce_only:
            return no("rejected", "below_min_notional")
        qty, status = intent.qty, "filled"
        if view.depth_usd > 0 and notional > view.depth_usd * c.max_depth_frac and not intent.reduce_only:
            qty, status = view.depth_usd * c.max_depth_frac / touch, "partial"
        depth_share = (qty * touch / view.depth_usd) if view.depth_usd > 0 else 1.0
        slip = (c.slippage_bps + c.impact_bps_full_depth * min(1.0, depth_share)) / 1e4
        price = touch * (1 + slip) if intent.side is Side.BUY else touch * (1 - slip)
        return Fill(intent.client_id, intent.symbol, intent.side, qty, price, qty * price * c.taker_fee,
                    view.ts, status)


class Ledger:
    """Applies fills to the Account. The only code that changes balance or positions."""

    def __init__(self, account: Account):
        self.account = account
        self.realized: list[dict] = []

    def apply(self, fill: Fill, intent: OrderIntent) -> dict | None:
        """Returns a closed-trade record when the fill reduces a position, else None."""
        if not fill.done:
            return None
        a = self.account
        signed = fill.qty if fill.side is Side.BUY else -fill.qty
        pos = a.positions.get(fill.symbol)
        a.balance -= fill.fee
        if pos is None:
            a.positions[fill.symbol] = Position(
                symbol=fill.symbol, qty=signed, entry_price=fill.price,
                stop_price=intent.stop_price or 0.0, target_price=intent.target_price or 0.0,
                opened_ts=fill.ts, setup_id=intent.setup_id,
            )
            return None
        if (pos.qty > 0) == (signed > 0):
            raise RuntimeError("ledger: adding to a position is not supported")
        closed = min(abs(signed), abs(pos.qty))
        pnl = closed * (fill.price - pos.entry_price) * (1 if pos.qty > 0 else -1)
        a.balance += pnl
        remaining = pos.qty + (closed if pos.qty < 0 else -closed)
        if abs(remaining) <= 1e-12:
            del a.positions[fill.symbol]
        else:
            a.positions[fill.symbol] = replace(pos, qty=remaining)
        rec = {"symbol": fill.symbol, "setup_id": pos.setup_id, "side": pos.side.value, "qty": closed,
               "entry": pos.entry_price, "exit": fill.price, "pnl": pnl, "exit_fee": fill.fee,
               "opened_ts": pos.opened_ts, "closed_ts": fill.ts, "reason": intent.reason}
        self.realized.append(rec)
        return rec

    def apply_funding(self, symbol: str, rate: float, mark: float) -> float:
        """Perp funding: longs pay a positive rate, shorts receive it. Returns the payment."""
        pos = self.account.positions.get(symbol)
        if pos is None or not math.isfinite(rate):
            return 0.0
        pay = pos.qty * mark * rate
        self.account.balance -= pay
        return pay


def reconcile(ledger_positions: dict[str, Position], broker_positions: dict[str, float],
              tol: float = 1e-6) -> list[str]:
    """Compare our ledger with the broker/exchange. Any mismatch must halt new orders."""
    problems = []
    for sym in sorted(set(ledger_positions) | set(broker_positions)):
        mine = ledger_positions[sym].qty if sym in ledger_positions else 0.0
        theirs = broker_positions.get(sym, 0.0)
        if abs(mine - theirs) > tol * max(1.0, abs(mine), abs(theirs)):
            problems.append(f"{sym}: ledger {mine:.8g} vs broker {theirs:.8g}")
    return problems
