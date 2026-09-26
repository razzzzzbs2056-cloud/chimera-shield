"""Markdown report generation.

Reports only *read* platform state (catalog, observation store, baseline,
exposure register, scenarios, audit ledger). Audit verdicts and reasons are
reproduced verbatim from the ledger — reporting code never paraphrases or
filters an auditor's findings.
"""

from __future__ import annotations

import math
from pathlib import Path

from src.agents.catalog import enriched_agents, load_catalog, subagent_dependencies
from src.auditing.ledger import AuditLedger
from src.common import CONFIG_DIR, REPORTS_DIR, ROOT, load_json, load_yaml, utc_now, write_text
from src.economic_model.target import (TARGET_USD, PriceFxCase, required_growth_table, required_per_capita,
                                       sensitivity_grid, untargeted_arrival_year)
from src.geopolitical_model.exposure import load_register
from src.orchestrator.taskgraph import waves
from src.scenario_engine.engine import load_scenarios

PENDING = "**PENDING**"


def _pct(x: float, dp: int = 2) -> str:
    return f"{x * 100:.{dp}f}%"


# ----------------------------------------------------------------------------- architecture
def architecture_report(path: Path = ROOT / "docs" / "architecture" / "architecture_report.md") -> Path:
    cat = load_catalog()
    agents = enriched_agents(cat)
    deps = subagent_dependencies(cat)
    wv = waves(deps)
    n_sub = sum(len(a["subagents"]) for a in agents)
    lines = [
        "# NEPAL 3T — Architecture Report",
        "",
        f"_Generated {utc_now()} by `python -m src.cli report`. Source of truth: `config/catalog.yaml`._",
        "",
        "## Summary",
        "",
        f"- Main agents: **{len(agents)}** (Division A: {sum(a['division'] == 'A' for a in agents)}, "
        f"Division B: {sum(a['division'] == 'B' for a in agents)})",
        f"- Subagent task specifications: **{n_sub}**",
        f"- Subagent dependency edges: **{sum(len(v) for v in deps.values())}**",
        f"- Dependency waves (critical-path length): **{len(wv)}**",
        "- Independent auditors: Agent 15 (domestic) and Agent 28 (geopolitical red team), writing only to a "
        "hash-chained, append-only ledger.",
        "",
        "## Agents",
        "",
        "| ID | Agent | Division | Role | Subagents | Consumes outputs of |",
        "|---|---|---|---|---|---|",
    ]
    for a in agents:
        lines.append(f"| {a['id']} | {a['name']} | {a['division']} | {a['role']} | {', '.join(a['subagents'])} | "
                     f"{', '.join(a['depends_on']) or '—'} |")
    lines += ["", "## Execution waves", "",
              "Tasks in the same wave have no dependencies on each other and *may* run in parallel within "
              "platform limits (`max_parallel` in `config/model_config.yaml`). This does not imply all run "
              "simultaneously.", ""]
    for i, w in enumerate(wv):
        lines.append(f"- **Wave {i}** ({len(w)} tasks): {', '.join(w)}")
    lines += [
        "", "## Agent-level dependency graph", "", "```mermaid", "graph LR",
    ]
    for a in agents:
        for d in a["depends_on"]:
            lines.append(f"  A{d} --> A{a['id']}")
    lines += ["```", "",
              "## Components", "",
              "| Layer | Module | Purpose |", "|---|---|---|",
              "| Orchestration | `src/orchestrator/` | task graph, waves, resumable run state, human-approval gate, finding validation |",
              "| Agents | `src/agents/`, `.claude/agents/` | catalog loader, generator, 29 definitions, 111 task specs |",
              "| Research | `src/research/` | source catalog, append-only observation store, duplicate/conflict/missing-source detection |",
              "| Data | `src/data/` | ingestion with raw-file hashing and metadata, baseline builder, data requirements |",
              "| Economic model | `src/economic_model/` | units, national-accounts identities, growth, projection, input-output, fiscal, energy, constraints, welfare, target arithmetic |",
              "| Geopolitical model | `src/geopolitical_model/` | transmission channels, international exposure register |",
              "| Scenarios | `src/scenario_engine/`, `scenarios/` | 10 mandatory scenarios, validation, compound composition without double-counting |",
              "| Auditing | `src/auditing/` | Agent 15 and Agent 28 checks, verdict logic, hash-chained ledger |",
              "| Reporting | `src/reporting/` | this report, baseline, target arithmetic, scenario and audit reports |",
              ""]
    write_text(path, "\n".join(lines) + "\n")
    return path


# ----------------------------------------------------------------------------- baseline
def baseline_report(path: Path = REPORTS_DIR / "baseline" / "baseline_report.md",
                    baseline_path: Path = ROOT / "data" / "processed" / "baseline.json") -> Path:
    b = load_json(baseline_path)
    s = b["summary"]
    lines = [
        "# NEPAL 3T — Baseline Report (first run)",
        "",
        f"_Generated {utc_now()} from `data/processed/baseline.json` (built {b['generated_at']}; "
        f"online retrieval attempted: {b['online_attempted']})._",
        "",
        f"**Requirements:** {s['requirements']} · **Available:** {s['available']} · **Pending:** {s['pending']}",
        "",
    ]
    if s["available"] == 0:
        lines += [
            "> **No empirical values are reported.** Every requirement below is PENDING because no source could "
            "be retrieved in this environment. No value has been estimated or substituted. The table lists "
            "exactly what is required and where it must come from.",
            "",
        ]
    lines += ["| Variable | Description | Status | Latest value | Owner | Primary source required | Cross-check series |",
              "|---|---|---|---|---|---|---|"]
    for e in b["entries"]:
        latest = PENDING
        if e["latest"]:
            L = e["latest"]
            latest = f"{L['value']:,} {L['unit']} ({L['period']}; {L['source_id']}; `{L['observation_id']}`)"
        xs = ", ".join(f"{x['source_id']}:{x['code']}" for x in e["cross_check_series"]) or "—"
        status = PENDING if e["status"] == "PENDING" else "available"
        lines.append(f"| `{e['variable']}` | {e['description']} ({e['required_unit']}) | {status} | {latest} | "
                     f"{e['owner']} | {e['primary_requirement']} | {xs} |")
    errs = [(e["variable"], a) for e in b["entries"] for a in e["retrieval_attempts"] if a["result"] != "retrieved"]
    if errs:
        lines += ["", "## Retrieval attempts that failed", "", "| Variable | Series | Error |", "|---|---|---|"]
        for var, a in errs:
            lines.append(f"| `{var}` | {a['series']['source_id']}:{a['series']['code']} | {a['error'][:160]} |")
    lines += ["", "## Source conflicts", ""]
    if b["conflicts"]:
        for c in b["conflicts"]:
            lines.append(f"- `{c['variable']}` {c['period']}: {c['a']['source_id']}={c['a']['value']} vs "
                         f"{c['b']['source_id']}={c['b']['value']} (rel. diff {c['relative_difference']:.3%}) — {c['resolution']}")
    else:
        lines.append("- None detected (no overlapping retrieved observations).")
    lines += ["", "## How to complete this baseline", "",
              "1. Run `python -m src.cli baseline --online` from an environment whose network policy allows the "
              "source hosts (see `docs/implementation/data_access.md`).",
              "2. For Nepal-official tables (NSO, NRB, MoF, NEA, DoFE), download the publication, extract a "
              "`period,value` CSV and ingest with `python -m src.cli ingest-csv <csv> <meta.json>`; the raw file is "
              "hashed and retained.",
              "3. Re-run `python -m src.cli report`. Agent 15A then verifies the retrieved values.", ""]
    write_text(path, "\n".join(lines) + "\n")
    return path


# ----------------------------------------------------------------------------- target arithmetic
def target_report(path: Path = REPORTS_DIR / "baseline" / "target_arithmetic.md") -> Path:
    cfg = load_yaml(CONFIG_DIR / "model_config.yaml")
    t = cfg["target_arithmetic"]
    base_year = t["grid_base_year"]["value"]
    cases = [PriceFxCase(c["name"], c["deflator"], c["depreciation"]) for c in t["price_fx_cases"]]
    grid_bases = t["hypothetical_base_usd_bn"]["value"]
    milestones = tuple(cfg["target"]["milestones"])
    lines = [
        "# US$3 Trillion — Required-Growth Arithmetic",
        "",
        f"_Generated {utc_now()} by `python -m src.cli report` from `src/economic_model/target.py` and "
        "`config/model_config.yaml`._",
        "",
        "> **Status: PARAMETRIC.** Nepal's verified base-year nominal GDP in USD is **PENDING** retrieval "
        "(see `reports/baseline/baseline_report.md`). The tables below use a grid of *hypothetical* base values "
        "so the arithmetic can be inspected now. They are not estimates of Nepal's GDP, and nothing here "
        "asserts that any path is achievable.",
        "",
        f"Target: US${TARGET_USD / 1e12:.0f} trillion nominal GDP. Grid base year (assumption "
        f"`{t['grid_base_year']['id']}`): {base_year}. Milestones: {', '.join(map(str, milestones))}.",
        "",
        "## 1. Required nominal USD growth for hypothetical base values",
        "",
        "Required constant annual growth of GDP measured in current US dollars:",
        "",
        "| Hypothetical base (US$ bn) | Required multiple | " + " | ".join(f"CAGR to {y}" for y in milestones) + " |",
        "|---|---|" + "---|" * len(milestones),
    ]
    for row in sensitivity_grid([b * 1e9 for b in grid_bases], base_year, milestones):
        lines.append(f"| {row['hypothetical_base_usd'] / 1e9:,.0f} | {row['required_multiple']:,.1f}× | "
                     + " | ".join(_pct(row[f'usd_cagr_to_{y}']) for y in milestones) + " |")
    lines += [
        "",
        "## 2. Real growth implied under explicit price and exchange-rate cases",
        "",
        "USD growth = (1 + real)(1 + GDP deflator) / (1 + NPR/USD depreciation) − 1. Real growth, domestic "
        "inflation and exchange-rate movement are kept separate. Cases are assumptions (ids in "
        "`config/model_config.yaml`), not forecasts.",
        "",
        "| Case | Deflator | NPR/USD depreciation | Implied USD price growth |",
        "|---|---|---|---|",
    ]
    for c in cases:
        lines.append(f"| {c.name} | {_pct(c.deflator, 1)} | {_pct(c.depreciation, 1)} | {_pct(c.usd_price_growth)} |")
    mid_base = t["illustrative_base_usd_bn"]["value"] * 1e9
    icors = tuple(t["icor_values"]["value"])
    lines += ["", f"Required **real** CAGR for a hypothetical base of US${mid_base / 1e9:,.0f} bn "
                  f"(assumption `{t['illustrative_base_usd_bn']['id']}`), with the gross investment/GDP ratio a "
                  f"constant ICOR would imply (ICOR values {', '.join(map(str, icors))}; assumption "
                  f"`{t['icor_values']['id']}`):", "",
              "| Milestone | Case | Required USD CAGR | Required real CAGR | " + " | ".join(
                  f"I/Y at ICOR {i:g}" for i in icors) + " |",
              "|---|---|---|---|" + "---|" * len(icors)]
    for r in required_growth_table(mid_base, base_year, cases, milestones, icor_values=icors):
        lines.append(f"| {r['milestone']} | {r['case']} | {_pct(r['required_nominal_usd_cagr'])} | "
                     f"{_pct(r['required_real_cagr'])} | " + " | ".join(
                         _pct(r[f'investment_rate_icor_{i:g}'], 1) for i in icors) + " |")
    lines += ["",
              "Investment ratios above 100% of GDP are arithmetically implied but physically impossible without "
              "external financing far beyond the size of the economy; they mark paths that are unattainable under "
              "that ICOR.", "",
              "## 3. Untargeted continuation: arrival year at constant growth", "",
              f"Hypothetical base US${mid_base / 1e9:,.0f} bn in {base_year}. No target is imposed; the table shows "
              "when US$3T would be reached if a constant real growth rate persisted.", "",
              "| Real growth | " + " | ".join(c.name for c in cases) + " |",
              "|---|" + "---|" * len(cases)]
    for g in t["continuation_real_growth"]["value"]:
        cells = []
        for c in cases:
            y = untargeted_arrival_year(mid_base, base_year, g, c)
            cells.append("never" if math.isinf(y) else f"{math.ceil(y)}")
        lines.append(f"| {_pct(g, 1)} | " + " | ".join(cells) + " |")
    lines += ["", "## 4. Implied GDP per capita at the target", "",
              "Population in the milestone years is **PENDING** (UN WPP / NSO projections, subagent 10C). "
              "For hypothetical populations:", "",
              "| Hypothetical population (mn) | GDP per capita at US$3T |", "|---|---|"]
    for p in t["hypothetical_population_mn"]["value"]:
        lines.append(f"| {p} | US${required_per_capita(TARGET_USD, p * 1e6):,.0f} |")
    lines += ["", "## 5. What this arithmetic does and does not establish", "",
              "- It establishes the growth rates that are *arithmetically required* for a given base, timeline "
              "and price/FX path.",
              "- It does **not** establish feasibility. Feasibility requires comparison with verified historical "
              "growth spells (01B), capital accumulation and financing limits (01A, 02C, 03C), labour and skills "
              "(09, 10), energy and infrastructure delivery constraints (05, 06) and external conditions "
              "(16-26).",
              "- The target is unattainable by a milestone whenever the sustainable USD growth rate falls below the "
              "required rate in section 1; section 2 shows how much of that must come from real growth rather "
              "than prices or exchange-rate appreciation.",
              "- Nominal USD GDP can rise through real appreciation without any change in living standards; "
              "welfare is tracked separately (`src/economic_model/welfare.py`).", ""]
    write_text(path, "\n".join(lines) + "\n")
    return path


# ----------------------------------------------------------------------------- exposure & scenarios
def exposure_report(path: Path = ROOT / "research" / "global_exposure" / "exposure_register.md") -> Path:
    entries = load_register()
    lines = ["# International Exposure Register", "", f"_Generated {utc_now()} from `exposure_register.json`._", "",
             f"Entries: {len(entries)} · measured: {sum(e.status == 'measured' for e in entries)} · pending: "
             f"{sum(e.status == 'pending' for e in entries)}", "",
             "| ID | Exposure | Channel | Counterparties | Metric | Owner | Sources | Scenarios | Status |",
             "|---|---|---|---|---|---|---|---|---|"]
    for e in entries:
        status = PENDING if e.status == "pending" else f"{e.value} {e.unit} ({e.period}, `{e.observation_id}`)"
        lines.append(f"| {e.id} | {e.title} | {e.channel} | {', '.join(e.counterparties)} | {e.metric} | {e.owner} | "
                     f"{', '.join(e.source_ids)} | {', '.join(e.scenarios)} | {status} |")
    write_text(path, "\n".join(lines) + "\n")
    return path


def scenario_report(results: dict[str, dict], path: Path = REPORTS_DIR / "baseline" / "scenario_status.md") -> Path:
    scs = load_scenarios()
    lines = ["# Scenario Status", "", f"_Generated {utc_now()}. Scenarios are hypothetical stress tests, not forecasts._",
             "", "| ID | Title | Category | Channels | Shocks | Engine status |", "|---|---|---|---|---|---|"]
    for sid, s in sorted(scs.items()):
        r = results.get(sid, {})
        comps = f" (components: {', '.join(s.components)})" if s.components else ""
        lines.append(f"| {sid} | {s.raw['title']}{comps} | {s.raw['category']} | {', '.join(s.raw['channels'])} | "
                     f"{len(s.shocks)} | {r.get('status', 'not run')} |")
    lines += ["", "QUALITATIVE_ONLY means transmission channels, exposures and responses are defined but every shock "
                  "magnitude is pending evidence, so no quantitative result is produced.", ""]
    write_text(path, "\n".join(lines) + "\n")
    return path


# ----------------------------------------------------------------------------- audits
def audit_report(ledger: AuditLedger | None = None, path: Path = REPORTS_DIR / "audits" / "audit_summary.md") -> Path:
    ledger = ledger or AuditLedger()
    recs = ledger.records()
    problems = ledger.verify()
    lines = ["# Independent Audit Summary", "",
             f"_Generated {utc_now()} from `reports/audits/audit_ledger.jsonl`. Verdicts and reasons are reproduced "
             "verbatim; this report cannot alter them._", "",
             f"Ledger records: {len(recs)} · chain integrity: {'OK' if not problems else 'BROKEN — ' + '; '.join(problems)}",
             ""]
    for r in recs:
        who = "Agent 15 (domestic)" if r.auditor == "15" else "Agent 28 (geopolitical red team)"
        lines += [f"## {r.subject_id} — {who}{' — DISSENT' if r.kind == 'dissent' else ''}", "",
                  f"- Verdict: **{r.verdict}**", f"- Recorded: {r.created_at}",
                  f"- Subject hash: `{r.subject_sha256[:16]}…` · record hash: `{r.record_hash[:16]}…`",
                  "- Reasons:"]
        lines += [f"  - {reason}" for reason in r.reasons]
        lines.append("")
    write_text(path, "\n".join(lines) + "\n")
    return path


def strategy_report(path: Path = REPORTS_DIR / "strategies" / "strategy_register.md") -> Path:
    cfg = load_yaml(CONFIG_DIR / "strategies.yaml")
    items = cfg["required_calculations"]
    lines = ["# Development Strategy Register", "", f"_Generated {utc_now()} from `config/strategies.yaml`._", "",
             "Strategies are alternative research pathways for human decision-makers. None is endorsed or ranked. "
             "All quantities are **PENDING** until the verified baseline exists (Phase 2) and the model is "
             "calibrated (Phase 3).", "",
             "| ID | Strategy | Lead agents | Status |", "|---|---|---|---|"]
    for s in cfg["strategies"]:
        lines.append(f"| {s['id']} | {s['name']} | {', '.join(s['lead_agents'])} | {s['status']} |")
    lines += ["", "## Calculations required for every strategy", "",
              "| Item | Owner | Status |", "|---|---|---|"]
    for it in items:
        lines.append(f"| {it['item']} | {it['owner']} | {PENDING} |")
    write_text(path, "\n".join(lines) + "\n")
    return path


# ----------------------------------------------------------------------------- data gaps
FEASIBILITY_CRITICAL = [
    ("gdp_nominal_usd", "Base value for every required-growth calculation"),
    ("real_gdp_growth", "Historical real growth to compare against required rates"),
    ("gdp_deflator_growth", "Separates price effects from real growth"),
    ("fx_npr_usd", "Converts NPR GDP to USD; peg history constrains FX assumptions"),
    ("population", "Per-capita income at the target; labour supply"),
    ("gfcf_share", "Investment rate and ICOR; capital-accumulation feasibility"),
    ("remittances_share", "External financing of consumption; exposure to S01/S04/S06"),
    ("gov_gross_debt_share", "Fiscal room to finance investment"),
]


def data_gaps_report(path: Path = REPORTS_DIR / "baseline" / "data_gaps.md",
                     baseline_path: Path = ROOT / "data" / "processed" / "baseline.json") -> Path:
    b = load_json(baseline_path)
    status = {e["variable"]: e for e in b["entries"]}
    reg = load_register()
    scs = load_scenarios()
    pending_shocks = [(sid, sh.id, sh.channel, sh.variable) for sid, s in sorted(scs.items())
                      for sh in s.shocks if sh.magnitude is None]
    lines = ["# Material Data Gaps and Research Dependencies", "",
             f"_Generated {utc_now()}. Regenerate with `python -m src.cli report`._", "",
             "## Blocking condition in the current run", "",
             f"Online retrieval attempted: {b['online_attempted']}. Values retrieved: {b['summary']['available']} of "
             f"{b['summary']['requirements']}. Where attempts failed, the errors are listed in "
             "`reports/baseline/baseline_report.md`.", "",
             "## 1. Feasibility-critical inputs for the US$3T question", "",
             "| Variable | Why it matters | Status | Owner | Required from |", "|---|---|---|---|---|"]
    for var, why in FEASIBILITY_CRITICAL:
        e = status[var]
        lines.append(f"| `{var}` | {why} | {PENDING if e['status'] == 'PENDING' else 'available'} | {e['owner']} | "
                     f"{e['primary_requirement']} |")
    lines += ["", "Also required before any feasibility statement (research, not single series):", "",
              "- Frequency and preconditions of sustained high-growth spells in comparable economies (01B; Maddison, PWT).",
              "- Capital-stock and TFP estimates for Nepal (01A; PWT, NSO).",
              "- Population projections by variant to 2070 (10C; UN WPP, NSO).",
              "- Historical capital-budget execution and project delivery lags (02B, 06C; MoF, OAG).",
              "- Electricity balance, pipeline completion rates and export prices (05A, 22B; NEA, CEA).", "",
              f"## 2. All baseline requirements ({b['summary']['pending']} pending)", "",
              "See `reports/baseline/baseline_report.md` for the full table with sources and series codes.", "",
              f"## 3. International exposure register ({sum(e.status == 'pending' for e in reg)} of {len(reg)} pending)", "",
              "| ID | Metric | Owner | Sources |", "|---|---|---|---|"]
    for e in reg:
        if e.status == "pending":
            lines.append(f"| {e.id} | {e.metric} | {e.owner} | {', '.join(e.source_ids)} |")
    lines += ["", f"## 4. Scenario shock magnitudes ({len(pending_shocks)} pending)", "",
              "| Scenario | Shock | Channel | Variable |", "|---|---|---|---|"]
    lines += [f"| {a} | {b_} | {c} | {d} |" for a, b_, c, d in pending_shocks]
    lines += ["", "## 5. Model components awaiting calibration", "",
              "- Base-year `ProjectionAssumptions` (needs verified nominal GDP, NPR/USD, population).",
              "- Input-output table for Nepal (NSO supply-use tables, if published; otherwise documented construction).",
              "- BoP, fiscal and household modules linking non-aggregate channels (remittances, fuel, tourism) to the "
              "projection; until then those shocks are recorded as transmission pathways only.",
              "- Provincial welfare indicators (NLSS, census) for distributional analysis.", ""]
    write_text(path, "\n".join(lines) + "\n")
    return path
