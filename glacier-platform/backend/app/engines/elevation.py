"""
Elevation correction (lapse-rate) engine.

A weather model reports 2 m air temperature at its *grid* elevation, which in
steep Himalayan terrain can be a valley floor 1-3 km below the glacier. Using
that valley reading as glacier temperature is a category error the spec
explicitly forbids. We correct with a lapse rate and clearly label the result
as an ESTIMATE, not a measurement.

We store, per the spec:
  model_grid_elevation, glacier_elevation, elevation_difference,
  raw_model_temperature, adjusted_glacier_temperature, lapse_rate_assumption

Confidence is downgraded as the elevation correction grows, because lapse-rate
assumptions accumulate error over large vertical distances.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..core import Confidence, Observation, Provenance, ValueKind

# Environmental lapse rate: temperature falls ~6.5 degC per 1000 m.
# Free-atmosphere/saturated rates differ; this is a documented assumption, not
# a measured local gradient. Configurable per glacier if a local rate is known.
DEFAULT_LAPSE_RATE_C_PER_M = 6.5 / 1000.0


@dataclass
class ElevationAdjustment:
    model_grid_elevation_m: Optional[float]
    glacier_elevation_m: Optional[float]
    elevation_difference_m: Optional[float]
    raw_model_temp_c: Optional[float]
    adjusted_temp_c: Optional[float]
    lapse_rate_c_per_m: float
    lapse_rate_assumption: str
    confidence: Confidence

    def to_dict(self) -> dict:
        return {
            "model_grid_elevation_m": self.model_grid_elevation_m,
            "glacier_elevation_m": self.glacier_elevation_m,
            "elevation_difference_m": self.elevation_difference_m,
            "raw_model_temp_c": self.raw_model_temp_c,
            "adjusted_temp_c": self.adjusted_temp_c,
            "lapse_rate_c_per_m": self.lapse_rate_c_per_m,
            "lapse_rate_assumption": self.lapse_rate_assumption,
            "estimated_not_measured": True,
            "confidence": self.confidence.value,
        }


def adjust_temperature(
    raw_model_temp_c: Optional[float],
    model_grid_elevation_m: Optional[float],
    glacier_elevation_m: Optional[float],
    base_confidence: Confidence = Confidence.MEDIUM,
    lapse_rate: float = DEFAULT_LAPSE_RATE_C_PER_M,
) -> ElevationAdjustment:
    """Apply lapse-rate correction from model grid elevation to glacier
    elevation. If inputs are missing, returns an UNKNOWN-confidence result with
    adjusted_temp_c=None (never a guessed value)."""
    if (raw_model_temp_c is None or model_grid_elevation_m is None
            or glacier_elevation_m is None):
        return ElevationAdjustment(
            model_grid_elevation_m, glacier_elevation_m, None,
            raw_model_temp_c, None, lapse_rate,
            f"environmental lapse rate {lapse_rate*1000:.1f} degC/km", Confidence.UNKNOWN,
        )
    diff = glacier_elevation_m - model_grid_elevation_m  # +ve => glacier higher
    adjusted = raw_model_temp_c - diff * lapse_rate
    # Downgrade confidence with the magnitude of correction.
    conf = base_confidence
    ad = abs(diff)
    if ad > 2000:
        conf = base_confidence.downgrade(2)
    elif ad > 1000:
        conf = base_confidence.downgrade(1)
    return ElevationAdjustment(
        round(model_grid_elevation_m, 1), round(glacier_elevation_m, 1),
        round(diff, 1), round(raw_model_temp_c, 2), round(adjusted, 2),
        lapse_rate, f"environmental lapse rate {lapse_rate*1000:.1f} degC/km",
        conf,
    )


def as_observation(adj: ElevationAdjustment, base_prov: Provenance,
                   is_forecast: bool = False) -> Observation[float]:
    """Wrap an adjusted temperature as an ELEVATION_ADJUSTED[_FORECAST]
    observation -- explicitly estimated, not measured."""
    kind = (ValueKind.ELEVATION_ADJUSTED_FORECAST if is_forecast
            else ValueKind.ELEVATION_ADJUSTED)
    prov = base_prov.model_copy(update={
        "value_kind": kind,
        "notes": (f"Elevation-adjusted estimate (lapse rate "
                  f"{adj.lapse_rate_c_per_m*1000:.1f} degC/km over "
                  f"{adj.elevation_difference_m} m). Estimated, not measured."),
    })
    if adj.adjusted_temp_c is None:
        return Observation.unknown(prov, unit="degC")
    return Observation(
        value=adj.adjusted_temp_c, unit="degC", confidence=adj.confidence,
        provenance=prov, raw_value=adj.raw_model_temp_c, raw_unit="degC",
    )
