"""Odds math: conversions, vig removal, expected value, Kelly sizing, arbitrage.

All prices are handled internally as *decimal* odds (e.g. 1.91 == -110 American).
"""
from __future__ import annotations

from typing import Iterable, Sequence


# ---------------------------------------------------------------- conversions

def american_to_decimal(american: float) -> float:
    if american == 0:
        raise ValueError("American odds cannot be 0")
    return 1 + (american / 100 if american > 0 else 100 / -american)


def decimal_to_american(decimal: float) -> int:
    if decimal <= 1:
        raise ValueError("Decimal odds must be > 1")
    if decimal >= 2:
        return round((decimal - 1) * 100)
    return round(-100 / (decimal - 1))


def implied_prob(decimal: float) -> float:
    return 1 / decimal


def fair_price(prob: float) -> float:
    """Decimal price with zero margin for a given probability."""
    return 1 / prob


# ---------------------------------------------------------------- margin / vig

def overround(prices: Sequence[float]) -> float:
    """Bookmaker margin for a complete market, e.g. 0.045 == 4.5% vig."""
    return sum(1 / p for p in prices) - 1


def devig_multiplicative(prices: Sequence[float]) -> list[float]:
    """Scale implied probabilities so they sum to 1."""
    raw = [1 / p for p in prices]
    total = sum(raw)
    return [r / total for r in raw]


def devig_power(prices: Sequence[float], tol: float = 1e-10) -> list[float]:
    """Power method: find k so sum(p_i ** k) == 1.

    Handles favourite/longshot bias better than the multiplicative method,
    because longshots carry proportionally more of the margin.
    """
    raw = [1 / p for p in prices]
    if abs(sum(raw) - 1) < tol:
        return raw
    lo, hi = 0.5, 3.0
    for _ in range(200):
        k = (lo + hi) / 2
        s = sum(r ** k for r in raw)
        if abs(s - 1) < tol:
            break
        # sum decreases as k increases (all r < 1)
        if s > 1:
            lo = k
        else:
            hi = k
    probs = [r ** k for r in raw]
    total = sum(probs)
    return [p / total for p in probs]


DEVIG_METHODS = {
    "multiplicative": devig_multiplicative,
    "power": devig_power,
}


def devig(prices: Sequence[float], method: str = "power") -> list[float]:
    try:
        return DEVIG_METHODS[method](prices)
    except KeyError:
        raise ValueError(f"Unknown devig method {method!r}; use one of {list(DEVIG_METHODS)}")


# ---------------------------------------------------------------- edge / sizing

def expected_value(prob: float, decimal: float) -> float:
    """EV per 1 unit staked. 0.03 == +3% edge."""
    return prob * decimal - 1


def kelly_fraction(prob: float, decimal: float) -> float:
    """Full-Kelly fraction of bankroll (0 if no edge)."""
    b = decimal - 1
    if b <= 0:
        return 0.0
    f = (prob * b - (1 - prob)) / b
    return max(0.0, f)


def closing_line_value(bet_price: float, closing_price: float) -> float:
    """CLV as a fraction: 0.05 means you beat the close by 5%."""
    return bet_price / closing_price - 1


# ---------------------------------------------------------------- arbitrage

def arbitrage(prices: Sequence[float]) -> float | None:
    """Return guaranteed profit margin if the best prices form an arb, else None."""
    inv = sum(1 / p for p in prices)
    if inv < 1:
        return 1 / inv - 1
    return None


def arb_stakes(prices: Sequence[float], total_stake: float) -> list[float]:
    """Split total_stake so every outcome returns the same payout."""
    inv = [1 / p for p in prices]
    s = sum(inv)
    return [total_stake * i / s for i in inv]


def median(values: Iterable[float]) -> float:
    vals = sorted(values)
    if not vals:
        raise ValueError("median of empty sequence")
    mid = len(vals) // 2
    return vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2
