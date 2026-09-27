"""Source leads: primary documents located by agents but not yet downloaded.

When the environment cannot reach source hosts, agents still locate the exact
documents (URL, publisher, what table/series they contain). `collect_leads`
merges them from all finding files; `fetch_leads` downloads each one when the
network allows, keeping the raw bytes (hashed) so values can then be extracted
and ingested as observations. Leads never carry values.
"""

from __future__ import annotations

from pathlib import Path

from src.common import RESEARCH_DIR, load_json, utc_now, write_json
from src.data.ingest import DataUnavailable, http_get, store_raw

LEADS_PATH = RESEARCH_DIR / "sources" / "source_leads.json"
FINDINGS_DIR = RESEARCH_DIR / "findings"


def collect_leads(findings_dir: Path = FINDINGS_DIR, out_path: Path = LEADS_PATH) -> dict:
    existing = load_json(out_path)["leads"] if out_path.exists() else []
    by_url = {lead["url"]: lead for lead in existing}
    for f in sorted(findings_dir.glob("*/*.json")):
        doc = load_json(f)
        for lead in doc.get("source_leads", []) or []:
            entry = by_url.setdefault(lead["url"], {
                "url": lead["url"], "title": lead.get("title"), "publisher": lead.get("publisher"),
                "source_id": lead.get("source_id"), "contains": [], "found_by": [], "status": "not_fetched",
            })
            if lead.get("contains") and lead["contains"] not in entry["contains"]:
                entry["contains"].append(lead["contains"])
            if doc["subagent_id"] not in entry["found_by"]:
                entry["found_by"].append(doc["subagent_id"])
    data = {"updated_at": utc_now(), "leads": sorted(by_url.values(), key=lambda x: x["url"])}
    write_json(out_path, data)
    return data


def fetch_leads(path: Path = LEADS_PATH, getter=http_get, **store_kw) -> dict:
    data = load_json(path)
    for lead in data["leads"]:
        if lead["status"] == "fetched":
            continue
        try:
            content = getter(lead["url"])
            ctype = "application/pdf" if lead["url"].lower().endswith(".pdf") else "application/octet-stream"
            rec = store_raw(content, lead.get("source_id") or "leads", lead["url"], content_type=ctype, **store_kw)
            lead.update(status="fetched", raw_path=rec.raw_path, raw_sha256=rec.sha256, fetched_at=rec.retrieved_at)
        except DataUnavailable as exc:
            lead.update(status="unavailable", last_error=str(exc)[:300], last_attempt=utc_now())
    data["updated_at"] = utc_now()
    write_json(path, data)
    return data
