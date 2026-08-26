"""
Seed reference glaciers for the default monitoring area (Nepal-Tibet border).

IMPORTANT PROVENANCE NOTE
-------------------------
The coordinates, elevations and polygons below are *reference geometry* used to
locate monitoring targets and query data providers. They are approximate,
sourced from public gazetteers / glacier inventories, and are explicitly NOT
measurements produced by this platform. No environmental measurement (area,
temperature, velocity, lake area, ...) is seeded here -- those only ever come
from real connectors at runtime, and are UNKNOWN until observed.

Elevations are used for lapse-rate temperature correction and freezing-level
comparison; where a value is uncertain it is flagged in ``elevation_source``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class ReferenceGlacier:
    id: str
    name: str
    # Representative point (roughly glacier centroid / terminus area)
    latitude: float
    longitude: float
    # Elevation band in metres a.s.l. (approximate reference geometry)
    terminus_elevation_m: Optional[float]
    median_elevation_m: Optional[float]
    headwall_elevation_m: Optional[float]
    country: str
    catchment: str
    river_system: str
    # Default monitoring radius in km (configurable per glacier by the admin)
    monitor_radius_km: float = 100.0
    # Optional coarse polygon [(lon, lat), ...]; None => point-buffer used
    polygon: Optional[List[Tuple[float, float]]] = None
    elevation_source: str = "approximate reference geometry (public gazetteer)"
    notes: str = ""


# --- Default Nepal-Tibet / Himalayan border monitoring set ------------------
# Coordinates are approximate reference points near the Bhote Koshi / Trishuli
# (Lhende) corridor around the Rasuwagadhi border crossing.
SEED_GLACIERS: List[ReferenceGlacier] = [
    ReferenceGlacier(
        id="purepu",
        name="Purepu Glacier",
        latitude=28.30,
        longitude=85.38,
        terminus_elevation_m=5200,
        median_elevation_m=5700,
        headwall_elevation_m=6200,
        country="Nepal/Tibet border",
        catchment="Lhende Khola",
        river_system="Trishuli / Bhote Koshi",
        notes=(
            "Reference target in the Lhende Khola catchment upstream of the "
            "Rasuwagadhi corridor. Geometry approximate."
        ),
    ),
    ReferenceGlacier(
        id="lhende_upper",
        name="Upper Lhende Catchment Glacier",
        latitude=28.34,
        longitude=85.42,
        terminus_elevation_m=5100,
        median_elevation_m=5650,
        headwall_elevation_m=6100,
        country="Tibet (CN)",
        catchment="Lhende Khola",
        river_system="Trishuli / Bhote Koshi",
        notes="Upstream contributing glacier to the Lhende Khola.",
    ),
    ReferenceGlacier(
        id="gyirong_north",
        name="Gyirong Region Glacier (North)",
        latitude=28.52,
        longitude=85.30,
        terminus_elevation_m=5300,
        median_elevation_m=5900,
        headwall_elevation_m=6500,
        country="Tibet (CN)",
        catchment="Gyirong / Kyirong",
        river_system="Trishuli / Bhote Koshi",
        notes="Gyirong (Kyirong) valley region north of the border.",
    ),
]


# --- Downstream infrastructure / settlements at risk in the corridor --------
# Reference locations used to compute downstream-affected areas for alerts.
@dataclass
class Infrastructure:
    id: str
    name: str
    kind: str  # settlement | bridge | road | hydropower | border
    latitude: float
    longitude: float
    elevation_m: Optional[float] = None
    river_system: str = "Bhote Koshi"
    notes: str = ""


SEED_INFRASTRUCTURE: List[Infrastructure] = [
    Infrastructure("rasuwagadhi", "Rasuwagadhi (border / hydropower)", "hydropower",
                   28.278, 85.377, 1800, notes="Rasuwagadhi HEP & border crossing."),
    Infrastructure("timure", "Timure", "settlement", 28.257, 85.377, 1750),
    Infrastructure("syabrubesi", "Syabrubesi", "settlement", 28.163, 85.335, 1450,
                   notes="Downstream confluence town; trekking hub."),
    Infrastructure("bhotekoshi_bridge", "Bhote Koshi Bridge (corridor)", "bridge",
                   28.20, 85.36, 1600),
    Infrastructure("gyirong_town", "Gyirong Town (Kyirong)", "settlement",
                   28.85, 85.30, 2800, river_system="Kyirong/Trishuli"),
]


def get_glacier(glacier_id: str) -> Optional[ReferenceGlacier]:
    for g in SEED_GLACIERS:
        if g.id == glacier_id:
            return g
    return None


def downstream_of(glacier: ReferenceGlacier) -> List[Infrastructure]:
    """Infrastructure hydrologically downstream (same river system, lower
    elevation). This is a coarse reference relationship for alert routing --
    a full implementation would trace the DEM flow network (see engines/terrain
    interface). Labelled accordingly wherever surfaced."""
    out = []
    for infra in SEED_INFRASTRUCTURE:
        same_system = (
            glacier.river_system.split("/")[0].strip().lower()
            in infra.river_system.lower()
            or infra.river_system.split("/")[0].strip().lower()
            in glacier.river_system.lower()
            or "bhote koshi" in infra.river_system.lower()
        )
        lower = (
            glacier.terminus_elevation_m is None
            or infra.elevation_m is None
            or infra.elevation_m < glacier.terminus_elevation_m
        )
        if same_system and lower:
            out.append(infra)
    return out
