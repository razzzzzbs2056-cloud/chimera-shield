"""
Glacier risk engine -- transparent, weighted, auditable.

The spec is emphatic: DO NOT simply average every factor. Build a transparent
weighted model where every score exposes:
    factor, value, source, weight, contribution, confidence, observation age.

Design
------
* Each risk *factor* normalises a real indicator to a 0-100 sub-score with an
  explicit, documented mapping (``normalize``). A factor with no data is
  excluded from its component (weights renormalised over available factors) and
  the missing coverage is reported -- we never treat "no data" as "zero risk".
* A risk *component* (thermal, lake, ice, rock-slope, seismic, hydrological) is
  a weighted blend of its factors.
* The overall glacier risk score is a weighted blend of components.
* Confidence propagates as the weakest link, further downgraded by low coverage.

Every number is traceable back to its evidence. The output is labelled an
"Experimental hazard indicator -- not an official evacuation warning".
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from ..core import Confidence

# --- Risk levels ------------------------------------------------------------
RISK_LEVELS = [
    (0, 20, "LOW"),
    (21, 40, "WATCH"),
    (41, 60, "ELEVATED"),
    (61, 80, "HIGH"),
    (81, 100, "CRITICAL INVESTIGATION"),
]


def level_for(score: Optional[float]) -> str:
    if score is None:
        return "UNKNOWN"
    for lo, hi, name in RISK_LEVELS:
        if lo <= score <= hi:
            return name
    return "UNKNOWN"


def _clamp(x: float) -> float:
    return max(0.0, min(100.0, x))


def linear_map(value: float, lo: float, hi: float) -> float:
    """Map value in [lo, hi] -> [0, 100], clamped. If hi<lo, inverts."""
    if hi == lo:
        return 0.0
    return _clamp((value - lo) / (hi - lo) * 100.0)


@dataclass
class Factor:
    """One evidence-bearing input to a component score."""

    name: str
    raw_value: Optional[float]
    unit: Optional[str]
    source: Optional[str]
    weight: float
    confidence: Confidence
    age_seconds: Optional[float]
    # Maps raw_value -> 0..100 sub-score. Only called when raw_value is not None.
    normalize: Callable[[float], float] = field(repr=False, default=lambda v: 0.0)
    note: Optional[str] = None

    def subscore(self) -> Optional[float]:
        if self.raw_value is None:
            return None
        return round(_clamp(self.normalize(self.raw_value)), 1)

    def to_dict(self, contribution: Optional[float]) -> dict:
        return {
            "factor": self.name,
            "value": self.raw_value,
            "unit": self.unit,
            "source": self.source,
            "subscore_0_100": self.subscore(),
            "weight": self.weight,
            "contribution": contribution,
            "confidence": self.confidence.value,
            "age_seconds": self.age_seconds,
            "note": self.note,
            "available": self.raw_value is not None,
        }


@dataclass
class ComponentResult:
    name: str
    score: Optional[float]
    confidence: Confidence
    coverage: float  # fraction of factor weight with data
    factors: List[dict]

    def to_dict(self) -> dict:
        return {
            "component": self.name,
            "score_0_100": self.score,
            "level": level_for(self.score),
            "confidence": self.confidence.value,
            "coverage": round(self.coverage, 2),
            "factors": self.factors,
        }


def score_component(name: str, factors: List[Factor]) -> ComponentResult:
    """Weighted blend over factors that have data; renormalise weights so a
    missing factor doesn't silently count as zero risk."""
    available = [f for f in factors if f.subscore() is not None]
    total_weight = sum(f.weight for f in factors)
    avail_weight = sum(f.weight for f in available)
    coverage = (avail_weight / total_weight) if total_weight else 0.0

    factor_dicts: List[dict] = []
    if not available:
        for f in factors:
            factor_dicts.append(f.to_dict(contribution=None))
        return ComponentResult(name, None, Confidence.UNKNOWN, 0.0, factor_dicts)

    score = 0.0
    for f in factors:
        ss = f.subscore()
        if ss is None:
            factor_dicts.append(f.to_dict(contribution=None))
            continue
        contribution = round(ss * (f.weight / avail_weight), 2)
        score += contribution
        factor_dicts.append(f.to_dict(contribution=contribution))

    conf = Confidence.weakest(*[f.confidence for f in available])
    # Low coverage further downgrades confidence.
    if coverage < 0.5:
        conf = conf.downgrade(1)
    return ComponentResult(name, round(_clamp(score), 1), conf, coverage, factor_dicts)


@dataclass
class GlacierRisk:
    score: Optional[float]
    level: str
    confidence: Confidence
    components: List[dict]
    component_weights: dict

    def to_dict(self) -> dict:
        return {
            "glacier_risk_score_0_100": self.score,
            "risk_level": self.level,
            "confidence": self.confidence.value,
            "component_weights": self.component_weights,
            "components": self.components,
            "disclaimer": ("Experimental hazard indicator -- NOT an official "
                           "evacuation warning. CRITICAL does not mean a "
                           "disaster is certain."),
        }


# Default component weights (documented, tunable). Thermal + lake + rock-slope
# dominate for GLOF/slope hazards; seismic is a trigger multiplier-like input
# but kept additive & transparent here.
DEFAULT_COMPONENT_WEIGHTS = {
    "thermal_stress": 0.22,
    "lake_instability": 0.24,
    "ice_instability": 0.16,
    "rock_slope_instability": 0.20,
    "seismic_trigger": 0.08,
    "hydrological_stress": 0.10,
}


def aggregate(components: List[ComponentResult],
              weights: Optional[dict] = None) -> GlacierRisk:
    weights = weights or DEFAULT_COMPONENT_WEIGHTS
    available = [c for c in components if c.score is not None]
    if not available:
        return GlacierRisk(None, "UNKNOWN", Confidence.UNKNOWN,
                           [c.to_dict() for c in components], weights)
    avail_weight = sum(weights.get(c.name, 0) for c in available)
    if avail_weight == 0:
        return GlacierRisk(None, "UNKNOWN", Confidence.UNKNOWN,
                           [c.to_dict() for c in components], weights)
    score = sum(c.score * (weights.get(c.name, 0) / avail_weight) for c in available)
    conf = Confidence.weakest(*[c.confidence for c in available])
    total_component_weight = sum(weights.values())
    if avail_weight / total_component_weight < 0.6:
        conf = conf.downgrade(1)
    score = round(_clamp(score), 1)
    return GlacierRisk(score, level_for(score), conf,
                       [c.to_dict() for c in components], weights)
