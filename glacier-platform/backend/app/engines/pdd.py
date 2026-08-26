"""
Positive Degree Day (PDD) engine.

PDD is a standard, transparent melt-pressure index:

    PDD(day) = max(mean_daily_temperature_C, 0)

We compute 24 h, 7 d, 30 d and seasonal cumulative PDD, plus an anomaly versus
an ERA5-derived baseline. PDD is a *melt indicator*, NOT proof that a dangerous
flood will occur -- surfaced with that caveat everywhere.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


def daily_pdd(mean_daily_temp_c: Optional[float]) -> Optional[float]:
    if mean_daily_temp_c is None:
        return None
    return max(mean_daily_temp_c, 0.0)


def cumulative_pdd(daily_means_c: List[Optional[float]]) -> Optional[float]:
    """Sum of positive degree days. Returns None only if there are no valid days
    at all (we do not invent zeros for missing days, but we do skip them and
    note coverage separately via ``coverage``)."""
    vals = [max(t, 0.0) for t in daily_means_c if t is not None]
    if not vals and all(t is None for t in daily_means_c):
        return None
    return round(sum(vals), 2)


def coverage(daily_means_c: List[Optional[float]]) -> float:
    if not daily_means_c:
        return 0.0
    known = sum(1 for t in daily_means_c if t is not None)
    return known / len(daily_means_c)


@dataclass
class PDDResult:
    pdd_24h: Optional[float]
    pdd_7d: Optional[float]
    pdd_30d: Optional[float]
    pdd_seasonal: Optional[float]
    baseline_30d: Optional[float]
    anomaly_30d_pct: Optional[float]
    coverage_30d: float

    def to_dict(self) -> dict:
        return {
            "pdd_24h": self.pdd_24h,
            "pdd_7d_cumulative": self.pdd_7d,
            "pdd_30d_cumulative": self.pdd_30d,
            "pdd_seasonal_cumulative": self.pdd_seasonal,
            "baseline_30d": self.baseline_30d,
            "anomaly_30d_pct": self.anomaly_30d_pct,
            "coverage_30d": round(self.coverage_30d, 2),
            "caveat": "PDD is a melt-pressure indicator, not proof of flooding.",
        }


def compute(
    daily_means_c: List[Optional[float]],
    seasonal_means_c: Optional[List[Optional[float]]] = None,
    baseline_30d_pdd: Optional[float] = None,
) -> PDDResult:
    """``daily_means_c`` ordered oldest->newest; last element is most recent day.
    ``baseline_30d_pdd`` is the climatological 30-day cumulative PDD for this
    period (from ERA5), used for the anomaly."""
    last = daily_means_c[-1] if daily_means_c else None
    pdd_24h = daily_pdd(last)
    pdd_7d = cumulative_pdd(daily_means_c[-7:]) if daily_means_c else None
    pdd_30d = cumulative_pdd(daily_means_c[-30:]) if daily_means_c else None
    pdd_seasonal = (cumulative_pdd(seasonal_means_c)
                    if seasonal_means_c is not None else None)
    anomaly = None
    if pdd_30d is not None and baseline_30d_pdd not in (None, 0):
        anomaly = round((pdd_30d - baseline_30d_pdd) / baseline_30d_pdd * 100, 1)
    return PDDResult(
        pdd_24h, pdd_7d, pdd_30d, pdd_seasonal, baseline_30d_pdd, anomaly,
        coverage(daily_means_c[-30:]) if daily_means_c else 0.0,
    )
