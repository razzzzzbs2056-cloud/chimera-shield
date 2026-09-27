"""Scheduling, resumability, approvals and finding validation."""
import pytest

from src.agents.catalog import load_catalog, subagent_dependencies
from src.orchestrator.approvals import ApprovalRequired, record_approval, require_approval
from src.orchestrator.findings import validate_finding
from src.orchestrator.taskgraph import RunState, batches, task_brief, waves
from src.research.observations import ObservationStore


def test_waves_respect_dependencies():
    deps = subagent_dependencies(load_catalog())
    wv = waves(deps)
    level = {t: i for i, w in enumerate(wv) for t in w}
    assert sum(len(w) for w in wv) == 111
    for t, ds in deps.items():
        assert all(level[d] < level[t] for d in ds)


def test_batches_limit_parallelism():
    b = batches([["a", "b", "c"], ["d"]], 2)
    assert b == [["a", "b"], ["c"], ["d"]]
    with pytest.raises(ValueError):
        batches([["a"]], 0)


def test_run_state_is_resumable(tmp_path):
    rs = RunState(tmp_path / "state.json")
    ready = rs.ready()
    assert "00A" in ready and "15A" not in ready
    with pytest.raises(ValueError):
        rs.set_status("15A", "in_progress")  # dependencies not done
    rs.set_status("00A", "in_progress")
    rs.set_status("00A", "done", output="x.json")
    resumed = RunState(tmp_path / "state.json")  # a new process picks up saved state
    assert resumed.load()["tasks"]["00A"]["status"] == "done"
    assert "00A" not in resumed.ready()
    assert resumed.summary()["done"] == 1


def test_task_brief_mentions_spec():
    assert "src/agents/specs/05B.md" in task_brief("05B")


def test_approval_gate(tmp_path):
    path = tmp_path / "approvals.json"
    detail = {"target": "email", "to": "someone"}
    with pytest.raises(ApprovalRequired):
        require_approval("contact_third_party", detail, path)
    with pytest.raises(ValueError):
        record_approval("contact_third_party", detail, "Agent 00", path)
    with pytest.raises(ValueError):
        record_approval("contact_third_party", detail, "15A", path)
    record_approval("contact_third_party", detail, "Human Reviewer", path)
    assert require_approval("contact_third_party", detail, path)["approver"] == "Human Reviewer"
    with pytest.raises(ApprovalRequired):
        require_approval("contact_third_party", {"target": "other"}, path)


def _finding(**over):
    doc = {"subagent_id": "22E", "task_id": "t1", "generated_at": "2099-01-01", "summary": "s",
           "findings": [{"claim": "export price", "type": "pending", "value": None}],
           "data_gaps": ["export price series"], "assumptions": [], "challenges": [],
           "uncertainty": "high", "specific": {"opportunity_cost_table": "pending"}}
    doc.update(over)
    return doc


def test_valid_pending_finding(tmp_path):
    assert validate_finding(_finding(), ObservationStore(tmp_path / "o.jsonl")) == []


def test_fact_without_evidence_rejected(tmp_path):
    doc = _finding(findings=[{"claim": "price is 5", "type": "fact", "value": 5.0, "unit": "percent"}])
    assert any("observation_ids" in p for p in validate_finding(doc, ObservationStore(tmp_path / "o.jsonl")))


def test_missing_specific_field_rejected(tmp_path):
    assert any("opportunity_cost_table" in p
               for p in validate_finding(_finding(specific={}), ObservationStore(tmp_path / "o.jsonl")))


def test_source_leads_validated(tmp_path):
    store = ObservationStore(tmp_path / "o.jsonl")
    good = {"url": "https://example.invalid/r.pdf", "title": "T", "publisher": "P", "contains": "table 1"}
    assert validate_finding(_finding(source_leads=[good]), store) == []
    bad = dict(good, value=5.0)
    assert any("must not carry values" in p for p in validate_finding(_finding(source_leads=[bad]), store))
    assert any("url" in p for p in validate_finding(_finding(source_leads=[dict(good, url="ftp://x")]), store))


def test_collect_and_fetch_leads(tmp_path):
    import json
    from src.data.ingest import DataUnavailable
    from src.research.leads import collect_leads, fetch_leads
    d = tmp_path / "findings" / "05"
    d.mkdir(parents=True)
    lead = {"url": "https://example.invalid/r.pdf", "title": "T", "publisher": "P", "contains": "table 1"}
    (d / "05A-t.json").write_text(json.dumps(_finding(subagent_id="05A", source_leads=[lead])))
    (d / "05C-t.json").write_text(json.dumps(_finding(subagent_id="05C", source_leads=[lead])))
    out = tmp_path / "leads.json"
    data = collect_leads(tmp_path / "findings", out)
    assert len(data["leads"]) == 1 and data["leads"][0]["found_by"] == ["05A", "05C"]

    def blocked(url):
        raise DataUnavailable("blocked")
    assert fetch_leads(out, getter=blocked)["leads"][0]["status"] == "unavailable"
    ok = fetch_leads(out, getter=lambda url: b"%PDF", data_dir=tmp_path / "data", root=tmp_path)
    assert ok["leads"][0]["status"] == "fetched" and ok["leads"][0]["raw_sha256"]


def test_invalid_unit_code_rejected(tmp_path):
    doc = _finding(findings=[{"claim": "x", "type": "pending", "value": None, "unit": "USD"}])
    assert any("unknown unit" in p for p in validate_finding(doc, ObservationStore(tmp_path / "o.jsonl")))


def test_assumption_labels_enforced(tmp_path):
    store = ObservationStore(tmp_path / "o.jsonl")
    ok = _finding(assumptions=[{"id": "A1", "text": "t", "basis": "assumption"}])
    assert validate_finding(ok, store) == []
    bad = _finding(assumptions=["plain string", {"id": "A2", "text": "t", "basis": "design"}])
    probs = validate_finding(bad, store)
    assert any("assumption 0" in p for p in probs) and any("E2" in p for p in probs)
