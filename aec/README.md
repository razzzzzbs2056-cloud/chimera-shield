# Chimera AEC — multi-agent architecture & engineering workflow

A full-stack app that behaves like a digital architecture/engineering consultancy. Specialist agents call **deterministic engineering solvers**, pass models, loads and constraints to each other, and iterate the design until it converges. The pipeline then authors an **IFC4 BIM model**, checks it **clause by clause** against versioned codes, prices it, plans its construction, and **independently verifies** the key results. Claude explains and recommends, but it never produces the numbers.

> Engineering outputs are scheme-level decision support. A licensed engineer must review and seal any design.

## Quick start

```bash
cd aec
npm install
npm run dev          # seeds the demo workspace on first run (≈5 s), then serves http://localhost:3100
```

Sign in with **demo@chimera.build / demo1234** (pre-filled on the login page). That account has six seeded projects (SF office tower, Seattle hospital, Austin mass-timber residential, London labs, Melbourne 45-storey residential, Chicago school in operation), each with borehole logs, a full engineering run, clashes, RFIs, design options and operational assets. A new account starts with an empty workspace and can load any sample from the Projects page.

Optional: `cp .env.example .env.local` and set `ANTHROPIC_API_KEY` to turn on the Claude-powered project assistant (`claude-opus-5-5`, grounded in the run results). Without a key, the assistant answers with a deterministic summary drawn from the solver output.

| Command | Purpose |
|---|---|
| `npm run dev` | Seed if needed, then start the dev server on :3100 |
| `npm run build && npm start` | Production build and server |
| `npm test` | Solver and workflow tests (closed-form FE, eigen, ISO 7730 PMV, equilibrium, IFC export) |
| `npm run typecheck` | TypeScript check |
| `npm run db:reset` | Delete the SQLite database and re-seed |

## How the workflow runs

```
Intake ─▶ Agent routing ─▶ Code intelligence (editions, version control)
   │
   ├▶ Geotech (boreholes → Vs30 → site class, bearing, settlement, liquefaction)
   │      └─ site class ─▶ Seismic parameters (Fa/Fv, SDS/SD1, SDC)
   ├▶ Fire ⇄ Architecture (exits, stair capacity, core sizing)
   ├▶ Structural system selection (8 systems × FE analysis, ranked by priorities)
   ├▶ Structural ⇄ Seismic loop (drift / P-Δ / column / punching → resize members, add outriggers)
   ├▶ Wind (gust factor, drift, accelerations, vortex, façade pressures, pedestrian comfort)
   ├▶ Foundation optimiser (pads, raft, piles, barrettes, piled raft)
   ├▶ HVAC → Electrical, Hydraulics, Façade, Physics, Energy, Accessibility
   ├▶ BIM authoring → physical + semantic clash detection → issues
   ├▶ QTO → BOQ → cost → embodied carbon → value engineering (re-solved, not guessed)
   ├▶ Construction (CPM, 4D links, 5D cash flow, cranes, temporary works, constructability)
   ├▶ Resilience, clause-level compliance
   └▶ Independent verifier (second method for every key quantity)
```

Every message, design change and iteration is logged on the **Agents** tab.

## Feature map

| Capability | Where | Implementation |
|---|---|---|
| Project intake engine | New project, Brief | City presets fill climate & hazard data; editable |
| Automatic agent routing | Agents | `lib/engine/agents.ts` |
| Multi-agent collaboration | Agents | `lib/engine/workflow.ts` design loop and message log |
| Design alternatives | Design | 8 concepts solved with the full engine, Pareto cost/carbon |
| Parametric generator | Design | Engine runs **in the browser** on every slider change |
| Structural system selection | Design | ASCE 7-22 Table 12.2-1 R/Cd/Ω₀ and height limits, FE drift per system |
| Loads | Structure | Live (Table 4.3-1), snow (Ch. 7), seismic ELF (§12.8), wind (Ch. 26–27) |
| FE analysis | Structure | 2D frame direct-stiffness solver, banded LDLᵀ (`frame2d.ts`) |
| Earthquake | Seismic & Wind | Modal (Jacobi), CQC response spectrum with §12.9.1.4 scaling, drift, P-Δ, torsion, capacity-spectrum pushover, Newmark MDOF time-history with a spectrum-scaled record, nonlinear ESDOF hysteresis |
| Wind | Seismic & Wind | §26.11.5 flexible gust factor, accelerations, vortex screening, C&C pressure map, Lawson comfort |
| Geotechnics & foundations | Geotech | Borehole CRUD, Imai Vs, Vesić bearing, 2:1 and Boussinesq settlement, Youd 2001 liquefaction, α/β piles, 5-way optimiser |
| HVAC / electrical / hydraulics | MEP | Zoned loads, 62.1 ventilation, N+1 plant, ISO 7730 PMV; load schedule, transformer, cable and VD sizing, fault level, PV/BESS/EV/generator; Hunter flow, pressure zones, boosters, rational-method storm, rainwater and greywater |
| Fire & accessibility | Fire & Access | Occupant load, exits, egress width, travel distance, construction type, sprinklers, SFPE evacuation, smoke-filling ASET; ADA/IBC checks |
| Façade, physics, energy | Envelope & Energy | Mullion and glass sizing, ψ-values, fRsi condensation, water test, façade fire; daylight factor, acoustics; monthly energy and scenarios |
| Carbon & resilience | Carbon & Resilience | A1–A5 by element and system; hazard register and redundancy |
| Clause-level compliance & code versions | Compliance, Code library | Requirement, clause, evidence, value/limit and PASS/FAIL for each check; pinned/superseded/draft editions |
| BIM / IFC / clashes | BIM & Clashes | Canvas viewer; IFC4 export (validated with IfcOpenShell: 0 schema issues); AABB plus semantic rules; issue CRUD that auto-syncs on every run |
| Drawings & specs | Drawings & Specs | Plans, services plans, sections and elevations from the model; schedules; MasterFormat specs linked to IFC types |
| QTO, BOQ, cost, VE | Cost & BOQ | Location-factored rates, BOQ CSV, cost by discipline and floor, VE with performance consequences |
| Construction, 4D, 5D | Construction | CPM Gantt, 4D model slider, S-curve, cranes, temporary works, constructability |
| Digital twin & maintenance | Operations | Asset CRUD, Weibull failure probability and remaining life, anomaly detection, optimisation recommendations |
| Verification | Verification | Equilibrium, Rayleigh vs eigen, statics vs FE, Boussinesq vs 2:1, BIM volume vs QTO, CPM closure, and more |

## Architecture

- **Next.js 15 (App Router) + React 19 + Tailwind**. Server components read SQLite directly; client components handle interaction, optimistic updates and charts (Recharts).
- **SQLite (better-sqlite3)** at `data/aec.db`: users, sessions, projects, boreholes, runs (full JSON result, last 10 kept), design_options, issues, standards, assets, activity.
- **Auth**: scrypt password hashes and opaque session tokens (SHA-256 at rest, httpOnly cookie). Middleware gates pages, and every query checks project ownership.
- **Engine** (`lib/engine/*`): dependency-free TypeScript, so the same code runs on the server and in the browser.

## Honest limitations

- Structural analysis uses a **planar equivalent frame** (frame lines lumped, rigid diaphragm assumed). It suits scheme design; final design needs a 3D model.
- Pushover is a capacity-spectrum method on a bilinear backbone, and the nonlinear time-history uses an equivalent SDOF. Neither is a fibre-section model.
- Wind dynamics, vortex shedding and pedestrian comfort are code-level screening. They do not replace CFD or a wind tunnel.
- Clause references are encoded for US codes, plus key UK/AU/NZ/CA equivalents. Checks without a local clause are labelled **proxy method**.
- Unit rates, carbon factors and sensor feeds are realistic generic values, not live market or BMS data.
