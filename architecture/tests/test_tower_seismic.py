"""Tests for architecture/tower/calcs/seismic_tower.py (Division 4, 30-storey tower, OpenSeesPy stick model)."""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("openseespy.opensees")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tower" / "calcs"))
import seismic_tower as st  # noqa: E402


@pytest.fixture(scope="module")
def r():
    return st.run()


def _uniform_props(EI, GA, n=1):
    return [{"A": 10.0, "EI": {"X": EI, "Y": EI}, "GA": {"X": GA, "Y": GA}, "GJ": 1e9} for _ in range(n)]


def test_closed_form_sdof_tip_mass():
    """Single Timoshenko element with tip mass: T = 2 pi sqrt(m / k), 1/k = H^3/(3 EI) + H/GA."""
    H, m, EI, GA = 10.0, 100.0, 2.0e7, 5.0e6
    out = st.stick_modal([H], [m], _uniform_props(EI, GA))
    cl = st.classify(out["modes"], np.array([m]), np.zeros(1))
    k = 1.0 / (H ** 3 / (3 * EI) + H / GA)
    T_cf = 2 * math.pi * math.sqrt(m / k)
    for d in ("X", "Y"):
        assert cl[d][0]["T"] == pytest.approx(T_cf, rel=1e-6)
        assert cl[d][0]["ratio"][d] == pytest.approx(1.0, abs=1e-9)


def test_uniform_cantilever_converges_to_flexural_closed_form():
    """40 equal lumped masses, shear rigid: T1 -> 2 pi / 1.875^2 sqrt(mbar L^4 / EI) (lumping error < 2 %)."""
    n, H, mbar, EI = 40, 80.0, 50.0, 1.0e9
    z = np.linspace(H / n, H, n); m = np.full(n, mbar * H / n); m[-1] /= 2
    out = st.stick_modal(z, m, _uniform_props(EI, 1e14, n))
    T = st.classify(out["modes"], m, np.zeros(n))["X"][0]["T"]
    T_cf = 2 * math.pi / 1.875104 ** 2 * math.sqrt(mbar * H ** 4 / EI)
    assert T == pytest.approx(T_cf, rel=0.02)


def test_mass_ratios(r):
    for d in ("X", "Y", "RZ"):
        assert r["modal"]["sum_all_modes"][d] == pytest.approx(1.0, abs=1e-6)
    for d in ("X", "Y"):
        q = [x["mass_ratio"] for x in r["modal"][d]]
        assert 0.55 < q[0] < 0.70                 # flexural cantilever ~0.61 (uniform: 0.613)
        assert sum(q) >= 0.90
    assert r["inputs"]["total_mass_t"] * st.G_ACC == pytest.approx(r["inputs"]["W_kN"], rel=1e-3)


def test_opensees_vs_hand_and_structure_sanity(r):
    for d in ("X", "Y"):
        T_os = [x["T_s"] for x in r["modal"][d]]
        h = r["hand"][d]
        for a, b in zip(T_os, h["T_s"]):
            assert a == pytest.approx(b, rel=5e-3)
        assert T_os[0] == pytest.approx(h["structure_sanity_T1_s"], rel=0.02)
        assert h["closed_form"]["T_southwell"] == pytest.approx(T_os[0], rel=0.15)
    assert r["modal"]["Y"][0]["T_s"] == pytest.approx(4.55, abs=0.05)
    assert r["modal"]["X"][0]["T_s"] == pytest.approx(3.30, abs=0.05)


def test_equilibrium_and_units(r):
    for d in ("X", "Y"):
        eq = r["response_per_unit_Sa"][d]["equilibrium_mode1"]
        assert eq["V_reaction_kN"] == pytest.approx(eq["V_applied_kN"], rel=1e-6)
        assert eq["M_reaction_kNm"] == pytest.approx(eq["M_applied_kNm"], rel=1e-6)
        assert eq["roof_static_m"] == pytest.approx(abs(eq["roof_modal_m"]), rel=1e-3)
        m1 = r["response_per_unit_Sa"][d]["mode1_per_g"]
        assert m1["V_kN"] == pytest.approx(r["modal"][d][0]["mass_ratio"] * r["inputs"]["total_mass_t"] * 9.81, rel=1e-9)
        T = r["modal"][d][0]["T_s"]
        Sd = 9.81 * (T / (2 * math.pi)) ** 2
        assert r["response_per_unit_Sa"][d]["per_mode_per_g"][0]["Sd_m_per_g"] == pytest.approx(Sd, rel=1e-9)


def test_sensitivity(r):
    sc, sm = r["sensitivity_T1_s"]["cracked"], r["sensitivity_T1_s"]["mass"]
    for d in ("X", "Y"):
        assert sc["0.35"][d] > sc["0.5"][d] > sc["0.7"][d] > sc["1.0"][d]
        assert sc["1.0"][d] == pytest.approx(st.STRUCT["lateral_gross"][d]["T1_s"], rel=0.02)
        assert sm["1.1"][d] / sm["1.0"][d] == pytest.approx(math.sqrt(1.1), rel=1e-6)


def test_torsion_and_p_delta(r):
    t = r["torsion"]
    assert max(t["e_m"]) < 1e-6
    assert t["CR_frame_m"] == pytest.approx([15.0, 12.0], abs=1e-6)
    for d in ("X", "Y"):
        pd = r["p_delta_opensees"][d]
        assert pd["T1_PDelta_s"] > pd["T1_linear_s"]
        hand = r["response_per_unit_Sa"][d]["p_delta_theta"]["mode1_max"]
        assert pd["theta_equiv"] == pytest.approx(hand, rel=0.3)


def test_independent_check_and_all_checks(r):
    assert r["verification"]["compare"]["decision"] == "PROCEED"
    failed = [c["check"] for c in r["checks"] if not c["pass"]]
    assert not failed, failed
