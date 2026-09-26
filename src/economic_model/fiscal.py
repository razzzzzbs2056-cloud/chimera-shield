"""Public debt dynamics.

Debt ratio law of motion with a foreign-currency share:

    d_{t+1} = d_t · [ (1−s)(1+i_d) + s(1+i_f)(1+ε) ] / (1+g_n)  −  pb_{t+1}

where d is debt/GDP, s the foreign-currency share of debt, i_d and i_f the
effective domestic and foreign interest rates, ε the depreciation of the
local currency against the debt currency, g_n nominal LCU GDP growth and pb
the primary balance/GDP (surplus positive). Stock-flow adjustments (e.g.
called guarantees) enter as `sfa` (ratio to GDP, positive increases debt).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DebtAssumptions:
    initial_debt_ratio: float
    foreign_share: float
    domestic_rate: float
    foreign_rate: float
    nominal_growth: list[float]
    primary_balance: list[float]
    depreciation: list[float]
    sfa: list[float] = field(default_factory=list)

    def __post_init__(self) -> None:
        n = len(self.nominal_growth)
        if not (len(self.primary_balance) == len(self.depreciation) == n):
            raise ValueError("growth, primary balance and depreciation paths must have equal length")
        if self.sfa and len(self.sfa) != n:
            raise ValueError("sfa path must match other paths")
        if not 0.0 <= self.foreign_share <= 1.0:
            raise ValueError("foreign_share must be in [0, 1]")


def debt_path(a: DebtAssumptions) -> list[float]:
    path = [a.initial_debt_ratio]
    s = a.foreign_share
    for t in range(len(a.nominal_growth)):
        gross = (1 - s) * (1 + a.domestic_rate) + s * (1 + a.foreign_rate) * (1 + a.depreciation[t])
        d_next = path[-1] * gross / (1 + a.nominal_growth[t]) - a.primary_balance[t]
        if a.sfa:
            d_next += a.sfa[t]
        path.append(d_next)
    return path


def debt_stabilising_primary_balance(debt_ratio: float, effective_rate: float, nominal_growth: float) -> float:
    """pb* = d (i − g) / (1 + g) for a single-currency approximation."""
    return debt_ratio * (effective_rate - nominal_growth) / (1.0 + nominal_growth)


def interest_burden(debt_ratio: float, effective_rate: float, revenue_ratio: float) -> float:
    """Interest payments as a share of government revenue."""
    if revenue_ratio <= 0:
        raise ValueError("revenue_ratio must be positive")
    return debt_ratio * effective_rate / revenue_ratio
