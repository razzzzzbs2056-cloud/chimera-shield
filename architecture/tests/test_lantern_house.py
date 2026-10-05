"""Plan integrity for the 3-storey Lantern House: each level tiles the 12 x 10 m footprint; cores stack."""
import re
from itertools import combinations
from pathlib import Path

import pytest

PAGE = (Path(__file__).resolve().parent.parent / "house" / "lantern-house-3d.html").read_text()
block = PAGE.split("PLAN-START")[1].split("PLAN-END")[0]
ROOMS = [dict(L=int(m.group(1)), name=m.group(2), kind=m.group(3), x0=float(m.group(4)), y0=float(m.group(5)), x1=float(m.group(6)), y1=float(m.group(7)))
         for m in re.finditer(r"L: (\d), name: '([^']+)', kind: '(\w+)', x0: ([\d.]+), y0: ([\d.]+), x1: ([\d.]+), y1: ([\d.]+)", block)]
area = lambda r: (r["x1"] - r["x0"]) * (r["y1"] - r["y0"])
inside = lambda r: r["x1"] <= 12 and r["y1"] <= 10


def test_each_level_tiles_footprint():
    for L in (0, 1, 2):
        rs = [r for r in ROOMS if r["L"] == L and inside(r)]
        assert sum(area(r) for r in rs) == pytest.approx(120.0), L
        for a, b in combinations(rs, 2):
            ox = min(a["x1"], b["x1"]) - max(a["x0"], b["x0"]); oy = min(a["y1"], b["y1"]) - max(a["y0"], b["y0"])
            assert not (ox > 1e-9 and oy > 1e-9), (L, a["name"], b["name"])


def test_three_bedrooms_and_floor_area():
    beds = [r for r in ROOMS if "edroom" in r["name"]]
    assert len(beds) == 3
    gfa = sum(area(r) for r in ROOMS if r["kind"] in ("in", "stair", "lift"))
    assert gfa == pytest.approx(288.56)


def test_stair_lift_and_wet_rooms_stack():
    for name in ("Stair", "Lift"):
        rects = {(r["x0"], r["y0"], r["x1"], r["y1"]) for r in ROOMS if r["name"] == name}
        assert len(rects) == 1 and len([r for r in ROOMS if r["name"] == name]) == 3
    bath = next(r for r in ROOMS if r["name"] == "Family bath"); ens = next(r for r in ROOMS if r["name"] == "Ensuite")
    assert (bath["x0"], bath["y0"], bath["x1"], bath["y1"]) == (ens["x0"], ens["y0"], ens["x1"], ens["y1"])


def test_double_height_void_sits_over_living():
    liv = next(r for r in ROOMS if r["name"] == "Living"); void = next(r for r in ROOMS if r["kind"] == "void")
    assert (liv["x0"], liv["y0"], liv["x1"], liv["y1"]) == (void["x0"], void["y0"], void["x1"], void["y1"])
