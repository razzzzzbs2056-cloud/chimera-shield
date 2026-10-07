---
name: chimera-aec-agents
description: Run Chimera AEC's 23 specialist architecture & engineering agents (structural, seismic, wind, geotechnical, foundations, HVAC, electrical, hydraulics, fire, façade, energy, carbon, accessibility, BIM/clash, cost/BOQ, value engineering, construction planning, code compliance, independent verification) on a building brief and explain the results. Use when the user asks for building feasibility, scheme design, structural system selection, earthquake/wind checks, foundation options, MEP sizing, egress, energy or embodied carbon, cost estimate/BOQ, construction programme, or clause-level code compliance for a proposed building. Requires AEC_API_KEY.
---

# Chimera AEC agents

The agents run deterministic engineering solvers behind a metered API. **Never invent engineering numbers.** Call the API and report what it returns.

## Setup

- `AEC_API_KEY` — a key created in the Chimera AEC app under **Settings → API keys** (format `aec_live_…`).
- `AEC_API_URL` — base URL of the deployment (default `http://localhost:3100`).

If `AEC_API_KEY` is missing, tell the user to create one and stop. Do not guess results.

## Workflow

1. **Gather the brief.** You need building type, city, number of storeys, and whichever agents the question needs. Optional: site size, budget, targets, boreholes, design overrides. See `references/request-schema.md`.
2. **Pick agents.** Use the IDs in `references/agents.md`. Request only what the question needs. `codes` and `verifier` are always useful.
3. **Run.** `python3 scripts/analyze.py request.json`, or POST the JSON to `$AEC_API_URL/api/v1/analyze` with `Authorization: Bearer $AEC_API_KEY`.
4. **Report.** Lead with the answer. Quote KPIs (`kpis`), any failing checks (`failing`, each with standard and clause), design changes the agents made (`changes`) and the relevant agent sections. Say which verification checks disagree, if any.
5. **Always** include the response's `disclaimer`: results are decision support and must be reviewed and sealed by a licensed professional.

## Example

```json
{ "buildingType": "office", "city": "Seattle", "floors": 24,
  "intake": { "budget": 180000000, "targetCarbon": 450 },
  "agents": ["structural", "seismic", "foundation", "cost", "codes", "verifier"] }
```

## Errors

| Status | Meaning | Action |
|---|---|---|
| 401 | Missing or invalid key | Ask the user for a valid `AEC_API_KEY` |
| 429 | Monthly quota reached | Tell the user; suggest upgrading the plan |
| 400 / 422 | Bad input or analysis failed | Fix the field named in `error` and retry once |
