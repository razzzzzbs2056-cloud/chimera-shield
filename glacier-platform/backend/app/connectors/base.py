"""Connector base utilities.

A connector's job is to fetch real data from a real provider and return it
wrapped in ``Observation`` envelopes with correct provenance -- or to return
UNKNOWN when data is unavailable / credentials are missing. A connector must
never invent a number.
"""
from __future__ import annotations

import math
from typing import Any, Optional

import httpx

from ..config import settings


class ConnectorError(Exception):
    """Raised for a genuine fetch/parse failure. Callers convert to UNKNOWN
    observations rather than propagating fabricated data."""


async def get_json(url: str, params: Optional[dict] = None,
                   headers: Optional[dict] = None,
                   timeout: Optional[float] = None) -> Any:
    timeout = timeout or settings.http_timeout_s
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        return resp.json()


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km."""
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2)
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))
