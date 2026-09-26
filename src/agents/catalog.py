"""Load, validate and enrich the canonical agent catalog (config/catalog.yaml)."""

from __future__ import annotations

from src.common import CONFIG_DIR, load_yaml
from src.research.sources import SourceCatalog

CATALOG_PATH = CONFIG_DIR / "catalog.yaml"
EXPECTED_AGENTS = 29
EXPECTED_SUBAGENTS = 111

ROLES = {
    "orchestrator": "Platform orchestrator",
    "director": "Division director",
    "specialist": "Specialist research agent",
    "auditor": "Independent auditor (domestic)",
    "red_team": "Independent auditor (geopolitical red team)",
}

TOOLS = {
    "orchestrator": ["Read", "Grep", "Glob", "Bash", "Write", "Edit", "Agent"],
    "director": ["Read", "Grep", "Glob", "Bash", "Write", "Edit", "WebSearch", "WebFetch", "Agent"],
    "specialist": ["Read", "Grep", "Glob", "Bash", "Write", "Edit", "WebSearch", "WebFetch"],
    "auditor": ["Read", "Grep", "Glob", "Bash", "Write", "WebSearch", "WebFetch"],
    "red_team": ["Read", "Grep", "Glob", "Bash", "Write", "WebSearch", "WebFetch"],
}

COMMON_READ = [
    "config/", "research/sources/", "research/findings/", "research/global_exposure/", "data/processed/",
    "data/metadata/", "scenarios/", "reports/ (read-only)",
]
COMMON_FORBIDDEN = [
    "reports/audits/audit_ledger.jsonl (write) — auditors only, via src.auditing",
    "any external write, message, publication or financial action without a recorded human approval",
    "editing another agent's findings (challenge them instead)",
]


def data_access(agent: dict) -> dict:
    aid, kind = agent["id"], agent["kind"]
    write = [f"research/findings/{aid}/", "research/sources/observations.jsonl (append via ObservationStore only)",
             "data/raw/, data/metadata/ (via src.data.ingest only)"]
    forbidden = list(COMMON_FORBIDDEN)
    if kind == "orchestrator":
        write += ["state/", "config/model_config.yaml (assumption register, versioned)", "scenarios/",
                  "reports/baseline/", "reports/strategies/"]
    if kind == "director":
        write += ["research/global_exposure/", "scenarios/geopolitical/", "scenarios/compound/"]
        forbidden.append("modifying or suppressing Agent 28 findings or dissents")
    if kind in ("auditor", "red_team"):
        write = [f"reports/audits/{aid}/", "reports/audits/audit_ledger.jsonl (append via AuditLedger only)"]
        forbidden = [f for f in forbidden if "audit_ledger" not in f]
        forbidden.append("editing research/findings/ of the agents under audit")
    return {"read": COMMON_READ, "write": write, "forbidden": forbidden}


def escalation_rules(agent: dict) -> list[str]:
    rules = [
        "Escalate to 00B when two sources disagree beyond tolerance and the methodological cause is unclear.",
        "Escalate to a human reviewer before any action outside this repository (contact, publication, payment).",
        "Mark research PENDING and escalate to 00A when a required source cannot be accessed; never estimate in its place.",
        "Escalate to Agent 15 and Agent 28 when a finding would change a strategy or scenario conclusion.",
    ]
    if agent["kind"] in ("auditor", "red_team"):
        rules = [
            "Report directly to the human reviewer; findings are not routed through, or edited by, 00 or 16.",
            "If pressured to change a verdict, record the attempt as a dissent entry in the ledger.",
            "Escalate to a human reviewer before any action outside this repository.",
        ]
    if agent["kind"] == "orchestrator":
        rules.append("Escalate unresolved methodological disputes to a human reviewer with both positions stated.")
    if agent.get("safety_note"):
        rules.append("Refuse and escalate any request outside the safety note: " + agent["safety_note"].strip())
    return rules


def validation_requirements(agent: dict) -> list[str]:
    reqs = [
        "Every finding validates against the subagent output schema (`python -m src.cli validate-finding`).",
        "Every fact or estimate cites observation ids in research/sources/observations.jsonl.",
        "Units use codes from src/economic_model/units.py; periods state fiscal vs calendar year.",
        "Facts, estimates, assumptions and pending items are labelled separately.",
        "Uncertainty and data gaps are stated explicitly.",
    ]
    if agent["kind"] in ("auditor", "red_team"):
        reqs = [
            "Every verdict is one of VERIFIED / CONDITIONAL / UNVERIFIED / INCONSISTENT with specific reasons.",
            "Ledger chain verifies (`python -m src.cli audit-verify`).",
            "Re-computations are reproducible from committed inputs.",
        ]
    return reqs


REPORTING_FORMAT = (
    "JSON finding file per subagent task at research/findings/<agent>/<subagent>-<task>.json following "
    "docs/methodology/finding_schema.md, plus an optional Markdown summary. Include: summary, findings "
    "(each typed fact|estimate|assumption|pending with value, unit, period, source/observation ids), "
    "data_gaps, assumptions, challenges to other agents, uncertainty, and the subagent-specific fields."
)


def output_schema(sub: dict) -> dict:
    return {
        "type": "object",
        "required": ["subagent_id", "task_id", "generated_at", "summary", "findings", "data_gaps", "assumptions",
                     "challenges", "uncertainty", "specific"],
        "properties": {
            "subagent_id": {"const": sub["id"]},
            "findings": {
                "type": "array",
                "items": {
                    "required": ["claim", "type"],
                    "properties": {
                        "type": {"enum": ["fact", "estimate", "assumption", "pending"]},
                        "value": {"type": ["number", "null"]}, "unit": {"type": "string"},
                        "period": {"type": "string"}, "observation_ids": {"type": "array"},
                        "source_ids": {"type": "array"},
                    },
                },
            },
            "specific": {"type": "object", "required": list(sub["outputs"])},
        },
    }


def load_catalog() -> dict:
    return load_yaml(CATALOG_PATH)


def subagent_index(cat: dict) -> dict[str, dict]:
    idx = {}
    for a in cat["agents"]:
        for s in a["subagents"]:
            idx[s["id"]] = {**s, "parent": a["id"]}
    return idx


def expand_refs(refs: list[str], cat: dict) -> list[str]:
    agents = {a["id"]: a for a in cat["agents"]}
    subs = subagent_index(cat)
    out: list[str] = []
    for r in refs:
        r = str(r)
        if r in agents:
            out += [s["id"] for s in agents[r]["subagents"]]
        elif r in subs:
            out.append(r)
        else:
            raise KeyError(f"unknown dependency reference {r!r}")
    return sorted(set(out))


def subagent_dependencies(cat: dict) -> dict[str, list[str]]:
    deps = {}
    for a in cat["agents"]:
        base = expand_refs([str(x) for x in a.get("depends_on", [])], cat)
        for s in a["subagents"]:
            extra = expand_refs([str(x) for x in s.get("extra_depends_on", [])], cat)
            deps[s["id"]] = sorted(set(base + extra) - {s["id"]})
    return deps


def validate_catalog(cat: dict, sources: SourceCatalog | None = None) -> list[str]:
    problems = []
    agents = cat["agents"]
    ids = [a["id"] for a in agents]
    if len(agents) != EXPECTED_AGENTS:
        problems.append(f"expected {EXPECTED_AGENTS} agents, found {len(agents)}")
    if len(set(ids)) != len(ids):
        problems.append("duplicate agent ids")
    sub_ids = [s["id"] for a in agents for s in a["subagents"]]
    if len(sub_ids) != EXPECTED_SUBAGENTS:
        problems.append(f"expected {EXPECTED_SUBAGENTS} subagents, found {len(sub_ids)}")
    if len(set(sub_ids)) != len(sub_ids):
        problems.append("duplicate subagent ids")
    for a in agents:
        for f in ("id", "slug", "name", "division", "kind", "mission", "responsibilities", "deliverables", "subagents"):
            if not a.get(f):
                problems.append(f"agent {a.get('id')}: missing {f}")
        if a.get("kind") not in ROLES:
            problems.append(f"agent {a['id']}: unknown kind {a.get('kind')}")
        for s in a["subagents"]:
            if not s["id"].startswith(a["id"]):
                problems.append(f"subagent {s['id']} does not belong to agent {a['id']}")
            for f in ("name", "focus", "questions", "data", "outputs"):
                if not s.get(f):
                    problems.append(f"subagent {s['id']}: missing {f}")
            if sources is not None:
                for sid in s.get("sources", []):
                    if sid not in sources:
                        problems.append(f"subagent {s['id']}: unknown source {sid}")
    try:
        deps = subagent_dependencies(cat)
        topo_order(deps)
    except (KeyError, ValueError) as exc:
        problems.append(str(exc))
    for a in agents:
        if a.get("kind") in ("auditor", "red_team") and not a.get("independent"):
            problems.append(f"agent {a['id']}: auditors must be marked independent")
    return problems


def topo_order(deps: dict[str, list[str]]) -> list[str]:
    """Kahn's algorithm; raises ValueError on a cycle."""
    indeg = {n: 0 for n in deps}
    for n, ds in deps.items():
        for d in ds:
            if d not in deps:
                raise KeyError(f"{n} depends on unknown {d}")
            indeg[n] += 1
    dependents: dict[str, list[str]] = {n: [] for n in deps}
    for n, ds in deps.items():
        for d in ds:
            dependents[d].append(n)
    ready = sorted(n for n, k in indeg.items() if k == 0)
    order = []
    while ready:
        n = ready.pop(0)
        order.append(n)
        for m in sorted(dependents[n]):
            indeg[m] -= 1
            if indeg[m] == 0:
                ready.append(m)
        ready.sort()
    if len(order) != len(deps):
        stuck = sorted(n for n, k in indeg.items() if k > 0)
        raise ValueError(f"dependency cycle among: {stuck[:12]}")
    return order


def enriched_agents(cat: dict) -> list[dict]:
    sub_deps = subagent_dependencies(cat)
    subs = subagent_index(cat)
    agent_deps: dict[str, set[str]] = {}
    for a in cat["agents"]:
        ds = set()
        for s in a["subagents"]:
            ds |= {subs[d]["parent"] for d in sub_deps[s["id"]]}
        ds.discard(a["id"])
        agent_deps[a["id"]] = ds
    depended_by = {a["id"]: sorted(k for k, v in agent_deps.items() if a["id"] in v) for a in cat["agents"]}
    out = []
    for a in cat["agents"]:
        out.append({
            "id": a["id"], "slug": a["slug"], "name": a["name"], "division": a["division"],
            "division_name": cat["divisions"][a["division"]], "kind": a["kind"], "role": ROLES[a["kind"]],
            "independent": bool(a.get("independent", False)), "mission": " ".join(a["mission"].split()),
            "responsibilities": a["responsibilities"], "permitted_tools": TOOLS[a["kind"]],
            "data_access": data_access(a), "depends_on": sorted(agent_deps[a["id"]]),
            "depended_by": depended_by[a["id"]], "deliverables": a["deliverables"],
            "reporting_format": REPORTING_FORMAT, "escalation_rules": escalation_rules(a),
            "validation_requirements": validation_requirements(a),
            "safety_note": " ".join(a["safety_note"].split()) if a.get("safety_note") else None,
            "subagents": [s["id"] for s in a["subagents"]],
        })
    return out


def enriched_subagents(cat: dict, sources: SourceCatalog) -> list[dict]:
    deps = subagent_dependencies(cat)
    out = []
    for a in cat["agents"]:
        for s in a["subagents"]:
            src = sources.rank(list(s.get("sources", [])))
            out.append({
                "id": s["id"], "parent": a["id"], "parent_name": a["name"], "name": s["name"],
                "instructions": {"focus": s["focus"], "questions": s["questions"]},
                "evidence_requirements": {
                    "data_required": s["data"],
                    "sources_in_priority_order": src,
                    "rules": [
                        "Retrieve primary documents; record each value via ObservationStore with raw-file hash.",
                        "Report publication date and data period for every value.",
                        "When sources disagree keep both values and explain the methodological difference.",
                        "If a source is inaccessible, record the item as pending with the exact data required.",
                    ],
                },
                "depends_on": deps[s["id"]],
                "output_schema": output_schema(s),
                "acceptance_criteria": [
                    "Finding file validates against output_schema.",
                    "Every question is answered or explicitly marked pending with the data required.",
                    "All required specific fields are present: " + ", ".join(s["outputs"]) + ".",
                    "No fact or estimate lacks an observation id.",
                ],
            })
    return out
