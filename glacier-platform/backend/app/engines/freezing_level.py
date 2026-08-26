"""
Freezing-level engine.

The freezing level (0 degC isotherm altitude) is provided directly by the
weather model (``freezing_level_height``). We track its current value, daily
max, overnight value, and compare it against glacier terminus / median /
headwall elevations. Prolonged periods with the freezing level well above the
glacier are flagged for attention -- as an indicator, not a verdict.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class FreezingLevelResult:
    current_m: Optional[float]
    max_24h_m: Optional[float]
    overnight_m: Optional[float]
    hours_above_terminus_7d: Optional[int]
    hours_above_median_7d: Optional[int]
    terminus_elevation_m: Optional[float]
    median_elevation_m: Optional[float]
    headwall_elevation_m: Optional[float]

    def to_dict(self) -> dict:
        return {
            "current_m": self.current_m,
            "max_24h_m": self.max_24h_m,
            "overnight_m": self.overnight_m,
            "hours_above_terminus_7d": self.hours_above_terminus_7d,
            "hours_above_median_7d": self.hours_above_median_7d,
            "glacier_terminus_m": self.terminus_elevation_m,
            "glacier_median_m": self.median_elevation_m,
            "glacier_headwall_m": self.headwall_elevation_m,
        }


def compute(
    times: List[datetime],
    freezing_level_m: List[Optional[float]],
    terminus_m: Optional[float],
    median_m: Optional[float],
    headwall_m: Optional[float],
) -> FreezingLevelResult:
    pairs = [(t, v) for t, v in zip(times, freezing_level_m) if v is not None]
    current = pairs[-1][1] if pairs else None

    last24 = [v for t, v in pairs if pairs and t >= pairs[-1][0].replace(
        hour=0, minute=0, second=0, microsecond=0)]
    max_24h = max(last24) if last24 else None

    # Overnight = local-ish night hours (UTC 18:00-06:00 as a coarse proxy).
    overnight_vals = [v for t, v in pairs[-24:] if t.hour >= 18 or t.hour < 6]
    overnight = (sum(overnight_vals) / len(overnight_vals)) if overnight_vals else None

    def hours_above(threshold: Optional[float]) -> Optional[int]:
        if threshold is None or not pairs:
            return None
        cutoff = pairs[-1][0].timestamp() - 7 * 86400
        return sum(1 for t, v in pairs if t.timestamp() >= cutoff and v > threshold)

    return FreezingLevelResult(
        round(current, 0) if current is not None else None,
        round(max_24h, 0) if max_24h is not None else None,
        round(overnight, 0) if overnight is not None else None,
        hours_above(terminus_m),
        hours_above(median_m),
        terminus_m, median_m, headwall_m,
    )
