"""Missing-source detection, duplicates and contradictory inputs."""
import pytest

from src.research.observations import (Observation, ObservationStore, find_conflicts, find_duplicates,
                                       validate_observation)
from src.research.sources import SourceCatalog


def obs(tmp_path, value=1.0, source="wb_wdi", period="2020", vintage="v1", **kw):
    raw = tmp_path / "raw.json"
    raw.write_text("{}")
    base = dict(variable="gdp", country="NPL", period=period, unit="USD_current", status="retrieved", value=value,
                source_id=source, source_url="https://example.invalid", retrieved_at="2099-01-01T00:00:00+00:00",
                retrieval_method="api", raw_sha256="0" * 64, raw_path="raw.json", data_vintage=vintage)
    base.update(kw)
    return Observation(**base)


def test_valid_observation(tmp_path):
    assert validate_observation(obs(tmp_path), SourceCatalog(), root=tmp_path) == []


@pytest.mark.parametrize("field", ["source_id", "source_url", "retrieved_at", "raw_sha256", "raw_path"])
def test_missing_source_fields_detected(tmp_path, field):
    o = obs(tmp_path, **{field: None})
    assert any(field in p for p in validate_observation(o, SourceCatalog(), root=tmp_path))


def test_unknown_source_detected(tmp_path):
    probs = validate_observation(obs(tmp_path, source="made_up_source"), SourceCatalog(), root=tmp_path)
    assert any("not in source catalog" in p for p in probs)


def test_missing_raw_file_detected(tmp_path):
    probs = validate_observation(obs(tmp_path, raw_path="nope.json"), SourceCatalog(), root=tmp_path)
    assert any("not found" in p for p in probs)


def test_pending_with_value_is_rejected():
    o = Observation("gdp", "NPL", "2020", "USD_current", "pending", value=42.0)
    assert any("fabrication" in p for p in validate_observation(o))


def test_verified_requires_verifier(tmp_path):
    assert any("verified_by" in p for p in validate_observation(obs(tmp_path, status="verified"), root=tmp_path))


def test_store_rejects_invalid_and_is_idempotent(tmp_path):
    store = ObservationStore(tmp_path / "o.jsonl")
    with pytest.raises(ValueError):
        store.append(obs(tmp_path, source_url=None), SourceCatalog(), root=tmp_path)
    good = obs(tmp_path)
    store.append(good, SourceCatalog(), root=tmp_path)
    store.append(good, SourceCatalog(), root=tmp_path)
    assert len(store.load()) == 1


def test_duplicates_detected(tmp_path):
    a = obs(tmp_path)
    b = obs(tmp_path, notes="re-entered")
    b.id = "obs-other"
    assert find_duplicates([a, b]) == [(a.id, "obs-other")]


def test_contradictory_sources_preserved_as_conflict(tmp_path):
    a = obs(tmp_path, value=100.0, source="wb_wdi")
    b = obs(tmp_path, value=110.0, source="imf_weo")
    c = find_conflicts([a, b])
    assert len(c) == 1 and c[0]["a"]["value"] == 100.0 and c[0]["b"]["value"] == 110.0
    assert "investigate" in c[0]["resolution"]


def test_small_differences_within_tolerance_not_conflicts(tmp_path):
    assert find_conflicts([obs(tmp_path, value=100.0), obs(tmp_path, value=100.00001, source="imf_weo")]) == []


def test_source_catalog_ranking():
    cat = SourceCatalog()
    assert cat.rank(["academic", "imf_weo", "nso_nepal"]) == ["nso_nepal", "imf_weo", "academic"]
