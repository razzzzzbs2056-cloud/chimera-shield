import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "seismic"))
from validate_return import validate  # noqa: E402
from verify_compare import compare  # noqa: E402
from pareto import pareto  # noqa: E402

H = ["INPUTS USED", "ASSUMPTIONS", "METHOD", "CALCULATIONS", "RESULTS", "CODE / STANDARD", "UNCERTAINTIES", "FAILED CHECKS", "RECOMMENDATIONS", "REQUIRED HUMAN REVIEW"]


def doc(results="Value 1.0", order=H, skip=None):
    return "\n".join(f"## {h}\n{results if h == 'RESULTS' else 'None'}\n" for h in order if h != skip)


def test_valid_and_invalid_returns():
    assert validate(doc()) == []
    assert any("missing" in e for e in validate(doc(skip="FAILED CHECKS")))
    assert any("order" in e for e in validate(doc(order=H[::-1])))
    assert any("empty" in e for e in validate(doc().replace("## METHOD\nNone", "## METHOD\n")))
    assert any("earthquake proof" in e for e in validate(doc("The building is earthquake proof.")))


def test_fire_verdict_rules():
    assert validate(doc("Egress: PASS. Smoke: PROFESSIONAL REVIEW REQUIRED."), fire=True) == []
    assert any("verdict" in e for e in validate(doc("Exits look adequate."), fire=True))
    assert any("hedged" in e for e in validate(doc("PASS, probably safe overall."), fire=True))


def test_comparator_proceed_and_investigate():
    assert compare({"T": 1.00}, {"T": 1.04})["decision"] == "PROCEED"
    assert compare({"T": 1.00}, {"T": 1.20})["decision"] == "INVESTIGATE"
    assert compare({"T": 1.00}, {"T": 1.20}, {"T": {"rel": 0.25}})["decision"] == "PROCEED"
    assert compare({"T": 1.0, "W": 5.0}, {"T": 1.0})["decision"] == "INVESTIGATE"   # a check B did not do is not agreement


def test_pareto_front():
    opts = {"A cheapest": {"cost": 10, "carbon": 500, "daylight": 0.3}, "B low carbon": {"cost": 14, "carbon": 300, "daylight": 0.4},
            "C dominated": {"cost": 15, "carbon": 520, "daylight": 0.3}, "D daylight": {"cost": 16, "carbon": 450, "daylight": 0.7}}
    r = pareto(opts, {"cost": "min", "carbon": "min", "daylight": "max"})
    assert set(r["front"]) == {"A cheapest", "B low carbon", "D daylight"} and r["dominated"] == ["C dominated"]
    assert r["best_per_objective"] == {"cost": "A cheapest", "carbon": "B low carbon", "daylight": "D daylight"}


def test_seismic_pipeline_returns_valid_format_and_proceeds():
    pytest.importorskip("numpy")
    import pipeline
    res = pipeline.run()
    assert res["errors"] == []
    assert res["compare"]["decision"] == "PROCEED"
    assert abs(res["a"]["T1_s"] - res["b"]["T1_s"]) / res["a"]["T1_s"] < 0.10
