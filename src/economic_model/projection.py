"""Long-run GDP projection with separate real, price and exchange-rate paths.

The projector is deliberately simple: it is an accounting device that makes
every assumption explicit, not a behavioural forecast. Sector, fiscal and
external modules supply constraints and cross-checks around it.

Period convention: integer years label Nepal's fiscal year by its ending
calendar year (FY2023/24 → 2024) unless an input says otherwise; the label
is recorded in `ProjectionAssumptions.period_convention`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .growth import per_capita


@dataclass(frozen=True)
class Path:
    """A per-year rate path. `values` override `default` from their year onward
    (step-hold): {2030: 0.05} means 5% from 2030 until the next key."""

    default: float
    values: Mapping[int, float] = field(default_factory=dict)
    label: str = ""

    def at(self, year: int) -> float:
        keys = sorted(k for k in self.values if k <= year)
        return self.values[keys[-1]] if keys else self.default

    def shifted(self, delta_by_year: Mapping[int, float]) -> "Path":
        """Return a copy with additive shocks applied to specific years only."""
        years = set(self.values) | set(delta_by_year)
        # materialise the step path on affected years, then add shocks
        new_values = dict(self.values)
        for y in sorted(delta_by_year):
            new_values[y] = self.at(y) + delta_by_year[y]
            if y + 1 not in years:
                new_values[y + 1] = self.at(y + 1)  # restore baseline after the shocked year
        return Path(self.default, new_values, self.label)


@dataclass(frozen=True)
class ProjectionAssumptions:
    base_year: int
    base_nominal_gdp_lcu: float  # NPR, current prices, units (not millions)
    base_fx_lcu_per_usd: float  # NPR per USD, period average for base year
    base_population: float  # persons
    real_growth: Path
    deflator_growth: Path
    fx_depreciation: Path  # growth of NPR per USD
    population_growth: Path
    period_convention: str = "fiscal year labelled by ending calendar year"
    provenance: Mapping[str, str] = field(default_factory=dict)  # variable -> observation/assumption id


@dataclass(frozen=True)
class ProjectionRow:
    year: int
    real_gdp_lcu_base_prices: float
    deflator_index: float  # base year = 100
    nominal_gdp_lcu: float
    fx_lcu_per_usd: float
    nominal_gdp_usd: float
    population: float
    gdp_per_capita_usd: float
    real_growth: float
    deflator_growth: float
    fx_depreciation: float

    def as_dict(self) -> dict:
        return self.__dict__.copy()


def project(a: ProjectionAssumptions, end_year: int) -> list[ProjectionRow]:
    if end_year < a.base_year:
        raise ValueError("end_year must not precede base_year")
    for name in ("base_nominal_gdp_lcu", "base_fx_lcu_per_usd", "base_population"):
        if getattr(a, name) <= 0:
            raise ValueError(f"{name} must be positive")
    real = a.base_nominal_gdp_lcu  # real GDP at base-year prices equals nominal in the base year
    defl = 100.0
    fx = a.base_fx_lcu_per_usd
    pop = a.base_population
    rows = []
    for year in range(a.base_year, end_year + 1):
        if year == a.base_year:
            g = p = d = 0.0
        else:
            g, p, d = a.real_growth.at(year), a.deflator_growth.at(year), a.fx_depreciation.at(year)
            real *= 1.0 + g
            defl *= 1.0 + p
            fx *= 1.0 + d
            pop *= 1.0 + a.population_growth.at(year)
        nominal = real * defl / 100.0
        usd = nominal / fx
        rows.append(
            ProjectionRow(year, real, defl, nominal, fx, usd, pop, per_capita(usd, pop), g, p, d)
        )
    return rows


def first_year_reaching(rows: list[ProjectionRow], usd_target: float) -> int | None:
    for r in rows:
        if r.nominal_gdp_usd >= usd_target:
            return r.year
    return None
