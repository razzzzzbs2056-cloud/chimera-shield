"""Report generation reproduces audit findings verbatim and never shows invented values."""
import json

from src.auditing.auditors import GeopoliticalAuditor
from src.auditing.ledger import AuditLedger
from src.data.baseline import build_baseline
from src.reporting import reports as R
from src.research.observations import ObservationStore


def test_audit_report_reproduces_reasons_verbatim(tmp_path):
    ledger = AuditLedger(tmp_path / "l.jsonl")
    text = "Dissent: the transit assumption ignores monsoon road closures (28B)."
    GeopoliticalAuditor(ledger).dissent("SCN-S02", {"id": "SCN-S02"}, text, "UNVERIFIED")
    out = R.audit_report(ledger, tmp_path / "a.md").read_text()
    assert text in out and "DISSENT" in out and "chain integrity: OK" in out


def test_audit_report_flags_broken_chain(tmp_path):
    ledger = AuditLedger(tmp_path / "l.jsonl")
    GeopoliticalAuditor(ledger).dissent("X", {"id": "X"}, "reason", "UNVERIFIED")
    rec = json.loads(ledger.path.read_text())
    rec["reasons"] = ["edited"]
    ledger.path.write_text(json.dumps(rec) + "\n")
    assert "BROKEN" in R.audit_report(ledger, tmp_path / "a.md").read_text()


def test_baseline_report_marks_pending(tmp_path):
    b = tmp_path / "baseline.json"
    data = build_baseline(online=False, store=ObservationStore(tmp_path / "o.jsonl"), out_path=b)
    assert data["summary"]["available"] == 0
    text = R.baseline_report(tmp_path / "b.md", baseline_path=b).read_text()
    assert "**PENDING**" in text and "No empirical values are reported" in text


def test_target_and_architecture_reports(tmp_path):
    t = R.target_report(tmp_path / "t.md").read_text()
    assert "PARAMETRIC" in t and "hypothetical" in t.lower() and "does **not** establish feasibility" in t
    a = R.architecture_report(tmp_path / "arch.md").read_text()
    assert "Main agents: **29**" in a and "Subagent task specifications: **111**" in a


def test_strategy_and_exposure_reports(tmp_path):
    s = R.strategy_report(tmp_path / "s.md").read_text()
    assert "STR-0" in s and "STR-E" in s and "None is endorsed or ranked" in s
    e = R.exposure_report(tmp_path / "e.md").read_text()
    assert "EXP-01" in e and "**PENDING**" in e


def test_data_gaps_report(tmp_path):
    b = tmp_path / "baseline.json"
    build_baseline(online=False, store=ObservationStore(tmp_path / "o.jsonl"), out_path=b)
    text = R.data_gaps_report(tmp_path / "g.md", baseline_path=b).read_text()
    assert "gdp_nominal_usd" in text and "S10" in text and "EXP-20" in text
