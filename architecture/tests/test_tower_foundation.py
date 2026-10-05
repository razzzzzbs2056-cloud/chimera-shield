"""Tests for architecture/tower/calcs/foundation_tower.py."""
import json
import sys
from pathlib import Path

import pytest

TOWER = Path(__file__).resolve().parent.parent / "tower"
sys.path.insert(0, str(TOWER / "calcs"))
import foundation_tower as ft  # noqa: E402


@pytest.fixture(scope="module")
def r():
    return ft.run()


def test_pressure_is_load_over_area(r):
    for v in r["raft_pressures"].values():
        assert v["gross_service_kPa"] == pytest.approx(v["total_service_kN"] / v["area_m2"])
    assert ft.pressure_kPa(7200.0, 720.0) == pytest.approx(10.0)


def test_net_pressure_unloading(r):
    v = r["raft_pressures"]["tower_footprint"]
    assert v["net_after_unloading_kPa_by_gamma"]["gamma_18"] == pytest.approx(v["gross_service_kPa"] - 18 * v["founding_depth_m"])


def test_pile_table_monotonic(r):
    for key in ("all_load_tower_raft", "all_load_enlarged_raft", "core_only"):
        n = [x["n_piles"] for x in r["pile_counts_parametric"][key]]
        assert all(a > b for a, b in zip(n, n[1:]))
    for t in r["pile_counts_parametric"]["piled_raft_by_raft_share"].values():
        n = [x["n_piles"] for x in t]
        assert all(a >= b for a, b in zip(n, n[1:]))
    assert ft.piles_needed(10.0, 3.0) == 4


def test_pile_count_capacity_covers_load(r):
    P = r["pile_counts_parametric"]["total_tower_footprint_MN"]
    for x in r["pile_counts_parametric"]["all_load_tower_raft"]:
        assert x["n_piles"] * x["Pw_MN"] >= P > (x["n_piles"] - 1) * x["Pw_MN"]


def test_load_sum_consistent_with_structure():
    s = json.loads((TOWER / "data" / "structure.json").read_text())
    r = ft.run()
    L = r["loads"]
    assert L["core_G_kN"] + L["columns_G_kN"] == pytest.approx(s["gravity_totals_at_ground_kN"]["G"], rel=1e-4)
    assert L["service_GQ_kN"] == pytest.approx(s["gravity_totals_at_ground_kN"]["G"] + s["gravity_totals_at_ground_kN"]["Q"])
    assert L["factored_EC_kN"] == pytest.approx(1.35 * s["gravity_totals_at_ground_kN"]["G"] + 1.5 * s["gravity_totals_at_ground_kN"]["Q"])


def test_edge_pressure_formula():
    e = ft.edge_pressures(100000.0, 0.0, 30.0, 24.0)
    assert e["q_max"] == pytest.approx(e["q_min"])
    e = ft.edge_pressures(100000.0, 50000.0, 30.0, 24.0)
    assert (e["q_max"] + e["q_min"]) / 2 == pytest.approx(e["q_avg"])


def test_uplift_monotonic(r):
    u = [c["uplift_kN"] for c in r["uplift_parametric"]["cases"]]
    assert u == sorted(u)
