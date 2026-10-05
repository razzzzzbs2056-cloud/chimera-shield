"""Tests for architecture/tower/calcs/fire_tower.py (Division 12, 30-storey tower egress geometry)."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tower" / "calcs"))
import fire_tower as ft  # noqa: E402


@pytest.fixture(scope="module")
def r():
    return ft.run()


def test_occupancy_hand(r):
    # bedrooms: 2x1 + 4x2 + 2x3 = 16; 1.5 per bedroom = 24; x29 floors = 696
    assert r["occupancy"]["bedrooms_per_floor"] == 16
    assert r["occupancy"]["base"]["per_floor"] == pytest.approx(24.0)
    assert r["occupancy"]["base"]["total"] == pytest.approx(696.0)
    assert r["occupancy"]["high"]["total"] == pytest.approx(928.0)


def test_stair_doors_and_separation(r):
    s = r["egress"]["stair_separation"]
    assert r["egress"]["stair_doors"]["stair1"] == (9.0, 9.4)
    assert r["egress"]["stair_doors"]["stair2"] == (21.0, 14.6)
    assert s["straight_line_m"] == pytest.approx(math.hypot(12.0, 5.2))
    assert s["straight_line_m"] == pytest.approx(13.1, abs=0.05)  # architects' figure
    assert s["floor_diagonal_m"] == pytest.approx(math.hypot(30, 24))
    assert s["fraction_of_diagonal"] == pytest.approx(0.3404, abs=1e-3)


def test_ring_path_between_stairs_by_hand(r):
    # centreline ring 13.5 x 9.5 (perimeter 46); stair door projections (8.25,9.4),(21.75,14.6)
    # S route: 2.15 + 13.5 + 7.35 = 23.0 ; N route identical by symmetry; + 2 x 0.75 door offsets
    s = r["egress"]["stair_separation"]
    assert r["egress"]["ring"]["perimeter_m"] == pytest.approx(46.0)
    assert s["ring_path_short_m"] == pytest.approx(24.5)
    assert s["ring_path_long_m"] == pytest.approx(24.5)


def test_apartment_a04_by_hand(r):
    a = {x["name"]: x for x in r["egress"]["apartments"]}["A04 N"]
    assert a["door"] == pytest.approx((15.0, 17.5))
    assert a["inside_straight_m"] == pytest.approx(math.hypot(7.5, 6.5))
    # door offset 0.75 to (15,16.75); to W route: 6.75 along N, 7.35 down W-edge... compute independently
    to_xw = 15.0 - 8.25
    west = to_xw + (16.75 - 9.4) + 0.75 + 0.75
    assert a["routes"]["stair1"]["short"] == pytest.approx(west)
    assert a["corridor_to_nearest_stair_door_m"] == pytest.approx(10.4)


def test_all_eight_apartments_and_symmetry(r):
    apts = r["egress"]["apartments"]
    assert len(apts) == 8
    d = {x["name"]: x for x in apts}
    assert d["A01 SW corner"]["total_to_nearest_stair_m"] == pytest.approx(d["A05 NE corner"]["total_to_nearest_stair_m"])
    assert r["egress"]["max_total_to_nearest_stair_m"] == pytest.approx(23.30, abs=0.01)
    assert r["egress"]["max_total_to_other_stair_m"] == pytest.approx(35.91, abs=0.01)
    for a in apts:
        assert a["dead_end_m"] == 0.0
        assert a["total_to_other_stair_m"] >= a["total_to_nearest_stair_m"]


def test_ring_is_continuous_and_doors_touch_corridors():
    opt, floor = ft.load()
    corr = [x for x in floor if x["type"] == "corridor"]
    names = {c["name"]: c for c in corr}
    # S-W, W-N, N-E, E-S corridors share boundaries -> ring is closed
    pairs = [("Corridor S", "Corridor W"), ("Corridor W", "Corridor N"),
             ("Corridor N", "Corridor E"), ("Corridor E", "Corridor S")]
    for a, b in pairs:
        assert ft.shared_edge(names[a], names[b]) is not None
    for x in floor:
        if x["type"] in ft.BEDROOMS:
            assert ft.apartment_door(x, corr) is not None


def test_stair_flow_hand(r):
    row = r["stair_flow"]["base"]["rows"][0]  # 1.0 m
    assert row["t_both_min"] == pytest.approx(348 / 1.0 / 60)
    assert row["t_one_lost_min"] == pytest.approx(696 / 60)
