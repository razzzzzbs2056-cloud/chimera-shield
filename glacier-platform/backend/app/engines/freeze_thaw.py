"""
Freeze-thaw engine.

Detects diurnal transitions across 0 degC: a day-time excursion above freezing
followed by a night-time drop below freezing. Repeated cycles are a recognised
contributor to rock/ice fracturing (frost-cracking), so we count them and flag
abnormal increases. We do NOT claim a cycle count predicts failure -- it is one
instability *indicator* among several in the risk engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple


@dataclass
class FreezeThawResult:
    cycles_last_7d: int
    cycles_last_30d: int
    hours_above_freezing_7d: Optional[float]
    consecutive_warm_nights: int  # nights whose minimum stayed > 0 degC
    coverage_ok: bool

    def to_dict(self) -> dict:
        return {
            "freeze_thaw_cycles_7d": self.cycles_last_7d,
            "freeze_thaw_cycles_30d": self.cycles_last_30d,
            "hours_above_freezing_7d": self.hours_above_freezing_7d,
            "consecutive_warm_nights": self.consecutive_warm_nights,
            "coverage_ok": self.coverage_ok,
        }


def _daily_min_max(times: List[datetime], temps: List[Optional[float]]
                   ) -> List[Tuple[str, Optional[float], Optional[float]]]:
    """Group hourly temps into (date, min, max) per calendar day (UTC)."""
    buckets: dict = {}
    for t, v in zip(times, temps):
        if v is None:
            continue
        key = t.date().isoformat()
        lo, hi = buckets.get(key, (v, v))
        buckets[key] = (min(lo, v), max(hi, v))
    return [(k, lo, hi) for k, (lo, hi) in sorted(buckets.items())]


def compute(times: List[datetime], temps: List[Optional[float]]
            ) -> FreezeThawResult:
    """A freeze-thaw cycle for a day = daily max > 0 and daily min < 0."""
    days = _daily_min_max(times, temps)
    coverage_ok = len(days) >= 3

    def count_cycles(day_slice):
        return sum(1 for (_, lo, hi) in day_slice
                   if lo is not None and hi is not None and hi > 0 and lo < 0)

    cycles_7 = count_cycles(days[-7:])
    cycles_30 = count_cycles(days[-30:])

    # Hours above freezing over last ~7 days from hourly data.
    hours_above = None
    if temps:
        recent = [(t, v) for t, v in zip(times, temps) if v is not None]
        if recent:
            cutoff = recent[-1][0].timestamp() - 7 * 86400
            hrs = sum(1 for t, v in recent if t.timestamp() >= cutoff and v > 0)
            hours_above = float(hrs)

    # Consecutive most-recent nights whose minimum stayed above 0 degC.
    warm_nights = 0
    for (_, lo, _hi) in reversed(days):
        if lo is not None and lo > 0:
            warm_nights += 1
        else:
            break

    return FreezeThawResult(cycles_7, cycles_30, hours_above, warm_nights, coverage_ok)
