import sys
from pathlib import Path

import pytest

pytest.importorskip("ifcopenshell")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "bim")); sys.path.insert(0, str(ROOT / "calculations"))
import make_ifc  # noqa: E402


@pytest.fixture(scope="module")
def res(tmp_path_factory):
    return make_ifc.build(tmp_path_factory.mktemp("ifc") / "m.ifc")


def test_geometry_in_metres_and_inside_footprint(res):
    lo, hi = res["bbox_min"], res["bbox_max"]
    # edge columns (0.40 m) are centred on the grid, so the envelope is the grid +/- 0.20 m
    assert lo[0] == pytest.approx(-0.2, abs=0.01) and hi[0] == pytest.approx(48.2, abs=0.01)
    assert lo[1] == pytest.approx(-0.2, abs=0.01) and hi[1] == pytest.approx(32.2, abs=0.01)
    assert lo[2] == pytest.approx(-0.2, abs=0.01) and hi[2] == pytest.approx(13.9, abs=0.01)


def test_slab_area_and_volume_match_analytic(res):
    assert make_ifc.poly_area(make_ifc.SLAB_POLY) == pytest.approx(960.0)
    assert res["volume_by_material_m3"]["CLT 5-ply"] == pytest.approx(3 * 960 * 0.15, rel=1e-6)
    assert res["volume_by_material_m3"]["Concrete C30/37"] == pytest.approx(48 * 32 * 0.2, rel=1e-6)


def test_cores_match_seismic_model_wall_thickness(res):
    # two box cores 8x8 m, 0.4 m walls, 13.9 m high + three 0.2 m slabs each
    walls = 2 * (64 - 7.2 ** 2) * 13.9
    slabs = 2 * 3 * 7.2 ** 2 * 0.2
    assert res["volume_by_material_m3"]["Concrete C40/50"] == pytest.approx(walls + slabs, rel=1e-6)


def test_gfa_inconsistency_with_program_is_detected(res):
    assert res["gfa_m2"] == pytest.approx(3456.0)
    assert res["gfa_m2"] < 4188  # finding C-01: brief program exceeds geometry; fix the brief, not this test


def test_member_counts(res):
    assert res["counts"]["columns"] == 23 and res["counts"]["walls"] == 8


def test_beam_depth_is_vertical(res):
    import ifcopenshell, ifcopenshell.geom
    import numpy as np
    m = ifcopenshell.open(res["path"])
    st = ifcopenshell.geom.settings(); st.set("use-world-coords", True)
    for prefix, depth in (("Girder", make_ifc.GIRDER[1]), ("Joist", make_ifc.JOIST[1])):
        el = next(b for b in m.by_type("IfcBeam") if b.Name.startswith(prefix))
        v = np.array(ifcopenshell.geom.create_shape(st, el).geometry.verts).reshape(-1, 3)
        assert v[:, 2].max() - v[:, 2].min() == pytest.approx(depth, abs=1e-6)
