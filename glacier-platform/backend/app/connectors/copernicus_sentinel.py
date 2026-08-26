"""
Copernicus Sentinel-1 (SAR) & Sentinel-2 (optical) connector.

Behaviour:
  * When Copernicus Data Space credentials are configured, this connector
    queries the CDSE STAC catalogue for genuinely-available scenes and returns
    their real metadata (id, acquisition time, cloud cover, orbit, resolution).
    It reports *scene availability and metadata* -- the pixel-level index
    computation (NDSI/NDWI/lake extent/SAR change) is a heavier processing step
    that belongs in a Celery worker (interface in engines/change_detection.py).
  * When credentials are absent, it returns UNKNOWN with a clear note. It NEVER
    fabricates scenes, indices, cloud percentages, or change results.

Scientific rules:
  * Cloud-obscured optical scenes are flagged; the change-detection engine must
    not treat cloudy pixels as confirmed surface change.
  * SAR intensity changes are reported as *observations to be processed*, never
    as confirmed ground movement without proper InSAR processing + validation.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional

import httpx

from ..core import Confidence, DataSource, Observation, Provenance, ValueKind
from ..config import settings

S2_SOURCE = DataSource(
    id="sentinel2_l2a",
    name="Sentinel-2 L2A (Copernicus Data Space)",
    provider="ESA / Copernicus",
    authoritative=True,
    url="https://dataspace.copernicus.eu/",
    license="Copernicus open data",
)
S1_SOURCE = DataSource(
    id="sentinel1_grd",
    name="Sentinel-1 GRD (Copernicus Data Space)",
    provider="ESA / Copernicus",
    authoritative=True,
    url="https://dataspace.copernicus.eu/",
    license="Copernicus open data",
)

# Nominal ground sample distances (m) for the bands the spec lists.
S2_RESOLUTION_M = {"B02": 10, "B03": 10, "B04": 10, "B08": 10, "B11": 20, "B12": 20, "SCL": 20}


def _bbox_around(lat: float, lon: float, radius_km: float) -> List[float]:
    dlat = radius_km / 111.0
    dlon = radius_km / (111.0 * max(0.1, abs(__import__("math").cos(__import__("math").radians(lat)))))
    return [lon - dlon, lat - dlat, lon + dlon, lat + dlat]


async def _get_token() -> Optional[str]:
    if not settings.copernicus_configured():
        return None
    data = {
        "grant_type": "client_credentials",
        "client_id": settings.copernicus_client_id,
        "client_secret": settings.copernicus_client_secret,
    }
    try:
        async with httpx.AsyncClient(timeout=settings.http_timeout_s) as client:
            r = await client.post(settings.copernicus_token_url, data=data)
            r.raise_for_status()
            return r.json().get("access_token")
    except Exception:
        return None


async def _stac_search(collection: str, lat: float, lon: float,
                       radius_km: float, days: int, limit: int = 10) -> Optional[list]:
    token = await _get_token()
    if token is None:
        return None
    dt_from = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    dt_to = datetime.now(timezone.utc).isoformat()
    body = {
        "collections": [collection],
        "bbox": _bbox_around(lat, lon, radius_km),
        "datetime": f"{dt_from}/{dt_to}",
        "limit": limit,
        "sortby": [{"field": "properties.datetime", "direction": "desc"}],
    }
    try:
        async with httpx.AsyncClient(timeout=settings.http_timeout_s) as client:
            r = await client.post(settings.copernicus_catalog_url, json=body,
                                  headers={"Authorization": f"Bearer {token}"})
            r.raise_for_status()
            return r.json().get("features", [])
    except Exception:
        return None


def _unknown(source: DataSource, profile_note: str) -> Observation[list]:
    prov = Provenance(source=source, value_kind=ValueKind.MEASURED, notes=profile_note)
    return Observation.unknown(prov, unit="scenes", note=profile_note)


async def latest_sentinel2_scenes(lat: float, lon: float, radius_km: float = 30,
                                  days: int = 30) -> Observation[List[dict]]:
    """Return metadata for the most recent Sentinel-2 scenes over the target."""
    if not settings.copernicus_configured():
        return _unknown(
            S2_SOURCE,
            "Copernicus credentials not configured -> Sentinel-2 unavailable "
            "(no data invented). Set COPERNICUS_CLIENT_ID/SECRET.",
        )
    features = await _stac_search("SENTINEL-2", lat, lon, radius_km, days)
    if features is None:
        return _unknown(S2_SOURCE, "Copernicus STAC query failed; result unknown.")
    scenes = []
    latest_time = None
    for f in features:
        props = f.get("properties", {})
        acq = props.get("datetime")
        acq_dt = datetime.fromisoformat(acq.replace("Z", "+00:00")) if acq else None
        cloud = props.get("cloudCover", props.get("eo:cloud_cover"))
        latest_time = latest_time or acq_dt
        scenes.append({
            "scene_id": f.get("id"),
            "acquisition_time": acq,
            "cloud_cover_pct": cloud,
            "resolution_m": S2_RESOLUTION_M,
            "cloud_usable": (cloud is not None and cloud < 40),
            "note": ("high cloud -- do NOT treat as confirmed surface change"
                     if (cloud is not None and cloud >= 40) else None),
        })
    prov = Provenance(
        source=S2_SOURCE, value_kind=ValueKind.MEASURED,
        acquisition_time=latest_time, spatial_resolution_m=10,
        temporal_resolution_s=5 * 86400,
        notes=f"{len(scenes)} Sentinel-2 scenes within {radius_km} km / {days} d",
    )
    return Observation(value=scenes, unit="scenes",
                       confidence=Confidence.HIGH if scenes else Confidence.LOW,
                       provenance=prov)


async def latest_sentinel1_scenes(lat: float, lon: float, radius_km: float = 30,
                                  days: int = 30) -> Observation[List[dict]]:
    """Return metadata for the most recent Sentinel-1 SAR scenes. SAR sees
    through cloud, so it is the primary all-weather change source."""
    if not settings.copernicus_configured():
        return _unknown(
            S1_SOURCE,
            "Copernicus credentials not configured -> Sentinel-1 unavailable "
            "(no data invented). Set COPERNICUS_CLIENT_ID/SECRET.",
        )
    features = await _stac_search("SENTINEL-1", lat, lon, radius_km, days)
    if features is None:
        return _unknown(S1_SOURCE, "Copernicus STAC query failed; result unknown.")
    scenes = []
    latest_time = None
    for f in features:
        props = f.get("properties", {})
        acq = props.get("datetime")
        acq_dt = datetime.fromisoformat(acq.replace("Z", "+00:00")) if acq else None
        latest_time = latest_time or acq_dt
        scenes.append({
            "scene_id": f.get("id"),
            "acquisition_time": acq,
            "orbit_direction": props.get("orbitDirection") or props.get("sat:orbit_state"),
            "polarizations": props.get("polarization") or props.get("sar:polarizations"),
            "resolution_m": 10,
            "note": ("SAR intensity change is NOT ground movement without InSAR "
                     "processing + validation"),
        })
    prov = Provenance(
        source=S1_SOURCE, value_kind=ValueKind.MEASURED,
        acquisition_time=latest_time, spatial_resolution_m=10,
        temporal_resolution_s=6 * 86400,
        notes=f"{len(scenes)} Sentinel-1 scenes within {radius_km} km / {days} d",
    )
    return Observation(value=scenes, unit="scenes",
                       confidence=Confidence.HIGH if scenes else Confidence.LOW,
                       provenance=prov)
