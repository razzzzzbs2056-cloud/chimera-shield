# Engineering organisation

Generated from `org.json` by `tools/build_org.py`. Do not edit by hand.

```
                         CHIEF ENGINEERING DIRECTOR (bld-director)
        staff: requirements · task planning · routing · dependencies · iteration ·
               constraints · decisions · conflicts · memory · deliverables
                ┌───────────────────────┼───────────────────────┐
        bld-project-lead        bld-design-lead        bld-safety-qa-lead
                └───────────────────────┼───────────────────────┘
                     33 DIVISIONS (specialist agents, focus by sub-specialty)
```

**Dispatch constraint.** In Claude Code only the main-session agent can launch agents. Run `claude --agent bld-director`; the director launches staff, leads and specialists. Leads and staff plan and integrate; they do not launch agents themselves.

## Director's staff
| Agent | Role | Job |
|---|---|---|
| `bld-requirements-interpreter` | Requirements Interpreter | Turns a request ('Design a 40-storey mixed-use tower in Sydney') into a structured brief: use, scale, site, jurisdiction, performance targets, budget, programme, client values, and an explicit list of UNKNOWNs and questions for the client. |
| `bld-task-planner` | Engineering Task Planner | Breaks the brief into engineering tasks with owners, inputs, outputs, analysis level (PROTOCOL.md §3) and definition of done; writes the work breakdown. |
| `bld-discipline-router` | Discipline Router | Maps each task to the right division agent and sub-specialty focus using architecture/org.json; flags tasks no agent covers. |
| `bld-dependency-manager` | Dependency Manager | Orders tasks by data dependency (site and ground before foundations, structure before façade loads), finds what can run in parallel, and detects circular dependencies that need an iteration loop. |
| `bld-iteration-manager` | Design-Iteration Manager | Runs design → simulate → evaluate → modify loops: what changed between iterations, convergence criteria, iteration limits, and which results are invalidated by a change. |
| `bld-constraint-manager` | Constraint Manager | Keeps the single list of hard constraints (codes, strength, serviceability, drift, vibration, fire, accessibility, planning, budget, geometry) with their source class and value, and checks every option against it. |
| `bld-decision-manager` | Decision Manager | Records decisions with options considered, criteria, evidence, who decided (human or agent), and what would reopen them; prepares decisions that must go to a human. |
| `bld-conflict-resolver` | Conflict Resolver | Resolves clashes between disciplines (duct vs beam, glazing vs overheating, cost vs carbon) by stating the trade-off, quantifying each side, and recommending; never resolves a conflict by relaxing a safety constraint. |
| `bld-engineering-memory` | Engineering Memory Agent | Maintains architecture/memory/: assumptions register, facts with sources, decisions, lessons and known errors, so later agents start from the project's record instead of re-deriving or contradicting it. |
| `bld-deliverables-manager` | Deliverables Manager | Tracks every deliverable (reports, models, drawings, schedules, IFC, pages), its status, version, reviewer and whether it passed the return-format validator and Safety/QA gate. |

## Leads
| Agent | Scope |
|---|---|
| `bld-project-lead` | Project Agent: scope, programme, cost, procurement, construction, transport. |
| `bld-design-lead` | Design Agent: architecture and engineering design integration. |
| `bld-safety-qa-lead` | Safety / QA Agent: life safety, codes, accessibility, risk, critique and independent verification; holds the issue gate. |

## Divisions
| # | Division | Agent | Lead | Support | Sub-specialties |
|---|---|---|---|---|---|
| 2 | Architecture | `bld-concept-designer` | `bld-design-lead` | `bld-artist`, `bld-precedent-researcher` | 28 |
| 3 | Structural Engineering | `bld-structural-engineer` | `bld-design-lead` |  | 46 |
| 4 | Earthquake Engineering | `bld-seismic-engineer` | `bld-design-lead` | `bld-results-interpreter` | 24 |
| 5 | Geotechnical Engineering | `bld-geotech-civil` | `bld-design-lead` |  | 19 |
| 6 | Foundation Engineering | `bld-foundation-engineer` | `bld-design-lead` |  | 8 |
| 7 | Wind Engineering | `bld-wind-engineer` | `bld-design-lead` |  | 14 |
| 8 | Mechanical / HVAC | `bld-mechanical-hvac` | `bld-design-lead` | `bld-mep-engineer` | 21 |
| 9 | Building Energy | `bld-energy-modeller` | `bld-design-lead` |  | 10 |
| 10 | Electrical Engineering | `bld-electrical-engineer` | `bld-design-lead` | `bld-mep-engineer` | 23 |
| 11 | Hydraulic / Plumbing | `bld-plumbing-hydraulic` | `bld-design-lead` | `bld-mep-engineer` | 14 |
| 12 | Fire Engineering | `bld-fire-life-safety` | `bld-safety-qa-lead` |  | 16 |
| 13 | Façade Engineering | `bld-facade-engineer` | `bld-design-lead` |  | 18 |
| 14 | Building Physics | `bld-building-physicist` | `bld-design-lead` |  | 12 |
| 15 | Sustainability | `bld-sustainability-analyst` | `bld-design-lead` |  | 14 |
| 16 | Civil / Site Engineering | `bld-civil-site-engineer` | `bld-design-lead` | `bld-gis-site-analyst`, `bld-flood-stormwater`, `bld-transport-parking` | 16 |
| 17 | BIM | `bld-bim-coordinator` | `bld-design-lead` |  | 15 |
| 18 | Open-source BIM engine | engine: IfcOpenShell (ifcopenshell 0.9.0, IfcTester) | `bld-design-lead` |  | 9 |
| 19 | Quantity Surveyor | `bld-cost-planner` | `bld-project-lead` |  | 13 |
| 20 | Construction Engineering | `bld-construction-manager` | `bld-project-lead` |  | 14 |
| 21 | Planning | `bld-scheduler` | `bld-project-lead` |  | 10 |
| 22 | Codes | `bld-code-compliance` | `bld-safety-qa-lead` |  | 11 |
| 23 | Optimisation | `bld-optimisation-agent` | `bld-design-lead` |  | 7 |
| 24 | Engineering Critic | `bld-red-team-reviewer` | `bld-safety-qa-lead` |  | 14 |
| 25 | Independent Verification | `bld-independent-verifier` | `bld-safety-qa-lead` | `bld-reviewer` | 4 |
| 26 | Acoustics | `bld-acoustics-engineer` | `bld-design-lead` |  | 6 |
| 27 | Lighting / Daylight | `bld-lighting-daylight` | `bld-design-lead` |  | 6 |
| 28 | Flood / Stormwater | `bld-flood-stormwater` | `bld-design-lead` |  | 7 |
| 29 | Transportation / Parking | `bld-transport-parking` | `bld-project-lead` |  | 6 |
| 30 | Accessibility | `bld-accessibility` | `bld-safety-qa-lead` |  | 6 |
| 31 | Materials | `bld-materials-scientist` | `bld-design-lead` |  | 6 |
| 32 | Risk / Reliability | `bld-risk-reliability` | `bld-safety-qa-lead` |  | 6 |
| 33 | MEP Coordination | `bld-mep-engineer` | `bld-design-lead` |  | 4 |
| 34 | Computational Engineering | `bld-computational-engineer` | `bld-design-lead` |  | 5 |
| 35 | Simulation Results Interpretation | `bld-results-interpreter` | `bld-design-lead` |  | 6 |

## Every specialist returns
```
INPUTS USED
ASSUMPTIONS
METHOD
CALCULATIONS
RESULTS
CODE / STANDARD
UNCERTAINTIES
FAILED CHECKS
RECOMMENDATIONS
REQUIRED HUMAN REVIEW
```
Checked by `tools/validate_return.py` (fire returns also need a verdict: PASS / FAIL / INSUFFICIENT INFORMATION / PROFESSIONAL REVIEW REQUIRED).

## Requirement source classes (Codes division)
LAW, BUILDING CODE, REFERENCED STANDARD, GUIDANCE, PROJECT SPECIFICATION, CLIENT REQUIREMENT, ENGINEERING ASSUMPTION

## Pipelines
- **Earthquake:** seismic agent → OpenSees model → simulation → results interpreter → independent verifier + `verify_compare.py` (reference: `seismic/pipeline.py`).
- **Energy:** architect → geometry → energy modeller → EnergyPlus → optimisation agent → architect + HVAC (EnergyPlus not installed here).
- **Verification:** engineer A → solution; verifier B → independent method; `verify_compare.py` (C) → PROCEED or INVESTIGATE.
- **Options:** architecture generates A..E for named objectives → constraint manager filters → optimisation agent (`tools/pareto.py`, pymoo) → decision manager → human decision.
