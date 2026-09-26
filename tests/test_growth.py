"""Growth arithmetic and target arithmetic."""
import math

import pytest

from src.economic_model import growth as G
from src.economic_model.fiscal import DebtAssumptions, debt_path, debt_stabilising_primary_balance
from src.economic_model.projection import Path, ProjectionAssumptions, first_year_reaching, project
from src.economic_model.target import (PriceFxCase, required_growth_table, required_multiple, sensitivity_grid,
                                       untargeted_arrival_year)


def test_cagr_inverse_of_compound():
    r = G.cagr(100, 200, 10)
    assert G.compound(100, r, 10) == pytest.approx(200)


def test_doubling_time():
    assert G.years_to_target(1, 2, 0.07) == pytest.approx(math.log(2) / math.log(1.07))
    assert G.years_to_target(1, 2, 0.0) == math.inf
    assert G.years_to_target(2, 1, 0.05) == 0.0


def test_nominal_usd_decomposition_roundtrip():
    usd = G.nominal_usd_growth(0.05, 0.06, 0.03)
    assert usd == pytest.approx(1.05 * 1.06 / 1.03 - 1)
    assert G.implied_real_growth(usd, 0.06, 0.03) == pytest.approx(0.05)


def test_depreciation_offsets_inflation_in_usd_terms():
    assert G.usd_price_growth(0.04, 0.04) == pytest.approx(0.0)


def test_growth_accounting_residual():
    r = G.growth_accounting(0.05, 0.08, 0.02, 0.4)
    assert r["capital_contribution"] + r["labour_contribution"] + r["tfp_residual"] == pytest.approx(0.05)
    with pytest.raises(ValueError):
        G.growth_accounting(0.05, 0.08, 0.02, 1.2)


def test_capital_path_perpetual_inventory():
    assert G.capital_path(100, [10, 10], 0.1) == pytest.approx([100, 100, 100])


def test_projection_keeps_real_price_fx_separate():
    a = ProjectionAssumptions(2025, 1000.0, 100.0, 10.0, Path(0.05), Path(0.04), Path(0.02), Path(0.01))
    rows = project(a, 2035)
    last = rows[-1]
    assert last.nominal_gdp_lcu == pytest.approx(last.real_gdp_lcu_base_prices * last.deflator_index / 100)
    assert last.nominal_gdp_usd == pytest.approx(last.nominal_gdp_lcu / last.fx_lcu_per_usd)
    assert last.real_gdp_lcu_base_prices == pytest.approx(1000 * 1.05 ** 10)
    usd_rate = G.cagr(rows[0].nominal_gdp_usd, last.nominal_gdp_usd, 10)
    assert usd_rate == pytest.approx(G.nominal_usd_growth(0.05, 0.04, 0.02))


def test_path_step_hold_and_shift():
    p = Path(0.05, {2030: 0.03})
    assert p.at(2029) == 0.05 and p.at(2031) == 0.03
    s = p.shifted({2027: -0.02})
    assert s.at(2027) == pytest.approx(0.03) and s.at(2028) == 0.05 and s.at(2030) == 0.03


def test_first_year_reaching():
    a = ProjectionAssumptions(2025, 100.0, 1.0, 1.0, Path(0.10), Path(0.0), Path(0.0), Path(0.0))
    assert first_year_reaching(project(a, 2040), 200.0) == 2033  # 1.1^8 = 2.14


def test_required_growth_table_hits_target_exactly():
    rows = required_growth_table(50e9, 2025, [PriceFxCase("x", 0.05, 0.02)], (2050,), icor_values=(4,))
    r = rows[0]
    assert 50e9 * (1 + r["required_nominal_usd_cagr"]) ** 25 == pytest.approx(3e12)
    assert G.nominal_usd_growth(r["required_real_cagr"], 0.05, 0.02) == pytest.approx(r["required_nominal_usd_cagr"])
    assert r["investment_rate_icor_4"] == pytest.approx(4 * r["required_real_cagr"])


def test_required_multiple_and_grid_monotonic():
    assert required_multiple(30e9) == pytest.approx(100)
    grid = sensitivity_grid([30e9, 60e9], 2025)
    assert grid[0]["usd_cagr_to_2050"] > grid[1]["usd_cagr_to_2050"]
    assert grid[0]["usd_cagr_to_2050"] > grid[0]["usd_cagr_to_2070"]


def test_untargeted_arrival_never_when_no_growth():
    assert untargeted_arrival_year(50e9, 2025, 0.0, PriceFxCase("flat", 0, 0)) == math.inf


def test_milestone_before_base_rejected():
    with pytest.raises(ValueError):
        required_growth_table(50e9, 2060, [PriceFxCase("x", 0, 0)], (2050,))


def test_debt_dynamics_stabilising_balance():
    d, i, g = 0.5, 0.04, 0.08
    pb = debt_stabilising_primary_balance(d, i, g)
    path = debt_path(DebtAssumptions(d, 0.0, i, 0.0, [g] * 5, [pb] * 5, [0.0] * 5))
    assert path[-1] == pytest.approx(d)


def test_foreign_debt_depreciation_raises_ratio():
    base = debt_path(DebtAssumptions(0.5, 0.5, 0.05, 0.01, [0.08], [0.0], [0.0]))
    dep = debt_path(DebtAssumptions(0.5, 0.5, 0.05, 0.01, [0.08], [0.0], [0.10]))
    assert dep[-1] > base[-1]
