---
name: model-bakeoff
description: Compare several open-source and hosted models on ChimeraShield's cost-quality-latency frontier and recommend a triage/escalation pair. Use when choosing models for the cascade or deciding what to self-host.
---

# Model bake-off

1. List candidates from `GET /api/models` or `backend/llm/catalog.py` (filter by `role`; use `find_models(max_license_restrictive=True)` if commercial use must be unrestricted).
2. Include at least one hosted baseline (Claude) so open models are compared to a reference.
3. For each: run the `run-phishing-eval` skill on the same split, with identical prompts.
4. Build a table: recall@FPR=1%, ECE, parse-failure rate, p95 latency, cost/1k scans, hardware needed, license.
5. Pick the **triage** model (cheapest that keeps recall within CI of the best) and the **escalation** model (best quality on the cases triage was unsure about). Tune the escalation band on a validation split, then confirm on test.
6. Report the Pareto frontier, the recommendation, and what would change it. Save to `docs/chimera/eval-reports/`.
