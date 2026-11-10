"""Causal feature computation.

Every value at row k uses bars 0..k only (trailing rolling windows, no centering, no
shifting backwards). tests/test_state.py proves this by recomputing on truncated input.
The same function serves the live engine (last row of a window) and the backtest (all rows).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

FAST = 24
SLOW = 168
WARMUP = SLOW + 1  # bars needed before a row is usable

FEATURE_COLS = ("r1", "r6", "r24", "vol", "volr", "atr", "ma_f", "ma_s", "er", "rsi", "hi", "lo", "vz")


def compute_features(df: pd.DataFrame, bars_per_year: float) -> pd.DataFrame:
    """df needs columns open, high, low, close, volume in time order. Returns one row per bar."""
    c, h, lo_, v = df["close"], df["high"], df["low"], df["volume"]
    ret = c.pct_change()
    out = pd.DataFrame(index=df.index)
    out["r1"] = ret * 100
    out["r6"] = c.pct_change(6) * 100
    out["r24"] = c.pct_change(FAST) * 100
    vol_f = ret.rolling(FAST).std(ddof=0)
    vol_s = ret.rolling(SLOW).std(ddof=0)
    out["vol"] = vol_f * np.sqrt(bars_per_year) * 100
    out["volr"] = vol_f / vol_s.replace(0, np.nan)
    prev_c = c.shift(1)
    tr = pd.concat([h - lo_, (h - prev_c).abs(), (lo_ - prev_c).abs()], axis=1).max(axis=1)
    out["atr"] = tr.rolling(14).mean() / c * 100
    out["ma_f"] = (c / c.rolling(FAST).mean() - 1) * 100
    out["ma_s"] = (c / c.rolling(SLOW).mean() - 1) * 100
    path = c.diff().abs().rolling(FAST).sum()
    out["er"] = (c.diff(FAST).abs() / path.replace(0, np.nan)).fillna(0.0)
    delta = c.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    out["rsi"] = (100 - 100 / (1 + gain / loss.replace(0, np.nan))).fillna(100.0)
    out["hi"] = (c / h.rolling(SLOW).max() - 1) * 100
    out["lo"] = (c / lo_.rolling(SLOW).min() - 1) * 100
    vmean, vstd = v.rolling(SLOW).mean(), v.rolling(SLOW).std(ddof=0)
    out["vz"] = ((v - vmean) / vstd.replace(0, np.nan)).fillna(0.0)
    return out
