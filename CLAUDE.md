# CLAUDE.md — NEPAL 3T

This repository hosts **NEPAL 3T**, an independent AI-assisted research and simulation platform on Nepal's
development constraints and on whether (and under what conditions) Nepal could reach US$3 trillion in
annual nominal GDP. It also contains the earlier ChimeraShield prototype (`app/`, `frontend/`, `backend/`,
`docs/chimera/`), which NEPAL 3T does not use or modify.

## What this platform is not

- It is **not a government** and does not speak for one. Never impersonate an institution, claim official
  authority, enact policy, contact third parties, publish externally or commit funds.
- Any action outside this repository goes through `src/orchestrator/approvals.py` and needs a recorded
  approval from a named human.
- Do not assume US$3T is achievable. Work out the assumptions, timelines and structural changes it would
  require, and the conditions under which it is unattainable.
- Scenarios are stress tests, **not forecasts**. Do not assign probabilities without evidence.
- Do not rank or endorse political leaders, parties or electoral choices.
- Never optimise GDP at the expense of the other 11 objectives; report trade-offs
  (`src/economic_model/welfare.py`).

## Evidence rules (enforced in code and tests)

1. Every empirical value is an `Observation` in `research/sources/observations.jsonl`, with source id,
   URL, publication date or data vintage, retrieval time, and the SHA-256 of the raw file stored in `data/raw/`.
2. If a source cannot be reached, record the item as **pending** with the exact data required.
   **Never** substitute a model's guess, a remembered number or an unsourced estimate.
3. Label every finding `fact`, `estimate`, `assumption` or `pending`. Facts and estimates cite observation ids.
4. When sources disagree, keep both values and investigate the methodological difference
   (`find_conflicts`); do not silently pick one.
5. Source hierarchy (`research/sources/source_catalog.yaml`, tier 1 highest): Nepal official (NSO, NRB,
   MoF, ministries) → IMF/World Bank/ADB → UN/ILO/UNCTAD/WTO → foreign governments and central banks →
   IEA and energy authorities → ICIMOD and climate science → academic and independent analysis.
6. Keep real growth, inflation (GDP deflator) and exchange-rate effects separate. Nepal's fiscal year
   (mid-July) differs from calendar-year international series; never mix them without a documented conversion.
7. Use unit codes from `src/economic_model/units.py`. Sector growth enters GDP only through value added
   (`src/economic_model/sectors.py`).

## Independent audit

Agent 15 (domestic) and Agent 28 (geopolitical red team) audit every significant proposal and write only
to the hash-chained ledger `reports/audits/audit_ledger.jsonl`. Verdicts: VERIFIED, CONDITIONAL,
UNVERIFIED, INCONSISTENT, each with specific reasons. No agent may edit, filter or paraphrase an audit
record; reports reproduce them verbatim. Agent 28 may publish dissent that Agent 16 cannot modify.

## Layout

| Path | Contents |
|---|---|
| `config/catalog.yaml` | **Single source of truth** for the 29 agents and 111 subagents |
| `config/agents.json`, `config/subagents.json` | Generated full definitions (do not hand-edit) |
| `.claude/agents/nepal3t-*.md` | Generated Claude Code subagent definitions (29) |
| `src/agents/specs/*.md` | Generated subagent task specifications (111) |
| `.claude/skills/` | Workflow skills: evidence research, audit, scenario run, baseline |
| `config/model_config.yaml` | Shared assumption register (every parameter is evidence or a labelled assumption) |
| `config/strategies.yaml` | Strategy definitions STR-0 and STR-A..E |
| `src/` | Platform code (orchestrator, research, data, economic & geopolitical models, scenarios, auditing, reporting) |
| `research/` | Source catalog, observation store, findings, exposure register |
| `data/` | `raw/` (hashed original bytes), `metadata/`, `processed/` |
| `scenarios/` | 10 mandatory scenarios (YAML) |
| `reports/` | Baseline, target arithmetic, scenario status, strategies, audits |
| `docs/` | Methodology, architecture, implementation notes |
| `state/` | Orchestrator plan, resumable run state, human approvals |

## Commands

```bash
pip install -r requirements.txt
python -m pytest                      # full test suite
python -m src.cli first-run           # generate → exposure → baseline (online attempt) → scenarios → audit → reports → validate
python -m src.cli generate            # after editing config/catalog.yaml
python -m src.cli generate --check    # fail if generated files are stale
python -m src.cli validate            # catalog, scenarios, exposure register, observations, ledger
python -m src.cli next                # tasks whose dependencies are complete
python -m src.cli brief 05A           # prompt text for running a subagent task
python -m src.cli complete 05A research/findings/05/05A-t1.json
```

## Working as an agent

1. Read your definition in `.claude/agents/` and your task spec in `src/agents/specs/`.
2. Check dependencies with `python -m src.cli next`; mark work with `start` / `complete`.
3. Record every retrieved value with `ObservationStore.append` (or `ingest-csv` for manual downloads).
4. Write findings to `research/findings/<agent>/<subagent>-<task>.json`; validate with `validate-finding`.
5. Submit significant findings to both auditors (`python -m src.cli audit` or `src.auditing.auditors.audit_both`).
6. Run `python -m pytest` and `python -m src.cli validate` before committing. Never report tests as passing
   without running them.

Edit `config/catalog.yaml`, never the generated agent files; then run `python -m src.cli generate`.
