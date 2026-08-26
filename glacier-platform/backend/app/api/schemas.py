"""Pydantic request/response schemas for the API surface."""
from __future__ import annotations

from typing import List, Optional, Tuple

from pydantic import BaseModel, Field


class GlacierSummary(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    catchment: str
    river_system: str
    monitor_radius_km: float


class AddGlacierRequest(BaseModel):
    id: str = Field(..., description="Short unique slug")
    name: str
    latitude: float
    longitude: float
    terminus_elevation_m: Optional[float] = None
    median_elevation_m: Optional[float] = None
    headwall_elevation_m: Optional[float] = None
    country: str = "unknown"
    catchment: str = "unknown"
    river_system: str = "unknown"
    monitor_radius_km: float = 100.0
    polygon: Optional[List[Tuple[float, float]]] = Field(
        None, description="[(lon,lat), ...] optional glacier polygon")
