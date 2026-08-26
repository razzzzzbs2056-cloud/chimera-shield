"""
Open-Meteo connector -- REAL, public, no-auth.

Provides four capabilities used across the temperature/precip/snow engines:

  * ``fetch_recent_weather``  : hourly near-past weather (best-available model)
  * ``fetch_forecast``        : hourly/daily forecast (labelled FORECAST)
  * ``fetch_climatology``     : ERA5 reanalysis archive for historical normals
                                (labelled MODEL, not measured)
  * ``fetch_dem_elevation``   : model/DEM elevation at a point (for lapse-rate
                                correction and freezing-level comparison)

Scientific labelling enforced here:
  * ERA5 / model outputs are ``ValueKind.MODEL`` -- never a thermometer reading.
  * Forecast series are ``ValueKind.FORECAST`` -- never treated as observations.
  * 2 m air temperature is stored/returned separately from any surface/skin
    temperature; this connector only returns *air* temperature.
  * Kelvin is not used by Open-Meteo (it returns Celsius), but we still keep the
    raw source value alongside the processed value for auditability.

Note: Open-Meteo blends multiple NWP/reanalysis models. We record it as a MODEL
source of authoritative-quality meteorology, not a physical station.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import List, Optional

from ..core import (
    Confidence,
    DataSource,
    Observation,
    Provenance,
    ValueKind,
    qc_value,
)
from ..config import settings
from .base import get_json

FORECAST_SOURCE = DataSource(
    id="open_meteo_forecast",
    name="Open-Meteo Forecast (multi-model NWP blend)",
    provider="Open-Meteo / national weather services",
    authoritative=True,
    url="https://open-meteo.com/",
    license="CC-BY 4.0",
)
ARCHIVE_SOURCE = DataSource(
    id="open_meteo_era5",
    name="Open-Meteo Historical Reanalysis (ERA5 / ERA5-Land)",
    provider="ECMWF / Copernicus Climate Data Store (via Open-Meteo)",
    authoritative=True,
    url="https://open-meteo.com/en/docs/historical-weather-api",
    license="CC-BY 4.0",
)
ELEVATION_SOURCE = DataSource(
    id="open_meteo_elevation",
    name="Open-Meteo Elevation (Copernicus DEM GLO-90)",
    provider="ESA / Copernicus (via Open-Meteo)",
    authoritative=True,
    url="https://open-meteo.com/en/docs/elevation-api",
    license="CC-BY 4.0",
)

_HOURLY_VARS = [
    "temperature_2m",
    "dew_point_2m",
    "relative_humidity_2m",
    "surface_pressure",
    "wind_speed_10m",
    "wind_direction_10m",
    "shortwave_radiation",
    "cloud_cover",
    "precipitation",
    "rain",
    "snowfall",
    "snow_depth",
    "freezing_level_height",
]


class HourlySeries:
    """A parsed hourly weather series with typed accessors."""

    def __init__(self, hourly: dict, model_elevation_m: Optional[float]):
        self.times: List[datetime] = [
            datetime.fromisoformat(t).replace(tzinfo=timezone.utc)
            for t in hourly.get("time", [])
        ]
        self.model_elevation_m = model_elevation_m
        self._raw = hourly

    def var(self, name: str) -> List[Optional[float]]:
        return self._raw.get(name, [None] * len(self.times))

    def latest_index(self, not_after: Optional[datetime] = None) -> Optional[int]:
        if not self.times:
            return None
        if not_after is None:
            return len(self.times) - 1
        idx = None
        for i, t in enumerate(self.times):
            if t <= not_after:
                idx = i
        return idx


async def fetch_dem_elevation(lat: float, lon: float) -> Observation[float]:
    """Copernicus DEM elevation at a point (metres a.s.l.)."""
    try:
        data = await get_json(settings.open_meteo_elevation_url,
                              params={"latitude": lat, "longitude": lon})
        elev = data.get("elevation", [None])
        elev = elev[0] if isinstance(elev, list) else elev
        elev = qc_value("elevation_m", elev)
        prov = Provenance(
            source=ELEVATION_SOURCE,
            value_kind=ValueKind.MODEL,
            spatial_resolution_m=90.0,
            notes="Copernicus DEM GLO-90 sampled at point",
        )
        if elev is None:
            return Observation.unknown(prov, unit="m")
        return Observation(value=round(elev, 1), unit="m",
                           confidence=Confidence.HIGH, provenance=prov)
    except Exception as exc:
        prov = Provenance(source=ELEVATION_SOURCE, value_kind=ValueKind.MODEL,
                          notes=f"fetch failed: {exc}")
        return Observation.unknown(prov, unit="m")


async def fetch_recent_weather(lat: float, lon: float,
                               past_days: int = 5) -> Optional[HourlySeries]:
    """Recent hourly weather (best-available model), up to ``now``. Returns a
    HourlySeries or None on failure. Callers wrap individual values in
    Observations with the FORECAST_SOURCE tagged as MODEL for past hours."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(_HOURLY_VARS),
        "past_days": past_days,
        "forecast_days": 1,
        "timezone": "UTC",
    }
    try:
        data = await get_json(settings.open_meteo_forecast_url, params=params)
    except Exception:
        return None
    return HourlySeries(data.get("hourly", {}), data.get("elevation"))


async def fetch_forecast(lat: float, lon: float,
                         forecast_days: int = 10) -> Optional[HourlySeries]:
    """Hourly FORECAST series. Values from this MUST be labelled FORECAST."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(_HOURLY_VARS),
        "forecast_days": min(forecast_days, 16),
        "timezone": "UTC",
    }
    try:
        data = await get_json(settings.open_meteo_forecast_url, params=params)
    except Exception:
        return None
    return HourlySeries(data.get("hourly", {}), data.get("elevation"))


async def fetch_climatology_daily(
    lat: float, lon: float, start_year: int, end_year: int
) -> Optional[dict]:
    """ERA5 daily archive over [start_year, end_year], for building historical
    normals. Returns the raw daily dict (MODEL data) or None on failure.

    Returned series are ERA5 reanalysis -- model output, not measurements.
    """
    start = f"{start_year}-01-01"
    end = f"{end_year}-12-31"
    # Cap end at yesterday; archive is not real-time.
    yesterday = (datetime.now(timezone.utc) - timedelta(days=6)).date().isoformat()
    if end > yesterday:
        end = yesterday
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": "temperature_2m_mean,temperature_2m_max,temperature_2m_min,precipitation_sum,snowfall_sum",
        "timezone": "UTC",
    }
    try:
        data = await get_json(settings.open_meteo_archive_url, params=params)
    except Exception:
        return None
    return data.get("daily")


def air_temp_observation(series: HourlySeries, index: int) -> Observation[float]:
    """Wrap the 2 m air temperature at ``index`` as a MODEL observation.

    This is model meteorology at the model grid elevation -- NOT a station
    thermometer and NOT elevation-corrected. Elevation correction is applied
    downstream by engines/elevation.py.
    """
    temps = series.var("temperature_2m")
    t = qc_value("air_temp_c", temps[index]) if 0 <= index < len(temps) else None
    prov = Provenance(
        source=FORECAST_SOURCE,
        value_kind=ValueKind.MODEL,
        acquisition_time=series.times[index] if 0 <= index < len(series.times) else None,
        temporal_resolution_s=3600,
        notes=(f"2 m air temperature at model grid elevation "
               f"{series.model_elevation_m} m (not station, not surface/skin temp)"),
    )
    if t is None:
        return Observation.unknown(prov, unit="degC")
    return Observation(value=round(t, 2), unit="degC",
                       confidence=Confidence.MEDIUM, provenance=prov,
                       raw_value=temps[index], raw_unit="degC")
