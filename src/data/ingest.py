"""Data ingestion with raw-file retention and provenance metadata.

Every retrieval stores the exact bytes received under data/raw/<source>/,
keyed by SHA-256, with a metadata sidecar in data/metadata/. Parsed values
become `Observation`s with status "retrieved". Nothing is ever fabricated:
if a fetch fails, the caller receives `DataUnavailable` and the requirement
stays "pending".

Fetching public statistics is a read-only operation and does not require
human approval. Any write to an external system does (see
src/orchestrator/approvals.py).
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

from src.common import DATA_DIR, ROOT, sha256_bytes, utc_now, write_json
from src.research.observations import Observation

WB_API = "https://api.worldbank.org/v2/country/{country}/indicator/{code}?format=json&per_page=200"
IMF_API = "https://www.imf.org/external/datamapper/api/v1/{code}/{country}"


class DataUnavailable(RuntimeError):
    """Raised when a source cannot be reached or returns unusable content."""


@dataclass(frozen=True)
class RawRecord:
    source_id: str
    url: str
    sha256: str
    raw_path: str  # relative to repo root
    retrieved_at: str
    content_type: str


def store_raw(content: bytes, source_id: str, url: str, content_type: str = "application/json",
              data_dir: Path = DATA_DIR, root: Path = ROOT) -> RawRecord:
    digest = sha256_bytes(content)
    ext = ".json" if "json" in content_type else ".csv" if "csv" in content_type else ".bin"
    raw_file = data_dir / "raw" / source_id / f"{digest}{ext}"
    raw_file.parent.mkdir(parents=True, exist_ok=True)
    if not raw_file.exists():
        raw_file.write_bytes(content)
    rec = RawRecord(source_id, url, digest, str(raw_file.relative_to(root)), utc_now(), content_type)
    write_json(data_dir / "metadata" / f"{digest}.json", rec.__dict__)
    return rec


def http_get(url: str, timeout: float = 30.0) -> bytes:
    try:
        import requests
    except ImportError as exc:  # pragma: no cover
        raise DataUnavailable("requests is not installed") from exc
    try:
        resp = requests.get(url, timeout=timeout)
    except Exception as exc:  # network errors, proxy denials
        raise DataUnavailable(f"{url}: {type(exc).__name__}: {exc}") from exc
    if resp.status_code != 200:
        raise DataUnavailable(f"{url}: HTTP {resp.status_code}")
    return resp.content


def parse_worldbank(content: bytes) -> tuple[dict, list[tuple[str, float]]]:
    """Parse a World Bank API v2 JSON response -> (metadata, [(year, value)])."""
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise DataUnavailable("World Bank response is not JSON") from exc
    if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
        msg = payload[0].get("message") if isinstance(payload, list) and payload and isinstance(payload[0], dict) else None
        raise DataUnavailable(f"World Bank response has no data rows: {msg}")
    meta = payload[0]
    rows = [(str(r["date"]), float(r["value"])) for r in payload[1] if r.get("value") is not None]
    vintage = meta.get("lastupdated")
    return {"lastupdated": vintage, "total": meta.get("total")}, rows


def parse_imf_datamapper(content: bytes, code: str, country: str) -> tuple[dict, list[tuple[str, float]]]:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise DataUnavailable("IMF response is not JSON") from exc
    series = payload.get("values", {}).get(code, {}).get(country)
    if not series:
        raise DataUnavailable(f"IMF DataMapper has no {code}/{country} series")
    rows = sorted((str(y), float(v)) for y, v in series.items() if v is not None)
    # DataMapper includes projections; the caller must not treat them as outturns.
    return {"api_version": payload.get("api", {}).get("version")}, rows


WB_UNIT_HINTS = {
    "NY.GDP.MKTP.CD": "USD_current", "NY.GDP.MKTP.CN": "NPR_current", "SP.POP.TOTL": "persons",
    "PA.NUS.FCRF": "NPR_per_USD", "FI.RES.TOTL.MO": "months", "DT.DOD.DECT.CD": "USD_current",
}
IMF_UNIT_HINTS = {"NGDPD": "USD_current_bn", "LP": "persons_mn"}


def observations_from_rows(variable: str, rows: list[tuple[str, float]], unit: str, raw: RawRecord,
                           vintage: str | None, recorded_by: str, notes: str = "") -> list[Observation]:
    return [
        Observation(
            variable=variable, country="NPL", period=period, unit=unit, status="retrieved", value=value,
            source_id=raw.source_id, source_url=raw.url, data_vintage=vintage, retrieved_at=raw.retrieved_at,
            retrieval_method="api", raw_sha256=raw.sha256, raw_path=raw.raw_path, recorded_by=recorded_by,
            notes=notes,
        )
        for period, value in rows
    ]


def fetch_worldbank(variable: str, code: str, recorded_by: str, getter=http_get, **store_kw) -> list[Observation]:
    url = WB_API.format(country="NPL", code=code)
    content = getter(url)
    meta, rows = parse_worldbank(content)
    raw = store_raw(content, "wb_wdi", url, **store_kw)
    unit = WB_UNIT_HINTS.get(code, "percent")
    return observations_from_rows(variable, rows, unit, raw, meta.get("lastupdated"), recorded_by,
                                  notes=f"WDI series {code}; calendar-year basis (Nepal fiscal year differs)")


def fetch_imf(variable: str, code: str, recorded_by: str, getter=http_get, **store_kw) -> list[Observation]:
    url = IMF_API.format(country="NPL", code=code)
    content = getter(url)
    meta, rows = parse_imf_datamapper(content, code, "NPL")
    raw = store_raw(content, "imf_weo", url, **store_kw)
    unit = IMF_UNIT_HINTS.get(code, "percent")
    return observations_from_rows(variable, rows, unit, raw, meta.get("api_version"), recorded_by,
                                  notes=f"IMF DataMapper {code}; later years are IMF projections, not outturns")


REQUIRED_MANUAL_META = ("source_id", "source_url", "document_title", "publication_date", "variable", "unit",
                        "recorded_by")


def ingest_manual_csv(csv_path: Path, meta: dict, **store_kw) -> list[Observation]:
    """Ingest a table a human downloaded from an official publication.

    The CSV must have `period,value` columns. `meta` must name the document
    and publication date so the value can be traced to its origin.
    """
    missing = [k for k in REQUIRED_MANUAL_META if not meta.get(k)]
    if missing:
        raise ValueError(f"manual ingestion metadata missing: {missing}")
    content = Path(csv_path).read_bytes()
    raw = store_raw(content, meta["source_id"], meta["source_url"], content_type="text/csv", **store_kw)
    reader = csv.DictReader(content.decode("utf-8").splitlines())
    if reader.fieldnames is None or not {"period", "value"} <= set(reader.fieldnames):
        raise ValueError("CSV must have 'period' and 'value' columns")
    out = []
    for row in reader:
        if row["value"].strip() == "":
            continue
        out.append(Observation(
            variable=meta["variable"], country=meta.get("country", "NPL"), period=row["period"].strip(),
            unit=meta["unit"], status="retrieved", value=float(row["value"]), source_id=meta["source_id"],
            source_url=meta["source_url"], document_title=meta["document_title"],
            publication_date=meta["publication_date"], data_vintage=meta.get("data_vintage"),
            retrieved_at=raw.retrieved_at, retrieval_method="manual_download", raw_sha256=raw.sha256,
            raw_path=raw.raw_path, recorded_by=meta["recorded_by"], notes=meta.get("notes", ""),
        ))
    return out
