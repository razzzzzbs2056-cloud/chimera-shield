---
name: independent-audit
description: Run the NEPAL 3T independent audit (Agent 15 domestic, Agent 28 geopolitical) on a proposal, strategy, scenario or finding and record verdicts in the hash-chained ledger. Use when acting as Agent 15 or 28, or when a significant result needs review.
---

# Independent audit (Agents 15 and 28)

Auditors are independent: nobody may instruct them to approve, and nobody may edit their records.

1. Express the subject as a proposal dict (schema: `docs/methodology/audit_protocol.md`). Describe it
   honestly: unevidenced inputs are `pending` claims; modelling choices are `basis: assumption`.
2. Run both reviews:
   ```python
   from src.auditing.auditors import audit_both
   from src.research.observations import ObservationStore
   obs = {o.id: o for o in ObservationStore().load()}
   audit_both(proposal, obs)
   ```
   or `python -m src.cli audit` for the platform's standing artifacts.
3. Beyond the automated checks, the auditor reviews substance: re-compute key numbers from committed inputs
   (15A / 28E), look for omitted dependencies (28C), rights and legal risks (15C / 28D), and alternative
   interpretations (28B). Record substantive disagreement with
   `GeopoliticalAuditor().dissent(subject_id, subject, text, verdict)` (Agent 28) or a new audit record.
4. `python -m src.cli audit-verify` must print `ledger OK`.
5. `python -m src.cli report` regenerates `reports/audits/audit_summary.md`, which quotes every verdict and
   reason verbatim.

Verdicts: VERIFIED (evidence and calculations meet requirements) · CONDITIONAL (depends on named
assumptions, financing or institutional change) · UNVERIFIED (insufficient evidence) · INCONSISTENT
(contradictions or calculation errors).
