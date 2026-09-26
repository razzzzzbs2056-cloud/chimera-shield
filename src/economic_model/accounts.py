"""National accounting identities.

Each account class holds components as `Quantity` objects in one declared unit
and exposes `checks()`, which returns `IdentityCheck` results. A statistical
discrepancy is never absorbed silently: it must be supplied explicitly, and
any residual beyond tolerance fails the check.

Identities implemented
----------------------
Expenditure:  GDP = C_hh + C_npish + C_gov + GFCF + ΔInventories + X − M + SD
Production:   GDP = Σ GVA_sector (basic prices) + taxes on products − subsidies on products
Income:       GNI  = GDP + net primary income from abroad
              GNDI = GNI + net secondary income from abroad (incl. workers' remittances)
Saving:       Gross national saving = GNDI − final consumption
              Current account = Gross national saving − gross capital formation
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .units import Quantity, sum_quantities

DEFAULT_REL_TOL = 1e-6


@dataclass(frozen=True)
class IdentityCheck:
    name: str
    lhs: float
    rhs: float
    unit: str
    rel_tol: float

    @property
    def difference(self) -> float:
        return self.lhs - self.rhs

    @property
    def relative_difference(self) -> float:
        denom = max(abs(self.lhs), abs(self.rhs), 1e-12)
        return abs(self.difference) / denom

    @property
    def passed(self) -> bool:
        return self.relative_difference <= self.rel_tol

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "lhs": self.lhs,
            "rhs": self.rhs,
            "unit": self.unit,
            "difference": self.difference,
            "relative_difference": self.relative_difference,
            "rel_tol": self.rel_tol,
            "passed": self.passed,
        }


@dataclass
class ExpenditureAccounts:
    unit: str
    household_consumption: Quantity
    government_consumption: Quantity
    gross_fixed_capital_formation: Quantity
    change_in_inventories: Quantity
    exports: Quantity
    imports: Quantity
    gdp: Quantity
    npish_consumption: Quantity | None = None
    statistical_discrepancy: Quantity | None = None
    rel_tol: float = DEFAULT_REL_TOL

    def final_consumption(self) -> Quantity:
        parts = [self.household_consumption, self.government_consumption]
        if self.npish_consumption is not None:
            parts.append(self.npish_consumption)
        return sum_quantities(parts, self.unit)

    def gross_capital_formation(self) -> Quantity:
        return sum_quantities([self.gross_fixed_capital_formation, self.change_in_inventories], self.unit)

    def implied_gdp(self) -> Quantity:
        total = self.final_consumption() + self.gross_capital_formation() + self.exports - self.imports
        if self.statistical_discrepancy is not None:
            total = total + self.statistical_discrepancy
        return total

    def checks(self) -> list[IdentityCheck]:
        return [
            IdentityCheck(
                "expenditure_gdp", self.gdp.to(self.unit).value, self.implied_gdp().value, self.unit, self.rel_tol
            )
        ]


@dataclass
class ProductionAccounts:
    unit: str
    sector_gva: dict[str, Quantity]
    taxes_on_products: Quantity
    subsidies_on_products: Quantity
    gdp: Quantity
    rel_tol: float = DEFAULT_REL_TOL

    def gva_basic_prices(self) -> Quantity:
        return sum_quantities(list(self.sector_gva.values()), self.unit)

    def implied_gdp(self) -> Quantity:
        return self.gva_basic_prices() + self.taxes_on_products - self.subsidies_on_products

    def sector_shares(self) -> dict[str, float]:
        total = self.gva_basic_prices()
        return {k: v.to(self.unit).value / total.value for k, v in self.sector_gva.items()}

    def checks(self) -> list[IdentityCheck]:
        return [
            IdentityCheck(
                "production_gdp", self.gdp.to(self.unit).value, self.implied_gdp().value, self.unit, self.rel_tol
            )
        ]


@dataclass
class IncomeAccounts:
    unit: str
    gdp: Quantity
    net_primary_income_abroad: Quantity
    net_secondary_income_abroad: Quantity  # includes personal remittances
    gni: Quantity | None = None
    gndi: Quantity | None = None
    rel_tol: float = DEFAULT_REL_TOL

    def implied_gni(self) -> Quantity:
        return self.gdp.to(self.unit) + self.net_primary_income_abroad

    def implied_gndi(self) -> Quantity:
        return self.implied_gni() + self.net_secondary_income_abroad

    def checks(self) -> list[IdentityCheck]:
        out = []
        if self.gni is not None:
            out.append(IdentityCheck("gni", self.gni.to(self.unit).value, self.implied_gni().value, self.unit, self.rel_tol))
        if self.gndi is not None:
            out.append(
                IdentityCheck("gndi", self.gndi.to(self.unit).value, self.implied_gndi().value, self.unit, self.rel_tol)
            )
        return out


@dataclass
class SavingInvestment:
    """S − I = CA. Uses the same unit and period for all components."""

    unit: str
    gndi: Quantity
    final_consumption: Quantity
    gross_capital_formation: Quantity
    current_account: Quantity | None = None  # as reported in the BoP, converted to the same unit
    rel_tol: float = DEFAULT_REL_TOL

    def gross_national_saving(self) -> Quantity:
        return self.gndi.to(self.unit) - self.final_consumption

    def implied_current_account(self) -> Quantity:
        return self.gross_national_saving() - self.gross_capital_formation

    def checks(self) -> list[IdentityCheck]:
        if self.current_account is None:
            return []
        return [
            IdentityCheck(
                "saving_investment_current_account",
                self.current_account.to(self.unit).value,
                self.implied_current_account().value,
                self.unit,
                self.rel_tol,
            )
        ]


@dataclass
class BalanceOfPayments:
    """Current account = goods + services + primary income + secondary income."""

    unit: str
    goods_balance: Quantity
    services_balance: Quantity
    primary_income: Quantity
    secondary_income: Quantity
    current_account: Quantity
    rel_tol: float = DEFAULT_REL_TOL

    def implied_current_account(self) -> Quantity:
        return sum_quantities(
            [self.goods_balance, self.services_balance, self.primary_income, self.secondary_income], self.unit
        )

    def checks(self) -> list[IdentityCheck]:
        return [
            IdentityCheck(
                "bop_current_account",
                self.current_account.to(self.unit).value,
                self.implied_current_account().value,
                self.unit,
                self.rel_tol,
            )
        ]


@dataclass
class AccountsBundle:
    """All accounts for one period; `run_checks` gathers every identity."""

    period: str
    accounts: list = field(default_factory=list)

    def run_checks(self) -> list[IdentityCheck]:
        results: list[IdentityCheck] = []
        for acc in self.accounts:
            results.extend(acc.checks())
        return results

    def all_passed(self) -> bool:
        return all(c.passed for c in self.run_checks())
