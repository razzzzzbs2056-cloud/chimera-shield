"""ChimeraRule: the rule baseline from ../trader, rebuilt as a freqtrade strategy.

Freqtrade (GPL-3.0) supplies the exchange connection, order handling, dry-run wallet,
backtester, database, Telegram and web UI. This file supplies only the decisions:

  signal   - the same deterministic scoring rule as trader/src/trader/reflex/rule.py
  gate     - quality >= 2, confidence > 0.88, no crisis cooldown, no low-confidence pause
  sizing   - fractional Kelly (quarter Kelly at most) capped at 2% of equity at risk
  exits    - ATR stop, target at rr x stop, time stop, thesis invalidation price
  limits   - 5% daily loss, 15% drawdown kill switch (latched), 1x position cap, 2x gross cap

Every number here is a hypothesis, not evidence of an edge. See README.md for results.
The pure functions at module level have no freqtrade dependency and are unit-tested.
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

# --- thesis per pair (docs/RESEARCH.md in ../trader, dated 2026-11-10) -------------------
# pair -> (bias, invalidation price or None). Anything not listed here is never traded.
SETUPS: dict[str, tuple[str, float | None]] = {
    "HYPE/USDT:USDT": ("long", 60.0),
    "AAVE/USDT:USDT": ("long", None),
    "SKY/USDT:USDT": ("long", 0.0358),
    "UNI/USDT:USDT": ("long", None),
    "TRX/USDT:USDT": ("long", None),
    "LINK/USDT:USDT": ("long", None),
    "XRP/USDT:USDT": ("short", None),
    "ADA/USDT:USDT": ("short", None),
}
CONTEXT_PAIR = "BTC/USDT:USDT"

# --- policy v001 (same numbers as trader/policies/v001.json) -----------------------------
FAST, SLOW = 24, 168
MIN_QUALITY = 2
MIN_CONFIDENCE = 0.88
PAUSE_CONFIDENCE = 0.60
PAUSE_BARS = 12
CRISIS_COOLDOWN_BARS = 72
KELLY_MULT = 0.25  # quarter Kelly is the ceiling
RR = 2.0
STOP_ATR_MULT = 2.5
TIME_STOP_BARS = 96
ER_FULL, TREND_MIN, BREAKOUT_BAND, RSI_CAP = 0.45, 2.0, 4.0, 78.0
HV_RATIO, CRISIS_BTC_DROP, TOXIC_IMBALANCE = 1.8, 8.0, 0.6
CAL_SHRINK, CAL_MAX_P = 0.5, 0.80

# --- hard limits: no signal can relax these ----------------------------------------------
RISK_PER_TRADE = 0.02
MAX_DAILY_LOSS = 0.05
KILL_DRAWDOWN = 0.15
MAX_LEVERAGE = 2.0  # cap on gross exposure / equity
MAX_POSITION_FRAC = 1.0  # one position is at most 1x equity
MIN_RISK_SCALE = 0.25
POSITION_LEVERAGE = 1.0  # leverage requested per position
ROUND_TRIP_COST = 0.0015  # assumption: 2 x 0.05% taker fee + spread and slippage


# ========================= pure functions (no freqtrade imports) =========================

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Causal features: row k uses bars 0..k only. Columns are prefixed f_."""
    c, h, lo = df["close"], df["high"], df["low"]
    ret = c.pct_change()
    df["f_r24"] = c.pct_change(FAST) * 100
    vol_f = ret.rolling(FAST).std(ddof=0)
    vol_s = ret.rolling(SLOW).std(ddof=0)
    df["f_volr"] = vol_f / vol_s.replace(0, np.nan)
    prev_c = c.shift(1)
    tr = pd.concat([h - lo, (h - prev_c).abs(), (lo - prev_c).abs()], axis=1).max(axis=1)
    df["f_atr"] = tr.rolling(14).mean() / c * 100
    df["f_ma_f"] = (c / c.rolling(FAST).mean() - 1) * 100
    df["f_ma_s"] = (c / c.rolling(SLOW).mean() - 1) * 100
    path = c.diff().abs().rolling(FAST).sum()
    df["f_er"] = (c.diff(FAST).abs() / path.replace(0, np.nan)).fillna(0.0)
    delta = c.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    df["f_rsi"] = (100 - 100 / (1 + gain / loss.replace(0, np.nan))).fillna(100.0)
    df["f_hi"] = (c / h.rolling(SLOW).max() - 1) * 100
    df["f_lo"] = (c / lo.rolling(SLOW).min() - 1) * 100
    return df


def add_rule(df: pd.DataFrame, bias: str) -> pd.DataFrame:
    """Score every bar. Needs f_* columns and btc_r24, btc_volr, btc_ma_s. Adds:
    crisis, conf, quality, directional, gate_ok (all causal)."""
    sign = 1.0 if bias == "long" else -1.0
    crisis = (df["btc_r24"] <= -CRISIS_BTC_DROP) | ((df["btc_volr"] >= 3.0) & (df["btc_r24"] <= -5.0))
    high_vol = ~crisis & (df["f_volr"] >= HV_RATIO)
    stressed = crisis | high_vol

    trend = (sign * df["f_ma_f"] > 0) & (sign * df["f_ma_s"] >= TREND_MIN)
    market = sign * df["btc_ma_s"] > 0
    near = (df["f_hi"] >= -BREAKOUT_BAND) if sign > 0 else (df["f_lo"] <= BREAKOUT_BAND)
    momentum = (sign * df["f_r24"] > 0) & near
    rsi_ok = (df["f_rsi"] < RSI_CAP) if sign > 0 else (df["f_rsi"] > 100 - RSI_CAP)
    n = trend.astype(int) + market.astype(int) + momentum.astype(int) + (rsi_ok & ~stressed).astype(int)

    conf_dir = 0.50 + 0.09 * n + 0.09 * (df["f_er"] / ER_FULL).clip(upper=1.0)
    conf_neutral = (0.95 - 0.10 * n).clip(lower=0.60)
    df["crisis"] = crisis
    df["directional"] = trend
    df["conf"] = np.where(trend, conf_dir, conf_neutral).clip(max=0.95).round(3)
    df["quality"] = (trend.astype(int) + market.astype(int) + momentum.astype(int)).clip(upper=3)

    # Crisis pauses all new risk for CRISIS_COOLDOWN_BARS after the last crisis bar.
    cooling = crisis.astype(int).rolling(CRISIS_COOLDOWN_BARS + 1, min_periods=1).max() > 0
    # A confidence below the floor pauses this pair for PAUSE_BARS.
    low = (df["conf"] < PAUSE_CONFIDENCE).astype(int)
    paused = low.rolling(PAUSE_BARS + 1, min_periods=1).max() > 0
    complete = df[["f_ma_s", "f_atr", "f_volr", "btc_r24", "btc_volr", "btc_ma_s"]].notna().all(axis=1)
    df["gate_ok"] = (
        complete & trend & ~cooling & ~paused
        & (df["quality"] >= MIN_QUALITY) & (df["conf"] > MIN_CONFIDENCE) & (df["f_atr"] > 0)
    )
    return df


def p_win(confidence: float) -> float:
    """Uncalibrated confidence is shrunk halfway to 0.5 and capped."""
    c = min(1.0, max(0.0, confidence))
    return min(CAL_MAX_P, 0.5 + CAL_SHRINK * (c - 0.5))


def stop_fraction(atr_pct: float) -> float:
    """Stop distance as a fraction of price, from ATR (% of price)."""
    return min(0.25, max(0.003, STOP_ATR_MULT * atr_pct / 100))


def risk_scale(drawdown: float) -> float:
    """1.0 at the equity peak, falling linearly to MIN_RISK_SCALE at the kill level."""
    return max(MIN_RISK_SCALE, 1.0 - max(0.0, drawdown) / KILL_DRAWDOWN)


def stake_for(equity: float, confidence: float, stop_frac: float, drawdown: float,
              gross_open: float, cost_frac: float = ROUND_TRIP_COST) -> tuple[float, str]:
    """Position notional in stake currency and the reason. Zero means no trade."""
    if not all(math.isfinite(x) for x in (equity, confidence, stop_frac)) or equity <= 0 or stop_frac <= 0:
        return 0.0, "bad_inputs"
    gain = RR * stop_frac - cost_frac
    loss = stop_frac + cost_frac
    if gain <= 0:
        return 0.0, "costs_exceed_reward"
    p = p_win(confidence)
    kelly = p - (1 - p) / (gain / loss)
    if kelly <= 0:
        return 0.0, "no_edge"
    risk_frac = min(min(KELLY_MULT, 0.25) * kelly, RISK_PER_TRADE * risk_scale(drawdown))
    notional = risk_frac * equity / loss
    notional = min(notional, MAX_POSITION_FRAC * equity)
    headroom = MAX_LEVERAGE * equity - gross_open
    if headroom <= 0:
        return 0.0, "no_leverage_headroom"
    return min(notional, headroom), "ok"


def equity_state(closed: list[tuple[datetime, float]], start: float, now: datetime,
                 cleared_at: datetime | None = None) -> dict:
    """Realised equity curve from closed trades [(close time, profit)].

    killed latches once drawdown from the peak reaches KILL_DRAWDOWN. Only a human can
    clear it, by setting cleared_at (config key chimera_kill_cleared_at) to a later time;
    the peak then restarts from the equity at that time.
    """
    if cleared_at is not None and cleared_at > now:
        cleared_at = None  # a clear dated in the future has no effect yet
    eq = peak = float(start)
    killed = False
    day_pnl = 0.0
    for when, profit in sorted(closed, key=lambda x: x[0]):
        eq += profit
        if cleared_at is not None and when <= cleared_at:
            peak, killed = eq, False
        else:
            peak = max(peak, eq)
            if peak > 0 and (peak - eq) / peak >= KILL_DRAWDOWN:
                killed = True
        if when.date() == now.date():
            day_pnl += profit
    dd = (peak - eq) / peak if peak > 0 else 1.0
    day_start = eq - day_pnl
    return {
        "equity": eq, "peak": peak, "drawdown": dd, "killed": killed or eq <= 0,
        "day_pnl": day_pnl,
        "daily_stop": day_start > 0 and day_pnl <= -MAX_DAILY_LOSS * day_start,
    }


def book_imbalance(book: dict, levels: int = 10) -> float:
    """(bid size - ask size) / total over the top levels, in [-1, 1]. Raises on a bad book."""
    bids, asks = book.get("bids") or [], book.get("asks") or []
    if not bids or not asks or bids[0][0] >= asks[0][0]:
        raise ValueError("empty or crossed order book")
    bq = sum(float(x[1]) for x in bids[:levels])
    aq = sum(float(x[1]) for x in asks[:levels])
    if bq + aq <= 0:
        raise ValueError("order book has no size")
    return (bq - aq) / (bq + aq)


# ================================ freqtrade strategy =====================================

try:  # the pure functions above stay importable without freqtrade installed
    from freqtrade.enums import RunMode
    from freqtrade.persistence import Trade
    from freqtrade.strategy import IStrategy, informative, stoploss_from_open
except ImportError:  # pragma: no cover
    IStrategy = None  # type: ignore[assignment,misc]

if IStrategy is not None:

    class ChimeraRule(IStrategy):
        INTERFACE_VERSION = 3
        timeframe = "1h"
        can_short = True
        startup_candle_count = SLOW + CRISIS_COOLDOWN_BARS + 2
        process_only_new_candles = True

        stoploss = -0.30  # backstop only; the real stop is custom_stoploss
        use_custom_stoploss = True
        minimal_roi = {"0": 100.0}  # off; the target is custom_roi
        use_custom_roi = True
        use_exit_signal = True  # needed for custom_exit; no indicator exit signal is set
        exit_profit_only = False
        position_adjustment_enable = False

        # ---- indicators and signal ----

        @informative("1h", CONTEXT_PAIR, fmt="btcraw_{column}")
        def populate_indicators_btc(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
            dataframe = add_features(dataframe)
            return dataframe[["date", "f_r24", "f_volr", "f_ma_s"]].copy()

        def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
            dataframe = add_features(dataframe)
            dataframe["btc_r24"] = dataframe["btcraw_f_r24"]
            dataframe["btc_volr"] = dataframe["btcraw_f_volr"]
            dataframe["btc_ma_s"] = dataframe["btcraw_f_ma_s"]
            bias = SETUPS.get(metadata["pair"], (None, None))[0]
            if bias is None:
                dataframe["gate_ok"] = False
                dataframe["conf"] = 0.0
                return dataframe
            return add_rule(dataframe, bias)

        def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
            bias, inval = SETUPS.get(metadata["pair"], (None, None))
            if bias is None:
                return dataframe
            ok = dataframe["gate_ok"] & (dataframe["volume"] > 0)
            if inval is not None:
                ok &= (dataframe["close"] > inval) if bias == "long" else (dataframe["close"] < inval)
            col = "enter_long" if bias == "long" else "enter_short"
            dataframe.loc[ok, col] = 1
            dataframe.loc[ok, "enter_tag"] = "rule_" + bias
            return dataframe

        def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
            return dataframe  # exits are stop, target, time stop, invalidation and kill only

        # ---- account state from the trade database ----

        def _state(self, now: datetime) -> dict:
            closed = [
                (t.close_date_utc, float(t.close_profit_abs or 0.0))
                for t in Trade.get_trades_proxy(is_open=False)
                if t.close_date is not None
            ]
            cleared = self.config.get("chimera_kill_cleared_at")
            cleared_at = datetime.fromisoformat(cleared).astimezone(timezone.utc) if cleared else None
            start = float(self.wallets.get_starting_balance()) if self.wallets else 0.0
            return equity_state(closed, start, now, cleared_at)

        def _signal_candle(self, pair: str, before: datetime):
            df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
            if df is None or df.empty:
                return None
            rows = df.loc[df["date"] < before.replace(minute=0, second=0, microsecond=0)]
            return rows.iloc[-1] if not rows.empty else None

        def _stop_frac(self, trade: Trade) -> float | None:
            sf = trade.get_custom_data("stop_frac")
            if sf is None:
                row = self._signal_candle(trade.pair, trade.open_date_utc)
                if row is None or not math.isfinite(row["f_atr"]):
                    return None
                sf = stop_fraction(float(row["f_atr"]))
                trade.set_custom_data("stop_frac", sf)
            return float(sf)

        # ---- sizing and the final entry check ----

        def leverage(self, pair: str, current_time: datetime, current_rate: float, proposed_leverage: float,
                     max_leverage: float, entry_tag: str | None, side: str, **kwargs) -> float:
            return POSITION_LEVERAGE

        def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                                proposed_stake: float, min_stake: float | None, max_stake: float,
                                leverage: float, entry_tag: str | None, side: str, **kwargs) -> float:
            row = self._signal_candle(pair, current_time)
            if row is None:
                return 0.0
            st = self._state(current_time)
            if st["killed"] or st["daily_stop"]:
                return 0.0
            gross = sum(float(t.stake_amount) * float(t.leverage or 1.0) for t in Trade.get_trades_proxy(is_open=True))
            notional, _ = stake_for(st["equity"], float(row["conf"]), stop_fraction(float(row["f_atr"])),
                                    st["drawdown"], gross)
            stake = min(notional / max(leverage, 1.0), max_stake)
            if stake <= 0 or (min_stake is not None and stake < min_stake):
                return 0.0
            return stake

        def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                                time_in_force: str, current_time: datetime, entry_tag: str | None,
                                side: str, **kwargs) -> bool:
            bias = SETUPS.get(pair, (None, None))[0]
            if bias != side:
                return False
            st = self._state(current_time)
            if st["killed"] or st["daily_stop"]:
                return False
            if self.dp.runmode in (RunMode.LIVE, RunMode.DRY_RUN):
                # Order-book check exists only on live data; a book we cannot read blocks the entry.
                try:
                    imb = book_imbalance(self.dp.orderbook(pair, 20))
                except Exception:
                    return False
                if (1.0 if side == "long" else -1.0) * imb <= -TOXIC_IMBALANCE:
                    return False
            return True

        # ---- exits ----

        def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime, current_rate: float,
                            current_profit: float, after_fill: bool, **kwargs) -> float | None:
            sf = self._stop_frac(trade)
            if sf is None:
                return None
            lev = float(trade.leverage or 1.0)
            return stoploss_from_open(-sf * lev, current_profit, is_short=trade.is_short, leverage=lev)

        def custom_roi(self, pair: str, trade: Trade, current_time: datetime, trade_duration: int,
                       entry_tag: str | None, side: str, **kwargs) -> float | None:
            sf = self._stop_frac(trade)
            return None if sf is None else RR * sf * float(trade.leverage or 1.0)

        def custom_exit(self, pair: str, trade: Trade, current_time: datetime, current_rate: float,
                        current_profit: float, **kwargs) -> str | None:
            if self._state(current_time)["killed"]:
                return "kill_switch"
            if current_time - trade.open_date_utc >= timedelta(hours=TIME_STOP_BARS):
                return "time_stop"
            inval = SETUPS.get(pair, (None, None))[1]
            if inval is not None:
                if (not trade.is_short and current_rate <= inval) or (trade.is_short and current_rate >= inval):
                    return "thesis_invalidated"
            return None
