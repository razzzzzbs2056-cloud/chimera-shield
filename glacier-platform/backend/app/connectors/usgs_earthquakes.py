"""
USGS earthquake connector -- REAL, public, near-real-time.

Uses the USGS FDSN event web service (GeoJSON). No credentials required. This
connector produces genuine near-real-time data, so its observations MAY be
labelled live when recent (see freshness profile "earthquake").

Scientific rule: we report spatial and temporal association between an
earthquake and a monitored target. We never assert the earthquake *caused*
an avalanche or any downstream event -- that classification is left to the
risk/analyst layer, which only ever says "temporal/spatial association" or
"possible trigger / insufficient evidence".
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from ..core import (
    Confidence,
    DataSource,
    Observation,
    Provenance,
    ValueKind,
    utcnow,
)
from ..config import settings
from .base import ConnectorError, get_json, haversine_km

SOURCE = DataSource(
    id="usgs_earthquakes",
    name="USGS Earthquake Catalog (FDSN event service)",
    provider="USGS",
    authoritative=True,
    url="https://earthquake.usgs.gov/fdsnws/event/1/",
    license="public domain",
)


class EarthquakeEvent:
    def __init__(self, feature: dict, ref_lat: float, ref_lon: float):
        props = feature.get("properties", {})
        geom = feature.get("geometry", {}) or {}
        coords = geom.get("coordinates", [None, None, None])
        self.event_id: str = feature.get("id", "unknown")
        self.magnitude: Optional[float] = props.get("mag")
        self.longitude: Optional[float] = coords[0]
        self.latitude: Optional[float] = coords[1]
        self.depth_km: Optional[float] = coords[2]
        self.place: str = props.get("place", "")
        # USGS times are epoch ms UTC
        t = props.get("time")
        self.origin_time: Optional[datetime] = (
            datetime.fromtimestamp(t / 1000, tz=timezone.utc) if t else None
        )
        u = props.get("updated")
        self.update_time: Optional[datetime] = (
            datetime.fromtimestamp(u / 1000, tz=timezone.utc) if u else None
        )
        self.distance_km: Optional[float] = (
            haversine_km(ref_lat, ref_lon, self.latitude, self.longitude)
            if self.latitude is not None and self.longitude is not None
            else None
        )

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "magnitude": self.magnitude,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "depth_km": self.depth_km,
            "place": self.place,
            "origin_time": self.origin_time.isoformat() if self.origin_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None,
            "distance_km": round(self.distance_km, 1) if self.distance_km is not None else None,
        }


async def fetch_earthquakes(
    lat: float,
    lon: float,
    radius_km: float = 200.0,
    days: int = 30,
    min_magnitude: float = 2.5,
) -> Observation[List[dict]]:
    """Fetch earthquakes within ``radius_km`` of a point over the last ``days``.

    Returns an Observation whose value is a list of event dicts sorted by
    origin time (most recent first). On failure returns UNKNOWN, never [] as if
    it were a confirmed 'no earthquakes' result unless the query genuinely
    returned zero features.
    """
    start = utcnow().timestamp() - days * 86400
    starttime = datetime.fromtimestamp(start, tz=timezone.utc).isoformat()
    params = {
        "format": "geojson",
        "latitude": lat,
        "longitude": lon,
        "maxradiuskm": radius_km,
        "starttime": starttime,
        "minmagnitude": min_magnitude,
        "orderby": "time",
    }
    try:
        data = await get_json(settings.usgs_earthquake_url, params=params)
    except Exception as exc:  # network / HTTP / parse
        prov = Provenance(source=SOURCE, value_kind=ValueKind.MEASURED,
                          notes=f"fetch failed: {exc}")
        return Observation.unknown(prov, unit="events",
                                   note="USGS query failed; result unknown")

    features = data.get("features", [])
    events = [EarthquakeEvent(f, lat, lon) for f in features]
    events = [e for e in events if e.distance_km is not None]
    events.sort(key=lambda e: e.origin_time or datetime.min.replace(tzinfo=timezone.utc),
                reverse=True)

    most_recent = events[0].origin_time if events else None
    prov = Provenance(
        source=SOURCE,
        value_kind=ValueKind.MEASURED,
        acquisition_time=most_recent,       # age reflects the latest event, if any
        temporal_resolution_s=60,           # continuously updated feed
        notes=(f"{len(events)} events within {radius_km} km over {days} d, "
               f"M>={min_magnitude}"),
    )
    # Confidence: the catalog itself is authoritative & near-real-time.
    conf = Confidence.HIGH if events else Confidence.MEDIUM
    return Observation(
        value=[e.to_dict() for e in events],
        unit="events",
        confidence=conf,
        provenance=prov,
    )


def classify_association(distance_km: Optional[float], magnitude: Optional[float],
                         depth_km: Optional[float]) -> str:
    """Coarse, honest classification of an earthquake's relationship to a
    monitored slope/glacier. Deliberately conservative wording -- never
    'caused'."""
    if distance_km is None or magnitude is None:
        return "insufficient evidence"
    # Very rough shaking-relevance heuristic. Not a ground-motion model.
    if magnitude >= 5.5 and distance_km <= 50:
        return "possible trigger (strong shaking nearby) -- requires verification"
    if magnitude >= 4.0 and distance_km <= 100:
        return "spatial + temporal association -- possible influence, unverified"
    if distance_km <= 200:
        return "temporal association only"
    return "insufficient evidence"
