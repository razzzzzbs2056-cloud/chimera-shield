"""Input-output accounting: value added, not gross output, enters GDP."""
import pytest

from src.economic_model.constraints import DeliveryConstraints, constrained_delivery
from src.economic_model.energy import MarginalUseComparison
from src.economic_model.sectors import IOTable, invert, matvec
from src.economic_model.welfare import ObjectiveAssessment


def table():
    # synthetic 2-sector economy, balanced by construction
    Z = [[10.0, 20.0], [15.0, 5.0]]
    m = [5.0, 15.0]
    va = [70.0, 40.0]
    # outputs from columns: s1 = 10+15+5+70 = 100, s2 = 20+5+15+40 = 80
    f = [100 - 30.0, 80 - 20.0]
    return IOTable(["s1", "s2"], Z, m, va, f, "USD_current_bn")


def test_io_table_balances():
    assert all(r["passed"] for r in table().check_balance())


def test_gdp_is_value_added_not_gross_output():
    t = table()
    assert t.gdp_basic_prices() == pytest.approx(110)
    assert t.gross_output_total() == pytest.approx(180)
    # GDP = final demand for domestic output minus imported intermediates
    assert t.gdp_basic_prices() == pytest.approx(sum(t.final_demand) - sum(t.imported_inputs))


def test_final_demand_shock_adds_less_than_gross_output():
    r = table().impact_of_final_demand({"s1": 10.0})
    assert r["delta_gross_output_total"] > 10.0  # multiplier on output
    assert r["delta_gdp"] < r["delta_gross_output_total"]
    # all of the shock is either domestic value added or imported inputs
    assert r["delta_gdp"] + r["delta_imported_inputs_total"] == pytest.approx(10.0)


def test_matrix_inverse():
    m = [[2.0, 1.0], [1.0, 3.0]]
    inv = invert(m)
    assert matvec(m, matvec(inv, [1.0, 2.0])) == pytest.approx([1.0, 2.0])


def test_unknown_sector_rejected():
    with pytest.raises(KeyError):
        table().impact_of_final_demand({"mining": 1.0})


def test_delivery_constraints_bind():
    c = DeliveryConstraints(approval_lag_years=1, unit_cost=2.0, max_units_per_year=5, execution_rate=0.8)
    out = constrained_delivery([10, 0, 0], [100, 4, 100], c)
    assert out[0]["delivered"] == 0 and out[0]["binding"] == "approval_lag"
    assert out[1]["binding"] == "financing" and out[1]["delivered"] == pytest.approx(2 * 0.8)
    assert out[2]["binding"] == "capacity"
    assert sum(o["delivered"] for o in out) < 10


def test_marginal_electricity_use_comparison():
    m = MarginalUseComparison(10, 1, 20, 8, 3, "USD_per_GWh")
    s = m.summary()
    assert s["export_net_value_per_gwh"] == 9 and s["domestic_net_value_per_gwh"] == 25


def test_welfare_tradeoffs_reported_separately_from_gdp():
    a = ObjectiveAssessment("STR-X", {"growth": "+", "poverty_inclusion": "-", "resilience": "+"})
    assert a.tradeoffs() == ["poverty_inclusion"]
    assert "fiscal_financial" in a.unassessed()
    with pytest.raises(ValueError):
        ObjectiveAssessment("bad", {"gdp_only": "+"})
