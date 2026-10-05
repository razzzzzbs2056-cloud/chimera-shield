"""Tests for architecture/tower/calcs/structure_gravity.py (30-storey tower, Division 3 concept)."""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tower" / "calcs"))
import structure_gravity as sg  # noqa: E402


@pytest.fixture(scope="module")
def r():
    return sg.run()


def test_tributary_areas_sum_to_floor_minus_core(r):
    td = sg.takedown()
    a = td["trib"]["area_m2"]
    assert sum(a.values()) == pytest.approx(30 * 24 - 12 * 8, abs=1e-6)
    assert sum(v["trib_area_m2"] for v in r["columns"].values()) + r["core"]["trib_slab_area_m2"] \
        == pytest.approx(624.0, abs=1e-3)
    assert td["trib"]["core_interior_m2"] == pytest.approx(96.0, abs=1e-6)
    assert sum(td["facade"].values()) == pytest.approx(2 * (30 + 24), abs=1e-6)


def test_grid_symmetric_and_on_perimeter(r):
    g = r["grid"]
    assert len(g) == 14
    for x, y in g.values():
        assert x in (0.0, 30.0) or y in (0.0, 24.0)
        assert [30 - x, 24 - y] in g.values()


def _independent_totals(r):
    """Total G and Q at ground computed by whole-floor area, independent of tributary split."""
    A = r["assumptions"]
    g_rc = A["gamma_rc_kN_m3"]
    z = r["levels"]["z_m"]; hs = r["levels"]["storey_height_m"]
    out_area, perim = 624.0, 108.0
    core_int = 96.0 * A["core_floor_fraction"]
    corr = (12 + 2 * A["corridor_band_m"]) * (8 + 2 * A["corridor_band_m"]) - 96.0
    g_slab = A["slab_thickness_m"] * g_rc
    G = Q = 0.0
    for lv in range(1, 31):
        if lv == 30:
            G += (g_slab + A["roof_sdl_kPa"] + A["roof_plant_kPa"]) * out_area
            Q += A["roof_live_kPa"] * out_area
        else:
            G += (g_slab + A["sdl_kPa"] + A["partitions_kPa"]) * out_area
            Q += A["live_res_kPa"] * (out_area - corr) + A["live_corridor_kPa"] * corr
        G += A["facade_kN_m"] * perim + (g_slab + A["sdl_kPa"]) * core_int
        Q += A["core_live_kPa"] * core_int
        zone = sg.zone_of(lv)
        G += sum(c["size_by_zone_m"][zone] ** 2 for c in r["columns"].values()) * hs[lv - 1] * g_rc
    for lv in range(1, 32):
        t = A["core_wall_t_zones_m"][sg.zone_of(lv)]
        walls = 96.0 - (12 - 2 * t) * (8 - 2 * t) + A["core_internal_wall_count"] * (8 - 2 * t) * A["core_internal_wall_t_m"]
        G += walls * hs[lv - 1] * g_rc
    G += (g_slab + A["roof_sdl_kPa"] + A["core_roof_plant_kPa"]) * 96.0
    Q += A["roof_live_kPa"] * 96.0
    assert len(z) == 31
    return G, Q


def test_takedown_equilibrium_columns_plus_core_equal_total(r):
    G, Q = _independent_totals(r)
    sumG = sum(c["G_base_kN"] for c in r["columns"].values()) + r["core"]["G_base_kN"]
    sumQ = sum(c["Q_base_kN"] for c in r["columns"].values()) + r["core"]["Q_base_kN"]
    assert sumG == pytest.approx(G, rel=1e-6)
    assert sumQ == pytest.approx(Q, rel=1e-6)
    assert r["gravity_totals_at_ground_kN"]["G"] == pytest.approx(G, rel=1e-6)


def test_column_sizes_respect_stress_limit(r):
    lim = r["assumptions"]["column_stress_limit_frac_fck"]
    for c in r["columns"].values():
        assert c["N_Ed_kN"] / (c["base_size_m"] ** 2 * r["concrete"]["fck_MPa"] * 1000) <= lim + 1e-9
        assert c["N_Ed_kN"] == pytest.approx(max(1.35 * c["G_base_kN"] + 1.5 * c["Q_base_kN"],
                                                 1.2 * c["G_base_kN"] + 1.6 * c["Q_base_kN"]))


def test_masses_sum_to_W_over_g(r):
    m = r["mass_t_per_level"]
    assert len(m) == 31 and len(r["levels"]["z_m"]) == 31
    assert sum(m) * sg.G_ACC == pytest.approx(r["W_kN"], rel=1e-12)
    assert r["levels"]["z_m"][29] == pytest.approx(94.4)
    assert 9.0 < r["unit_weight_kPa_per_floor"] < 15.0   # plausibility band for RC residential


def test_seismic_weight_consistent_with_gravity(r):
    """W = G above base - lower half of ground-storey verticals + psi*Q (core-roof live and floor live)."""
    G, Q = _independent_totals(r)
    sw = sg.seismic_weights(sg.takedown())
    psi = r["assumptions"]["psi_live_seismic"]
    assert r["W_kN"] == pytest.approx(G - sw["W_lower_half_ground_storey_to_base_kN"] + psi * Q, rel=1e-9)


def test_closed_form_uniform_cantilever_flexure_and_shear():
    L, n, mbar, EI, GA = 90.0, 120, 30.0, 2.0e9, 5.0e7
    z = np.linspace(L / n, L, n)
    m = np.full(n, mbar * L / n); m[-1] /= 2
    Tf = sg.periods(m, sg.flexibility(z, lambda s: EI, lambda s: 1e30))[0]
    assert Tf == pytest.approx(sg.closed_form_flexure_T(mbar, L, EI), rel=0.01)
    Ts = sg.periods(m, sg.flexibility(z, lambda s: 1e30, lambda s: GA))[0]
    assert Ts == pytest.approx(sg.closed_form_shear_T(mbar, L, GA), rel=0.01)
    T = sg.periods(m, sg.flexibility(z, lambda s: EI, lambda s: GA))[0]
    assert max(Tf, Ts) <= T <= math.sqrt(Tf ** 2 + Ts ** 2) * 1.001   # monotonicity / Dunkerley bound


def test_tip_mass_cantilever():
    z, m, EI = np.array([10.0]), np.array([100.0]), 5.0e7
    T = sg.periods(m, sg.flexibility(z, lambda s: EI, lambda s: 1e30))[0]
    assert T == pytest.approx(2 * math.pi * math.sqrt(100.0 * 10 ** 3 / (3 * EI)), rel=1e-4)


def test_core_section_and_period_sanity(r):
    c = sg.core_section(0.6)
    assert c["I_x_m4"] == pytest.approx((12 * 8 ** 3 - 10.8 * 6.8 ** 3) / 12)
    assert c["I_y_m4"] > c["I_x_m4"]
    lc, lg = r["lateral_cracked"], r["lateral_gross"]
    for d in ("X", "Y"):
        assert lc[d]["T1_s"] == pytest.approx(lg[d]["T1_s"] / math.sqrt(r["cracked_factor"]), rel=1e-6)
    assert r["T1_sanity_direction"] == "Y"
    assert 1.0 < r["T1_sanity_s"] < 8.0
