"""Data ingestion. All payloads here are SYNTHETIC test fixtures, not Nepal data."""
import json

import pytest

from src.data.baseline import build_baseline
from src.data.ingest import (DataUnavailable, fetch_imf, fetch_worldbank, ingest_manual_csv, parse_worldbank,
                             store_raw)
from src.research.observations import ObservationStore, validate_observation
from src.research.sources import SourceCatalog

WB_FIXTURE = json.dumps([
    {"page": 1, "pages": 1, "per_page": 200, "total": 3, "sourceid": "2", "lastupdated": "2099-01-01"},
    [
        {"indicator": {"id": "TEST"}, "date": "2002", "value": 3.0},
        {"indicator": {"id": "TEST"}, "date": "2001", "value": None},
        {"indicator": {"id": "TEST"}, "date": "2000", "value": 1.5},
    ],
]).encode()
IMF_FIXTURE = json.dumps({"values": {"NGDPD": {"NPL": {"2000": 1.0, "2001": 2.0}}},
                          "api": {"version": "test"}}).encode()


def test_parse_worldbank_skips_nulls_and_keeps_vintage():
    meta, rows = parse_worldbank(WB_FIXTURE)
    assert meta["lastupdated"] == "2099-01-01"
    assert rows == [("2002", 3.0), ("2000", 1.5)]


def test_parse_worldbank_error_payload():
    with pytest.raises(DataUnavailable):
        parse_worldbank(json.dumps([{"message": [{"key": "Invalid value"}]}]).encode())


def test_store_raw_hashes_and_writes_metadata(tmp_path):
    rec = store_raw(b"abc", "wb_wdi", "https://example.invalid", data_dir=tmp_path / "data", root=tmp_path)
    assert (tmp_path / rec.raw_path).read_bytes() == b"abc"
    assert rec.sha256 == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert (tmp_path / "data" / "metadata" / f"{rec.sha256}.json").exists()


def test_fetch_worldbank_produces_valid_observations(tmp_path):
    obs = fetch_worldbank("x", "TEST", "01A", getter=lambda url: WB_FIXTURE,
                          data_dir=tmp_path / "data", root=tmp_path)
    assert len(obs) == 2 and all(o.status == "retrieved" for o in obs)
    cat = SourceCatalog()
    assert all(validate_observation(o, cat, root=tmp_path) == [] for o in obs)


def test_fetch_imf(tmp_path):
    obs = fetch_imf("gdp", "NGDPD", "01C", getter=lambda url: IMF_FIXTURE, data_dir=tmp_path / "data", root=tmp_path)
    assert [o.value for o in obs] == [1.0, 2.0] and obs[0].unit == "USD_current_bn"


def test_network_failure_leaves_requirement_pending(tmp_path):
    def failing(url):
        raise DataUnavailable("blocked by test")
    store = ObservationStore(tmp_path / "obs.jsonl")
    b = build_baseline(online=True, store=store, getter=failing, out_path=tmp_path / "baseline.json")
    assert b["summary"]["available"] == 0
    assert all(e["status"] == "PENDING" and e["latest"] is None for e in b["entries"])
    assert any(a["result"] == "unavailable" for e in b["entries"] for a in e["retrieval_attempts"])
    assert store.load() == []  # nothing invented


def test_manual_csv_requires_document_metadata(tmp_path):
    csv = tmp_path / "t.csv"
    csv.write_text("period,value\n2020,1.0\n2021,\n")
    with pytest.raises(ValueError):
        ingest_manual_csv(csv, {"source_id": "nso_nepal"}, data_dir=tmp_path / "data", root=tmp_path)
    meta = {"source_id": "nso_nepal", "source_url": "https://example.invalid/table.pdf",
            "document_title": "TEST TABLE", "publication_date": "2099-01-01", "variable": "t",
            "unit": "percent", "recorded_by": "01A"}
    obs = ingest_manual_csv(csv, meta, data_dir=tmp_path / "data", root=tmp_path)
    assert len(obs) == 1 and obs[0].retrieval_method == "manual_download"
