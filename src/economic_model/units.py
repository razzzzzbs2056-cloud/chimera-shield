"""Units, currencies and price bases.

Every significant model value is a `Quantity` carrying a `Unit`. Arithmetic
between quantities is only allowed when dimension, currency and price basis
match; scale differences (million vs billion) are converted automatically.
Currency conversion and price-basis conversion must be explicit, using an
exchange rate or deflator that is itself a documented input.

Unit codes
----------
Money:   ``{CUR}_{BASIS}[_{SCALE}]``
         CUR   = NPR | USD | INR
         BASIS = current | const{YEAR}   (e.g. const2010 — base-year prices)
         SCALE = k | mn | bn | tn | crore | arba   (omitted = units)
         e.g. ``NPR_current_mn``, ``USD_current_bn``, ``NPR_const2010_mn``
Rates:   ``NPR_per_USD``, ``NPR_per_INR``, ``INR_per_USD``
Other:   ``percent``, ``ratio``, ``index``, ``persons``, ``persons_mn``,
         ``persons_k``, ``GWh``, ``MW``, ``months``, ``years``
"""

from __future__ import annotations

import re
from dataclasses import dataclass

SCALES = {
    "": 1.0,
    "k": 1e3,
    "mn": 1e6,
    "bn": 1e9,
    "tn": 1e12,
    "crore": 1e7,  # Nepali/Indian numbering: 1 crore = 10 million
    "arba": 1e9,  # Nepali numbering: 1 arba = 1 billion
}
CURRENCIES = {"NPR", "USD", "INR"}

_MONEY_RE = re.compile(r"^(NPR|USD|INR)_(current|const\d{4})(?:_(k|mn|bn|tn|crore|arba))?$")
_RATE_RE = re.compile(r"^(NPR|USD|INR)_per_(NPR|USD|INR)$")

_SIMPLE = {
    "percent": ("percent", 1.0),
    "ratio": ("ratio", 1.0),
    "index": ("index", 1.0),
    "persons": ("persons", 1.0),
    "persons_k": ("persons", 1e3),
    "persons_mn": ("persons", 1e6),
    "GWh": ("energy", 1.0),
    "MW": ("power", 1.0),
    "months": ("time", 1.0 / 12.0),
    "years": ("time", 1.0),
}


class UnitError(ValueError):
    """Raised when quantities with incompatible units are combined."""


@dataclass(frozen=True)
class Unit:
    code: str
    dimension: str
    scale: float = 1.0
    currency: str | None = None
    price_basis: str | None = None  # "current" or "constYYYY"
    numerator: str | None = None  # for exchange rates
    denominator: str | None = None

    @property
    def family(self) -> tuple:
        """Everything except scale: quantities in one family are addable."""
        return (self.dimension, self.currency, self.price_basis, self.numerator, self.denominator)


def parse_unit(code: str) -> Unit:
    m = _MONEY_RE.match(code)
    if m:
        cur, basis, scale = m.group(1), m.group(2), m.group(3) or ""
        return Unit(code, "money", SCALES[scale], cur, basis)
    m = _RATE_RE.match(code)
    if m:
        if m.group(1) == m.group(2):
            raise UnitError(f"degenerate exchange-rate unit {code!r}")
        return Unit(code, "fx_rate", 1.0, numerator=m.group(1), denominator=m.group(2))
    if code in _SIMPLE:
        dim, scale = _SIMPLE[code]
        return Unit(code, dim, scale)
    raise UnitError(f"unknown unit code {code!r}")


@dataclass(frozen=True)
class Quantity:
    value: float
    unit: str
    period: str | None = None  # e.g. "FY2023/24" or "2023"

    @property
    def u(self) -> Unit:
        return parse_unit(self.unit)

    def to(self, unit: str) -> "Quantity":
        src, dst = self.u, parse_unit(unit)
        if src.family != dst.family:
            raise UnitError(f"cannot convert {self.unit} to {unit}: different dimension/currency/price basis")
        return Quantity(self.value * src.scale / dst.scale, unit, self.period)

    def _coerce(self, other: "Quantity") -> "Quantity":
        if not isinstance(other, Quantity):
            raise UnitError("can only combine a Quantity with another Quantity")
        if self.period and other.period and self.period != other.period:
            raise UnitError(f"period mismatch: {self.period} vs {other.period}")
        return other.to(self.unit)

    def __add__(self, other: "Quantity") -> "Quantity":
        o = self._coerce(other)
        return Quantity(self.value + o.value, self.unit, self.period or other.period)

    def __sub__(self, other: "Quantity") -> "Quantity":
        o = self._coerce(other)
        return Quantity(self.value - o.value, self.unit, self.period or other.period)

    def scaled(self, factor: float) -> "Quantity":
        return Quantity(self.value * factor, self.unit, self.period)

    def ratio_to(self, other: "Quantity") -> float:
        """Dimensionless ratio of two same-family quantities."""
        return self.value / self._coerce(other).value


def convert_currency(amount: Quantity, rate: Quantity, target_currency: str) -> Quantity:
    """Convert a current-price money amount using an explicit exchange rate.

    `rate` must be expressed as ``X_per_Y``. Converting constant-price values
    across currencies is refused: that needs a PPP or base-year rate decision
    that the caller has to make explicitly.
    """
    a, r = amount.u, rate.u
    if a.dimension != "money" or r.dimension != "fx_rate":
        raise UnitError("convert_currency needs a money amount and an fx_rate")
    if a.price_basis != "current":
        raise UnitError("only current-price amounts can be converted with a market exchange rate")
    if amount.period and rate.period and amount.period != rate.period:
        raise UnitError(f"exchange rate period {rate.period} does not match amount period {amount.period}")
    scale_suffix = amount.unit.split("_")[2] if amount.unit.count("_") == 2 else ""
    target_code = f"{target_currency}_current" + (f"_{scale_suffix}" if scale_suffix else "")
    if (r.numerator, r.denominator) == (a.currency, target_currency):
        value = amount.value / rate.value
    elif (r.numerator, r.denominator) == (target_currency, a.currency):
        value = amount.value * rate.value
    else:
        raise UnitError(f"rate {rate.unit} cannot convert {a.currency} to {target_currency}")
    return Quantity(value, target_code, amount.period or rate.period)


def sum_quantities(items: list[Quantity], unit: str) -> Quantity:
    total = Quantity(0.0, unit)
    for q in items:
        total = total + q.to(unit)
    return total
