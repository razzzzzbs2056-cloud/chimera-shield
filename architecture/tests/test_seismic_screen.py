import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "calculations"))
import seismic_screen as ss  # noqa: E402


def test_single_dof_matches_closed_form():
    # tip-mass cantilever: T = 2*pi*sqrt(m L^3 / 3EI)
    m, L, EI = np.array([100.0]), np.array([10.0]), 5.0e7
    res = ss.modal(m, ss.flexibility(L, EI, None))
    expected = 2 * math.pi * math.sqrt(m[0] * L[0] ** 3 / (3 * EI))
    assert res["T"][0] == pytest.approx(expected, rel=1e-9)
    assert res["eff_mass_ratio"][0] == pytest.approx(1.0)


def test_shear_flexibility_lengthens_period_and_mass_ratios_sum_to_one():
    r = ss.run()
    assert r["flexure + shear"]["T"][0] > r["flexure only"]["T"][0]
    for k in ("flexure only", "flexure + shear"):
        assert r[k]["eff_mass_ratio"].sum() == pytest.approx(1.0, abs=1e-9)


def test_mass_total_and_period_plausible():
    r = ss.run()
    assert r["masses"]["m"].sum() == pytest.approx(r["masses"]["W_kN"] / ss.G, rel=1e-12)
    assert 0.03 < r["flexure + shear"]["T"][0] < 1.0   # squat core-wall building, reasonableness only


def test_demand_scales_linearly_with_sa():
    d = ss.run()["demand"]
    assert d[1]["V_kN"] == pytest.approx(2 * d[0]["V_kN"], rel=1e-9)
    assert d[3]["M_base_kNm"] == pytest.approx(8 * d[0]["M_base_kNm"], rel=1e-9)


def test_symmetric_layout_has_no_eccentricity_and_no_amplification():
    els = [(4, 4, 1, 1), (44, 4, 1, 1), (4, 28, 1, 1), (44, 28, 1, 1)]
    t = ss.plan_torsion(els, (24, 16), 1000.0, 48, 32, 32)
    assert abs(t["e_y"]) < 1e-9
    assert t["edge_amplification"] == pytest.approx(1.0, abs=1e-9)


def test_north_cores_are_torsionally_irregular_and_south_elements_fix_it():
    r = ss.run()
    a, b = r["torsion_A"], r["torsion_B"]
    assert a["e_over_B"] > 0.15 and a["edge_amplification"] > 1.2
    assert b["e_over_B"] < 0.05 and b["edge_amplification"] < a["edge_amplification"]


def test_opensees_agrees_with_hand_model():
    pytest.importorskip("openseespy.opensees")
    r = ss.run()
    v = ss.verify_with_opensees(r["masses"]["m"], r["core"]["EI"], r["core"]["GA"])
    assert v["EB"][0] == pytest.approx(r["flexure only"]["T"][0], rel=0.01)
    assert v["Timoshenko"][0] == pytest.approx(r["flexure + shear"]["T"][0], rel=0.01)
