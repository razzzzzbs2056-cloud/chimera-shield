"""Build the Nepal baseline from the observation store.

`build_baseline(online=True)` first attempts to retrieve each machine-readable
cross-check series and appends successful retrievals to the observation
store. Every requirement without a retrieved value is reported as PENDING
together with the exact data required and the retrieval errors seen.
"""

from __future__ import annotations

from pathlib import Path

from src.common import DATA_DIR, utc_now, write_json
from src.research.observations import ObservationStore, find_conflicts
from src.research.sources import SourceCatalog

from .ingest import DataUnavailable, fetch_imf, fetch_worldbank
from .requirements import REQUIREMENTS

BASELINE_PATH = DATA_DIR / "processed" / "baseline.json"


def _attempt_fetch(req, store: ObservationStore, catalog: SourceCatalog, getter) -> list[dict]:
    attempts = []
    for series in req.api:
        fetch = fetch_worldbank if series["source_id"] == "wb_wdi" else fetch_imf
        kwargs = {"getter": getter} if getter else {}
        try:
            obs = fetch(req.variable, series["code"], req.owner, **kwargs)
            for o in obs:
                store.append(o, catalog)
            attempts.append({"series": series, "result": "retrieved", "rows": len(obs), "at": utc_now()})
        except DataUnavailable as exc:
            attempts.append({"series": series, "result": "unavailable", "error": str(exc), "at": utc_now()})
    return attempts


def build_baseline(online: bool = False, store: ObservationStore | None = None, getter=None,
                   out_path: Path = BASELINE_PATH) -> dict:
    store = store or ObservationStore()
    catalog = SourceCatalog()
    entries = []
    for req in REQUIREMENTS:
        attempts = _attempt_fetch(req, store, catalog, getter) if online else []
        obs = store.latest(req.variable)
        if obs:
            ranked = sorted(obs, key=lambda o: (catalog.get(o.source_id).tier, o.period), reverse=False)
            # most recent period from the highest-priority source
            best_tier = catalog.get(ranked[0].source_id).tier
            top = max((o for o in obs if catalog.get(o.source_id).tier == best_tier), key=lambda o: o.period)
            entry = {
                "variable": req.variable, "status": "available", "latest": {
                    "period": top.period, "value": top.value, "unit": top.unit, "source_id": top.source_id,
                    "observation_id": top.id, "observation_status": top.status, "data_vintage": top.data_vintage,
                },
                "sources_present": sorted({o.source_id for o in obs}),
                "primary_source_retrieved": any(catalog.get(o.source_id).tier == 1 for o in obs),
            }
        else:
            entry = {"variable": req.variable, "status": "PENDING", "latest": None}
        entry.update({
            "description": req.description, "required_unit": req.unit, "owner": req.owner,
            "primary_requirement": req.primary, "cross_check_series": req.api, "periods_required": req.periods,
            "retrieval_attempts": attempts,
        })
        entries.append(entry)
    result = {
        "generated_at": utc_now(),
        "online_attempted": online,
        "summary": {
            "requirements": len(entries),
            "available": sum(e["status"] == "available" for e in entries),
            "pending": sum(e["status"] == "PENDING" for e in entries),
        },
        "conflicts": find_conflicts(store.load()),
        "entries": entries,
    }
    write_json(out_path, result)
    return result
