"""State engine: turns raw feeds into ONE compact numeric snapshot.

The snapshot is the only thing a REFLEX sees. Everything in it is computed here, in code.
The engine refuses to build a snapshot (raises DataFault) when data is missing, stale,
from the future, malformed, or when the local clock disagrees with the exchange.
A DataFault means: no new orders on this candle.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Sequence

import pandas as pd
from pydantic import BaseModel, ConfigDict

from trader.state.features import FEATURE_COLS, WARMUP, compute_features
from trader.types import Book, Candle, Direction, RiskState

TOKEN_BUDGET = 400
# Conservative estimate: numeric JSON tokenises at roughly 2.5-3.5 chars per token.
# We divide by 2.5 so the estimate errs high. Not a measured tokenizer count.
CHARS_PER_TOKEN = 2.5


class DataFault(Exception):
    """Raised when inputs are unsafe to decide on. kind is machine-readable."""

    def __init__(self, kind: str, detail: str):
        super().__init__(f"{kind}: {detail}")
        self.kind = kind
        self.detail = detail


class Snapshot(BaseModel):
    """Short keys on purpose: this is serialised into the REFLEX prompt on every candle."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    t: int  # decision time, epoch seconds (the close of the last bar)
    sym: str
    tf: str
    bias: Direction  # the only direction the researched thesis permits
    px: float  # mid (live) or last close (backtest)
    spr: float | None  # spread, bps; None when no order book is available
    imb: float | None  # top-of-book imbalance in [-1, 1]; positive = bid heavy
    r1: float  # % returns over 1, 6, 24 bars
    r6: float
    r24: float
    vol: float  # realised vol over 24 bars, annualised %
    volr: float  # 24-bar vol divided by 168-bar vol
    atr: float  # 14-bar ATR as % of price
    ma_f: float  # % distance of price from its 24-bar mean
    ma_s: float  # % distance of price from its 168-bar mean
    er: float  # 24-bar efficiency ratio, 0 (chop) to 1 (straight line)
    rsi: float
    hi: float  # % below the 168-bar high (<= 0)
    lo: float  # % above the 168-bar low (>= 0)
    vz: float  # volume z-score
    fund: float | None  # perp funding rate, % per interval
    btc_r24: float  # BTC context
    btc_ma_s: float
    btc_volr: float
    inval: float | None  # % distance from px to the thesis invalidation price
    inv: float  # signed position notional / equity for this symbol
    exp: float  # gross exposure / equity, all symbols
    dd: float  # drawdown from equity peak, %
    dpl: float  # today's PnL, % of day-start equity
    npos: int  # open positions
    rs: RiskState  # risk state computed by the hard risk layer

    def to_prompt(self) -> str:
        return json.dumps(self.model_dump(mode="json"), separators=(",", ":"))

    def token_estimate(self) -> int:
        return math.ceil(len(self.to_prompt()) / CHARS_PER_TOKEN)


@dataclass(frozen=True)
class AccountView:
    """Account numbers the engine copies into the snapshot. Computed by the ledger, not here."""

    inventory_frac: float
    exposure_frac: float
    drawdown_pct: float
    daily_pnl_pct: float
    open_positions: int
    risk_state: RiskState


@dataclass(frozen=True)
class EngineConfig:
    tf: str = "1h"
    tf_seconds: int = 3600
    max_book_age_s: int = 15
    max_clock_skew_s: float = 2.0
    require_book: bool = True
    book_levels: int = 10

    @property
    def bars_per_year(self) -> float:
        return 365 * 86400 / self.tf_seconds


def _r(x: float, n: int = 3) -> float:
    return round(float(x), n)


def candles_to_frame(candles: Sequence[Candle]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "open": [c.open for c in candles],
            "high": [c.high for c in candles],
            "low": [c.low for c in candles],
            "close": [c.close for c in candles],
            "volume": [c.volume for c in candles],
        }
    )


def validate_candles(candles: Sequence[Candle], asof: int, cfg: EngineConfig, label: str) -> None:
    if len(candles) < WARMUP + 1:
        raise DataFault("missing_data", f"{label}: {len(candles)} bars, need {WARMUP + 1}")
    last = candles[-1]
    if any(c.ts_close > asof for c in candles):
        raise DataFault("lookahead", f"{label}: a bar closes after asof={asof}")
    if asof - last.ts_close >= cfg.tf_seconds:
        raise DataFault("stale_data", f"{label}: last bar closed {asof - last.ts_close}s before asof")
    prev = None
    for c in candles:
        vals = (c.open, c.high, c.low, c.close, c.volume)
        if not all(math.isfinite(x) for x in vals) or min(vals[:4]) <= 0 or c.volume < 0:
            raise DataFault("bad_data", f"{label}: non-finite or non-positive bar at {c.ts_open}")
        if c.high < max(c.open, c.close) or c.low > min(c.open, c.close):
            raise DataFault("bad_data", f"{label}: inconsistent high/low at {c.ts_open}")
        if c.ts_close - c.ts_open != cfg.tf_seconds:
            raise DataFault("bad_data", f"{label}: bar length is not {cfg.tf_seconds}s at {c.ts_open}")
        if prev is not None and c.ts_open != prev.ts_close:
            raise DataFault("missing_data", f"{label}: gap between {prev.ts_close} and {c.ts_open}")
        prev = c


def book_metrics(book: Book, asof: int, cfg: EngineConfig) -> tuple[float, float, float]:
    """Returns (mid, spread_bps, imbalance). Raises DataFault on any problem."""
    if book.ts > asof:
        raise DataFault("lookahead", f"book ts {book.ts} is after asof {asof}")
    if asof - book.ts > cfg.max_book_age_s:
        raise DataFault("stale_data", f"book is {asof - book.ts}s old")
    if not book.bids or not book.asks:
        raise DataFault("missing_data", "empty order book side")
    bid, ask = book.bids[0][0], book.asks[0][0]
    if not (math.isfinite(bid) and math.isfinite(ask)) or bid <= 0 or ask <= 0:
        raise DataFault("bad_data", "non-finite or non-positive book price")
    if bid >= ask:
        raise DataFault("bad_data", f"crossed book: bid {bid} >= ask {ask}")
    mid = (bid + ask) / 2
    bq = sum(q for _, q in book.bids[: cfg.book_levels])
    aq = sum(q for _, q in book.asks[: cfg.book_levels])
    if bq + aq <= 0:
        raise DataFault("bad_data", "zero book depth")
    return mid, (ask - bid) / mid * 1e4, (bq - aq) / (bq + aq)


def check_clock(local_ts: float, exchange_ts: float, cfg: EngineConfig) -> None:
    skew = abs(local_ts - exchange_ts)
    if skew > cfg.max_clock_skew_s:
        raise DataFault("clock_skew", f"local clock differs from exchange by {skew:.2f}s")


def assemble(
    *,
    asof: int,
    symbol: str,
    cfg: EngineConfig,
    bias: Direction,
    feat: dict[str, float],
    btc: dict[str, float],
    px: float,
    spread_bps: float | None,
    imbalance: float | None,
    funding_pct: float | None,
    invalidation_price: float | None,
    account: AccountView,
) -> Snapshot:
    """Build the snapshot from already-validated numbers. Shared by live and backtest paths."""
    for k in FEATURE_COLS:
        if not math.isfinite(feat[k]):
            raise DataFault("bad_data", f"{symbol}: feature {k} is not finite")
    for k in ("r24", "ma_s", "volr"):
        if not math.isfinite(btc[k]):
            raise DataFault("bad_data", f"BTC context {k} is not finite")
    snap = Snapshot(
        t=asof,
        sym=symbol,
        tf=cfg.tf,
        bias=bias,
        px=float(f"{px:.6g}"),
        spr=None if spread_bps is None else _r(spread_bps, 2),
        imb=None if imbalance is None else _r(imbalance, 2),
        r1=_r(feat["r1"], 2),
        r6=_r(feat["r6"], 2),
        r24=_r(feat["r24"], 2),
        vol=_r(feat["vol"], 1),
        volr=_r(feat["volr"], 2),
        atr=_r(feat["atr"], 2),
        ma_f=_r(feat["ma_f"], 2),
        ma_s=_r(feat["ma_s"], 2),
        er=_r(feat["er"], 2),
        rsi=_r(feat["rsi"], 1),
        hi=_r(feat["hi"], 2),
        lo=_r(feat["lo"], 2),
        vz=_r(feat["vz"], 2),
        fund=None if funding_pct is None else _r(funding_pct, 4),
        btc_r24=_r(btc["r24"], 2),
        btc_ma_s=_r(btc["ma_s"], 2),
        btc_volr=_r(btc["volr"], 2),
        inval=None if invalidation_price is None else _r((invalidation_price / px - 1) * 100, 2),
        inv=_r(account.inventory_frac, 3),
        exp=_r(account.exposure_frac, 3),
        dd=_r(account.drawdown_pct, 2),
        dpl=_r(account.daily_pnl_pct, 2),
        npos=account.open_positions,
        rs=account.risk_state,
    )
    if snap.token_estimate() >= TOKEN_BUDGET:
        raise DataFault("bad_data", f"snapshot estimate {snap.token_estimate()} tokens exceeds budget")
    return snap


def build_snapshot(
    *,
    asof: int,
    symbol: str,
    cfg: EngineConfig,
    bias: Direction,
    candles: Sequence[Candle],
    btc_candles: Sequence[Candle],
    book: Book | None,
    funding_pct: float | None,
    invalidation_price: float | None,
    account: AccountView,
    local_ts: float | None = None,
    exchange_ts: float | None = None,
) -> Snapshot:
    """Live path: validate every feed, then assemble. Any problem raises DataFault."""
    if local_ts is not None and exchange_ts is not None:
        check_clock(local_ts, exchange_ts, cfg)
    validate_candles(candles, asof, cfg, symbol)
    validate_candles(btc_candles, asof, cfg, "BTC")
    feat = compute_features(candles_to_frame(candles), cfg.bars_per_year).iloc[-1].to_dict()
    btc = compute_features(candles_to_frame(btc_candles), cfg.bars_per_year).iloc[-1].to_dict()
    px, spr, imb = candles[-1].close, None, None
    if book is not None:
        px, spr, imb = book_metrics(book, asof, cfg)
    elif cfg.require_book:
        raise DataFault("missing_data", f"{symbol}: no order book")
    if funding_pct is not None and not math.isfinite(funding_pct):
        raise DataFault("bad_data", f"{symbol}: funding is not finite")
    return assemble(
        asof=asof, symbol=symbol, cfg=cfg, bias=bias, feat=feat, btc=btc, px=px, spread_bps=spr,
        imbalance=imb, funding_pct=funding_pct, invalidation_price=invalidation_price, account=account,
    )
