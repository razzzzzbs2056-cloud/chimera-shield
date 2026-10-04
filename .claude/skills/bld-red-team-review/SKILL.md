---
name: bld-red-team-review
description: Adversarial review that tries to make the building fail or the design contradict itself; produces failure modes (cause, mechanism, consequence, detection, mitigation, residual risk) and a risk register. Use before issuing any report or design change.
---

# Red-team review

Agent: `bld-red-team-reviewer`. Agreement is not success.
1. Re-run `python -m pytest -q architecture/tests` and every script cited in the report.
2. Hunt contradictions between brief, drawings, take-off, IFC model and analysis (areas, levels, sizes, carbon).
3. Attack: strong shaking, torsion, soft storey, column/wall shear, joints, diaphragms, settlement, liquefaction, overturning, pounding, fire, progressive collapse, construction stage, non-structural.
4. For each credible mechanism: CAUSE · MECHANISM · CONSEQUENCE · DETECTION METHOD · MITIGATION · RESIDUAL RISK.
5. Update the risk register table (Risk | Probability | Consequence | Severity | Evidence | Mitigation | Verification) and raise change records for design changes.
6. State what was not checked.
