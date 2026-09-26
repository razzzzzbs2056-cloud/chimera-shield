"""Scenario definitions, dependencies and compound composition."""
import copy

import pytest

from src.economic_model.projection import Path, ProjectionAssumptions
from src.geopolitical_model.exposure import load_register, validate_entry
from src.scenario_engine.engine import (Scenario, compose, dependency_order, load_scenarios, run_scenario,
                                        validate_scenario)

MANDATORY = {f"S{i:02d}" for i in range(1, 11)}


@pytest.fixture(scope="module")
def scs():
    return load_scenarios()


@pytest.fixture(scope="module")
def exposure_ids():
    return {e.id for e in load_register()}


def test_all_ten_mandatory_scenarios_present(scs):
    assert set(scs) == MANDATORY


def test_all_scenarios_valid(scs, exposure_ids):
    for s in scs.values():
        assert validate_scenario(s, exposure_ids, set(scs)) == [], s.id


def test_no_scenario_has_unevidenced_magnitudes(scs):
    for s in scs.values():
        for sh in s.shocks:
            assert sh.magnitude is None or sh.evidence or sh.illustrative


def test_scenario_dependency_order(scs):
    order = dependency_order(scs)
    assert order.index("S10") > max(order.index(c) for c in scs["S10"].components)


def test_dependency_cycle_detected(scs):
    a = copy.deepcopy(scs["S01"].raw); a["depends_on"] = ["S02"]
    b = copy.deepcopy(scs["S02"].raw); b["depends_on"] = ["S01"]
    with pytest.raises(ValueError):
        dependency_order({"S01": Scenario(a), "S02": Scenario(b)})


def test_unknown_references_rejected(scs, exposure_ids):
    raw = copy.deepcopy(scs["S01"].raw)
    raw["channels"].append("telepathy")
    raw["exposure_refs"].append("EXP-99")
    raw["audits_required"] = ["15"]
    probs = validate_scenario(Scenario(raw), exposure_ids, set(scs))
    assert any("telepathy" in p for p in probs)
    assert any("EXP-99" in p for p in probs)
    assert any("Agent 28" in p for p in probs)


def test_magnitude_without_evidence_rejected(scs, exposure_ids):
    raw = copy.deepcopy(scs["S04"].raw)
    raw["shocks"][0]["magnitude"] = -0.1
    assert any("without evidence" in p for p in validate_scenario(Scenario(raw), exposure_ids, set(scs)))


def test_pending_scenarios_are_qualitative_only(scs):
    for sid in MANDATORY:
        assert run_scenario(scs[sid], scs, None, 2070)["status"] == "QUALITATIVE_ONLY"


def _baseline():
    return ProjectionAssumptions(2025, 1000.0, 100.0, 1.0, Path(0.05), Path(0.04), Path(0.02), Path(0.01))


def _synthetic(sid, shocks, components=()):
    return Scenario({"id": sid, "title": sid, "category": "compound" if components else "geopolitical",
                     "channels": sorted({s["channel"] for s in shocks}), "components": list(components),
                     "shocks": shocks})


def _shock(i, mag, ch="aggregate_real_growth", var="real_growth", illustrative=True):
    return {"id": i, "channel": ch, "variable": var, "unit": "pp", "magnitude": mag,
            "start_offset_years": 1, "duration_years": 1, "evidence": [], "illustrative": illustrative}


def test_compound_counts_shared_shock_once():
    a = _synthetic("A", [_shock("a1", -0.02)])
    b = _synthetic("B", [_shock("b1", -0.02)])
    c = _synthetic("C", [], components=["A", "B"])
    all_ = {"A": a, "B": b, "C": c}
    comp = compose(c, all_)
    assert len(comp["shocks"]) == 1 and comp["overlaps"][0]["kind"] == "duplicate_counted_once"
    single = run_scenario(a, all_, _baseline(), 2030)
    combined = run_scenario(c, all_, _baseline(), 2030)
    assert combined["deltas"][-1]["real_gdp_pct"] == pytest.approx(single["deltas"][-1]["real_gdp_pct"])


def test_conflicting_overlap_is_not_summed():
    a = _synthetic("A", [_shock("a1", -0.02)])
    b = _synthetic("B", [_shock("b1", -0.05)])
    c = _synthetic("C", [], components=["A", "B"])
    comp = compose(c, {"A": a, "B": b, "C": c})
    assert comp["overlaps"][0]["kind"] == "conflicting_magnitudes"
    assert comp["shocks"][0].magnitude is None


def test_illustrative_shock_labelled_and_applied_consistently():
    a = _synthetic("A", [_shock("a1", -0.02)])
    r = run_scenario(a, {"A": a}, _baseline(), 2030)
    assert r["status"] == "ILLUSTRATIVE"
    assert r["deltas"][0]["real_gdp_pct"] == pytest.approx(0.0)
    assert r["deltas"][1]["real_gdp_pct"] == pytest.approx((1.03 / 1.05 - 1) * 100)
    # level effect: one year of growth 3% instead of 5% persists afterwards
    assert r["deltas"][-1]["real_gdp_pct"] == pytest.approx((1.03 / 1.05 - 1) * 100)


def test_exposure_register_valid_and_pending():
    reg = load_register()
    assert len(reg) >= 20
    for e in reg:
        assert validate_entry(e) == []
        assert e.status == "pending" and e.value is None
