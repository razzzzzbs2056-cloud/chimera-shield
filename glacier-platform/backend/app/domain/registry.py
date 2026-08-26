"""
Glacier registry + report cache.

Holds the set of monitored glaciers (seeded defaults plus any the administrator
adds at runtime) and a short TTL cache of assembled reports so we don't refetch
identical upstream data on every request. The cache stores the *observation
timestamps*, so freshness is recomputed on read and never misrepresented as
newer than the underlying data.
"""
from __future__ import annotations

import time
from typing import Dict, List, Optional

from .assemble import assemble_glacier_report
from .glaciers import ReferenceGlacier, SEED_GLACIERS

# Runtime registry (seed + admin-added). A production deployment persists this
# in PostGIS (see db/schema.sql -> glaciers table); this in-memory copy keeps
# the API runnable without a database for evaluation.
_REGISTRY: Dict[str, ReferenceGlacier] = {g.id: g for g in SEED_GLACIERS}

_CACHE: Dict[str, tuple] = {}      # glacier_id -> (expires_at, report)
_CACHE_TTL_S = 300                 # 5 min; upstream cadence is >= hourly anyway


def list_glaciers() -> List[ReferenceGlacier]:
    return list(_REGISTRY.values())


def get(glacier_id: str) -> Optional[ReferenceGlacier]:
    return _REGISTRY.get(glacier_id)


def add_glacier(g: ReferenceGlacier) -> ReferenceGlacier:
    _REGISTRY[g.id] = g
    _CACHE.pop(g.id, None)
    return g


async def get_report(glacier_id: str, radius_km: Optional[float] = None,
                     force: bool = False) -> Optional[dict]:
    g = _REGISTRY.get(glacier_id)
    if g is None:
        return None
    now = time.time()
    cached = _CACHE.get(glacier_id)
    if cached and not force and cached[0] > now and radius_km is None:
        return cached[1]
    report = await assemble_glacier_report(g, radius_km=radius_km)
    if radius_km is None:
        _CACHE[glacier_id] = (now + _CACHE_TTL_S, report)
    return report
