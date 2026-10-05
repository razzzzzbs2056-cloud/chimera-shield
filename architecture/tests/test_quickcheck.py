import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import quickcheck as q  # noqa: E402


def test_factored_load():
    assert q.factored_load_ec(1.7, 4.0) == pytest.approx(8.295)


def test_beam_statics_and_deflection():
    m, v = q.simply_supported(10, 6)
    assert (m, v) == (45, 30)
    # 5wL^4/384EI: w=10 N/mm, L=6000, E=10000, I=1e9 -> 5*10*1.296e15/(384*1e13)
    assert q.deflection_mm(10, 6, 10000, 1e9) == pytest.approx(16.875)


def test_beam_sizing_passes_its_own_checks():
    r = q.size_timber_beam(8, 4, 1.7, 4.0)
    assert r["h_selected_mm"] >= r["h_req_bending_mm"]
    assert r["span_over_deflection"] >= 300
    assert r["h_selected_mm"] % 40 == 0


def test_all_csvs_rectangular():
    for f in (ROOT / "data").glob("*.csv"):
        rows = list(csv.reader(open(f, newline="")))
        assert {len(r) for r in rows} == {len(rows[0])}, f.name


def test_takeoff_materials_exist_and_carbon_ordering():
    ec = q.embodied_carbon()
    assert 0 < ec["low_t"] < ec["high_t"]
    assert ec["biogenic_t"] > 0


def test_bad_unit_rejected(tmp_path):
    p = tmp_path / "t.csv"
    p.write_text("element,material,quantity,unit,note\nx,Float glass,1,m2,\n")
    with pytest.raises(ValueError):
        q.embodied_carbon(p)
