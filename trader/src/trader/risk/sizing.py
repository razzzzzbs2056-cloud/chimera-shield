"""Position sizing: fractional Kelly on a calibrated probability, capped by hard limits.

Kelly for a bet that wins b units per unit risked with probability p: f* = p - (1 - p) / b.
We risk at most kelly_mult * f* of equity (kelly_mult is clamped to 0.25) and never more
than the per-trade risk limit. A non-positive Kelly fraction means no trade.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

MAX_KELLY_MULT = 0.25


def kelly_fraction(p: float, b: float) -> float:
    if not (0.0 <= p <= 1.0) or b <= 0 or not math.isfinite(b):
        return 0.0
    return p - (1.0 - p) / b


@dataclass(frozen=True)
class SizeResult:
    qty: float
    risk_usd: float
    risk_frac: float
    kelly_full: float
    net_rr: float
    reason: str  # "ok" or why qty is zero


def size_position(
    *,
    equity: float,
    price: float,
    stop: float,
    p_win: float,
    rr: float,
    risk_per_trade: float,
    kelly_mult: float,
    cost_frac: float,  # round-trip fees + slippage as a fraction of notional
    gross_exposure: float,
    max_leverage: float,
    depth_usd: float | None = None,
    max_depth_frac: float = 0.05,
    lot: float = 0.0,
    min_notional: float = 5.0,
) -> SizeResult:
    def none(reason: str, k: float = 0.0, b: float = 0.0) -> SizeResult:
        return SizeResult(0.0, 0.0, 0.0, k, b, reason)

    if not all(math.isfinite(x) for x in (equity, price, stop, p_win, rr)) or equity <= 0 or price <= 0:
        return none("bad_inputs")
    stop_dist = abs(price - stop)
    if stop_dist <= 0:
        return none("zero_stop_distance")
    cost_per_unit = price * max(0.0, cost_frac)
    loss_per_unit = stop_dist + cost_per_unit
    gain_per_unit = rr * stop_dist - cost_per_unit
    if gain_per_unit <= 0:
        return none("costs_exceed_reward")
    b = gain_per_unit / loss_per_unit
    k = kelly_fraction(p_win, b)
    if k <= 0:
        return none("no_edge", k, b)
    risk_frac = min(min(kelly_mult, MAX_KELLY_MULT) * k, risk_per_trade)
    qty = risk_frac * equity / loss_per_unit
    reason = "ok"
    headroom = max_leverage * equity - gross_exposure
    if headroom <= 0:
        return none("no_leverage_headroom", k, b)
    if qty * price > headroom:
        qty, reason = headroom / price, "ok_capped_by_leverage"
    if depth_usd is not None and qty * price > depth_usd * max_depth_frac:
        qty, reason = depth_usd * max_depth_frac / price, "ok_capped_by_liquidity"
    if lot > 0:
        qty = math.floor(qty / lot + 1e-9) * lot
    if qty <= 0 or qty * price < min_notional:
        return none("below_min_notional", k, b)
    risk_usd = qty * loss_per_unit
    return SizeResult(qty, risk_usd, risk_usd / equity, k, b, reason)
