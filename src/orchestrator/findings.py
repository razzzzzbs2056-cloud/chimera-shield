"""Validation of subagent finding files against their output schema."""

from __future__ import annotations

from pathlib import Path

from src.common import CONFIG_DIR, load_json
from src.economic_model.units import UnitError, parse_unit
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
        if fnd.get("unit"):
            try:
                parse_unit(fnd["unit"])
            except UnitError as exc:
                problems.append(f"finding {i}: {exc} (see src/economic_model/units.py)")
        if t == "pending" and fnd.get("value") is not None:
            problems.append(f"finding {i}: pending finding carries a value")
    if not str(doc.get("uncertainty", "")).strip():
        problems.append("uncertainty statement is empty")
    problems += validate_leads(doc.get("source_leads", []))
    return problems


LEAD_FIELDS = ("url", "title", "publisher", "contains")
LEAD_FORBIDDEN = ("value", "values", "figure", "number")


def validate_leads(leads: list) -> list[str]:
    """Source leads point to primary documents to download later.

    A lead records *where* evidence is, never the evidence itself: numeric
    values seen in search snippets are not retrieved evidence and are refused.
    """
    problems = []
    if not isinstance(leads, list):
        return ["source_leads must be a list"]
    for i, lead in enumerate(leads):
        if not isinstance(lead, dict):
            problems.append(f"lead {i}: must be an object")
            continue
        for f in LEAD_FIELDS:
            if not str(lead.get(f, "")).strip():
                problems.append(f"lead {i}: missing {f}")
        if not str(lead.get("url", "")).startswith(("http://", "https://")):
            problems.append(f"lead {i}: url must be http(s)")
        bad = [f for f in LEAD_FORBIDDEN if f in lead]
        if bad:
            problems.append(f"lead {i}: leads must not carry values ({bad}); retrieve the document instead")
    return problems


def validate_finding_file(path: Path) -> list[str]:
    return validate_finding(load_json(path))
