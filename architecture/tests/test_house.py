"""Plan integrity for the 3-bedroom house: rooms tile the 15 x 10 m footprint with no gaps or overlaps."""
import json
import re
from itertools import combinations
from pathlib import Path

import pytest

PAGE = (Path(__file__).resolve().parent.parent / "house" / "three-bed-house-3d.html").read_text()
block = PAGE.split("PLAN-START")[1].split("PLAN-END")[0]
ROOMS = [dict(name=m.group(1), x0=float(m.group(2)), y0=float(m.group(3)), x1=float(m.group(4)), y1=float(m.group(5)), zone=m.group(6))
         for m in re.finditer(r"name: '([^']+)', x0: ([\d.]+), y0: ([\d.]+), x1: ([\d.]+), y1: ([\d.]+), floor: '\w+', zone: '(\w+)'", block)]


def area(r):
    return (r["x1"] - r["x0"]) * (r["y1"] - r["y0"])


def test_rooms_parsed_and_three_bedrooms():
    assert len(ROOMS) == 14
    assert sum(1 for r in ROOMS if r["zone"] == "bed") == 3


def test_rooms_tile_footprint_exactly():
    assert sum(area(r) for r in ROOMS) == pytest.approx(150.0)
    for a, b in combinations(ROOMS, 2):
        ox = min(a["x1"], b["x1"]) - max(a["x0"], b["x0"])
        oy = min(a["y1"], b["y1"]) - max(a["y0"], b["y0"])
        assert not (ox > 1e-9 and oy > 1e-9), (a["name"], b["name"])
    assert all(0 <= r["x0"] < r["x1"] <= 15 and 0 <= r["y0"] < r["y1"] <= 10 for r in ROOMS)


def test_minimum_room_sizes_reasonable():
    # JUDGMENT thresholds for a family home; local codes set their own minimums
    beds = [r for r in ROOMS if r["zone"] == "bed"]
    assert all(area(r) >= 9.0 and min(r["x1"] - r["x0"], r["y1"] - r["y0"]) >= 2.7 for r in beds)
    living = sum(area(r) for r in ROOMS if r["zone"] == "live")
    assert living >= 45
