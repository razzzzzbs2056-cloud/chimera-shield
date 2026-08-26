"""Unit tests for the pure computation engines and scientific-integrity core.

These run without network access -- they validate the maths and the integrity
guarantees (no fabrication, correct labelling, confidence propagation)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.core import (
    Confidence,
    DataSource,
    Observation,
    Provenance,
    ValueKind,
    kelvin_to_celsius,
    qc_value,
)
from app.core.freshness import classify, humanize_age, may_call_live
from app.engines import elevation, freeze_thaw, pdd, precipitation, risk, temperature


UTC = timezone.utc
SRC = DataSource(id="t", name="test", provider="test")


def _prov(kind=ValueKind.MODEL, acq=None):
    return Provenance(source=SRC, value_kind=kind, acquisition_time=acq)


# --- core: units -----------------------------------------------------------
def test_kelvin_to_celsius():
    assert kelvin_to_celsius(273.15) == 0.0
    assert kelvin_to_celsius(None) is None


def test_qc_rejects_impossible():
    assert qc_value("air_temp_c", 15.0) == 15.0
    assert qc_value("air_temp_c", 500.0) is None   # rejected, not clamped
    assert qc_value("air_temp_c", None) is None


# --- core: confidence propagation -----------------------------------------
def test_confidence_weakest_and_downgrade():
    assert Confidence.weakest(Confidence.HIGH, Confidence.LOW) is Confidence.LOW
    assert Confidence.HIGH.downgrade(2) is Confidence.LOW
    assert Confidence.LOW.downgrade(5) is Confidence.UNKNOWN


# --- core: provenance & freshness -----------------------------------------
def test_forecast_has_no_age():
    p = _prov(ValueKind.FORECAST, acq=datetime.now(UTC) - timedelta(hours=5))
    assert p.age_seconds() is None   # a forecast has no 'age'


def test_never_live_when_not_near_real_time():
    # even 1-second-old data isn't 'live' if the source isn't near-real-time
    assert may_call_live(1, source_is_near_real_time=False) is False
    assert may_call_live(1, source_is_near_real_time=True) is True
    assert may_call_live(3600, source_is_near_real_time=True) is False


def test_freshness_classify_and_human():
    assert classify(60, 3600, 86400).value == "FRESH"
    assert classify(7200, 3600, 86400).value == "DELAYED"
    assert classify(200000, 3600, 86400).value == "STALE"
    assert classify(None, 1, 2).value == "UNKNOWN"
    assert "minutes ago" in humanize_age(600)
    assert humanize_age(None) == "unknown"


def test_unknown_observation_is_none_not_zero():
    obs = Observation.unknown(_prov(), unit="degC")
    assert obs.value is None
    assert obs.confidence is Confidence.UNKNOWN
    assert obs.is_known() is False


# --- elevation lapse-rate --------------------------------------------------
def test_elevation_adjustment_cools_with_height():
    adj = elevation.adjust_temperature(10.0, 2000.0, 5000.0)  # 3000 m higher
    assert adj.adjusted_temp_c == pytest.approx(10.0 - 3000 * 0.0065, abs=1e-6)
    # large correction downgrades confidence
    assert adj.confidence is Confidence.MEDIUM.downgrade(2)


def test_elevation_adjustment_unknown_on_missing_input():
    adj = elevation.adjust_temperature(None, 2000.0, 5000.0)
    assert adj.adjusted_temp_c is None
    assert adj.confidence is Confidence.UNKNOWN


# --- PDD -------------------------------------------------------------------
def test_pdd_only_positive():
    means = [-5.0, 2.0, 0.0, 3.5, -1.0]
    res = pdd.compute(means, baseline_30d_pdd=4.0)
    assert res.pdd_24h == 0.0            # last day was -1.0
    assert res.pdd_30d == pytest.approx(2.0 + 3.5)
    assert res.anomaly_30d_pct == pytest.approx((5.5 - 4.0) / 4.0 * 100, abs=0.1)


def test_pdd_missing_days_not_invented():
    assert pdd.cumulative_pdd([None, None]) is None
    assert pdd.coverage([1.0, None, 2.0, None]) == 0.5


# --- freeze-thaw -----------------------------------------------------------
def test_freeze_thaw_counts_cycles():
    base = datetime(2026, 1, 1, tzinfo=UTC)
    times, temps = [], []
    # two days each swinging +3 (noon) / -3 (midnight)
    for d in range(2):
        for h in range(24):
            times.append(base + timedelta(days=d, hours=h))
            temps.append(3.0 if 9 <= h <= 15 else -3.0)
    res = freeze_thaw.compute(times, temps)
    assert res.cycles_last_7d == 2
    assert res.consecutive_warm_nights == 0


# --- precipitation phase ---------------------------------------------------
def test_precip_phase_uncertain_near_freezing():
    base = datetime(2026, 6, 1, tzinfo=UTC)
    times = [base + timedelta(hours=h) for h in range(24)]
    precip = [0.0] * 23 + [2.0]
    temps = [5.0] * 23 + [0.5]     # last hour near freezing with precip
    res = precipitation.compute(times, precip, [0.0]*24, [0.0]*24, temps)
    assert res.phase_uncertain is True
    assert res.precip_24h_mm == pytest.approx(2.0)


# --- temperature intelligence ---------------------------------------------
def test_temperature_anomaly():
    base = datetime(2026, 6, 1, tzinfo=UTC)
    times = [base + timedelta(hours=h) for h in range(48)]
    temps = [(-2.0 + 0.05 * h) for h in range(48)]  # warming trend
    res = temperature.compute(times, temps, climatological_normal_c=-5.0)
    assert res.current_c == pytest.approx(temps[-1])
    assert res.anomaly_c == pytest.approx(temps[-1] - (-5.0), abs=1e-6)
    assert res.trend_c_per_day is not None and res.trend_c_per_day > 0


# --- risk: transparency & no-fake ------------------------------------------
def test_risk_missing_factor_renormalises_not_zero():
    factors = [
        risk.Factor("a", 50.0, "x", "src", 0.5, Confidence.HIGH, None,
                    normalize=lambda v: v),
        risk.Factor("b", None, "x", "src", 0.5, Confidence.HIGH, None,
                    normalize=lambda v: v),
    ]
    comp = risk.score_component("thermal_stress", factors)
    # only factor 'a' has data -> component score == a's subscore (50), not 25
    assert comp.score == pytest.approx(50.0)
    assert comp.coverage == pytest.approx(0.5)


def test_risk_all_missing_is_unknown_not_zero():
    factors = [risk.Factor("a", None, "x", "src", 1.0, Confidence.HIGH, None)]
    comp = risk.score_component("lake_instability", factors)
    assert comp.score is None
    assert comp.confidence is Confidence.UNKNOWN


def test_risk_levels():
    assert risk.level_for(10) == "LOW"
    assert risk.level_for(50) == "ELEVATED"
    assert risk.level_for(90) == "CRITICAL INVESTIGATION"
    assert risk.level_for(None) == "UNKNOWN"


def test_risk_aggregate_transparent_breakdown():
    thermal = risk.score_component("thermal_stress", [
        risk.Factor("t", 80.0, "x", "src", 1.0, Confidence.MEDIUM, None,
                    normalize=lambda v: v)])
    g = risk.aggregate([thermal])
    d = g.to_dict()
    assert d["glacier_risk_score_0_100"] is not None
    assert d["components"][0]["factors"][0]["contribution"] is not None
    assert "experimental" in d["disclaimer"].lower()
