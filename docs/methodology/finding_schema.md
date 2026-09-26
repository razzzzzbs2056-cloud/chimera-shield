# Finding file schema

Path: `research/findings/<agent id>/<subagent id>-<task id>.json`. Validated by
`python -m src.cli validate-finding <file>` (`src/orchestrator/findings.py`).

```json
{
  "subagent_id": "05A",
  "task_id": "baseline-2026",
  "generated_at": "2026-09-26T00:00:00+00:00",
  "summary": "One-paragraph answer to the task.",
  "findings": [
    {"claim": "Installed capacity at end of FY...", "type": "fact", "value": 0.0, "unit": "MW",
     "period": "FY2024/25", "observation_ids": ["obs-…"], "source_ids": ["nea"]},
    {"claim": "Dry-season deficit trend", "type": "pending", "value": null,
     "source_ids": ["nea"], "note": "NEA monthly generation tables required"}
  ],
  "data_gaps": ["Monthly generation by plant, FY2015/16 onward (NEA annual reports)"],
  "assumptions": [{"id": "05A-A1", "text": "...", "basis": "assumption"}],
  "challenges": [{"to": "22E", "text": "Export price series mixes bilateral and exchange sales"}],
  "uncertainty": "Where the main uncertainty lies and how large it is.",
  "specific": {"electricity_balance": "...", "seasonal_profile": "...", "pipeline_completion_rate": "...",
               "transmission_bottlenecks": "..."}
}
```

Rules: `fact` and `estimate` need `observation_ids` present in the store and a `unit` when a value is given;
`pending` must not carry a value; `uncertainty` must be non-empty; all subagent-specific fields listed in
`config/subagents.json` must be present in `specific` (use "pending" when not yet available).
