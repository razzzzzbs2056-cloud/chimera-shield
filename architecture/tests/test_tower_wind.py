"""Tests for architecture/tower/calcs/wind_tower.py (Division 7, 30-storey tower)."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tower" / "calcs"))
import wind_tower as wt  # noqa: E402


@pytest.fixture(scope="module")
def r():
    return wt.run()


def test_q_hand_values():
    assert wt.q_of_v(45.0) == pytest.approx(0.5 * 1.25 * 45.0 ** 2)
    assert wt.q_of_v(35.0) == pytest.approx(765.625)
    assert wt.q_of_v(55.0) == pytest.approx(1890.625)


def test_q_scales_with_v_squared():
    assert wt.q_of_v(55.0) / wt.q_of_v(35.0) == pytest.approx((55 / 35) ** 2)
    assert wt.q_of_v(90.0) == pytest.approx(4 * wt.q_of_v(45.0))


def test_profile_power_law_and_ratio():
    z = [10.0, 40.0, 94.4]
    q = wt.q_profile(45.0, z)
    assert q[1] / q[0] == pytest.approx((4.0) ** (2 * wt.ALPHA))
    assert q[0] == pytest.approx(wt.q_of_v(45.0 / wt.GUST_RATIO))
    assert wt.q_profile(45.0, 3.0) == pytest.approx(wt.q_profile(45.0, 10.0))  # held below 10 m


def test_vcr_formula():
    assert wt.v_crit(4.0, 24.0, 0.12) == pytest.approx(24.0 / (4.0 * 0.12))
    assert wt.v_crit(2.0, 30.0, 0.15) == pytest.approx(100.0)
    assert wt.v_crit(4.55, 24.0, 0.12) == pytest.approx(43.97, abs=0.05)


def test_mean_loads_scale_with_v_squared(r):
    for face in ("wind_on_30m_face", "wind_on_24m_face"):
        a = r["cases"][face]["35"]["cracked"]
        b = r["cases"][face]["55"]["cracked"]
        assert b["mean_base_shear_kN"] / a["mean_base_shear_kN"] == pytest.approx((55 / 35) ** 2, rel=1e-6)
        assert b["mean_base_moment_kNm"] / a["mean_base_moment_kNm"] == pytest.approx((55 / 35) ** 2, rel=1e-6)


def test_mean_base_shear_matches_closed_form(r):
    # Integral of q_ref (z/10)^(2a) dz from 10 to H plus constant q_ref below 10 m, width 30 up to 94.4 m
    v = 45.0
    q10 = wt.q_of_v(v / wt.GUST_RATIO) / 1000.0
    p = 2 * wt.ALPHA
    zroof = wt.H_ROOF
    body = q10 * (10.0 + (zroof ** (p + 1) - 10.0 ** (p + 1)) / ((p + 1) * 10.0 ** p))
    plant = q10 * ((wt.H_TOP / 10.0) ** p) * (wt.H_TOP - zroof)
    f = wt.CF * (30.0 * body + wt.PLANT_WIDTH["Y"] * plant)
    got = r["cases"]["wind_on_30m_face"]["45"]["cracked"]["mean_base_shear_kN"]
    assert got == pytest.approx(f, rel=0.01)


def test_30m_face_governs_and_gust_greater_than_one(r):
    a = r["cases"]["wind_on_30m_face"]["45"]["cracked"]
    b = r["cases"]["wind_on_24m_face"]["45"]["cracked"]
    assert a["base_shear_kN"] > b["base_shear_kN"]
    assert a["gust"]["G"] > 1.0 and b["gust"]["G"] > 1.0
    assert a["base_moment_kNm"] / a["base_shear_kN"] < wt.H_TOP  # arm below height


def test_flexible_case_deflects_more_than_gross(r):
    for face in ("wind_on_30m_face", "wind_on_24m_face"):
        c = r["cases"][face]["45"]
        assert c["cracked"]["top_deflection_mm"] > c["gross"]["top_deflection_mm"]


def test_cantilever_tip_load_closed_form():
    import numpy as np
    dz = 0.1
    n = 100
    zm = (np.arange(n) + 0.5) * dz
    w = np.ones(n)  # 1 kN/m over L=10 m
    ei = np.full(n, 1e5)
    ga = np.full(n, 1e12)
    _, _, _, y = wt.cantilever_response(w, zm, ei, ga, dz)
    assert y[-1] == pytest.approx(1.0 * 10.0 ** 4 / (8 * 1e5), rel=0.02)


def test_periods_taken_from_structure(r):
    c = r["cases"]["wind_on_30m_face"]["45"]
    assert c["cracked"]["period_s"] == pytest.approx(4.548, abs=0.01)
    assert c["gross"]["period_s"] == pytest.approx(3.216, abs=0.01)
    assert r["cases"]["wind_on_24m_face"]["45"]["cracked"]["period_s"] == pytest.approx(3.304, abs=0.01)


def test_vortex_shedding_values(r):
    row = r["crosswind"]["wind_on_24m_face"]["cracked"]["St"]["0.12"]
    assert row["V_cr_m_s"] == pytest.approx(24.0 / (4.548 * 0.12), rel=1e-3)
