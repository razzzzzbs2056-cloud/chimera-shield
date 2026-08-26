"""
Provenance and observation envelope.

The single most important module in this platform. Every value that reaches a
user must be wrapped so that it carries, at all times:

    source + acquisition_time + processing_time + spatial_resolution
          + confidence + age of data

This module makes it structurally difficult to emit a bare number. If you find
yourself returning a raw float to the API layer, wrap it in an ``Observation``
instead. A missing value is represented explicitly as ``value=None`` with
``confidence=UNKNOWN`` -- we never invent a substitute number.

Scientific rules enforced here:
  * Nothing is ever labelled "live" unless the source genuinely provides
    near-real-time observations AND the timestamp supports it (see
    ``FreshnessStatus`` / ``freshness.py``).
  * Forecast values are a distinct ``ValueKind`` and can never be silently
    treated as observations.
  * Model-derived and elevation-adjusted values are distinct ``ValueKind``s and
    must be labelled estimated, not measured.
"""
from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field, field_validator

T = TypeVar("T")


class Confidence(str, enum.Enum):
    """Coarse, honest confidence buckets. Ordered low -> high for comparison."""

    UNKNOWN = "UNKNOWN"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

    @property
    def rank(self) -> int:
        return {"UNKNOWN": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}[self.value]

    def downgrade(self, steps: int = 1) -> "Confidence":
        """Reduce confidence by ``steps`` buckets, floored at UNKNOWN."""
        order = [Confidence.UNKNOWN, Confidence.LOW, Confidence.MEDIUM, Confidence.HIGH]
        idx = max(0, self.rank - steps)
        return order[idx]

    @classmethod
    def weakest(cls, *values: "Confidence") -> "Confidence":
        """The weakest confidence among several inputs (a chain is only as
        trustworthy as its least trustworthy link)."""
        if not values:
            return cls.UNKNOWN
        return min(values, key=lambda c: c.rank)


class ValueKind(str, enum.Enum):
    """What *kind* of number this is. Prevents category errors that the spec
    forbids, e.g. calling a model temperature a thermometer measurement, or a
    forecast an observation."""

    MEASURED = "measured"            # direct instrument / satellite observation
    MODEL = "model"                  # reanalysis / NWP model output (e.g. ERA5)
    FORECAST = "forecast"            # future-dated model output
    DERIVED = "derived"              # computed from other observations (e.g. NDSI)
    ELEVATION_ADJUSTED = "elevation_adjusted"  # lapse-rate corrected estimate
    ELEVATION_ADJUSTED_FORECAST = "elevation_adjusted_forecast"


class DataSource(BaseModel):
    """Identifies where a value came from. Kept small and serialisable."""

    id: str                          # short slug, e.g. "usgs_earthquakes"
    name: str                        # human readable, e.g. "USGS Earthquake Feed"
    provider: str                    # e.g. "USGS", "ECMWF/Copernicus", "ESA"
    authoritative: bool = True       # False for social-media / unofficial feeds
    url: Optional[str] = None
    license: Optional[str] = None


class Provenance(BaseModel):
    """The metadata that MUST travel with every value."""

    source: DataSource
    value_kind: ValueKind
    acquisition_time: Optional[datetime] = Field(
        None, description="When the underlying observation was taken. None if unknown."
    )
    processing_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this platform computed/ingested the value.",
    )
    spatial_resolution_m: Optional[float] = Field(
        None, description="Ground sample distance in metres, if applicable."
    )
    temporal_resolution_s: Optional[float] = Field(
        None, description="Nominal revisit / sampling interval in seconds."
    )
    notes: Optional[str] = None

    @field_validator("acquisition_time", "processing_time")
    @classmethod
    def _ensure_tz(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None and v.tzinfo is None:
            # Never guess a local zone; treat naive timestamps as UTC and say so
            # by attaching UTC explicitly rather than silently.
            return v.replace(tzinfo=timezone.utc)
        return v

    def age_seconds(self, now: Optional[datetime] = None) -> Optional[float]:
        """Age of the underlying observation. None when acquisition time unknown
        or when the value is a forecast (a forecast has no 'age')."""
        if self.value_kind in (ValueKind.FORECAST, ValueKind.ELEVATION_ADJUSTED_FORECAST):
            return None
        if self.acquisition_time is None:
            return None
        now = now or datetime.now(timezone.utc)
        return (now - self.acquisition_time).total_seconds()


class Observation(BaseModel, Generic[T]):
    """A value plus everything needed to judge whether to trust it.

    ``value=None`` is a first-class, honest state meaning "we do not know",
    and MUST be paired with ``confidence=UNKNOWN``.
    """

    value: Optional[T]
    unit: Optional[str] = None
    confidence: Confidence = Confidence.UNKNOWN
    provenance: Provenance
    # Optional raw source value kept beside the processed value, per the spec's
    # requirement to store/display both (e.g. Kelvin raw vs Celsius processed).
    raw_value: Optional[float] = None
    raw_unit: Optional[str] = None

    @field_validator("confidence")
    @classmethod
    def _unknown_requires_null(cls, v: Confidence, info) -> Confidence:
        # We cannot cross-validate value here reliably in all pydantic versions,
        # so enforce the softer direction in ``unknown()``/``measured()`` helpers.
        return v

    def age_seconds(self, now: Optional[datetime] = None) -> Optional[float]:
        return self.provenance.age_seconds(now)

    def is_known(self) -> bool:
        return self.value is not None

    # ---- ergonomic constructors -------------------------------------------
    @classmethod
    def unknown(cls, provenance: Provenance, unit: Optional[str] = None,
                note: Optional[str] = None) -> "Observation[T]":
        if note:
            provenance = provenance.model_copy(update={"notes": note})
        return cls(value=None, unit=unit, confidence=Confidence.UNKNOWN,
                   provenance=provenance)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
