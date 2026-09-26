# Architecture overview

`architecture_report.md` (generated) lists every agent, dependency wave and module. This page explains the
design choices.

## Single source of truth

`config/catalog.yaml` defines all 29 agents and 111 subagents. `python -m src.cli generate` derives
`config/agents.json`, `config/subagents.json`, 29 Claude Code agent files in `.claude/agents/` and 111 task
specifications in `src/agents/specs/`. Role-dependent fields (permitted tools, data-access rules, escalation,
validation) are computed from the agent's `kind`, so they cannot drift between agents. A test fails if the
generated files are stale.

## Execution model

- **Claude Code native mechanisms** do the research: each main agent is a Claude Code subagent definition;
  workflows are Claude Code skills (`.claude/skills/`).
- **The Python orchestrator** (`src/orchestrator/`) does not call language models. It holds the task graph
  (111 nodes, dependency edges from the catalog), computes waves, persists resumable run state, produces task
  briefs, validates returned findings and gates external actions behind human approval. No third-party
  orchestration framework is used because none would add functionality here.
- **Parallelism** is bounded by `orchestration.max_parallel`; tasks in one wave *may* run in parallel, but
  the platform does not assume all 111 subagents execute simultaneously.

## Data flow

```
sources ──► src/data/ingest (raw bytes hashed → data/raw, metadata) ──► ObservationStore (append-only)
                                                                             │
  findings (research/findings, schema-validated) ◄── agents ◄── task briefs ◄┤
                                                                             ▼
                      economic_model / scenario_engine / geopolitical_model (units + identities enforced)
                                                                             │
                   auditing: Agent 15 + Agent 28 → hash-chained ledger ◄─────┘
                                                                             │
                                reporting (reads everything, edits nothing) ─┘
```

## Independence guarantees

- Auditor `audit()` takes only the proposal and the evidence; there is no way to pass a desired verdict.
- The ledger accepts records only from auditors 15 and 28, requires reasons, and chains hashes; any edit or
  deletion is detected (`audit-verify`, and the audit report prints the chain status).
- Agent 28 dissents are stored verbatim; Agent 16's data-access rules forbid modifying them.
