import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
for sub in ("bim", "calculations", "scripts", "models/calculix_beam"):
    sys.path.insert(0, str(ROOT / sub))


def test_check_stack_reports_core_tools():
    import check_stack
    st = check_stack.check()
    assert st["numpy"]["ok"] and st["ifcopenshell"]["ok"]
    assert "gmsh" in st and "gmsh-cli" in st   # module and CLI reported separately
    assert all("use" in v for v in st.values())


def test_ids_passes_on_generated_model_and_fails_without_data(tmp_path):
    pytest.importorskip("ifctester.ids")
    import ifcopenshell
    import ifcopenshell.api.root, ifcopenshell.api.project, ifcopenshell.api.aggregate, ifcopenshell.api.spatial
    import make_ifc
    import requirements_ids as rq
    make_ifc.build(tmp_path / "ok.ifc")
    assert all(r["pass"] for r in rq.validate(tmp_path / "ok.ifc"))
    # negative case: a column with no material, no psets, not in a storey must fail
    m = ifcopenshell.api.project.create_file(version="IFC4")
    p = ifcopenshell.api.root.create_entity(m, ifc_class="IfcProject", name="neg")
    ifcopenshell.api.root.create_entity(m, ifc_class="IfcColumn", name="bare column")
    m.write(str(tmp_path / "bad.ifc"))
    col = next(r for r in rq.validate(tmp_path / "bad.ifc") if r["spec"].startswith("IFCCOLUMN"))
    assert not col["pass"] and col["failed"] == 1


@pytest.mark.skipif(not shutil.which("ccx"), reason="CalculiX not installed")
def test_calculix_beam_matches_timoshenko_and_equilibrium():
    pytest.importorskip("gmsh")
    import run_beam
    for case in ("iso", "ortho"):
        r = run_beam.run(case, nx=40, ny=2, nz=8)          # coarse mesh keeps the test fast
        assert r["reaction_N"] == pytest.approx(r["applied_N"], rel=1e-6)
        assert r["ratio_rel"] == pytest.approx(1.0, abs=0.04)
    fine = run_beam.run("iso")
    assert fine["ratio_rel"] == pytest.approx(1.0, abs=0.01)


def test_pymoo_optimum_agrees_with_grid_and_meets_constraints():
    pytest.importorskip("pymoo")
    import optimise_lateral as ol
    o, g = ol.optimise(), ol.grid(step_s=0.01, step_y=0.5)
    m, tol = o["metrics"], 1e-3      # GA sits on the active constraint; allow solver tolerance only
    assert m["amp"] <= ol.LIMITS["amp"] + tol and m["e_over_B"] <= ol.LIMITS["e_over_B"] + tol
    assert m["omega"] >= ol.LIMITS["omega"] - tol
    assert o["s"] == pytest.approx(g["s"], abs=0.02)
    assert o["s"] < 0.5          # CR-003 proposal (0.5) keeps margin over the bare optimum
