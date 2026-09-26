"""Generate agent definitions and subagent specifications from the catalog.

Outputs (all derived; edit config/catalog.yaml instead):
  config/agents.json, config/subagents.json
  .claude/agents/nepal3t-<id>-<slug>.md      (29 Claude Code subagent definitions)
  src/agents/specs/<subagent id>.md           (111 subagent task specifications)
"""

from __future__ import annotations

import json
from pathlib import Path

from src.common import ROOT
from src.research.sources import SourceCatalog

from .catalog import enriched_agents, enriched_subagents, load_catalog, validate_catalog

HEADER = "<!-- GENERATED from config/catalog.yaml by `python -m src.cli generate`. Do not edit by hand. -->\n"


def _bullets(items) -> str:
    return "\n".join(f"- {x}" for x in items) if items else "- (none)"


def render_agent_md(a: dict, subs: list[dict]) -> str:
    desc = f"NEPAL 3T Agent {a['id']} — {a['name']}. {a['mission']}"
    fm = (
        "---\n"
        f"name: nepal3t-{a['id']}-{a['slug']}\n"
        f"description: {json.dumps(desc, ensure_ascii=False)}\n"
        f"tools: {', '.join(a['permitted_tools'])}\n"
        "---\n"
    )
    sub_rows = "\n".join(
        f"| {s['id']} | {s['name']} | {', '.join(s['depends_on']) or '—'} | `src/agents/specs/{s['id']}.md` |"
        for s in subs
    )
    safety = f"\n## Safety note\n\n{a['safety_note']}\n" if a["safety_note"] else ""
    indep = (
        "\n## Independence\n\nThis agent reports independently. It must not be instructed to approve a proposal, "
        "and no other agent may alter its findings. Verdicts are written only to the append-only audit ledger.\n"
        if a["independent"] else ""
    )
    return (
        fm + "\n" + HEADER + f"""
# Agent {a['id']} — {a['name']}

**Identifier:** `{a['id']}` · **Division {a['division']}:** {a['division_name']} · **Role:** {a['role']}

You are part of NEPAL 3T, an independent research and simulation platform. You are not a government body.
You do not enact policy, contact third parties, publish externally or commit funds. Read `CLAUDE.md` first.

## Mission

{a['mission']}

## Research responsibilities

{_bullets(a['responsibilities'])}

## Permitted tools

{', '.join(f'`{t}`' for t in a['permitted_tools'])}

## Data-access rules

**Read:**
{_bullets(a['data_access']['read'])}

**Write:**
{_bullets(a['data_access']['write'])}

**Forbidden:**
{_bullets(a['data_access']['forbidden'])}

## Dependencies

- Consumes outputs of agents: {', '.join(a['depends_on']) or 'none'}
- Outputs consumed by agents: {', '.join(a['depended_by']) or 'none'}

## Deliverables

{_bullets(a['deliverables'])}

## Subagents

| ID | Name | Depends on | Task specification |
|---|---|---|---|
{sub_rows}

When invoked, work through the subagent specifications that are ready (all dependencies complete — see
`python -m src.cli next`). Subagent tasks can be delegated with the Agent tool where the platform allows;
they are not guaranteed to run simultaneously.

## Reporting format

{a['reporting_format']}

## Escalation rules

{_bullets(a['escalation_rules'])}

## Validation requirements

{_bullets(a['validation_requirements'])}
{indep}{safety}
## Non-negotiables

- Cite real, retrievable sources. Never fabricate citations, statistics, model outputs or expert opinions.
- If a source cannot be accessed, mark the item PENDING and state exactly what data is required.
- Separate facts, estimates and assumptions. Disclose uncertainty.
- Never optimise GDP at the expense of the other objectives; report trade-offs.
- Do not rank or endorse political leaders or parties. Do not claim to represent any government.
"""
    )


def render_subagent_md(s: dict) -> str:
    q = "\n".join(f"{i + 1}. {x}" for i, x in enumerate(s["instructions"]["questions"]))
    fields = s["output_schema"]["properties"]["specific"]["required"]
    return HEADER + f"""
# Subagent {s['id']} — {s['name']}

**Parent agent:** {s['parent']} — {s['parent_name']}
**Depends on:** {', '.join(s['depends_on']) or 'none'}

## Instructions

{s['instructions']['focus']}

Answer these research questions:

{q}

## Evidence requirements

**Data required:**
{_bullets(s['evidence_requirements']['data_required'])}

**Sources (priority order; see research/sources/source_catalog.yaml):**
{_bullets(s['evidence_requirements']['sources_in_priority_order'] or ['derived from other agents / platform records'])}

**Rules:**
{_bullets(s['evidence_requirements']['rules'])}

## Output schema

Write `research/findings/{s['parent']}/{s['id']}-<task>.json` with the common fields
(`subagent_id`, `task_id`, `generated_at`, `summary`, `findings`, `data_gaps`, `assumptions`,
`challenges`, `uncertainty`, `specific`) and these subagent-specific fields inside `specific`:

{_bullets(f'`{f}`' for f in fields)}

Full JSON schema: `config/subagents.json` → `{s['id']}.output_schema`.

## Acceptance criteria

{_bullets(s['acceptance_criteria'])}
"""


def render_all(root: Path = ROOT) -> dict[Path, str]:
    cat = load_catalog()
    sources = SourceCatalog()
    problems = validate_catalog(cat, sources)
    if problems:
        raise ValueError("catalog invalid:\n" + "\n".join(problems))
    agents = enriched_agents(cat)
    subs = enriched_subagents(cat, sources)
    files: dict[Path, str] = {
        root / "config" / "agents.json": json.dumps({"version": cat["version"], "agents": agents}, indent=2,
                                                    ensure_ascii=False) + "\n",
        root / "config" / "subagents.json": json.dumps({"version": cat["version"], "subagents": subs}, indent=2,
                                                       ensure_ascii=False) + "\n",
    }
    by_parent: dict[str, list[dict]] = {}
    for s in subs:
        by_parent.setdefault(s["parent"], []).append(s)
        files[root / "src" / "agents" / "specs" / f"{s['id']}.md"] = render_subagent_md(s)
    for a in agents:
        files[root / ".claude" / "agents" / f"nepal3t-{a['id']}-{a['slug']}.md"] = render_agent_md(a, by_parent[a["id"]])
    return files


def write_all(root: Path = ROOT) -> list[Path]:
    files = render_all(root)
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return sorted(files)


def stale_files(root: Path = ROOT) -> list[Path]:
    """Generated files that are missing or differ from the catalog."""
    return sorted(p for p, c in render_all(root).items() if not p.exists() or p.read_text(encoding="utf-8") != c)
