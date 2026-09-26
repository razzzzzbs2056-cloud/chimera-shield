# Independent audit protocol

Every significant proposal passes two separate reviews: **Agent 15** (domestic) and **Agent 28**
(geopolitical red team). Each runs independently, does not see the other's verdict, and writes only to the
hash-chained ledger `reports/audits/audit_ledger.jsonl` (`src/auditing/ledger.py`).

## Proposal schema

```json
{
  "id": "STR-A-v1", "title": "...", "owner": "05", "kind": "strategy | proposal | scenario | finding",
  "claims": [{"text": "...", "type": "fact|estimate|assumption|pending", "value": 1.0, "unit": "percent",
              "observation_ids": ["obs-..."]}],
  "assumptions": [{"id": "A1", "text": "...", "basis": "evidence|assumption"}],
  "identity_checks": [{"name": "expenditure_gdp", "passed": true}],
  "unit_errors": [],
  "uncertainty": "...",
  "investment_requirement": {"amount": 0, "unit": "USD_current_bn"},
  "financing": [{"item": "...", "identified": true}],
  "schedule": {"planned_execution_rate": 0.7, "historical_execution_rate": 0.8},
  "contingent_liabilities": [],
  "legal_requirements": ["..."],
  "distribution": {"by_income": "...", "by_province": "..."},
  "environment": {"quantified": true} ,
  "welfare_effects": {"growth": "+", "poverty_inclusion": "?"},
  "international_assumptions": [{"text": "...", "source_ids": [], "observation_ids": []}],
  "external_financing": [{"item": "...", "identified": false}],
  "regional_dependencies": ["EXP-03"],
  "treaty_constraints_checked": true,
  "probabilities": [{"event": "...", "probability": 0.1, "evidence": ["obs-..."]}],
  "cross_border_environment": "...",
  "compound_shock_tested": true
}
```

## Checks

| ID | Check | Auditor | Severity | Applies to |
|---|---|---|---|---|
| E1 | facts/estimates linked to retrieved observations | 15, 28 | evidence | all |
| E4 | no conclusions rest on pending inputs | 15, 28 | evidence | all |
| E2 | facts separated from assumptions | 15 | evidence | all |
| E3 | uncertainty disclosed | 15, 28 | evidence | all |
| C1 | units valid/consistent | 15, 28 | calc | all |
| C2 | accounting identities hold | 15, 28 | calc | all |
| F1 | investment matched to financing | 15 | condition | strategy, proposal |
| F2 | schedule vs historical execution | 15 | condition | strategy, proposal |
| F3 | contingent liabilities disclosed | 15 | condition | strategy, proposal |
| L1 | legal requirements | 15 | evidence | strategy, proposal |
| L2 | distribution by income and province | 15 | evidence | + scenario |
| L3 | environmental costs | 15 | evidence | + scenario |
| L4 | welfare separate from GDP; trade-offs | 15 | evidence/condition | + scenario |
| G1 | international assumptions sourced | 28 | evidence | all |
| G2 | external financing identified | 28 | condition | all |
| G3 | regional dependencies listed | 28 | evidence | + scenario |
| G4 | treaty/trade constraints checked | 28 | evidence | + scenario |
| G5 | no unsupported probabilities | 28 | calc | all |
| G6 | cross-border environmental consequences | 28 | evidence | + scenario |
| G7 | compound-shock resilience | 28 | condition | strategy, proposal |

## Verdict rule

calc failure → **INCONSISTENT**; else evidence failure → **UNVERIFIED**; else any condition warning or
labelled assumption → **CONDITIONAL**; else **VERIFIED**. Every verdict carries the specific failing checks
as reasons.

Automated checks are the floor, not the ceiling: auditors also re-compute numbers, look for omitted
dependencies and competing interpretations, and may record dissent. Records cannot be edited; a changed view
is a new record. `python -m src.cli audit-verify` detects any alteration or deletion.
