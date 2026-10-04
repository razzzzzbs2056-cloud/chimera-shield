# Engineering Protocol

Binding on every `bld-*` agent. Short version: **safety and structural integrity override aesthetics, and AI analysis is not certified engineering.**

## 1. Evidence rule
Label every important conclusion with exactly one tag. Never present an assumption as a fact.

| Tag | Meaning |
|---|---|
| **FACT** | Directly supported by data, code, testing or authoritative evidence (cite it) |
| **ASSUMPTION** | Used because information is missing (state it and who must confirm it) |
| **CALCULATION** | Derived mathematically (equation, units, script and test) |
| **SIMULATION** | Derived from a computational model (model file, version, verification status) |
| **JUDGMENT** | Reasoned professional interpretation |
| **UNKNOWN** | Cannot yet be determined |

## 2. Evidence ranking (high to low)
1 Applicable law/code · 2 Official engineering standard · 3 Government technical publication · 4 Peer-reviewed research · 5 Established textbook · 6 University research · 7 Manufacturer engineering documentation · 8 Professional guidance · 9 General web. Blogs and marketing are never equivalent to standards. Determine the **jurisdiction first**; never assume one country's code applies elsewhere; never fabricate clauses (write "verify against current code").

## 3. Analysis hierarchy
L1 conceptual load path → L2 hand calculations → L3 linear static → L4 response spectrum → L5 nonlinear pushover → L6 nonlinear time-history → L7 advanced FE. Climb only when the lower level cannot answer the question. A complex wrong model is worse than a simple correct one.

## 4. Model verification (every model, every time)
Geometry · units · boundary conditions · loads · seismic mass · mesh · equilibrium (reactions = applied loads) · modal shapes plausible · period plausible · drift plausible · hand-calculation comparison · sensitivity of uncertain inputs. Record the result in the report; an unverified model is labelled SIMULATION (unverified).

## 5. Inputs that may never be invented
Soil parameters (need investigation data), seismic hazard (need jurisdiction maps), code clauses, site survey, prices. If missing, list as UNKNOWN and parameterise.

## 6. Reproducibility
Calculations are scripts with equations, units, assumptions, references and tests. Layout: `docs/ architecture/ structure/ geotechnical/ seismic/ mep/ fire/ bim/ gis/ calculations/ models/ data/ scripts/ tests/ reports/ references/`. Use Git. Every design change records: WHAT CHANGED · WHY · REQUESTED BY · STRUCTURAL IMPACT · COST IMPACT · CODE IMPACT · REQUIRED REANALYSIS (`reports/change-record-template.md`).

## 7. Reviewer rule
The independent reviewer (`bld-red-team-reviewer`) does not treat agreement as success. Finding weaknesses is success. Every credible failure mechanism is written as CAUSE · MECHANISM · CONSEQUENCE · DETECTION · MITIGATION · RESIDUAL RISK.

## 8. Final safety rule
Never say a building is "earthquake proof". State the hazard and the intended performance level (operational / immediate occupancy / life safety / collapse prevention). Never issue construction-ready dimensions, reinforcement, connection details, foundation capacities or approvals from AI reasoning. Construction needs survey, geotechnical investigation, calculations, jurisdiction-specific code compliance, certified drawings, inspection, and licensed professional review and approval.
