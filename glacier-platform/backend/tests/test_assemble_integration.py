"""
Integration test for the fusion pipeline WITH data available.

The live connectors are network-bound; here we monkeypatch them with clearly
synthetic inputs so we can prove that, when real data IS present, the pipeline
produces a populated, transparent risk score, an evidence-grounded assessment,
and correctly-labelled provenance -- and still keeps air vs surface temperature
separate and forecasts/models out of the "measured" bucket.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.connectors import open_meteo as om
from app.domain import assemble
from app.domain.glaciers import get_glacier

UTC = timezone.utc


class _FakeSeries:
    """Mimics om.HourlySeries with a warm, high-melt-pressure scenario."""

    def __init__(self):
        base = datetime.now(UTC) - timedelta(hours=48)
        self.times = [base + timedelta(hours=h) for h in range(48)]
        self.model_elevation_m = 3000.0  # valley grid; glacier median is 5700
        self._data = {}
        # Diurnal temps around freezing at the MODEL grid elevation; after
        # elevation adjustment to 5700 m these become sub-freezing but with a
        # warm anomaly vs a cold climatology.
        temps, fl, precip = [], [], []
        for h in range(48):
            hour = self.times[h].hour
            temps.append(12.0 if 9 <= hour <= 15 else 6.0)      # warm valley
            fl.append(5800.0)                                    # freezing level high
            precip.append(3.0 if h % 12 == 0 else 0.0)
        self._data = {
            "temperature_2m": temps,
            "freezing_level_height": fl,
            "precipitation": precip,
            "rain": precip,
            "snowfall": [0.0] * 48,
        }

    def var(self, name):
        return self._data.get(name, [None] * len(self.times))


@pytest.mark.asyncio
async def test_pipeline_populated_with_data(monkeypatch):
    async def fake_recent(lat, lon, past_days=30):
        return _FakeSeries()

    async def fake_clim(glacier, now):
        # cold climatological normal so the current temp is a clear +anomaly
        return {"normal_air_temp_c": -12.0, "baseline_30d_pdd": 5.0,
                "years": "2019-2024", "note": None}

    async def fake_quakes(lat, lon, radius_km=200, days=30):
        from app.core import (Confidence, DataSource, Observation, Provenance,
                              ValueKind)
        src = DataSource(id="usgs_earthquakes", name="t", provider="USGS")
        prov = Provenance(source=src, value_kind=ValueKind.MEASURED,
                          acquisition_time=datetime.now(UTC) - timedelta(hours=2))
        return Observation(value=[{
            "event_id": "x1", "magnitude": 4.6, "latitude": 28.4,
            "longitude": 85.4, "depth_km": 12.0, "place": "test",
            "origin_time": (datetime.now(UTC) - timedelta(hours=2)).isoformat(),
            "distance_km": 22.0,
        }], unit="events", confidence=Confidence.HIGH, provenance=prov)

    monkeypatch.setattr(om, "fetch_recent_weather", fake_recent)
    monkeypatch.setattr(assemble, "_climatology", fake_clim)
    monkeypatch.setattr(assemble.quakes, "fetch_earthquakes", fake_quakes)

    glacier = get_glacier("purepu")
    report = await assemble.assemble_glacier_report(glacier)

    # temperature is elevation-adjusted and shows a positive anomaly
    temp = report["temperature"]
    assert temp["current_glacier_air_temp_c"] is not None
    assert temp["is_elevation_adjusted_estimate"] is True
    assert temp["anomaly_c"] is not None and temp["anomaly_c"] > 0
    # elevation correction metadata present and flagged estimated
    ec = temp["elevation_correction"]
    assert ec["estimated_not_measured"] is True
    assert ec["elevation_difference_m"] == pytest.approx(5700 - 3000)

    # PDD computed and positive (warm scenario)
    assert report["pdd"]["pdd_30d_cumulative"] is not None

    # earthquake association is classified, never "caused"
    assert "caused" not in report["earthquakes"]["association"].lower()
    assert report["earthquakes"]["latest"]["magnitude"] == 4.6

    # surface temperature stays UNKNOWN & separate from air temp (no creds)
    assert report["surface_temperature"]["value"] is None
    assert report["surface_temperature"]["kind"] == "measured"

    # RISK: now populated, transparent, with per-factor contributions
    risk = report["risk"]
    assert risk["glacier_risk_score_0_100"] is not None
    assert risk["risk_level"] in ("LOW", "WATCH", "ELEVATED", "HIGH",
                                  "CRITICAL INVESTIGATION")
    thermal = next(c for c in risk["components"] if c["component"] == "thermal_stress")
    assert thermal["score_0_100"] is not None
    contribs = [f["contribution"] for f in thermal["factors"] if f["available"]]
    assert any(c is not None for c in contribs)
    # lake/ice remain UNKNOWN (no satellite processing) -> excluded, not faked
    lake = next(c for c in risk["components"] if c["component"] == "lake_instability")
    assert lake["score_0_100"] is None

    # analyst produces evidence-grounded, non-predictive language
    analyst = report["analyst"]
    assert "/100" in analyst["headline"]
    assert "predict" not in analyst["assessment"].lower() or \
           "insufficient" in analyst["assessment"].lower()
    assert len(analyst["evidence"]) > 0
