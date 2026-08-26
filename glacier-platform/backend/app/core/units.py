"""
Unit conversions and quality-control bounds.

Conversions are explicit and validated. The spec requires that we keep the raw
source value alongside the processed value (e.g. Kelvin vs Celsius), so these
helpers return the processed number while callers retain the raw.

We also expose physically-plausible bounds used by QC to *reject impossible
values* rather than silently clamp or invent replacements.
"""
from __future__ import annotations

from typing import Optional

# --- absolute physical plausibility bounds (reject outside these) ----------
# Chosen to be generous; anything beyond these is a data error, not weather.
BOUNDS = {
    "air_temp_c": (-90.0, 60.0),        # coldest/warmest surface air records + margin
    "surface_temp_c": (-100.0, 90.0),   # ice/rock LST can be colder/hotter than air
    "relative_humidity_pct": (0.0, 100.0),
    "surface_pressure_hpa": (300.0, 1100.0),  # 300 hPa ~ high Himalaya
    "wind_speed_ms": (0.0, 120.0),
    "precip_mm": (0.0, 2000.0),         # per accumulation window; still generous
    "snow_depth_m": (0.0, 60.0),
    "elevation_m": (-500.0, 9000.0),
    "freezing_level_m": (-500.0, 10000.0),
    "lake_area_km2": (0.0, 10000.0),
    "magnitude": (-1.0, 10.0),
}


def kelvin_to_celsius(k: Optional[float]) -> Optional[float]:
    if k is None:
        return None
    return round(k - 273.15, 3)


def celsius_to_kelvin(c: Optional[float]) -> Optional[float]:
    if c is None:
        return None
    return round(c + 273.15, 3)


def within_bounds(kind: str, value: Optional[float]) -> bool:
    """True if value is physically plausible for ``kind``. Unknown kinds pass
    (we do not reject data we have no rule for)."""
    if value is None:
        return False
    if kind not in BOUNDS:
        return True
    lo, hi = BOUNDS[kind]
    return lo <= value <= hi


def qc_value(kind: str, value: Optional[float]) -> Optional[float]:
    """Return the value if plausible, else None (UNKNOWN). Never invents data."""
    if value is None:
        return None
    return value if within_bounds(kind, value) else None
