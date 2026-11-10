"""Shared typed contracts. The REFLEX returns a ReflexDecision and nothing else."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Regime(StrEnum):
    TRENDING = "trending"
    MEAN_REVERTING = "mean_reverting"
    HIGH_VOL = "high_vol"
    CRISIS = "crisis"


class Direction(StrEnum):
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"


class RiskState(StrEnum):
    SAFE = "safe"
    NEAR_LIMIT = "near_limit"
    REDUCE = "reduce"


_RISK_ORDER = {RiskState.SAFE: 0, RiskState.NEAR_LIMIT: 1, RiskState.REDUCE: 2}


def worst_risk(a: RiskState, b: RiskState) -> RiskState:
    return a if _RISK_ORDER[a] >= _RISK_ORDER[b] else b


class ReflexDecision(BaseModel):
    """The only thing a REFLEX may return. It judges; it never sizes or orders."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    regime: Regime
    direction: Direction
    direction_confidence: float = Field(ge=0.0, le=1.0)
    toxic_flow: bool | None
    setup_quality: int = Field(ge=0, le=3)
    risk_state: RiskState


@dataclass(frozen=True)
class Candle:
    ts_open: int  # epoch seconds, start of the bar
    ts_close: int  # epoch seconds, end of the bar; the bar is usable only when ts_close <= asof
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class Book:
    ts: int  # epoch seconds the book was observed
    bids: tuple[tuple[float, float], ...]  # (price, qty), best first
    asks: tuple[tuple[float, float], ...]


class Side(StrEnum):
    BUY = "buy"
    SELL = "sell"


@dataclass(frozen=True)
class Position:
    symbol: str
    qty: float  # signed: positive long, negative short
    entry_price: float
    stop_price: float
    target_price: float
    opened_ts: int
    setup_id: str

    @property
    def side(self) -> Direction:
        return Direction.LONG if self.qty > 0 else Direction.SHORT

    def notional(self, mark: float) -> float:
        return abs(self.qty) * mark

    def unrealized(self, mark: float) -> float:
        return self.qty * (mark - self.entry_price)


@dataclass(frozen=True)
class OrderIntent:
    symbol: str
    side: Side
    qty: float
    ref_price: float  # price the decision was made at
    stop_price: float | None
    target_price: float | None
    reduce_only: bool
    setup_id: str
    client_id: str
    reason: str = ""
