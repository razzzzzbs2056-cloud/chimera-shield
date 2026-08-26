"""
Report assembly -- the evidence-fusion pipeline.

Fuses real connector data through the engines into a single glacier report that
carries provenance, freshness and confidence on every card. Missing inputs stay
UNKNOWN and are excluded from derived scores (never invented).

Pipeline (mirrors the spec's final product order):
  Satellite -> Weather+Temperature -> Change -> Lake -> Slope -> Earthquake ->
  Hydrology -> AI Fusion -> Risk
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from ..core import Confidence, PROFILES, humanize_age, may_call_live
from ..connectors import copernicus_sentinel as sat
from ..connectors import nasa_lst
from ..connectors import open_meteo as om
from ..connectors import usgs_earthquakes as quakes
from ..engines import (
    ai_analyst,
    elevation,
    freeze_thaw,
    freezing_level,
    pdd,
    precipitation,
    risk,
    temperature,
)
from ..engines.change_detection import choose_comparable
from .glaciers import ReferenceGlacier, downstream_of


def _daily_means_from_hourly(times: List[datetime], temps: List[Optional[float]]
                             ) -> List[Optional[float]]:
    buckets: dict = {}
    counts: dict = {}
    for t, v in zip(times, temps):
        if v is None:
            continue
        key = t.date().isoformat()
        buckets[key] = buckets.get(key, 0.0) + v
        counts[key] = counts.get(key, 0) + 1
    return [round(buckets[k] / counts[k], 3) for k in sorted(buckets)]


def _freshness_card(profile_key: str, acq_time: Optional[datetime]) -> dict:
    prof = PROFILES[profile_key]
    age = ((datetime.now(timezone.utc) - acq_time).total_seconds()
           if acq_time else None)
    return prof.describe(age)


async def _climatology(glacier: ReferenceGlacier, now: datetime) -> dict:
    """Best-effort ERA5 climatology: normal air temp for the current day-of-year
    and a 30-day baseline PDD, both elevation-adjusted to the glacier. Returns
    UNKNOWNs on failure rather than fabricated normals."""
    out = {"normal_air_temp_c": None, "baseline_30d_pdd": None,
           "years": None, "note": None}
    end_year = now.year - 1
    start_year = end_year - 5
    daily = await om.fetch_climatology_daily(
        glacier.latitude, glacier.longitude, start_year, end_year)
    if not daily or not daily.get("time"):
        out["note"] = "ERA5 climatology unavailable; anomalies UNKNOWN (not invented)."
        return out
    grid_elev = None  # archive response doesn't expose elevation via this helper
    times = [datetime.fromisoformat(d).replace(tzinfo=timezone.utc)
             for d in daily["time"]]
    means = daily.get("temperature_2m_mean", [])
    doy = now.timetuple().tm_yday

    # Same-window-of-year mean (+/- 7 days across years).
    window = [m for t, m in zip(times, means)
              if m is not None and abs(t.timetuple().tm_yday - doy) <= 7]
    normal_grid = sum(window) / len(window) if window else None

    # Elevation-adjust normal from ERA5 grid elevation to glacier median.
    # We approximate ERA5-Land grid elevation with the DEM at the point when the
    # archive elevation isn't returned; adjustment magnitude is reported by the
    # elevation engine and downgrades confidence accordingly.
    if normal_grid is not None and glacier.median_elevation_m is not None:
        adj = elevation.adjust_temperature(
            normal_grid, grid_elev if grid_elev is not None else glacier.terminus_elevation_m,
            glacier.median_elevation_m)
        out["normal_air_temp_c"] = adj.adjusted_temp_c
    # 30-day baseline PDD across years (mean of yearly 30-day-window PDD sums).
    yearly_pdd: dict = {}
    for t, m in zip(times, means):
        if m is None:
            continue
        if abs(t.timetuple().tm_yday - doy) <= 15:  # ~30-day window centred on DOY
            yearly_pdd.setdefault(t.year, []).append(max(m, 0.0))
    if yearly_pdd:
        sums = [sum(v) for v in yearly_pdd.values() if v]
        out["baseline_30d_pdd"] = round(sum(sums) / len(sums), 2) if sums else None
    out["years"] = f"{start_year}-{end_year}"
    return out


async def assemble_glacier_report(glacier: ReferenceGlacier,
                                  radius_km: Optional[float] = None) -> dict:
    now = datetime.now(timezone.utc)
    radius_km = radius_km or glacier.monitor_radius_km
    report: dict = {
        "generated_at": now.isoformat(),
        "glacier": {
            "id": glacier.id,
            "name": glacier.name,
            "latitude": glacier.latitude,
            "longitude": glacier.longitude,
            "terminus_elevation_m": glacier.terminus_elevation_m,
            "median_elevation_m": glacier.median_elevation_m,
            "headwall_elevation_m": glacier.headwall_elevation_m,
            "catchment": glacier.catchment,
            "river_system": glacier.river_system,
            "monitor_radius_km": radius_km,
            "geometry_note": "reference geometry (approximate), not a measurement",
        },
    }

    # --- Weather + temperature (REAL model data) --------------------------
    series = await om.fetch_recent_weather(glacier.latitude, glacier.longitude, past_days=30)
    clim = await _climatology(glacier, now)
    report["climatology"] = clim

    if series is None or not series.times:
        # Weather model unreachable/unavailable. Keep a STABLE contract: every
        # derived card is present but explicitly UNKNOWN. We never invent values.
        _unknown_note = ("weather model unavailable (source unreachable or "
                         "blocked); UNKNOWN, not invented")
        report["weather_available"] = False
        report["temperature"] = {"current_glacier_air_temp_c": None,
                                 "anomaly_c": None, "note": _unknown_note}
        report["pdd"] = {"pdd_24h": None, "pdd_7d_cumulative": None,
                         "pdd_30d_cumulative": None, "anomaly_30d_pct": None,
                         "note": _unknown_note}
        report["freeze_thaw"] = {"freeze_thaw_cycles_7d": None,
                                 "consecutive_warm_nights": None,
                                 "note": _unknown_note}
        report["freezing_level"] = {"current_m": None, "note": _unknown_note}
        report["precipitation"] = {"precip_24h_mm": None, "precip_3d_mm": None,
                                   "precip_7d_mm": None, "note": _unknown_note}
        adjusted_temps: List[Optional[float]] = []
        times: List[datetime] = []
    else:
        report["weather_available"] = True
        times = series.times
        raw_temps = series.var("temperature_2m")
        model_elev = series.model_elevation_m
        # Elevation-adjust the whole air-temperature series to glacier median.
        adjusted_temps = []
        for rt in raw_temps:
            adj = elevation.adjust_temperature(
                rt, model_elev, glacier.median_elevation_m)
            adjusted_temps.append(adj.adjusted_temp_c)

        temp_intel = temperature.compute(
            times, adjusted_temps, clim.get("normal_air_temp_c"))
        # Record the elevation-correction metadata for the current hour.
        latest_adj = elevation.adjust_temperature(
            raw_temps[-1] if raw_temps else None, model_elev,
            glacier.median_elevation_m)
        report["temperature"] = {
            **temp_intel.to_dict(),
            "elevation_correction": latest_adj.to_dict(),
            "freshness": _freshness_card("weather_hourly", times[-1]),
        }

        # PDD
        daily_means = _daily_means_from_hourly(times, adjusted_temps)
        pdd_res = pdd.compute(daily_means, seasonal_means_c=daily_means,
                              baseline_30d_pdd=clim.get("baseline_30d_pdd"))
        report["pdd"] = pdd_res.to_dict()

        # Freeze-thaw
        report["freeze_thaw"] = freeze_thaw.compute(times, adjusted_temps).to_dict()

        # Freezing level
        fl = freezing_level.compute(
            times, series.var("freezing_level_height"),
            glacier.terminus_elevation_m, glacier.median_elevation_m,
            glacier.headwall_elevation_m)
        report["freezing_level"] = fl.to_dict()

        # Precipitation & snow
        report["precipitation"] = precipitation.compute(
            times, series.var("precipitation"), series.var("rain"),
            series.var("snowfall"), adjusted_temps).to_dict()

    # --- Surface temperature (separate from air temp; UNKNOWN w/o creds) --
    st = await nasa_lst.fetch_surface_temperature(glacier.latitude, glacier.longitude)
    report["surface_temperature"] = {
        "value": st.value, "unit": st.unit, "confidence": st.confidence.value,
        "kind": st.provenance.value_kind.value,
        "note": st.provenance.notes,
        "freshness": _freshness_card("lst", st.provenance.acquisition_time),
    }

    # --- Earthquakes (REAL, near-real-time) -------------------------------
    eq_obs = await quakes.fetch_earthquakes(
        glacier.latitude, glacier.longitude, radius_km=max(radius_km, 200), days=30)
    eq_list = eq_obs.value or []
    latest_eq = eq_list[0] if eq_list else None
    assoc = "insufficient evidence"
    if latest_eq:
        assoc = quakes.classify_association(
            latest_eq.get("distance_km"), latest_eq.get("magnitude"),
            latest_eq.get("depth_km"))
    report["earthquakes"] = {
        "count_30d": len(eq_list),
        "latest": latest_eq,
        "association": assoc,
        "events": eq_list[:10],
        "confidence": eq_obs.confidence.value,
        "freshness": _freshness_card("earthquake", eq_obs.provenance.acquisition_time),
        "caveat": ("Association only. The platform never asserts an earthquake "
                   "caused an avalanche or landslide."),
    }

    # --- Satellite (REAL metadata w/ creds; UNKNOWN otherwise) ------------
    s1 = await sat.latest_sentinel1_scenes(glacier.latitude, glacier.longitude, min(radius_km, 40))
    s2 = await sat.latest_sentinel2_scenes(glacier.latitude, glacier.longitude, min(radius_km, 40))
    s1_scenes = s1.value or []
    s2_scenes = s2.value or []
    change_pair = choose_comparable(s2_scenes, "optical") if s2_scenes else None
    report["satellite"] = {
        "sentinel1": {
            "available": bool(s1_scenes),
            "count": len(s1_scenes),
            "latest_scene_time": s1_scenes[0]["acquisition_time"] if s1_scenes else None,
            "confidence": s1.confidence.value,
            "note": s1.provenance.notes,
            "freshness": _freshness_card("sentinel1", s1.provenance.acquisition_time),
        },
        "sentinel2": {
            "available": bool(s2_scenes),
            "count": len(s2_scenes),
            "latest_scene_time": s2_scenes[0]["acquisition_time"] if s2_scenes else None,
            "latest_cloud_cover_pct": s2_scenes[0].get("cloud_cover_pct") if s2_scenes else None,
            "confidence": s2.confidence.value,
            "change_pair_valid": change_pair.valid_for_change if change_pair else None,
            "change_note": change_pair.reason if change_pair else None,
            "freshness": _freshness_card("sentinel2", s2.provenance.acquisition_time),
        },
    }

    # --- Lake / velocity: require satellite processing; honest UNKNOWN ----
    report["lake"] = {
        "available": False,
        "latest_area_km2": None,
        "change_7d_pct": None,
        "change_30d_pct": None,
        "confidence": Confidence.UNKNOWN.value,
        "note": ("Automated glacial-lake delineation requires Sentinel-2/-1 "
                 "processing (worker). UNKNOWN until configured; no area invented."),
    }
    report["velocity"] = {
        "available": False,
        "confidence": Confidence.UNKNOWN.value,
        "note": ("Surface velocity requires feature-tracking on repeat imagery. "
                 "UNKNOWN until configured; no velocity invented."),
    }

    # --- Downstream exposure ---------------------------------------------
    report["downstream"] = [
        {"id": i.id, "name": i.name, "kind": i.kind,
         "latitude": i.latitude, "longitude": i.longitude,
         "elevation_m": i.elevation_m}
        for i in downstream_of(glacier)
    ]

    # --- Risk engine ------------------------------------------------------
    report["risk"] = _build_risk(report).to_dict()

    # --- AI analyst -------------------------------------------------------
    report["analyst"] = ai_analyst.build_assessment(report)
    return report


def _build_risk(report: dict) -> risk.GlacierRisk:
    """Assemble transparent risk components from computed evidence. Only real,
    available values become factors; missing ones are simply absent (their
    weight renormalises) so risk is never inflated or faked."""
    temp = report.get("temperature", {})
    pdd_d = report.get("pdd", {})
    fl = report.get("freezing_level", {})
    ft = report.get("freeze_thaw", {})
    eq = report.get("earthquakes", {})
    lake = report.get("lake", {})
    precip = report.get("precipitation", {})

    def conf(name: str, default=Confidence.MEDIUM) -> Confidence:
        v = report.get(name, {}).get("confidence")
        try:
            return Confidence(v) if v else default
        except ValueError:
            return default

    # --- thermal stress ---
    thermal = risk.score_component("thermal_stress", [
        risk.Factor("temperature_anomaly_c", temp.get("anomaly_c"), "degC",
                    "Open-Meteo/ERA5 (elevation-adjusted)", 0.4,
                    Confidence.MEDIUM, None,
                    normalize=lambda v: risk.linear_map(v, 0, 6)),
        risk.Factor("pdd_30d_anomaly_pct", pdd_d.get("anomaly_30d_pct"), "%",
                    "Open-Meteo/ERA5", 0.35, Confidence.MEDIUM, None,
                    normalize=lambda v: risk.linear_map(v, 0, 80)),
        risk.Factor("freezing_level_above_median_hours_7d",
                    fl.get("hours_above_median_7d"), "h", "Open-Meteo", 0.25,
                    Confidence.MEDIUM, None,
                    normalize=lambda v: risk.linear_map(v, 0, 168)),
    ])

    # --- rock-slope instability ---
    rock = risk.score_component("rock_slope_instability", [
        risk.Factor("freeze_thaw_cycles_7d", ft.get("freeze_thaw_cycles_7d"),
                    "cycles", "Open-Meteo (derived)", 0.4, Confidence.MEDIUM, None,
                    normalize=lambda v: risk.linear_map(v, 0, 7)),
        risk.Factor("consecutive_warm_nights", ft.get("consecutive_warm_nights"),
                    "nights", "Open-Meteo (derived)", 0.3, Confidence.MEDIUM, None,
                    normalize=lambda v: risk.linear_map(v, 0, 10)),
        risk.Factor("precip_7d_mm", precip.get("precip_7d_mm"), "mm",
                    "Open-Meteo", 0.3, Confidence.MEDIUM, None,
                    normalize=lambda v: risk.linear_map(v, 0, 150)),
    ])

    # --- seismic trigger ---
    latest_q = eq.get("latest") or {}
    seismic = risk.score_component("seismic_trigger", [
        risk.Factor("nearest_quake_magnitude", latest_q.get("magnitude"), "Mw",
                    "USGS", 0.6,
                    Confidence(eq.get("confidence", "MEDIUM")) if eq.get("confidence") in
                    ("LOW", "MEDIUM", "HIGH", "UNKNOWN") else Confidence.MEDIUM,
                    None, normalize=lambda v: risk.linear_map(v, 3.5, 6.5)),
        risk.Factor("nearest_quake_proximity", latest_q.get("distance_km"), "km",
                    "USGS", 0.4, Confidence.HIGH, None,
                    # closer = higher risk -> invert
                    normalize=lambda v: risk.linear_map(v, 200, 10)),
    ])

    # --- hydrological stress ---
    hydro = risk.score_component("hydrological_stress", [
        risk.Factor("precip_24h_mm", precip.get("precip_24h_mm"), "mm",
                    "Open-Meteo", 0.5, Confidence.MEDIUM, None,
                    normalize=lambda v: risk.linear_map(v, 0, 60)),
        risk.Factor("precip_3d_mm", precip.get("precip_3d_mm"), "mm",
                    "Open-Meteo", 0.5, Confidence.MEDIUM, None,
                    normalize=lambda v: risk.linear_map(v, 0, 120)),
    ])

    # --- lake instability (UNKNOWN until satellite processing configured) ---
    lake_comp = risk.score_component("lake_instability", [
        risk.Factor("lake_change_30d_pct", lake.get("change_30d_pct"), "%",
                    "Sentinel-2 (worker)", 1.0, Confidence.UNKNOWN, None,
                    normalize=lambda v: risk.linear_map(v, 0, 25)),
    ])

    # --- ice instability (UNKNOWN until velocity/SAR processing configured) ---
    ice_comp = risk.score_component("ice_instability", [
        risk.Factor("velocity_accel_pct", report.get("velocity", {}).get("accel_pct"),
                    "%", "Feature tracking (worker)", 1.0, Confidence.UNKNOWN, None,
                    normalize=lambda v: risk.linear_map(v, 0, 30)),
    ])

    return risk.aggregate([thermal, lake_comp, ice_comp, rock, seismic, hydro])
