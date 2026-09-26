"""The two independent auditors.

Independence rules enforced in code:
* `audit()` accepts only the proposal and the evidence store — there is no
  parameter through which a caller can request or suggest a verdict.
* Results are written straight to the append-only ledger by the auditor.
* Reports read the ledger; they cannot edit it (see src/reporting).
"""

from __future__ import annotations

from src.common import sha256_obj
from src.research.observations import Observation

from . import checks as C
from .ledger import AuditLedger, AuditRecord


class _Auditor:
    agent_id = ""
    subagents: tuple[str, ...] = ()

    def __init__(self, ledger: AuditLedger | None = None):
        self.ledger = ledger or AuditLedger()

    def run_checks(self, proposal: dict, obs: dict[str, Observation]) -> list[C.Check]:  # pragma: no cover
        raise NotImplementedError

    def audit(self, proposal: dict, observations: dict[str, Observation]) -> AuditRecord:
        if "id" not in proposal:
            raise ValueError("proposal needs an id")
        results = self.run_checks(proposal, observations)
        conditions = C.conditional_assumptions(proposal)
        verdict, reasons = C.verdict_from(results, conditions)
        rec = AuditRecord(
            auditor=self.agent_id, subagents=list(self.subagents), subject_id=proposal["id"],
            subject_sha256=sha256_obj(proposal), verdict=verdict, reasons=reasons,
            checks=[c.as_dict() for c in results], conditions=conditions,
        )
        return self.ledger.append(rec)


class DomesticAuditor(_Auditor):
    """Agent 15 — economic calculations, sources, finance, capacity, law, society, environment."""

    agent_id = "15"
    subagents = ("15A", "15B", "15C")

    def run_checks(self, p: dict, obs: dict[str, Observation]) -> list[C.Check]:
        return [
            C.check_claims_evidence(p, obs),  # 15A
            C.check_pending_inputs(p),
            C.check_units(p),
            C.check_identities(p),
            C.check_assumptions_labelled(p),
            C.check_uncertainty(p),
            C.check_financing(p),  # 15B
            C.check_schedule(p),
            C.check_contingent(p),
            C.check_legal(p),  # 15C
            C.check_distribution(p),
            C.check_environment(p),
            C.check_welfare_tradeoffs(p),
        ]


class GeopoliticalAuditor(_Auditor):
    """Agent 28 — international assumptions, external finance, dependencies, treaties, compound shocks."""

    agent_id = "28"
    subagents = ("28A", "28C", "28D", "28E")

    def run_checks(self, p: dict, obs: dict[str, Observation]) -> list[C.Check]:
        return [
            C.check_claims_evidence(p, obs),  # 28A
            C.check_pending_inputs(p),
            C.check_international_assumptions(p, obs),
            C.check_units(p),  # 28E reproduction of calculations
            C.check_identities(p),
            C.check_external_financing(p),
            C.check_regional_dependencies(p),
            C.check_treaties(p),
            C.check_probabilities(p),  # 28C
            C.check_cross_border_env(p),  # 28D
            C.check_compound(p),
            C.check_uncertainty(p),
        ]

    def dissent(self, subject_id: str, subject: dict, text: str, verdict: str) -> AuditRecord:
        """Publish a dissenting finding. Stored verbatim; the Director cannot edit it."""
        rec = AuditRecord(
            auditor="28", subagents=["28B"], subject_id=subject_id, subject_sha256=sha256_obj(subject),
            verdict=verdict, reasons=[text], checks=[], kind="dissent",
        )
        return self.ledger.append(rec)


def audit_both(proposal: dict, observations: dict[str, Observation], ledger: AuditLedger | None = None) -> dict:
    """Run both reviews. Each auditor evaluates independently; neither sees the other's verdict."""
    ledger = ledger or AuditLedger()
    d = DomesticAuditor(ledger).audit(proposal, observations)
    g = GeopoliticalAuditor(ledger).audit(proposal, observations)
    return {"15": d, "28": g}
