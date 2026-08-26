"""
Precipitation & snow engine.

Separates RAIN from SNOW using the model's own rain/snowfall split, and adds
extra phase uncertainty when temperatures sit near freezing (rain vs snow is
ambiguous there). Accumulates over 24 h / 3 d / 7 d / 30 d windows.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


def _sum_last(hours: int, times: List[datetime], vals: List[Optional[float]]
              ) -> Optional[float]:
    if not times:
        return None
    cutoff = times[-1].timestamp() - hours * 3600
    picked = [v for t, v in zip(times, vals)
              if v is not None and t.timestamp() >= cutoff]
    if not picked:
        return None
    return round(sum(picked), 2)


@dataclass
class PrecipitationResult:
    precip_24h_mm: Optional[float]
    precip_3d_mm: Optional[float]
    precip_7d_mm: Optional[float]
    precip_30d_mm: Optional[float]
    rain_24h_mm: Optional[float]
    snowfall_24h_cm: Optional[float]
    phase_uncertain: bool

    def to_dict(self) -> dict:
        return {
            "precip_24h_mm": self.precip_24h_mm,
            "precip_3d_mm": self.precip_3d_mm,
            "precip_7d_mm": self.precip_7d_mm,
            "precip_30d_mm": self.precip_30d_mm,
            "rain_24h_mm": self.rain_24h_mm,
            "snowfall_24h_cm": self.snowfall_24h_cm,
            "phase_uncertain_near_freezing": self.phase_uncertain,
        }


def compute(
    times: List[datetime],
    precip_mm: List[Optional[float]],
    rain_mm: List[Optional[float]],
    snowfall_cm: List[Optional[float]],
    temps_c: List[Optional[float]],
) -> PrecipitationResult:
    # Phase uncertainty: any recent (24 h) hour with measurable precip and temp
    # within +/- 1.5 degC of freezing.
    phase_uncertain = False
    if times:
        cutoff = times[-1].timestamp() - 24 * 3600
        for t, p, temp in zip(times, precip_mm, temps_c):
            if (t.timestamp() >= cutoff and p and p > 0.1
                    and temp is not None and abs(temp) <= 1.5):
                phase_uncertain = True
                break
    return PrecipitationResult(
        _sum_last(24, times, precip_mm),
        _sum_last(72, times, precip_mm),
        _sum_last(24 * 7, times, precip_mm),
        _sum_last(24 * 30, times, precip_mm),
        _sum_last(24, times, rain_mm),
        _sum_last(24, times, snowfall_cm),
        phase_uncertain,
    )
