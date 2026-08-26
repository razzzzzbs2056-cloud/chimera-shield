"""
NASA / satellite Land-Surface-Temperature (skin/surface temperature) connector.

Sources supported by design: VIIRS LST, MODIS LST, Landsat thermal, Sentinel-3
SLSTR. Access to these products requires NASA Earthdata credentials (and, for
some, granule subsetting services). When ``NASA_EARTHDATA_TOKEN`` is not set,
this connector returns UNKNOWN -- it never fabricates a surface temperature.

CRITICAL scientific rule enforced by types:
  Land/ice SURFACE (skin) temperature is NOT the same as 2 m atmospheric AIR
  temperature. This connector returns ValueKind.MEASURED *surface* temperature
  and stores it separately from air temperature. The two are never merged.
"""
from __future__ import annotations

from typing import Optional

from ..core import DataSource, Observation, Provenance, ValueKind
from ..config import settings

VIIRS_SOURCE = DataSource(
    id="viirs_lst",
    name="VIIRS Land Surface Temperature",
    provider="NASA (JPSS/Suomi-NPP)",
    authoritative=True,
    url="https://www.earthdata.nasa.gov/",
    license="NASA open data",
)


async def fetch_surface_temperature(lat: float, lon: float) -> Observation[float]:
    """Latest usable satellite surface (skin) temperature at the target.

    Returns UNKNOWN unless NASA Earthdata access is configured AND a cloud-free
    granule is genuinely available. This is a *surface* temperature in degC,
    kept strictly separate from air temperature.
    """
    prov = Provenance(
        source=VIIRS_SOURCE,
        value_kind=ValueKind.MEASURED,
        spatial_resolution_m=750.0,
        temporal_resolution_s=12 * 3600,
        notes="Land/ice SURFACE (skin) temperature -- not 2 m air temperature.",
    )
    if not settings.nasa_configured():
        return Observation.unknown(
            prov, unit="degC",
            note=("NASA Earthdata token not configured -> surface temperature "
                  "unavailable (no value invented). Set NASA_EARTHDATA_TOKEN."),
        )
    # With credentials, a real implementation performs Earthdata granule search +
    # subsetting (VIIRS VNP21 / MOD11) and applies QC/cloud flags. That heavy
    # path belongs in a worker; until wired, we honestly return UNKNOWN rather
    # than a placeholder measurement.
    return Observation.unknown(
        prov, unit="degC",
        note=("Earthdata configured but granule retrieval worker not yet wired; "
              "returning UNKNOWN rather than a fabricated surface temperature."),
    )
