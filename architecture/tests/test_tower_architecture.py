"""Tower architecture options: the typical floor tiles the 30 x 24 m plate exactly, and every metric recomputes.

Metrics are recomputed here with independent formulas (not by calling the script's helpers), then the stored
JSON is compared with a fresh run of the script so a stale data file is caught.
"""
import importlib.util
import json
import math
from itertools import combinations
from pathlib import Path

import pytest

ARCH = Path(__file__).resolve().parent.parent
TOWER = ARCH / "tower"
DATA = json.loads((TOWER / "data" / "architecture.json").read_text())
BASIS = json.loads((TOWER / "basis.json").read_text())
FLOOR = DATA["typical_floor"]
REF = DATA["options"][DATA["reference_option"]]
APT = {"1B", "2B", "3B"}
CORE = {"stair", "lift", "riser", "lobby"}
H_TYP = BASIS["geometry"]["typical_floor_to_floor_m"]


def area(r):
    return (r["x1"] - r["x0"]) * (r["y1"] - r["y0"])


def touches(a, b):
    """True if two rectangles share an edge segment of positive length."""
    ox = min(a["x1"], b["x1"]) - max(a["x0"], b["x0"])
    oy = min(a["y1"], b["y1"]) - max(a["y0"], b["y0"])
    return (abs(ox) < 1e-9 and oy > 1e-9) or (abs(oy) < 1e-9 and ox > 1e-9)


def test_reference_matches_basis():
    lx, ly = BASIS["geometry"]["floor_plate_m"]
    assert REF["plate"]["L"] == lx and REF["plate"]["W"] == ly
    assert REF["core_m"] == BASIS["geometry"]["core_m"]
    assert REF["apartments_per_floor"] == BASIS["use"]["apartments_per_floor_target"]
    assert REF["height_to_roof_slab_m"] == pytest.approx(BASIS["geometry"]["height_to_roof_slab_m"])


def test_rectangles_tile_plate_exactly():
    lx, ly = BASIS["geometry"]["floor_plate_m"]
    assert all(0 <= r["x0"] < r["x1"] <= lx and 0 <= r["y0"] < r["y1"] <= ly for r in FLOOR)
    assert sum(area(r) for r in FLOOR) == pytest.approx(lx * ly, abs=1e-9)
    for a, b in combinations(FLOOR, 2):
        ox = min(a["x1"], b["x1"]) - max(a["x0"], b["x0"])
        oy = min(a["y1"], b["y1"]) - max(a["y0"], b["y0"])
        assert not (ox > 1e-9 and oy > 1e-9), (a["name"], b["name"])
    # area sum + no overlap + inside bounds => exact tiling


def test_stated_areas_and_unique_names():
    assert len({r["name"] for r in FLOOR}) == len(FLOOR)
    for r in FLOOR:
        assert r["area_m2"] == pytest.approx(area(r), abs=0.01)


def test_apartment_count_mix_and_areas_match_reference():
    apts = [r for r in FLOOR if r["type"] in APT]
    assert len(apts) == REF["apartments_per_floor"] == 8
    for t, n in REF["mix"].items():
        assert sum(1 for r in apts if r["type"] == t) == n
    assert sum(area(r) for r in apts) == pytest.approx(REF["nsa_floor_m2"])
    assert sum(area(r) for r in FLOOR if r["type"] in CORE) == pytest.approx(REF["core_area_m2"])
    assert sum(area(r) for r in FLOOR if r["type"] == "corridor") == pytest.approx(REF["corridor_area_m2"])
    # JUDGMENT minimums for concept plans (local codes set their own)
    assert all(area(r) >= 40 and min(r["x1"] - r["x0"], r["y1"] - r["y0"]) >= 6.0 for r in apts)


def test_core_inside_12x8_and_components_present():
    core = [r for r in FLOOR if r["type"] in CORE]
    lc, wc = REF["core_m"]
    xs = [r["x0"] for r in core] + [r["x1"] for r in core]
    ys = [r["y0"] for r in core] + [r["y1"] for r in core]
    assert max(xs) - min(xs) == pytest.approx(lc) and max(ys) - min(ys) == pytest.approx(wc)
    assert sum(1 for r in core if r["type"] == "stair") == 2
    assert sum(1 for r in core if r["type"] == "lift") == REF["lifts_provided"]
    assert sum(1 for r in core if r["type"] == "riser") >= 2
    assert sum(1 for r in core if r["type"] == "lobby") == 1


def test_every_apartment_and_stair_reaches_circulation():
    circ = [r for r in FLOOR if r["type"] in ("corridor", "lobby")]
    for r in FLOOR:
        if r["type"] in APT:
            assert any(touches(r, c) for c in circ if c["type"] == "corridor"), r["name"]
        if r["type"] in ("stair", "lift"):
            assert any(touches(r, c) for c in circ), r["name"]
    lobby = next(r for r in FLOOR if r["type"] == "lobby")
    assert any(touches(lobby, c) for c in circ if c["type"] == "corridor")


def _plate(p):
    if p["shape"] == "rectangle":
        return p["L"] * p["W"], 2 * p["L"] + 2 * p["W"]
    c = p["chamfer"]
    a = p["L"] * p["W"] - 4 * (0.5 * c * c)
    per = (p["L"] - 2 * c) * 2 + (p["W"] - 2 * c) * 2 + 4 * math.hypot(c, c)
    return a, per


@pytest.mark.parametrize("name", list(DATA["options"]))
def test_option_metrics_recompute(name):
    o = DATA["options"][name]
    gfa, per = _plate(o["plate"])
    lc, wc = o["core_m"]
    w = o["corridor_width_m"]
    core = lc * wc
    ring = (lc + 2 * w) * (wc + 2 * w)
    nsa = gfa - ring
    n_res = o["storeys_above_grade"] - 1
    apts = sum(o["mix"].values())
    assert o["storeys_above_grade"] == 30
    assert o["gfa_floor_m2"] == pytest.approx(gfa, abs=0.01)
    assert o["core_area_m2"] == pytest.approx(core, abs=0.01)
    assert o["corridor_area_m2"] == pytest.approx(ring - core, abs=0.01)
    assert o["nsa_floor_m2"] == pytest.approx(nsa, abs=0.01)
    assert o["efficiency_nsa_gfa"] == pytest.approx(nsa / gfa, abs=6e-4)
    assert o["perimeter_m"] == pytest.approx(per, abs=0.01)
    assert o["facade_per_gfa"] == pytest.approx(per * H_TYP / gfa, abs=6e-4)
    depth = max(o["plate"]["L"] - lc, o["plate"]["W"] - wc) / 2
    assert o["max_depth_facade_to_core_m"] == pytest.approx(depth)
    assert o["apartment_depth_max_m"] == pytest.approx(depth - w)
    assert o["core_area_ratio"] == pytest.approx(core / gfa, abs=6e-4)
    assert o["apartments_per_floor"] == apts and o["apartments_total"] == apts * n_res
    assert o["nsa_total_m2"] == pytest.approx(nsa * n_res, abs=0.1)


def test_proxy_indices_recompute():
    w = DATA["proxy_weights"]
    ref = DATA["options"][DATA["reference_option"]]

    def raw(o, kf, key):
        gfa, per = _plate(o["plate"])
        nsa = gfa - (o["core_m"][0] + 2 * o["corridor_width_m"]) * (o["core_m"][1] + 2 * o["corridor_width_m"])
        return (o["proxy_factors"][key] * gfa + kf * per * H_TYP) / nsa

    for o in DATA["options"].values():
        c = raw(o, w["K_FC_facade_cost"], "cost_structure_factor") / raw(ref, w["K_FC_facade_cost"], "cost_structure_factor")
        e = raw(o, w["K_FE_facade_carbon"], "carbon_structure_factor") / raw(ref, w["K_FE_facade_carbon"], "carbon_structure_factor")
        assert o["cost_proxy_index"] == pytest.approx(c, abs=6e-4)
        assert o["carbon_proxy_index"] == pytest.approx(e, abs=6e-4)


def test_lift_check_recomputes_and_passes():
    la = DATA["lift_assumptions"]
    for name, lc in DATA["lift_check"].items():
        n = lc["residential_floors_served"]
        p = la["passengers_per_trip"]
        s = n * (1 - ((n - 1) / n) ** p)
        rise = BASIS["geometry"]["ground_floor_to_floor_m"] + (n - 1) * H_TYP
        rtt = 2 * rise / la["speed_m_s"] + (s + 1) * la["t_stop_s"] + 2 * p * la["t_pass_s"]
        hc = 300 * p / rtt
        demand = la["hc5_target_fraction"] * lc["population_total"]
        assert lc["round_trip_time_s"] == pytest.approx(rtt, abs=0.01)
        assert lc["lifts_required"] == max(2, math.ceil(demand / hc))
        assert lc["lifts_provided"] == DATA["options"][name]["lifts_provided"] >= lc["lifts_required"]
        assert lc["pass"] is True


def test_objective_senses_usable_by_pareto():
    import sys
    sys.path.insert(0, str(ARCH / "tools"))
    from pareto import pareto
    feasible = {k: v for k, v in DATA["options"].items()}
    res = pareto(feasible, DATA["objective_senses"])
    assert set(DATA["objective_senses"].values()) <= {"min", "max"}
    assert res["front"]  # non-empty
    assert res["best_per_objective"]["identity_score"] == "E_identity"
    assert res["best_per_objective"]["max_depth_facade_to_core_m"] == "D_best_daylight"
    assert res["best_per_objective"]["carbon_proxy_index"] == "B_lowest_carbon"
    assert res["best_per_objective"]["nsa_total_m2"] == "C_max_nsa"


def test_stored_json_matches_fresh_script_run():
    spec = importlib.util.spec_from_file_location("architecture_options", TOWER / "calcs" / "architecture_options.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fresh = json.loads(json.dumps(mod.build()))

    def same(a, b, path="root"):
        if isinstance(a, dict):
            assert set(a) == set(b), path
            for k in a:
                same(a[k], b[k], f"{path}.{k}")
        elif isinstance(a, list):
            assert len(a) == len(b), path
            for i, (x, y) in enumerate(zip(a, b)):
                same(x, y, f"{path}[{i}]")
        elif isinstance(a, bool) or isinstance(a, str) or a is None:
            assert a == b, path
        else:
            assert a == pytest.approx(b, abs=1.5e-3), path

    same(DATA, fresh)
