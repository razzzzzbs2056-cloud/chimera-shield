"""US$3 trillion target arithmetic.

This module answers purely arithmetic questions: *given* a base-year nominal
GDP in USD and explicit price and exchange-rate assumptions, what constant
growth is required to reach a target by a milestone year, and what does
that imply for real growth, per-capita income and investment?

It does not say whether any path is achievable. Feasibility is assessed by
comparing required rates with verified historical evidence (Agent 01B) and
with the capital, labour, energy, fiscal and external constraints produced
by other modules.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .growth import implied_real_growth, investment_rate_from_icor, required_cagr, usd_price_growth, years_to_target

TARGET_USD = 3.0e12
MILESTONES = (2050, 2060, 2070)


@dataclass(frozen=True)
class PriceFxCase:
    """A named (deflator, depreciation) pair, both annual decimal rates."""

    name: str
    deflator: float
    depreciation: float  # growth of NPR per USD

    @property
    def usd_price_growth(self) -> float:
        return usd_price_growth(self.deflator, self.depreciation)


def required_multiple(base_usd: float, target_usd: float = TARGET_USD) -> float:
    if base_usd <= 0:
        raise ValueError("base_usd must be positive")
    return target_usd / base_usd


def required_growth_table(
    base_usd: float,
    base_year: int,
    cases: list[PriceFxCase],
    milestones: tuple[int, ...] = MILESTONES,
    target_usd: float = TARGET_USD,
    icor_values: tuple[float, ...] = (),
) -> list[dict]:
    """One row per (milestone, price/FX case)."""
    rows = []
    for year in milestones:
        n = year - base_year
        if n <= 0:
            raise ValueError(f"milestone {year} is not after base year {base_year}")
        usd_rate = required_cagr(base_usd, target_usd, n)
        for c in cases:
            real = implied_real_growth(usd_rate, c.deflator, c.depreciation)
            row = {
                "milestone": year,
                "years": n,
                "case": c.name,
                "deflator": c.deflator,
                "depreciation": c.depreciation,
                "required_nominal_usd_cagr": usd_rate,
                "required_real_cagr": real,
                "required_multiple": target_usd / base_usd,
            }
            for icor in icor_values:
                row[f"investment_rate_icor_{icor:g}"] = investment_rate_from_icor(real, icor)
            rows.append(row)
    return rows


def required_per_capita(target_usd: float, population: float) -> float:
    if population <= 0:
        raise ValueError("population must be positive")
    return target_usd / population


def untargeted_arrival_year(base_usd: float, base_year: int, real_growth: float, case: PriceFxCase,
                            target_usd: float = TARGET_USD) -> float:
    """Year the target is reached at constant rates (inf if never)."""
    usd_rate = (1 + real_growth) * (1 + case.usd_price_growth) - 1
    yrs = years_to_target(base_usd, target_usd, usd_rate)
    return math.inf if math.isinf(yrs) else base_year + yrs


def sensitivity_grid(
    base_values_usd: list[float], base_year: int, milestones: tuple[int, ...] = MILESTONES,
    target_usd: float = TARGET_USD,
) -> list[dict]:
    """Required nominal USD CAGR for hypothetical base values.

    Used only while the verified base value is pending, to show how the
    answer scales. Rows are labelled `hypothetical_base` and must never be
    reported as Nepal's actual GDP.
    """
    rows = []
    for b in base_values_usd:
        row = {"hypothetical_base_usd": b, "required_multiple": target_usd / b}
        for y in milestones:
            row[f"usd_cagr_to_{y}"] = required_cagr(b, target_usd, y - base_year)
        rows.append(row)
    return rows
