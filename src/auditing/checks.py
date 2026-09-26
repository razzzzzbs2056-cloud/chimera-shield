"""Audit checks and verdict logic shared by both independent auditors.

A *proposal* is a JSON-serialisable dict (schema in docs/methodology/audit_protocol.md).
Each check returns a `Check`. Severity drives the verdict:

    calc       failure -> INCONSISTENT  (contradiction or calculation error)
    evidence   failure -> UNVERIFIED    (insufficient evidence for claimed effects)
    condition  failure/warn -> CONDITIONAL (depends on named assumptions, financing
                                            or institutional change)
Otherwise VERIFIED.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from src.economic_model.units import UnitError, parse_unit
from src.research.observations import Observation


@dataclass(frozen=True)
class Check:
    id: str
    name: str
    status: str  # pass | fail | warn | n/a
    severity: str  # calc | evidence | condition
    detail: str

    def as_dict(self) -> dict:
        return asdict(self)


POLICY_KINDS = ("strategy", "proposal")
IMPACT_KINDS = ("strategy", "proposal", "scenario")


def applies(p: dict, kinds: tuple[str, ...]) -> bool:
    """Some checks only make sense for policy proposals or impact assessments.

    A pure research `finding` (e.g. growth arithmetic) is not a policy and is
    not asked for legal or distributional analysis; the check reports n/a.
    """
    return p.get("kind", "proposal") in kinds


def _na(cid, name, severity, p) -> Check:
    return Check(cid, name, "n/a", severity, f"not applicable to kind {p.get('kind')!r}")


def _c(cid, name, ok, severity, detail_fail, detail_ok="ok", warn=False) -> Check:
    if ok:
        return Check(cid, name, "pass", severity, detail_ok)
    return Check(cid, name, "warn" if warn else "fail", severity, detail_fail)


# ---------------------------------------------------------------- shared
def check_claims_evidence(p: dict, obs: dict[str, Observation]) -> Check:
    bad = []
    for i, c in enumerate(p.get("claims", [])):
        if c.get("type") in ("fact", "estimate"):
            ids = c.get("observation_ids") or []
            if not ids:
                bad.append(f"claim {i} ({c.get('text', '')[:60]!r}) has no observation_ids")
                continue
            for oid in ids:
                o = obs.get(oid)
                if o is None:
                    bad.append(f"claim {i}: observation {oid} not found")
                elif o.status not in ("retrieved", "verified"):
                    bad.append(f"claim {i}: observation {oid} has status {o.status}")
        elif c.get("type") == "pending" and c.get("value") is not None:
            bad.append(f"claim {i}: pending claim carries a value")
    return _c("E1", "claims linked to retrieved evidence", not bad, "evidence", "; ".join(bad))


def check_pending_inputs(p: dict) -> Check:
    pending = [c.get("text", "?") for c in p.get("claims", []) if c.get("type") == "pending"]
    return _c("E4", "no conclusions rest on pending inputs", not pending, "evidence",
              f"inputs still pending evidence: {pending}")


def check_units(p: dict) -> Check:
    bad = list(p.get("unit_errors", []))
    for i, c in enumerate(p.get("claims", [])):
        if c.get("value") is not None:
            try:
                parse_unit(c.get("unit", ""))
            except UnitError as exc:
                bad.append(f"claim {i}: {exc}")
    return _c("C1", "units valid and consistent", not bad, "calc", "; ".join(bad))


def check_identities(p: dict) -> Check:
    failed = [c["name"] for c in p.get("identity_checks", []) if not c.get("passed")]
    return _c("C2", "accounting identities hold", not failed, "calc", f"failed identities: {failed}")


def check_assumptions_labelled(p: dict) -> Check:
    bad = [a.get("id", "?") for a in p.get("assumptions", []) if a.get("basis") not in ("evidence", "assumption")]
    return _c("E2", "facts separated from assumptions", not bad, "evidence", f"unlabelled assumptions: {bad}")


def check_uncertainty(p: dict) -> Check:
    ok = bool(str(p.get("uncertainty", "")).strip())
    return _c("E3", "uncertainty disclosed", ok, "evidence", "no uncertainty statement")


def conditional_assumptions(p: dict) -> list[str]:
    return [f"{a.get('id')}: {a.get('text')}" for a in p.get("assumptions", []) if a.get("basis") == "assumption"]


# ---------------------------------------------------------------- domestic (Agent 15)
def check_financing(p: dict) -> Check:
    if not applies(p, POLICY_KINDS):
        return _na("F1", "investment matched to financing", "condition", p)
    items = p.get("financing", [])
    if p.get("investment_requirement") is None and not items:
        return Check("F1", "investment matched to financing", "n/a", "condition", "no investment requirement")
    if p.get("investment_requirement") is not None and not items:
        return Check("F1", "investment matched to financing", "fail", "evidence", "investment stated with no financing plan")
    unidentified = [f.get("item") for f in items if not f.get("identified")]
    return _c("F1", "investment matched to financing", not unidentified, "condition",
              f"financing not yet identified for: {unidentified}", warn=True)


def check_schedule(p: dict) -> Check:
    if not applies(p, POLICY_KINDS):
        return _na("F2", "delivery schedule vs historical execution", "condition", p)
    s = p.get("schedule")
    if not s:
        return Check("F2", "delivery schedule vs historical execution", "n/a", "condition", "no schedule")
    planned, hist = s.get("planned_execution_rate"), s.get("historical_execution_rate")
    if hist is None:
        return Check("F2", "delivery schedule vs historical execution", "fail", "evidence",
                     "historical execution rate not evidenced")
    return _c("F2", "delivery schedule vs historical execution", planned is not None and planned <= hist, "condition",
              f"planned execution {planned} exceeds historical {hist}; requires institutional change", warn=True)


def check_contingent(p: dict) -> Check:
    if not applies(p, POLICY_KINDS):
        return _na("F3", "contingent liabilities disclosed", "condition", p)
    ok = "contingent_liabilities" in p
    return _c("F3", "contingent liabilities disclosed", ok, "condition", "contingent liabilities not addressed", warn=True)


def check_legal(p: dict) -> Check:
    if not applies(p, POLICY_KINDS):
        return _na("L1", "legal requirements identified", "evidence", p)
    ok = bool(p.get("legal_requirements"))
    return _c("L1", "legal requirements identified", ok, "evidence", "no legal requirements listed")


def check_distribution(p: dict) -> Check:
    if not applies(p, IMPACT_KINDS):
        return _na("L2", "distributional effects by income group and province", "evidence", p)
    d = p.get("distribution") or {}
    ok = bool(d.get("by_income")) and bool(d.get("by_province"))
    return _c("L2", "distributional effects by income group and province", ok, "evidence",
              "distributional effects not reported by income and province")


def check_environment(p: dict) -> Check:
    if not applies(p, IMPACT_KINDS):
        return _na("L3", "environmental costs quantified or flagged", "evidence", p)
    e = p.get("environment") or {}
    ok = e.get("quantified") is True or bool(e.get("unquantified_flag"))
    return _c("L3", "environmental costs quantified or flagged", ok, "evidence", "environmental costs not addressed")


def check_welfare_tradeoffs(p: dict) -> Check:
    if not applies(p, IMPACT_KINDS):
        return _na("L4", "welfare reported separately from GDP", "evidence", p)
    w = p.get("welfare_effects")
    if not w:
        return Check("L4", "welfare reported separately from GDP", "fail", "evidence", "no welfare assessment")
    if w.get("growth") == "+" and any(v == "-" for k, v in w.items() if k != "growth"):
        worse = [k for k, v in w.items() if v == "-"]
        return Check("L4", "welfare reported separately from GDP", "warn", "condition",
                     f"GDP gain with trade-offs against: {worse}")
    return Check("L4", "welfare reported separately from GDP", "pass", "condition", "ok")


# ---------------------------------------------------------------- geopolitical (Agent 28)
def check_international_assumptions(p: dict, obs: dict[str, Observation]) -> Check:
    bad = []
    for i, a in enumerate(p.get("international_assumptions", [])):
        ids = a.get("observation_ids") or []
        if not ids and not a.get("source_ids"):
            bad.append(f"international assumption {i} unsourced")
        for oid in ids:
            if oid not in obs:
                bad.append(f"international assumption {i}: observation {oid} not found")
    return _c("G1", "international assumptions sourced", not bad, "evidence", "; ".join(bad))


def check_external_financing(p: dict) -> Check:
    items = p.get("external_financing", [])
    if not items:
        return Check("G2", "external financing identified", "n/a", "condition", "no external financing")
    unidentified = [f.get("item") for f in items if not f.get("identified")]
    return _c("G2", "external financing identified", not unidentified, "condition",
              f"external financing assumed but not identified: {unidentified}", warn=True)


def check_regional_dependencies(p: dict) -> Check:
    if not applies(p, IMPACT_KINDS):
        return _na("G3", "regional dependencies listed", "evidence", p)
    ok = "regional_dependencies" in p and isinstance(p["regional_dependencies"], list)
    return _c("G3", "regional dependencies listed", ok, "evidence", "regional dependencies not listed")


def check_treaties(p: dict) -> Check:
    if not applies(p, IMPACT_KINDS):
        return _na("G4", "treaty and trade constraints checked", "evidence", p)
    ok = bool(p.get("treaty_constraints_checked"))
    return _c("G4", "treaty and trade constraints checked", ok, "evidence", "treaty/trade constraints not checked")


def check_probabilities(p: dict) -> Check:
    bad = [pr.get("event") for pr in p.get("probabilities", []) if not pr.get("evidence")]
    return _c("G5", "no unsupported probabilities", not bad, "calc",
              f"probabilities asserted without evidence: {bad}")


def check_cross_border_env(p: dict) -> Check:
    if not applies(p, IMPACT_KINDS):
        return _na("G6", "cross-border environmental consequences", "evidence", p)
    ok = bool(p.get("cross_border_environment"))
    return _c("G6", "cross-border environmental consequences", ok, "evidence", "not addressed")


def check_compound(p: dict) -> Check:
    if not applies(p, POLICY_KINDS):
        return _na("G7", "compound-shock resilience tested", "condition", p)
    ok = bool(p.get("compound_shock_tested"))
    return _c("G7", "compound-shock resilience tested", ok, "condition", "not tested against compound scenario S10",
              warn=True)


def verdict_from(checks: list[Check], conditions: list[str]) -> tuple[str, list[str]]:
    fails = [c for c in checks if c.status == "fail"]
    calc = [c for c in fails if c.severity == "calc"]
    evid = [c for c in fails if c.severity == "evidence"]
    cond = [c for c in checks if c.status in ("fail", "warn") and c.severity == "condition"]
    if calc:
        return "INCONSISTENT", [f"[{c.id}] {c.name}: {c.detail}" for c in calc + evid]
    if evid:
        return "UNVERIFIED", [f"[{c.id}] {c.name}: {c.detail}" for c in evid]
    if cond or conditions:
        reasons = [f"[{c.id}] {c.name}: {c.detail}" for c in cond]
        reasons += [f"depends on assumption {a}" for a in conditions]
        return "CONDITIONAL", reasons
    return "VERIFIED", ["all checks passed: " + ", ".join(c.id for c in checks if c.status == "pass")]
