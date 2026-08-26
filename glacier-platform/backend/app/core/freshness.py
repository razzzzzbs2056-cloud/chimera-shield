"""
Data-freshness system.

Turns an observation's age into a human label ("12 minutes ago"), a status
(FRESH / DELAYED / STALE), and a strict answer to: may we call this "live"?

The freshness thresholds depend on the data source's expected cadence -- a
Sentinel-1 SAR pass every ~6 days is "fresh" at 2 days old, whereas a weather
observation 2 days old is stale. Callers pass the expected cadence.
"""
from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Optional


class FreshnessStatus(str, enum.Enum):
    FRESH = "FRESH"
    DELAYED = "DELAYED"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


# Colour hints for the UI. The frontend owns final styling; these are defaults.
FRESHNESS_COLOR = {
    FreshnessStatus.FRESH: "#2ecc71",
    FreshnessStatus.DELAYED: "#f1c40f",
    FreshnessStatus.STALE: "#e74c3c",
    FreshnessStatus.UNKNOWN: "#7f8c8d",
}


def humanize_age(age_seconds: Optional[float]) -> str:
    """'12 minutes ago', '6 hours ago', '2 days ago', or 'unknown'."""
    if age_seconds is None:
        return "unknown"
    if age_seconds < 0:
        # A future acquisition time is nonsensical for an observation.
        return "in the future"
    s = int(age_seconds)
    if s < 90:
        return f"{s} seconds ago"
    m = s // 60
    if m < 90:
        return f"{m} minutes ago"
    h = s // 3600
    if h < 48:
        return f"{h} hours ago"
    d = s // 86400
    if d < 60:
        return f"{d} days ago"
    mo = d // 30
    if mo < 24:
        return f"{mo} months ago"
    return f"{d // 365} years ago"


def classify(
    age_seconds: Optional[float],
    fresh_max_s: float,
    delayed_max_s: float,
) -> FreshnessStatus:
    """FRESH if age <= fresh_max_s, DELAYED up to delayed_max_s, else STALE.
    UNKNOWN when age is unknown."""
    if age_seconds is None:
        return FreshnessStatus.UNKNOWN
    if age_seconds < 0:
        return FreshnessStatus.UNKNOWN
    if age_seconds <= fresh_max_s:
        return FreshnessStatus.FRESH
    if age_seconds <= delayed_max_s:
        return FreshnessStatus.DELAYED
    return FreshnessStatus.STALE


def may_call_live(
    age_seconds: Optional[float],
    source_is_near_real_time: bool,
    live_window_s: float = 15 * 60,
) -> bool:
    """The strict "never pretend delayed data is live" gate.

    Only returns True when the source itself is near-real-time AND the most
    recent observation is within ``live_window_s`` (default 15 min).
    """
    if not source_is_near_real_time:
        return False
    if age_seconds is None or age_seconds < 0:
        return False
    return age_seconds <= live_window_s


class FreshnessProfile:
    """Per-source cadence thresholds. Attach one to each connector."""

    def __init__(
        self,
        fresh_max_s: float,
        delayed_max_s: float,
        near_real_time: bool = False,
    ):
        self.fresh_max_s = fresh_max_s
        self.delayed_max_s = delayed_max_s
        self.near_real_time = near_real_time

    def describe(self, age_seconds: Optional[float]) -> dict:
        status = classify(age_seconds, self.fresh_max_s, self.delayed_max_s)
        return {
            "age_seconds": age_seconds,
            "age_human": humanize_age(age_seconds),
            "status": status.value,
            "color": FRESHNESS_COLOR[status],
            "is_live": may_call_live(age_seconds, self.near_real_time),
        }


# Sensible default profiles keyed by source cadence.
PROFILES = {
    # earthquakes: polled continuously; genuinely near-real-time
    "earthquake": FreshnessProfile(fresh_max_s=15 * 60, delayed_max_s=6 * 3600, near_real_time=True),
    # hourly weather / reanalysis-adjacent
    "weather_hourly": FreshnessProfile(fresh_max_s=90 * 60, delayed_max_s=24 * 3600, near_real_time=False),
    # river gauges (varies); treat like sub-hourly-to-hourly
    "river_gauge": FreshnessProfile(fresh_max_s=60 * 60, delayed_max_s=12 * 3600, near_real_time=False),
    # Sentinel-1 SAR ~ 6-day revisit at the equator, better with both orbits
    "sentinel1": FreshnessProfile(fresh_max_s=3 * 86400, delayed_max_s=10 * 86400, near_real_time=False),
    # Sentinel-2 optical ~ 5-day revisit, often cloud-blocked in the Himalaya
    "sentinel2": FreshnessProfile(fresh_max_s=3 * 86400, delayed_max_s=14 * 86400, near_real_time=False),
    # thermal LST (VIIRS/MODIS) ~ daily-ish usable passes
    "lst": FreshnessProfile(fresh_max_s=1 * 86400, delayed_max_s=4 * 86400, near_real_time=False),
    # forecast: no "age"; handled separately
    "forecast": FreshnessProfile(fresh_max_s=6 * 3600, delayed_max_s=24 * 3600, near_real_time=False),
}
