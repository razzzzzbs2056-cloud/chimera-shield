"""
Temperature intelligence engine.

Combines the hourly (elevation-adjusted) glacier air-temperature series with an
ERA5-derived climatological normal to produce:
  * current estimated glacier air temperature
  * 24 h min / max / mean
  * short-term trend (degC/day, least-squares over recent hours)
  * temperature anomaly vs same-day-of-year climatological mean

Air temperature and surface (skin) temperature are handled separately -- this
engine deals only with air temperature; surface temperature stays in its own
observation from the LST connector.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


def _mean(vals: List[float]) -> Optional[float]:
    vals = [v for v in vals if v is not None]
    return round(sum(vals) / len(vals), 2) if vals else None


def _trend_c_per_day(times: List[datetime], temps: List[Optional[float]]
                     ) -> Optional[float]:
    """Least-squares slope in degC/day over the provided window."""
    pts = [(t.timestamp(), v) for t, v in zip(times, temps) if v is not None]
    if len(pts) < 4:
        return None
    n = len(pts)
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    num = sum((x - mx) * (y - my) for x, y in pts)
    den = sum((x - mx) ** 2 for x, y in pts)
    if den == 0:
        return None
    slope_per_s = num / den
    return round(slope_per_s * 86400, 3)


@dataclass
class TemperatureIntelligence:
    current_c: Optional[float]
    min_24h_c: Optional[float]
    max_24h_c: Optional[float]
    mean_24h_c: Optional[float]
    trend_c_per_day: Optional[float]
    climatological_normal_c: Optional[float]
    anomaly_c: Optional[float]
    is_elevation_adjusted: bool

    def to_dict(self) -> dict:
        return {
            "current_glacier_air_temp_c": self.current_c,
            "min_24h_c": self.min_24h_c,
            "max_24h_c": self.max_24h_c,
            "mean_24h_c": self.mean_24h_c,
            "trend_c_per_day": self.trend_c_per_day,
            "climatological_normal_c": self.climatological_normal_c,
            "anomaly_c": self.anomaly_c,
            "is_elevation_adjusted_estimate": self.is_elevation_adjusted,
            "note": ("Air temperature (estimated, elevation-adjusted). "
                     "Not a station reading; not surface/skin temperature."),
        }


def compute(
    times: List[datetime],
    adjusted_temps_c: List[Optional[float]],
    climatological_normal_c: Optional[float],
    is_elevation_adjusted: bool = True,
) -> TemperatureIntelligence:
    """``adjusted_temps_c`` = elevation-adjusted glacier air temps, oldest->newest.
    ``climatological_normal_c`` = ERA5 mean for the current day-of-year at the
    glacier."""
    # Last 24 hourly samples as the "24 h" window (series is hourly, UTC).
    last_temps = adjusted_temps_c[-24:]

    known = [v for v in last_temps if v is not None]
    current = next((v for v in reversed(adjusted_temps_c) if v is not None), None)
    tmin = round(min(known), 2) if known else None
    tmax = round(max(known), 2) if known else None
    tmean = _mean(last_temps)
    trend = _trend_c_per_day(times[-48:], adjusted_temps_c[-48:])

    anomaly = None
    if current is not None and climatological_normal_c is not None:
        anomaly = round(current - climatological_normal_c, 2)

    return TemperatureIntelligence(
        current, tmin, tmax, tmean, trend, climatological_normal_c, anomaly,
        is_elevation_adjusted,
    )
