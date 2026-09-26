"""Validation of subagent finding files against their output schema."""

from __future__ import annotations

from pathlib import Path

from src.common import CONFIG_DIR, load_json
from src.research.observations import ObservationStore

FINDING_TYPES = {"fact", "estimate", "assumption", "pending"}


def _schema_for(sub_id: str) -> dict:
    subs = load_json(CONFIG_DIR / "subagents.json")["subagents"]
    for s in subs:
        if s["id"] == sub_id:
            return s["output_schema"]
    raise KeyError(f"unknown subagent {sub_id}")


def validate_finding(doc: dict, store: ObservationStore | None = None) -> list[str]:
    problems = []
    sub_id = doc.get("subagent_id")
    if not sub_id:
        return ["missing subagent_id"]
    schema = _schema_for(sub_id)
    for f in schema["required"]:
        if f not in doc:
            problems.append(f"missing field {f}")
    specific = doc.get("specific", {}) or {}
    for f in schema["properties"]["specific"]["required"]:
        if f not in specific:
            problems.append(f"missing specific field {f}")
    known = {o.id: o for o in (store or ObservationStore()).load()}
    for i, fnd in enumerate(doc.get("findings", [])):
        t = fnd.get("type")
        if t not in FINDING_TYPES:
            problems.append(f"finding {i}: invalid type {t!r}")
        if not fnd.get("claim"):
            problems.append(f"finding {i}: missing claim")
        if t in ("fact", "estimate"):
            ids = fnd.get("observation_ids") or []
            if not ids:
                problems.append(f"finding {i}: {t} without observation_ids")
            for oid in ids:
                if oid not in known:
                    problems.append(f"finding {i}: observation {oid} not in store")
            if fnd.get("value") is not None and not fnd.get("unit"):
                problems.append(f"finding {i}: value without unit")
        if t == "pending" and fnd.get("value") is not None:
            problems.append(f"finding {i}: pending finding carries a value")
    if not str(doc.get("uncertainty", "")).strip():
        problems.append("uncertainty statement is empty")
    return problems


def validate_finding_file(path: Path) -> list[str]:
    return validate_finding(load_json(path))
