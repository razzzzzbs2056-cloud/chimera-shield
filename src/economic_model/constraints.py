"""Physical, financial and administrative delivery constraints.

A planned programme never enters the model at face value. It passes through:
  1. approval lag (years before construction can start),
  2. a financing cap (money available / unit cost),
  3. a construction-capacity cap (units deliverable per year),
  4. a historical execution rate (share of feasible work actually completed).
All parameters must be documented inputs; the functions below supply none.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DeliveryConstraints:
    approval_lag_years: int
    unit_cost: float  # money per physical unit (e.g. per MW)
    max_units_per_year: float  # construction/contractor capacity
    execution_rate: float  # 0..1, historical share of planned work delivered

    def __post_init__(self) -> None:
        if self.approval_lag_years < 0:
            raise ValueError("approval lag cannot be negative")
        if self.unit_cost <= 0 or self.max_units_per_year < 0:
            raise ValueError("unit_cost must be positive and capacity non-negative")
        if not 0.0 <= self.execution_rate <= 1.0:
            raise ValueError("execution_rate must be in [0, 1]")


def constrained_delivery(
    planned_units: list[float], financing: list[float], c: DeliveryConstraints
) -> list[dict]:
    """Year-by-year feasible delivery. Unbuilt planned units carry forward."""
    if len(planned_units) != len(financing):
        raise ValueError("planned_units and financing must be the same length")
    backlog = 0.0
    out = []
    for t, (plan, money) in enumerate(zip(planned_units, financing)):
        backlog += plan
        if t < c.approval_lag_years:
            out.append({"t": t, "delivered": 0.0, "binding": "approval_lag", "backlog": backlog})
            continue
        caps = {
            "financing": money / c.unit_cost,
            "capacity": c.max_units_per_year,
            "backlog": backlog,
        }
        binding = min(caps, key=caps.get)
        delivered = caps[binding] * c.execution_rate
        backlog -= delivered
        out.append({"t": t, "delivered": delivered, "binding": binding, "backlog": backlog})
    return out
