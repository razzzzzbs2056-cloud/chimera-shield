"""National accounting identities (synthetic numbers — not Nepal data)."""
import pytest

from src.economic_model.accounts import (AccountsBundle, BalanceOfPayments, ExpenditureAccounts, IncomeAccounts,
                                         ProductionAccounts, SavingInvestment)
from src.economic_model.energy import ElectricityBalance
from src.economic_model.units import Quantity

U = "NPR_current_bn"


def q(v, u=U):
    return Quantity(v, u)


def expenditure(gdp=100.0, sd=None):
    return ExpenditureAccounts(U, q(80), q(10), q(25), q(2), q(8), q(25), q(gdp),
                               statistical_discrepancy=None if sd is None else q(sd))


def test_expenditure_identity_holds():
    assert all(c.passed for c in expenditure().checks())


def test_expenditure_identity_detects_error():
    c = expenditure(gdp=101.0).checks()[0]
    assert not c.passed and c.difference == pytest.approx(1.0)


def test_statistical_discrepancy_must_be_explicit():
    assert not expenditure(gdp=101.0).checks()[0].passed
    assert expenditure(gdp=101.0, sd=1.0).checks()[0].passed


def test_production_identity_and_mixed_scales():
    p = ProductionAccounts(U, {"agri": q(25), "industry": Quantity(15000, "NPR_current_mn"), "services": q(50)},
                           q(12), q(2), q(100))
    assert p.checks()[0].passed
    assert sum(p.sector_shares().values()) == pytest.approx(1.0)


def test_income_accounts():
    inc = IncomeAccounts(U, q(100), q(-1), q(24), gni=q(99), gndi=q(123))
    assert all(c.passed for c in inc.checks())
    bad = IncomeAccounts(U, q(100), q(-1), q(24), gndi=q(120))
    assert not bad.checks()[0].passed


def test_saving_investment_equals_current_account():
    e = expenditure()
    gndi = q(123)
    si = SavingInvestment(U, gndi, e.final_consumption(), e.gross_capital_formation(), current_account=q(6))
    # S = 123 - 90 = 33; I = 27; CA = 6
    assert si.gross_national_saving().value == pytest.approx(33)
    assert all(c.passed for c in si.checks())


def test_bop_current_account():
    b = BalanceOfPayments(U, q(-30), q(5), q(-1), q(32), q(6))
    assert b.checks()[0].passed


def test_bundle_collects_all_checks():
    bundle = AccountsBundle("2024", [expenditure(), expenditure(gdp=90)])
    assert len(bundle.run_checks()) == 2 and not bundle.all_passed()


def test_electricity_balance():
    ok = ElectricityBalance("FY2024", 100, 10, 80, 20, 10)
    assert ok.checks()[0].passed and ok.loss_rate == pytest.approx(10 / 110)
    assert not ElectricityBalance("FY2024", 100, 10, 80, 25, 10).checks()[0].passed
