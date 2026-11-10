"""Configuration: one YAML file, validated. Secrets never live here; they come from the
environment (see .env.example) and are never logged."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from trader.core import Setup
from trader.exec.broker import CostModel
from trader.risk.engine import RiskLimits
from trader.types import Direction

LIVE_APPROVAL_PHRASE = "I-APPROVE-LIVE-TRADING"


class _M(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LimitsCfg(_M):
    risk_per_trade: float = 0.02
    max_daily_loss: float = 0.05
    max_open_positions: int = 3
    max_leverage: float = 2.0
    kill_drawdown: float = 0.15
    max_position_frac: float = 1.0

    def build(self) -> RiskLimits:
        return RiskLimits(**self.model_dump())


class CostCfg(_M):
    taker_fee: float
    slippage_bps: float = 2.0
    impact_bps_full_depth: float = 20.0
    max_depth_frac: float = 0.25
    min_notional: float = 5.0

    def build(self) -> CostModel:
        return CostModel(**self.model_dump())


class ReflexCfg(_M):
    kind: Literal["rule", "haiku"] = "rule"
    latency_budget_s: float = Field(default=5.0, gt=0, le=60)


class SetupCfg(_M):
    id: str
    base: str
    symbol: str
    market: Literal["spot", "swap"]
    bias: Direction
    enabled: bool = True
    invalidation_price: float | None = None
    lot: float = 0.0
    bt_spread_bps: float = 3.0  # backtest assumption: today's measured spread applied to history
    bt_depth_usd: float = 100_000.0
    research: str = ""

    def build(self) -> Setup:
        return Setup(self.id, self.symbol, self.base, self.bias, self.market, self.invalidation_price,
                     self.lot, self.enabled)


class Config(_M):
    mode: Literal["paper", "testnet", "live"] = "paper"
    exchange: str = "okx"
    timeframe: Literal["15m", "1h", "4h", "1d"] = "1h"
    paper_balance: float = Field(default=1000.0, gt=0)
    context_symbol: str = "BTC/USDT"
    data_dir: str = "var"
    max_book_age_s: int = 15
    max_clock_skew_s: float = 2.0
    reflex: ReflexCfg = ReflexCfg()
    limits: LimitsCfg = LimitsCfg()
    costs: dict[str, CostCfg]
    denylist: dict[str, list[str]] = {}
    setups: list[SetupCfg]

    @model_validator(mode="after")
    def _check(self) -> "Config":
        self.limits.build()  # raises on reckless limits
        denied = {b.upper(): cat for cat, bases in self.denylist.items() for b in bases}
        ids = set()
        for s in self.setups:
            if s.id in ids:
                raise ValueError(f"duplicate setup id {s.id}")
            ids.add(s.id)
            if s.base.upper() in denied:
                raise ValueError(f"setup {s.id}: {s.base} is off-limits ({denied[s.base.upper()]})")
            if not s.symbol.upper().startswith(s.base.upper() + "/"):
                raise ValueError(f"setup {s.id}: symbol {s.symbol} does not match base {s.base}")
            if s.market not in self.costs:
                raise ValueError(f"setup {s.id}: no cost model for market {s.market}")
            s.build()
        return self

    def cost_of(self, symbol: str) -> CostModel:
        return self.costs["swap" if ":" in symbol else "spot"].build()

    def enabled_setups(self) -> list[Setup]:
        return [s.build() for s in self.setups if s.enabled]


def load_config(path: str | Path) -> Config:
    return Config(**yaml.safe_load(Path(path).read_text()))


def live_trading_allowed(cfg: Config, env: dict[str, str] | None = None) -> tuple[bool, str]:
    """Live orders need every one of these. Code-enforced; no model is consulted."""
    env = os.environ if env is None else env
    if cfg.mode != "live":
        return False, "mode is not live"
    if env.get("TRADER_LIVE_APPROVED") != LIVE_APPROVAL_PHRASE:
        return False, "TRADER_LIVE_APPROVED is not set to the approval phrase"
    for k in ("EXCHANGE_API_KEY", "EXCHANGE_API_SECRET", "EXCHANGE_API_PASSPHRASE"):
        if not env.get(k):
            return False, f"{k} is missing"
    return True, "ok"
