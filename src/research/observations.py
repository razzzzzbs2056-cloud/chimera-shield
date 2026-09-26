"""Observation store: every empirical value with its provenance.

Status lifecycle
----------------
pending    — required but not yet retrieved. `value` MUST be None.
retrieved  — obtained from a primary document or API; raw file hashed and stored.
verified   — retrieved AND independently checked by Agent 15A or 28A.
disputed   — a verified/retrieved value that conflicts with another source;
             both are kept and the methodological difference is investigated.
superseded — replaced by a newer vintage; kept for the audit trail.

Nothing in this module can create a value without a source. Validation
(`validate_observation`) is the missing-source detector used by tests,
auditors and report generation.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from src.common import ROOT, RESEARCH_DIR, sha256_obj, utc_now

from .sources import SourceCatalog

STORE_PATH = RESEARCH_DIR / "sources" / "observations.jsonl"
STATUSES = {"pending", "retrieved", "verified", "disputed", "superseded"}
VALUED_STATUSES = {"retrieved", "verified", "disputed", "superseded"}


@dataclass
class Observation:
    variable: str
    country: str
    period: str
    unit: str
    status: str
    value: float | None = None
    source_id: str | None = None
    source_url: str | None = None
    document_title: str | None = None
    publication_date: str | None = None
    data_vintage: str | None = None
    retrieved_at: str | None = None
    retrieval_method: str | None = None  # api | manual_download | document
    raw_sha256: str | None = None
    raw_path: str | None = None
    recorded_by: str | None = None
    notes: str = ""
    verified_by: str | None = None
    id: str = field(default="")

    def __post_init__(self) -> None:
        if not self.id:
            key = {
                "variable": self.variable, "country": self.country, "period": self.period,
                "unit": self.unit, "source_id": self.source_id, "data_vintage": self.data_vintage,
                "value": self.value, "status": self.status,
            }
            self.id = "obs-" + sha256_obj(key)[:12]

    def to_dict(self) -> dict:
        return asdict(self)


def validate_observation(o: Observation, catalog: SourceCatalog | None = None, root: Path = ROOT) -> list[str]:
    """Return a list of problems (empty = valid)."""
    problems = []
    if o.status not in STATUSES:
        problems.append(f"{o.id}: invalid status {o.status!r}")
    if o.status == "pending":
        if o.value is not None:
            problems.append(f"{o.id}: pending observation carries a value (fabrication risk)")
        return problems
    if o.value is None and o.status in VALUED_STATUSES:
        problems.append(f"{o.id}: status {o.status} but no value")
    required = ["source_id", "source_url", "retrieved_at", "retrieval_method", "raw_sha256", "raw_path"]
    for name in required:
        if not getattr(o, name):
            problems.append(f"{o.id}: missing {name}")
    if catalog is not None and o.source_id and o.source_id not in catalog:
        problems.append(f"{o.id}: source_id {o.source_id!r} not in source catalog")
    if o.raw_path and not (root / o.raw_path).exists():
        problems.append(f"{o.id}: raw file {o.raw_path} not found")
    if o.status == "verified" and not o.verified_by:
        problems.append(f"{o.id}: verified without verified_by")
    if not o.publication_date and not o.data_vintage:
        problems.append(f"{o.id}: neither publication_date nor data_vintage recorded")
    return problems


class ObservationStore:
    """Append-only JSONL store."""

    def __init__(self, path: Path = STORE_PATH):
        self.path = path

    def load(self) -> list[Observation]:
        if not self.path.exists():
            return []
        out = []
        with open(self.path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    out.append(Observation(**json.loads(line)))
        return out

    def append(self, obs: Observation, catalog: SourceCatalog | None = None, root: Path = ROOT) -> Observation:
        problems = validate_observation(obs, catalog, root)
        if problems:
            raise ValueError("; ".join(problems))
        existing = {o.id for o in self.load()}
        if obs.id in existing:
            return obs  # exact duplicate: idempotent
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(obs.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
        return obs

    def latest(self, variable: str, country: str = "NPL") -> list[Observation]:
        return [o for o in self.load() if o.variable == variable and o.country == country
                and o.status in {"retrieved", "verified", "disputed"}]


def find_duplicates(observations: list[Observation]) -> list[tuple[str, str]]:
    """Pairs of observations that repeat the same value from the same source and vintage."""
    seen: dict[tuple, str] = {}
    dups = []
    for o in observations:
        key = (o.variable, o.country, o.period, o.unit, o.source_id, o.data_vintage, o.value)
        if key in seen:
            dups.append((seen[key], o.id))
        else:
            seen[key] = o.id
    return dups


def find_conflicts(observations: list[Observation], rel_tol: float = 1e-3) -> list[dict]:
    """Same variable/country/period/unit with materially different values.

    Both values are preserved; the caller (Agent 00B) records the
    methodological investigation. Superseded observations are ignored.
    """
    groups: dict[tuple, list[Observation]] = {}
    for o in observations:
        if o.value is None or o.status == "superseded":
            continue
        groups.setdefault((o.variable, o.country, o.period, o.unit), []).append(o)
    conflicts = []
    for key, obs in groups.items():
        for i in range(len(obs)):
            for j in range(i + 1, len(obs)):
                a, b = obs[i], obs[j]
                denom = max(abs(a.value), abs(b.value), 1e-12)
                rel = abs(a.value - b.value) / denom
                if rel > rel_tol:
                    conflicts.append({
                        "variable": key[0], "country": key[1], "period": key[2], "unit": key[3],
                        "a": {"id": a.id, "value": a.value, "source_id": a.source_id, "vintage": a.data_vintage},
                        "b": {"id": b.id, "value": b.value, "source_id": b.source_id, "vintage": b.data_vintage},
                        "relative_difference": rel,
                        "detected_at": utc_now(),
                        "resolution": "open — investigate definitions, coverage, vintage and methodology",
                    })
    return conflicts
