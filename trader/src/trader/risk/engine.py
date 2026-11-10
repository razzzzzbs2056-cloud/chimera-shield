"""Hard risk layer. Pure code, no model input can relax it.

check_order() is called before EVERY order. Reduce-only orders that shrink an existing
position are always allowed (so the system can always get flatter); everything else must
pass every limit. The kill switch latches: once tripped it stays tripped until a human
clears it with the CLI.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from trader.types import OrderIntent, Position, RiskState, Side


@dataclass(frozen=True)
class RiskLimits:
    risk_per_trade: float = 0.02
    max_daily_loss: float = 0.05
    max_open_positions: int = 3
    max_leverage: float = 2.0
    kill_drawdown: float = 0.15
    max_position_frac: float = 1.0  # one position's notional may not exceed this share of equity
    near_fraction: float = 0.7  # "near_limit" starts at this share of the daily-loss or leverage limit
    min_risk_scale: float = 0.25  # floor for drawdown-based size reduction

    def __post_init__(self) -> None:
        if not (0 < self.risk_per_trade <= 0.05):
            raise ValueError("risk_per_trade must be in (0, 0.05]")
        if not (0 < self.max_daily_loss <= 0.2):
            raise ValueError("max_daily_loss must be in (0, 0.2]")
        if not (1 <= self.max_open_positions <= 10):
            raise ValueError("max_open_positions must be in [1, 10]")
        if not (0 < self.max_leverage <= 3.0):
            raise ValueError("max_leverage must be in (0, 3]")
        if not (0 < self.max_position_frac <= self.max_leverage):
            raise ValueError("max_position_frac must be in (0, max_leverage]")
        if not (0 < self.kill_drawdown <= 0.5):
            raise ValueError("kill_drawdown must be in (0, 0.5]")


@dataclass
class Account:
    """Mark-to-market account state. equity = balance + unrealised PnL."""

    balance: float
    peak_equity: float
    day: str  # UTC date of day_start_equity
    day_start_equity: float
    positions: dict[str, Position] = field(default_factory=dict)
    kill_latched: bool = False
    kill_reason: str = ""

    def equity(self, marks: dict[str, float]) -> float:
        return self.balance + sum(p.unrealized(marks[s]) for s, p in self.positions.items())

    def gross_exposure(self, marks: dict[str, float]) -> float:
        return sum(p.notional(marks[s]) for s, p in self.positions.items())


@dataclass(frozen=True)
class Verdict:
    ok: bool
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class RiskReading:
    state: RiskState
    equity: float
    drawdown: float  # fraction of peak, >= 0
    daily_loss: float  # fraction of day-start equity, >= 0 when losing
    leverage: float
    open_positions: int
    kill: bool
    reasons: tuple[str, ...]


class RiskEngine:
    def __init__(self, limits: RiskLimits):
        self.limits = limits

    def roll_day(self, acct: Account, utc_day: str, marks: dict[str, float]) -> None:
        if utc_day != acct.day:
            acct.day = utc_day
            acct.day_start_equity = acct.equity(marks)

    def read(self, acct: Account, marks: dict[str, float]) -> RiskReading:
        """Measure the account, update the peak, and latch the kill switch if breached."""
        L = self.limits
        eq = acct.equity(marks)
        if not math.isfinite(eq):
            acct.kill_latched, acct.kill_reason = True, "equity is not finite"
            return RiskReading(RiskState.REDUCE, eq, 1.0, 1.0, 0.0, len(acct.positions), True,
                               ("equity_not_finite",))
        acct.peak_equity = max(acct.peak_equity, eq)
        dd = max(0.0, 1 - eq / acct.peak_equity) if acct.peak_equity > 0 else 1.0
        dl = max(0.0, 1 - eq / acct.day_start_equity) if acct.day_start_equity > 0 else 1.0
        lev = acct.gross_exposure(marks) / eq if eq > 0 else math.inf
        reasons: list[str] = []
        if dd >= L.kill_drawdown or eq <= 0:
            if not acct.kill_latched:
                acct.kill_latched = True
                acct.kill_reason = f"drawdown {dd:.1%} >= kill {L.kill_drawdown:.0%}"
        if acct.kill_latched:
            reasons.append("kill_switch")
        if dl >= L.max_daily_loss:
            reasons.append("daily_loss_limit")
        if lev > L.max_leverage + 1e-9:
            reasons.append("leverage_limit")
        if reasons:
            state = RiskState.REDUCE
        else:
            # Drawdown is deliberately NOT here: it only recovers by trading, so gating on it
            # would deadlock the system below the kill level. Drawdown shrinks size instead
            # (risk_scale) and the kill switch is the hard stop.
            near = (
                dl >= L.near_fraction * L.max_daily_loss
                or lev >= L.near_fraction * L.max_leverage
                or len(acct.positions) >= L.max_open_positions
            )
            state = RiskState.NEAR_LIMIT if near else RiskState.SAFE
        return RiskReading(state, eq, dd, dl, lev, len(acct.positions), acct.kill_latched, tuple(reasons))

    def risk_scale(self, drawdown: float) -> float:
        """Share of the per-trade risk budget allowed at this drawdown: 1.0 at the peak,
        falling linearly to min_risk_scale at the kill level."""
        L = self.limits
        return max(L.min_risk_scale, 1.0 - max(0.0, drawdown) / L.kill_drawdown)

    def check_order(self, intent: OrderIntent, acct: Account, marks: dict[str, float],
                    est_cost: float = 0.0) -> Verdict:
        L = self.limits
        if not (math.isfinite(intent.qty) and intent.qty > 0):
            return Verdict(False, ("bad_qty",))
        if not (math.isfinite(intent.ref_price) and intent.ref_price > 0):
            return Verdict(False, ("bad_price",))
        if intent.symbol not in marks or not math.isfinite(marks[intent.symbol]):
            return Verdict(False, ("no_mark_price",))
        pos = acct.positions.get(intent.symbol)
        signed = intent.qty if intent.side is Side.BUY else -intent.qty

        if intent.reduce_only:
            if pos is None:
                return Verdict(False, ("reduce_only_without_position",))
            if (pos.qty > 0) == (signed > 0) or abs(signed) > abs(pos.qty) * (1 + 1e-9):
                return Verdict(False, ("reduce_only_would_increase_or_flip",))
            return Verdict(True)

        reading = self.read(acct, marks)
        reasons: list[str] = list(reading.reasons)
        if pos is not None:
            reasons.append("already_in_position")
        elif len(acct.positions) >= L.max_open_positions:
            reasons.append("max_open_positions")
        if intent.stop_price is None or not math.isfinite(intent.stop_price) or intent.stop_price <= 0:
            reasons.append("stop_required")
        else:
            wrong_side = (signed > 0 and intent.stop_price >= intent.ref_price) or (
                signed < 0 and intent.stop_price <= intent.ref_price
            )
            if wrong_side:
                reasons.append("stop_on_wrong_side")
            else:
                risk = intent.qty * abs(intent.ref_price - intent.stop_price) + max(0.0, est_cost)
                if risk > L.risk_per_trade * reading.equity * (1 + 1e-6):
                    reasons.append("trade_risk_exceeds_limit")
        if reading.equity > 0 and intent.qty * intent.ref_price > L.max_position_frac * reading.equity * (1 + 1e-6):
            reasons.append("position_too_large")
        new_gross = acct.gross_exposure(marks) + intent.qty * intent.ref_price
        if reading.equity <= 0 or new_gross / reading.equity > L.max_leverage + 1e-9:
            reasons.append("leverage_limit")
        return Verdict(not reasons, tuple(dict.fromkeys(reasons)))
