"""
API routes.

Implements the endpoints from the spec. Every endpoint returns provenance-,
freshness- and confidence-bearing data. Where a sub-resource depends on an
unconfigured connector, the response is explicit UNKNOWN rather than invented
data.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..config import settings
from ..domain import registry
from ..domain.glaciers import ReferenceGlacier
from ..engines import alerts as alerts_engine
from .schemas import AddGlacierRequest, GlacierSummary

router = APIRouter()


def _summary(g: ReferenceGlacier) -> GlacierSummary:
    return GlacierSummary(
        id=g.id, name=g.name, latitude=g.latitude, longitude=g.longitude,
        catchment=g.catchment, river_system=g.river_system,
        monitor_radius_km=g.monitor_radius_km)


@router.get("/glaciers", response_model=list[GlacierSummary], tags=["glaciers"])
async def list_glaciers():
    return [_summary(g) for g in registry.list_glaciers()]


@router.post("/glaciers", response_model=GlacierSummary, tags=["glaciers"])
async def add_glacier(body: AddGlacierRequest):
    if registry.get(body.id):
        raise HTTPException(409, f"glacier id '{body.id}' already exists")
    g = ReferenceGlacier(
        id=body.id, name=body.name, latitude=body.latitude, longitude=body.longitude,
        terminus_elevation_m=body.terminus_elevation_m,
        median_elevation_m=body.median_elevation_m,
        headwall_elevation_m=body.headwall_elevation_m,
        country=body.country, catchment=body.catchment,
        river_system=body.river_system, monitor_radius_km=body.monitor_radius_km,
        polygon=body.polygon,
        elevation_source="admin-provided",
    )
    registry.add_glacier(g)
    return _summary(g)


async def _report_or_404(glacier_id: str, radius_km: Optional[float] = None,
                         force: bool = False) -> dict:
    report = await registry.get_report(glacier_id, radius_km=radius_km, force=force)
    if report is None:
        raise HTTPException(404, f"glacier '{glacier_id}' not found")
    return report


@router.get("/glaciers/{glacier_id}", tags=["glaciers"])
async def glacier_full(glacier_id: str,
                       radius_km: Optional[float] = Query(None, gt=0, le=1000),
                       force: bool = False):
    return await _report_or_404(glacier_id, radius_km, force)


@router.get("/glaciers/{glacier_id}/temperature", tags=["glaciers"])
async def glacier_temperature(glacier_id: str):
    r = await _report_or_404(glacier_id)
    return {"temperature": r.get("temperature"), "pdd": r.get("pdd"),
            "freeze_thaw": r.get("freeze_thaw"),
            "freezing_level": r.get("freezing_level"),
            "surface_temperature": r.get("surface_temperature"),
            "climatology": r.get("climatology")}


@router.get("/glaciers/{glacier_id}/weather", tags=["glaciers"])
async def glacier_weather(glacier_id: str):
    r = await _report_or_404(glacier_id)
    return {"precipitation": r.get("precipitation"),
            "temperature": r.get("temperature"),
            "weather_available": r.get("weather_available")}


@router.get("/glaciers/{glacier_id}/satellite", tags=["glaciers"])
async def glacier_satellite(glacier_id: str):
    r = await _report_or_404(glacier_id)
    return r.get("satellite")


@router.get("/glaciers/{glacier_id}/lake", tags=["glaciers"])
async def glacier_lake(glacier_id: str):
    r = await _report_or_404(glacier_id)
    return r.get("lake")


@router.get("/glaciers/{glacier_id}/velocity", tags=["glaciers"])
async def glacier_velocity(glacier_id: str):
    r = await _report_or_404(glacier_id)
    return r.get("velocity")


@router.get("/glaciers/{glacier_id}/earthquakes", tags=["glaciers"])
async def glacier_earthquakes(glacier_id: str):
    r = await _report_or_404(glacier_id)
    return r.get("earthquakes")


@router.get("/glaciers/{glacier_id}/risk", tags=["glaciers"])
async def glacier_risk(glacier_id: str):
    r = await _report_or_404(glacier_id)
    return {"risk": r.get("risk"), "analyst": r.get("analyst")}


@router.get("/glaciers/{glacier_id}/timeline", tags=["glaciers"])
async def glacier_timeline(glacier_id: str):
    """Time-machine metadata. Full multi-year raster timelines are served by the
    tiling/worker layer; here we expose the available scene catalogue times so
    the frontend slider knows what exists (never fabricated frames)."""
    r = await _report_or_404(glacier_id)
    sat = r.get("satellite", {})
    return {
        "glacier_id": glacier_id,
        "sentinel2_latest": sat.get("sentinel2", {}).get("latest_scene_time"),
        "sentinel1_latest": sat.get("sentinel1", {}).get("latest_scene_time"),
        "note": ("Historical frames require the imagery worker + tile store. "
                 "Only real, available acquisition times are listed."),
    }


@router.get("/glaciers/{glacier_id}/alerts", tags=["alerts"])
async def glacier_alerts(glacier_id: str):
    r = await _report_or_404(glacier_id)
    return {"glacier_id": glacier_id, "alerts": alerts_engine.generate(r)}


@router.get("/alerts", tags=["alerts"])
async def all_alerts():
    out = []
    for g in registry.list_glaciers():
        r = await registry.get_report(g.id)
        if r:
            out.extend(alerts_engine.generate(r))
    out.sort(key=lambda a: a.get("severity"), reverse=True)
    return {"count": len(out), "alerts": out}


@router.get("/events", tags=["events"])
async def all_events():
    """Recent change/observation events across glaciers -- currently the most
    recent earthquake and satellite acquisitions per glacier (real). Pixel-level
    change events are emitted by the worker once configured."""
    events = []
    for g in registry.list_glaciers():
        r = await registry.get_report(g.id)
        if not r:
            continue
        eq = (r.get("earthquakes") or {}).get("latest")
        if eq:
            events.append({"glacier_id": g.id, "type": "earthquake", **eq})
    return {"count": len(events), "events": events}


@router.get("/config", tags=["meta"])
async def config_status():
    """Transparency endpoint: which connectors are live vs. UNKNOWN-only."""
    return {
        "connectors": {
            "usgs_earthquakes": {"status": "live", "auth_required": False},
            "open_meteo_weather": {"status": "live", "auth_required": False},
            "open_meteo_era5_climatology": {"status": "live", "auth_required": False},
            "open_meteo_elevation_dem": {"status": "live", "auth_required": False},
            "sentinel1_sar": {
                "status": "live" if settings.copernicus_configured() else "unconfigured (UNKNOWN)",
                "auth_required": True},
            "sentinel2_optical": {
                "status": "live" if settings.copernicus_configured() else "unconfigured (UNKNOWN)",
                "auth_required": True},
            "nasa_viirs_lst": {
                "status": "live" if settings.nasa_configured() else "unconfigured (UNKNOWN)",
                "auth_required": True},
        },
        "cesium_ion_token_present": bool(settings.cesium_ion_token),
        "principle": ("Connectors without credentials return UNKNOWN. The "
                      "platform never fabricates observations."),
    }
