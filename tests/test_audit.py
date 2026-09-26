"""Independent audit execution, verdict logic and ledger integrity."""
import inspect
import json

import pytest

from src.auditing.auditors import DomesticAuditor, GeopoliticalAuditor, audit_both
from src.auditing.ledger import AuditLedger, AuditRecord, LedgerError


def complete_strategy(**over):
    p = {
        "id": "STR-TEST", "kind": "strategy", "claims": [], "assumptions": [],
        "identity_checks": [{"name": "expenditure_gdp", "passed": True}],
        "uncertainty": "stated", "investment_requirement": {"amount": 1, "unit": "USD_current_bn"},
        "financing": [{"item": "budget", "identified": True}],
        "schedule": {"planned_execution_rate": 0.7, "historical_execution_rate": 0.8},
        "contingent_liabilities": [], "legal_requirements": ["statute X"],
        "distribution": {"by_income": "reported", "by_province": "reported"},
        "environment": {"quantified": True}, "welfare_effects": {"growth": "+", "poverty_inclusion": "+"},
        "international_assumptions": [], "external_financing": [], "regional_dependencies": [],
        "treaty_constraints_checked": True, "probabilities": [], "cross_border_environment": "assessed",
        "compound_shock_tested": True,
    }
    p.update(over)
    return p


@pytest.fixture
def ledger(tmp_path):
    return AuditLedger(tmp_path / "ledger.jsonl")


def test_verified_when_all_checks_pass(ledger):
    r = audit_both(complete_strategy(), {}, ledger)
    assert r["15"].verdict == "VERIFIED" and r["28"].verdict == "VERIFIED"


def test_conditional_on_labelled_assumption(ledger):
    p = complete_strategy(assumptions=[{"id": "A1", "text": "FDI doubles", "basis": "assumption"}])
    rec = DomesticAuditor(ledger).audit(p, {})
    assert rec.verdict == "CONDITIONAL" and any("A1" in r for r in rec.reasons)


def test_conditional_on_unidentified_financing(ledger):
    p = complete_strategy(financing=[{"item": "sovereign bond", "identified": False}])
    rec = DomesticAuditor(ledger).audit(p, {})
    assert rec.verdict == "CONDITIONAL" and any("sovereign bond" in r for r in rec.reasons)


def test_unverified_when_fact_lacks_evidence(ledger):
    p = complete_strategy(claims=[{"text": "exports grew", "type": "fact", "value": 1.0, "unit": "percent"}])
    rec = DomesticAuditor(ledger).audit(p, {})
    assert rec.verdict == "UNVERIFIED" and any("observation_ids" in r for r in rec.reasons)


def test_unverified_when_inputs_pending(ledger):
    p = complete_strategy(claims=[{"text": "base GDP", "type": "pending", "value": None}])
    assert GeopoliticalAuditor(ledger).audit(p, {}).verdict == "UNVERIFIED"


def test_inconsistent_when_identity_fails(ledger):
    p = complete_strategy(identity_checks=[{"name": "production_gdp", "passed": False}])
    rec = DomesticAuditor(ledger).audit(p, {})
    assert rec.verdict == "INCONSISTENT" and any("production_gdp" in r for r in rec.reasons)


def test_inconsistent_on_unsupported_probability(ledger):
    p = complete_strategy(probabilities=[{"event": "war", "probability": 0.3}])
    assert GeopoliticalAuditor(ledger).audit(p, {}).verdict == "INCONSISTENT"


def test_auditor_cannot_be_told_the_verdict():
    for cls in (DomesticAuditor, GeopoliticalAuditor):
        params = set(inspect.signature(cls.audit).parameters)
        assert params == {"self", "proposal", "observations"}


def test_only_auditors_may_write(ledger):
    with pytest.raises(LedgerError):
        ledger.append(AuditRecord("00", [], "X", "h", "VERIFIED", ["because"], []))
    with pytest.raises(LedgerError):
        ledger.append(AuditRecord("15", [], "X", "h", "APPROVED", ["because"], []))
    with pytest.raises(LedgerError):
        ledger.append(AuditRecord("15", [], "X", "h", "VERIFIED", [], []))


def test_ledger_detects_silent_alteration(ledger):
    audit_both(complete_strategy(), {}, ledger)
    assert ledger.verify() == []
    lines = ledger.path.read_text().splitlines()
    rec = json.loads(lines[0])
    rec["verdict"] = "VERIFIED" if rec["verdict"] != "VERIFIED" else "UNVERIFIED"
    lines[0] = json.dumps(rec, sort_keys=True)
    ledger.path.write_text("\n".join(lines) + "\n")
    assert any("altered" in p for p in ledger.verify())


def test_ledger_detects_deleted_record(ledger):
    audit_both(complete_strategy(), {}, ledger)
    audit_both(complete_strategy(id="STR-2"), {}, ledger)
    lines = ledger.path.read_text().splitlines()
    ledger.path.write_text("\n".join(lines[:1] + lines[2:]) + "\n")
    assert any("prev_hash" in p for p in ledger.verify())


def test_red_team_dissent_recorded_verbatim(ledger):
    text = "28B dissent: transit risk is understated because alternative routes lack capacity."
    rec = GeopoliticalAuditor(ledger).dissent("STR-TEST", complete_strategy(), text, "CONDITIONAL")
    assert ledger.records()[-1].reasons == [text] and rec.kind == "dissent"


def test_research_finding_not_asked_for_policy_checks(ledger):
    p = {"id": "F1", "kind": "finding", "claims": [], "assumptions": [], "identity_checks": [],
         "uncertainty": "stated", "international_assumptions": [], "probabilities": []}
    rec = DomesticAuditor(ledger).audit(p, {})
    statuses = {c["id"]: c["status"] for c in rec.checks}
    assert statuses["L1"] == "n/a" and statuses["F1"] == "n/a"
