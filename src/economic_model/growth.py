"""Growth arithmetic.

Conventions
-----------
* All rates are decimal fractions per year (0.05 = 5%).
* Real growth, domestic price growth (GDP deflator) and exchange-rate change
  are kept separate. For a currency quoted as LCU per USD, `depreciation`
  is the proportional increase in LCU per USD (positive = LCU weakens).

      nominal LCU growth = (1 + g_real)(1 + π) − 1
      nominal USD growth = (1 + g_real)(1 + π) / (1 + d) − 1
"""

from __future__ import annotations

import math
from collections.abc import Sequence


def compound(start: float, rate: float, years: float) -> float:
    return start * (1.0 + rate) ** years


def cagr(start: float, end: float, years: float) -> float:
    if start <= 0 or end <= 0:
        raise ValueError("CAGR requires positive start and end values")
    if years <= 0:
        raise ValueError("years must be positive")
    return (end / start) ** (1.0 / years) - 1.0


def required_cagr(start: float, target: float, years: float) -> float:
    """Constant annual growth needed to move from `start` to `target`."""
    return cagr(start, target, years)


def years_to_target(start: float, target: float, rate: float) -> float:
    """Years needed at constant `rate`; inf if the target is never reached."""
    if start <= 0 or target <= 0:
        raise ValueError("values must be positive")
    if target <= start:
        return 0.0
    if rate <= 0:
        return math.inf
    return math.log(target / start) / math.log1p(rate)


def nominal_lcu_growth(real: float, deflator: float) -> float:
    return (1.0 + real) * (1.0 + deflator) - 1.0


def nominal_usd_growth(real: float, deflator: float, depreciation: float) -> float:
    return (1.0 + real) * (1.0 + deflator) / (1.0 + depreciation) - 1.0


def implied_real_growth(usd_growth: float, deflator: float, depreciation: float) -> float:
    """Invert `nominal_usd_growth` for the real rate."""
    return (1.0 + usd_growth) * (1.0 + depreciation) / (1.0 + deflator) - 1.0


def usd_price_growth(deflator: float, depreciation: float) -> float:
    """Growth of the GDP deflator expressed in USD (π and d combined)."""
    return (1.0 + deflator) / (1.0 + depreciation) - 1.0


def growth_accounting(g_output: float, g_capital: float, g_labour: float, capital_share: float) -> dict:
    """Cobb-Douglas decomposition in log-approximation form.

    Returns the contributions and the TFP residual. `g_labour` can be
    quality-adjusted labour input if human-capital data are available.
    """
    if not 0.0 < capital_share < 1.0:
        raise ValueError("capital_share must be strictly between 0 and 1")
    k = capital_share * g_capital
    lab = (1.0 - capital_share) * g_labour
    return {"capital_contribution": k, "labour_contribution": lab, "tfp_residual": g_output - k - lab}


def capital_path(k0: float, investment: Sequence[float], depreciation_rate: float) -> list[float]:
    """Perpetual inventory: K_{t+1} = (1 − δ) K_t + I_t."""
    if not 0.0 <= depreciation_rate < 1.0:
        raise ValueError("depreciation_rate must be in [0, 1)")
    path = [k0]
    for inv in investment:
        path.append((1.0 - depreciation_rate) * path[-1] + inv)
    return path


def investment_rate_from_icor(real_growth: float, icor: float) -> float:
    """Gross investment / GDP implied by the incremental capital-output ratio.

    This is a crude consistency check, not a production function: it
    ignores depreciation dynamics and changing capital productivity.
    """
    if icor <= 0:
        raise ValueError("icor must be positive")
    return icor * real_growth


def per_capita(total: float, population: float) -> float:
    if population <= 0:
        raise ValueError("population must be positive")
    return total / population
