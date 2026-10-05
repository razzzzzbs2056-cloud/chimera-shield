# Chimera Pavilion — Feasibility Engineering Report v0.1

Prepared by the `bld-*` agent team under `architecture/PROTOCOL.md`. Date: 2026-10-04.

> **Status: concept feasibility. Not a design for construction.** No jurisdiction, site, survey or geotechnical data exists for this project. Every number below is tagged **FACT**, **ASSUMPTION**, **CALCULATION**, **SIMULATION**, **JUDGMENT** or **UNKNOWN**. Nothing here may be used for construction, permitting or procurement without a site investigation, jurisdiction-specific code compliance, certified drawings, and licensed professional review and approval.

Reproduce every number: `python -m pytest -q architecture/tests` (28 tests), then
`python architecture/calculations/seismic_screen.py`, `python architecture/bim/make_ifc.py`, `python architecture/calculations/takeoff_reconcile.py`, `python architecture/tools/quickcheck.py`.

---

## 1. Executive Summary

- **What it is.** A 3-storey timber–concrete hybrid community pavilion: 48 × 32 m footprint on an 8 m grid, 24 × 24 m column-free hall under a glulam diagrid roof, two reinforced-concrete cores at the north corners, CLT floors, copper-and-glass veil. **FACT** (design-brief.md).
- **Biggest finding: the lateral system is in the wrong place.** Both cores sit on the north edge. **CALCULATION** (`seismic_screen.py`): stiffness centre at y = 4.0 m, mass centre at y = 11.6 m, eccentricity 7.6 m = **24 % of plan depth**; rotational/translational frequency ratio 1.09; displacement at the south (glazed) edge **1.34×** the average under rigid-diaphragm assumptions. Adding two lateral elements at the south ends of the floor wings (each half a core's stiffness) cuts eccentricity to 1 %, raises the ratio to 1.38 and removes the amplification (0.99). **Recommendation: change the architecture before anything else is designed** (§6, CR-003).
- **Second finding: the diaphragm is a U.** The hall void removes 576 m² (37.5 %) of L1 and L2 and is open to the south, so each floor is two wings hanging off an 8 m north strip, made of CLT (a flexible diaphragm). The rigid-diaphragm torsion numbers above are therefore optimistic. **JUDGMENT**; quantification needs a Level 3 model with diaphragm flexibility (§12).
- **Third finding: the earlier design contradicts itself.** The IFC model generated from the brief's geometry gives **3,456 m²** of floor area against a **4,188 m²** program (−17.5 %), and **432 m³** of CLT against **630 m³** in the hand take-off. **SIMULATION (verified)**. Embodied carbon (A1–A3, partial scope) moves from 128–282 to **146–320 kgCO₂e/m²** on the real floor area; stored biogenic carbon from ~675 t to **~528 t**. The program must be cut or floor area added (CR-001, CR-002).
- **Dynamic character.** Fundamental period **0.12 s** (range 0.09–0.18 s with cracking assumptions), 86 % mass in mode 1: a short-period, stiff, wall-dominated structure. **CALCULATION**, independently reproduced in **OpenSeesPy to within 0.1 %** (**SIMULATION, verified**).
- **Seismic hazard: UNKNOWN.** Demands are given per unit spectral acceleration: elastic base shear ≈ **0.86 · Sa · W** with W = 22.3 MN. Whether the cores are adequate depends entirely on the jurisdiction's hazard and design rules.
- **Performance level** cannot be set until the jurisdiction is known. Proposed objective (JUDGMENT, for an assembly building of ~400 people): life safety at the design earthquake, collapse prevention at the rare earthquake, immediate occupancy for frequent events. The building is not, and will not be described as, "earthquake proof".

## 2. Project Assumptions

| # | Assumption | Tag | Who must confirm |
|---|---|---|---|
| A1 | Temperate climate, urban, level 2 ha plot, long axis east–west | ASSUMPTION | Client / GIS |
| A2 | Jurisdiction: none applied. Eurocode-style load factors used for gravity pre-sizing only | ASSUMPTION | Code specialist |
| A3 | Live load 4.0 kPa (assembly), dead 1.7 kPa on floors (`data/live_loads.csv`) | ASSUMPTION | Structural |
| A4 | Seismic mass = dead + 0.3 × live (combination factor is code-specific) | ASSUMPTION | Seismic |
| A5 | Cores: two 8 × 8 m boxes, 0.40 m walls, C40/50, E = 35 GPa, cracked factor 0.5 | ASSUMPTION | Structural |
| A6 | Base fixed at ground level; no soil–structure interaction | ASSUMPTION | Geotech / seismic |
| A7 | Floor masses split equally over L1–L3 | ASSUMPTION | Computational |
| A8 | Member sizes in the IFC model are placeholders (columns 0.40², joists 0.24 × 0.68, girders 0.32 × 0.88) | ASSUMPTION | Structural |
| A9 | Design life 50 years | ASSUMPTION | Client |
| A10 | Budget: none given | UNKNOWN | Client |

## 3. Required Missing Information

Priority order (each blocks the items after it):
1. **Location, coordinates and jurisdiction** → codes, seismic hazard, wind, snow, fire, accessibility, energy rules.
2. **Topographic and utilities survey.**
3. **Geotechnical investigation** (scope in §5).
4. **Seismic hazard**: site-specific spectrum or code map values, near-fault status, site class (needs Vs30).
5. **Basic wind speed, terrain category, snow load.**
6. **Client brief**: confirmed program area (resolves C-01), budget, design life, performance objectives, occupancy numbers.
7. **Local supply chain**: availability of glulam/CLT, copper, concrete grades; local contractor expertise in mass timber.

## 4. Site / GIS Assessment

**Status: UNKNOWN site.** Nothing in this section can be assessed without a location. Layer plan for `bld-gis-site-analyst` (QGIS project in `architecture/gis/`):

| Layer | Source class (prefer national/local authoritative data) | Decides |
|---|---|---|
| Parcel, setbacks, heights | Local government cadastre and planning portal | Massing limits |
| Terrain / contours / slope | National mapping agency DEM; Copernicus DEM as fallback | Grading, drainage, retaining |
| Flood zones | National flood maps | Floor level, basement, SuDS |
| Geology, faults | National geological survey; USGS (USA) | Foundations, near-fault effects |
| Seismic hazard | National seismic hazard model / code maps | Spectrum |
| Liquefaction / landslide susceptibility | Geological survey, local hazard maps | Ground improvement, piles |
| Utilities, roads, transport | Utility owners; OpenStreetMap (as indicative only) | Connections, access, logistics |
| Solar and wind | Climate files for the nearest station | Façade, energy, wind loads |
| Neighbours | Survey + OSM buildings | Pounding gaps, excavation risk, overshadowing |

Generic GIS data is not a substitute for a project survey. **JUDGMENT**

## 5. Geotechnical Assessment

**No geotechnical data. All soil parameters UNKNOWN.** The presumptive values in `data/soils.csv` are for orientation only and are not used in any calculation here.

Investigation scope to request (JUDGMENT, to be finalised by the geotechnical engineer to local practice): boreholes at the two core locations and at the hall perimeter, with depth governed by the expected foundation type and stress influence zone; SPT at regular intervals and/or CPTu soundings between boreholes; groundwater standpipes with monitoring through a wet season; laboratory classification, strength, consolidation and (if fines present) plasticity; **shear-wave velocity profile** (for site class / site response); liquefaction screening if saturated sands or silts are found; chemical tests for concrete aggressivity.

Evaluations that become possible only then: bearing capacity, total and differential settlement (critical here: heavy cores next to light timber bays), liquefaction and lateral spreading, soil amplification, uplift resistance under core overturning.

## 6. Architectural Concept

**FACT (design-brief.md, pavilion-concept.html):** three-part "chimera": concrete-and-earth heart, timber skeleton, copper skin. Hall 24 × 24 m south-central, foyer west, workshops north, back-of-house and toilets east, roof terrace, lattice canopy.

**Changes recommended by the engineering team (not yet accepted by the architect):**
1. **CR-003 — lateral elements at the south ends of both floor wings** (x ≈ 4 and 44 m, y ≈ 28 m): two cores, or two pairs of braced timber/steel bays, or concrete shear walls. They fit in the foyer and back-of-house bays without touching the hall. This is the single most effective change found (see §8).
2. **CR-001 — resolve the area gap**: either reduce the program by ~730 m², or add a gallery ring inside the hall at L1, or extend L2/L3 over parts of the hall with a long-span floor (structurally expensive).
3. **Glazed south wall**: the most flexible edge of the building carries the most brittle cladding. Specify drift-tolerant framing (§14).

## 7. Structural Concept

**Gravity:** CLT 150 mm deck → glulam joists at 4 m spacing spanning 8 m → glulam girders on gridlines → glulam columns on the 8 m grid → foundation. Hall roof: glulam diagrid (24 × 24 m) on perimeter columns. **FACT** (brief) / sizes **ASSUMPTION**.

**Lateral:** floor diaphragms (CLT) → collectors along gridlines → two RC cores → foundation. **FACT** (brief).

Pre-size, joist 8 m span, 4 m tributary: GL24h **240 × 680 mm**, M = 265 kNm, deflection L/476 under service load (limit L/300 in tool, project target L/350). **CALCULATION** (`tools/quickcheck.py`); shear, bearing, lateral-torsional stability, vibration, connections and fire design **not checked**.

System comparison (**JUDGMENT**, to be quantified when the site is known):

| System | Earthquake behaviour | Fire | Carbon | Fit for this building |
|---|---|---|---|---|
| RC cores + timber gravity frame (current) | Stiff, good if cores well placed and ductile; timber frame must follow drifts | Good (cores) | Low–medium | Good **after CR-003** |
| RC walls distributed (+ timber floors) | Robust, low torsion | Good | Medium | Good, more concrete |
| Steel braced frames + timber floors | Ductile if capacity designed; lighter | Needs protection | Medium | Good for south bays |
| Timber shear walls (CLT) | Ductility from connections only | Charring design | Lowest | Limited for 400-person hall, check |
| Base isolation | Reduces demand strongly on stiff short-period buildings like this one | — | Adds cost | Consider if hazard is high (§8) |

## 8. Earthquake Strategy

**Hazard: UNKNOWN.** Strategy below is configuration-first, then demand-parameterised.

**8.1 Dynamic properties (CALCULATION, verified by SIMULATION)**

| Model | T₁ (s) | T₂ | T₃ | Mode 1 mass |
|---|---|---|---|---|
| Cantilever cores, flexure only — hand | 0.090 | 0.015 | 0.005 | 76 % |
| Same in OpenSeesPy (elasticBeamColumn) | 0.0895 | 0.0146 | 0.0053 | — |
| Cantilever cores, flexure + shear — hand | 0.124 | 0.038 | 0.022 | 86 % |
| Same in OpenSeesPy (ElasticTimoshenkoBeam) | 0.1237 | 0.0378 | 0.0219 | — |

Sensitivity of T₁ to cracked stiffness factor 0.25 / 0.5 / 1.0: 0.175 / 0.124 / 0.088 s. Masses L1/L2/L3: 841 / 793 / 638 t; W = 22.3 MN. Shear deformation matters (+38 % period) because the cores are squat (H/L ≈ 1.7). **JUDGMENT:** soil–structure interaction and diaphragm flexibility will lengthen the real period; at this period range many design spectra are on or near their plateau, so the building should be expected to attract close to peak spectral acceleration.

**8.2 Elastic demand per unit hazard (CALCULATION; no force reduction, no code)**

| Sa | Base shear | V/W | Base moment | Core web shear stress |
|---|---|---|---|---|
| 0.1 g | 1.9 MN | 0.09 | 20.5 MN·m | 0.15 MPa |
| 0.2 g | 3.8 MN | 0.17 | 41.0 MN·m | 0.30 MPa |
| 0.4 g | 7.7 MN | 0.34 | 82.0 MN·m | 0.60 MPa |
| 0.8 g | 15.3 MN | 0.69 | 163.9 MN·m | 1.20 MPa |

Elastic storey drift ratios stay below 0.03 % at 0.8 g in this fixed-base, rigid-diaphragm model: **the cores are not drift-governed; strength, shear and foundation overturning will govern.** Compare the shear stresses only with the capacity rules of the applicable concrete code.

**8.3 Configuration (CALCULATION + JUDGMENT)**

| Check | Result | Severity |
|---|---|---|
| Torsion (cores only, scheme A) | e = 7.6 m (24 % of 32 m), Ω = 1.09, south-edge amplification 1.34 | **High** |
| Torsion (scheme B, + south elements) | e = 0.4 m (1 %), Ω = 1.38, amplification 0.99 | Resolved (if adopted) |
| Diaphragm opening | 37.5 % of L1/L2 removed, open to south; wings 8 × 24 m (west) and 16 × 24 m (east) cantilever from an 8 m strip | **High** |
| Soft/weak storey | Lateral system (cores) continuous; L0 is 5.5 m vs 4.2 m above, but gravity columns only | Medium (deformation compatibility) |
| Hall perimeter columns | 9.7 m unbraced on the hall side; slenderness L/i ≈ 84 for 0.40 m square | Medium (buckling, see §26) |
| Mass irregularity | Roof terrace 420 m² + plant: check vertical mass ratios when loads are firm | Unknown |
| Re-entrant corner | U-shaped floor plate | High (linked to diaphragm) |
| Pounding | Neighbours unknown | Unknown |

**8.4 Performance objectives (JUDGMENT, to be fixed with client and code):** frequent earthquake: immediate occupancy, no structural damage, façade intact. Design earthquake: life safety, repairable damage in cores, timber frame elastic. Rare earthquake: collapse prevention, no loss of gravity support. Aftershocks: damaged cores must retain residual capacity. Near-fault: check if mapped.

**8.5 Strategy:** (1) adopt CR-003 to fix torsion; (2) design collectors and chords for the U-shaped diaphragm, or add drag struts across the hall top at the lattice level; (3) capacity-design the cores (flexural yielding at the base, shear and foundation protected); (4) make the timber gravity frame deformation-compatible with core drifts amplified for torsion and diaphragm flexibility; (5) if hazard is high and the hall must stay usable after an event, evaluate base isolation, which is most effective on short-period stiff buildings like this one.

## 9. Structural Load Paths

**Gravity:** roof/floor → CLT deck → joists → girders → columns / core walls → foundation → soil.
Discontinuities flagged: (G1) hall: roof load → diagrid ribs → perimeter columns only, no intermediate support over 24 m; (G2) columns at (16, 32) and (24, 32) stop at 9.7 m (hall wall); (G3) entry cantilever ~4 m beyond the south face, load path not designed.

**Lateral:** earthquake/wind → CLT diaphragm → collectors on gridlines → cores → foundation → ground.
Discontinuities flagged: (L1) no lateral element in the south 24 m of the plan; (L2) diaphragm U-shape, west and east wings connect to cores only through the north strip; (L3) hall roof lattice is not connected to any lateral element except through perimeter columns: its diaphragm action and the south wall's out-of-plane wind load path are undefined; (L4) collectors from the wings into the cores have not been located.

## 10. Foundation Strategy

**Capacities UNKNOWN.** Options (JUDGMENT): pads under timber columns + rafts or pile groups under the cores; or a single raft; or piled raft if soft layers or liquefiable layers exist. Governing issues: differential settlement between heavy cores and light frame; overturning of the cores (base moment at 0.4 g elastic: 82 MN·m, before force reduction) and possible uplift; seismic sliding; groundwater. The hand take-off's 0.45 m raft over 1,500 m² is a placeholder and must not be priced or designed.

## 11. Preliminary Analysis

All CALCULATION, scripts and tests in the repository:
- Gravity joist pre-size (§7).
- Seismic mass, periods, modes, participation, demand per Sa, plan torsion (§8) — `calculations/seismic_screen.py`, 7 tests incl. closed-form SDOF and OpenSeesPy cross-check.
- Basic wind velocity pressure q = ½ρv² with ρ = 1.225 kg/m³: v = 25 / 35 / 45 m/s → **0.38 / 0.75 / 1.24 kPa** before exposure, height, gust and pressure coefficients (§15).
- Column slenderness: 0.40 m square, i = 0.115 m: storey columns 5.5 m → L/i ≈ 48; hall-wall columns 9.7 m → L/i ≈ 84.
- Quantities and carbon from the IFC model (§18, §21).

## 12. Computational Modelling Plan

| Level | Model | Question it answers | Status |
|---|---|---|---|
| L1 | Load-path diagrams | Is every load path complete? | Done (§9), gaps found |
| L2 | Hand checks, cantilever cores, plan torsion | Order of magnitude, configuration | **Done, verified** |
| L3 | 3-D linear model (OpenSeesPy): cores as shell/wide-column, CLT diaphragm as flexible springs, collectors, timber frame with pinned connections | Real torsion with flexible diaphragm; collector forces; drift at wing tips | **Next** |
| L4 | Response spectrum on L3 model, accidental torsion | Code-level forces | Needs hazard |
| L5 | Pushover of cores (fibre sections) | Ductility capacity, hinge locations | After L4 |
| L6 | Nonlinear time-history, scaled records | Only if base isolation or high hazard | Conditional |
| L7 | Component FE (CalculiX / Code_Aster): diagrid nodes, CLT-to-core connections | Stress concentration, connection design | Detailed design |

Every model passes PROTOCOL §4 checks; the L2 results already pass geometry, units (IFC unit bug found and fixed), equilibrium-by-construction, period plausibility and independent-code comparison.

## 13. Open-Source Tools Recommended

Full cards in `references/open-source-tools.md`. Summary:

| Tool | Purpose | Why | Inputs → outputs | Limitations | Validation |
|---|---|---|---|---|---|
| **OpenSeesPy** | Modal, response spectrum, pushover, time-history, SSI | Research-grade earthquake engine, scriptable | Nodes, elements, materials, masses, records → modes, forces, drifts | Easy to build wrong models; no code checking; convergence | Hand calcs, equilibrium, mesh/time-step studies (done for L2) |
| **NumPy / SciPy** | Hand-check models, eigen, optimisation, Monte Carlo | Transparent, testable | Arrays → results | You own all physics | Unit tests, closed forms |
| **IfcOpenShell** | IFC authoring, auditing, quantities | Open standard, scriptable | Geometry, properties → IFC, quantities | Geometry kernel edge cases; units defaults | Bounding box, analytic volumes (done) |
| **Bonsai (BlenderBIM)** | Interactive IFC modelling, drawings | Open IFC-native authoring | IFC ↔ IFC | Learning curve | Model checks, IDS |
| **FreeCAD (BIM/FEM)** | Parametric geometry, drawings, CalculiX front-end | Parametric + FE in one | Geometry → drawings, meshes | Not a code checker | Compare with hand calcs |
| **CalculiX** | Component FE (nodes, connections) | Robust solver | Meshes, materials → stresses | Mesh-dependent; contact difficult | Mesh convergence, hand checks |
| **Code_Aster** | Advanced nonlinear / thermal-mechanical FE | Validated industrial code | Meshes → nonlinear response | Steep learning curve | Benchmarks, convergence |
| **MFront** | Custom constitutive laws | For timber/concrete nonlinear models | Law definition → compiled behaviour | Only if needed | Material tests |
| **QGIS** | Site, hazard, utilities layers | Open, authoritative-data friendly | GIS layers → maps, constraints | Data quality = source quality | Survey comparison |
| **Blender** | Visualisation, sequencing animation | Presentation | Geometry → images | **Never evidence of feasibility** | — |

## 14. Seismic Detailing (topics for the detailed design; no details issued here)

Cores: flexural hinge zone at base with confinement and boundary elements; shear designed for capacity (overstrength) actions; lap splices outside hinge zones; anchorage into foundation; openings in cores placed away from boundary zones. Collectors and chords: continuous ties from wing tips into cores, connections designed for overstrength forces; CLT panel-to-panel and panel-to-core connections with ductile fasteners and capacity-protected brittle parts. Timber gravity frame: connections that tolerate amplified drift without losing bearing; positive anchorage of column bases. Hall diagrid: node connections protected from seismic overstress. Non-structural: glazing framed for in-plane drift with clearance; copper veil panels with slotted anchors; ceilings, ducts, pipes, sprinkler mains, tanks, PV and plant braced; lifts with seismic switches.

## 15. Wind Engineering

Basic wind speed **UNKNOWN**. Basic velocity pressure for orientation 0.38–1.24 kPa (v = 25–45 m/s) **CALCULATION**; code exposure, gust and pressure coefficients not applied. Concerns (JUDGMENT): large glazed south wall (out-of-plane load path L3, §9), uplift on the lattice canopy and pergola, edge and corner suctions on the copper veil, roof-terrace parapets and planting. Building is low and stiff: drift, acceleration and vortex shedding are unlikely to govern. Wind-tunnel testing is not justified for the building; consider it only for the canopy if its shape is unusual.

## 16. Fire / Life Safety

Governing fire code **UNKNOWN**. Facts and judgments: assembly hall ~400 people (FACT, brief) → at least two remote exits from the hall, exit widths and travel distances per the code; exposed timber: char rate ~0.65 mm/min (data, typical) → indicative R60 residual section check in brief §5; cores provide protected stairs; sprinklers recommended for a timber assembly building (JUDGMENT); smoke control for the 9.7 m hall; fire-stopping at CLT joints; firefighter access to the south and east faces; emergency power and lighting; **fire following earthquake**: brace sprinkler mains, flexible couplings at core interfaces, seismic gas shut-off.

## 17. MEP

Strategy (brief §7, FACT): passive first, heat pump, radiant floors, demand-controlled ventilation with heat recovery, PV, rainwater reuse, sprinklers. Coordination rules: **no cutting or notching of glulam or CLT without structural review**; services zone 0.5 m within 4.2 m floor-to-floor; risers in cores; plant on roof needs mass allowance and seismic restraint. Plant room ≈ 5.5 % GFA from program (FACT).

## 18. BIM / IFC Workflow

`architecture/bim/make_ifc.py` (IfcOpenShell) generates `chimera-pavilion-structure.ifc` (IFC4, metres) from the brief: 23 columns, 105 joists, 51 girders, 10 slabs, 8 core walls, storeys L0–L3. The audit extracts volumes from the geometry kernel and compares with analytic values in tests.

Defects found and fixed while building it (both are exactly the failures PROTOCOL §4 targets): (1) **units**: the library defaults to millimetres; every dimension was 1000× too small until metres were set explicitly; (2) **geometry**: girders were rotated so their depth was horizontal; caught by the bounding-box check and fixed.

Design inconsistencies found by the model: **C-01** floor area 3,456 m² vs program 4,188 m²; **C-02** CLT volume 432 vs 630 m³ in the take-off.

Pipeline (target): survey/GIS → architectural IFC (Bonsai) → structural IFC (this script → hand-modelled) → analytical model export to OpenSeesPy → MEP IFC → federation → clash detection → quantities (`takeoff_reconcile.py`) → 4D sequence → asset data. Keep IFC as the source of truth.

## 19. Construction Strategy

Sequence (JUDGMENT): enabling and investigation → foundations → **cores first** (they stabilise everything) → timber frame erected bay by bay, **braced back to the cores**; until CR-003 elements exist, the south wings are temporarily unstable laterally and need temporary bracing → CLT decks with immediate weather protection → hall diagrid assembled in segments on temporary shoring towers, released in a planned sequence → envelope → services → commissioning. Critical lifts: diagrid segments, CLT panels; crane position governed by hall centre reach. Inspection points: formation, rebar and cover before each core pour, concrete strength, timber moisture on arrival and before enclosure, connection installation (fastener counts, edge distances), steel node welds, fire-stopping, waterproofing.

## 20. Cost

No rates (UNKNOWN). Cost drivers (JUDGMENT, ranked): (1) bespoke diagrid nodes and long-span hall roof; (2) foundations (UNKNOWN ground); (3) envelope: copper veil and large glazing; (4) MEP for assembly use; (5) mass-timber package and its fire-protection requirements; (6) CR-003 lateral elements (adds cost, removes torsion risk; not a candidate for value engineering). Value-engineering candidates that do not touch safety: standardise diagrid node geometry; repeat CLT panel sizes; simplify veil panel types using the seeded pattern's discrete hole sizes.

## 21. Sustainability

Embodied carbon A1–A3, structure + glass + copper only (**CALCULATION**, `takeoff_reconcile.py`):

| Take-off | Total | per m² |
|---|---|---|
| v0.1 hand (CLT 630 m³), on 4,188 m² | 537–1,181 tCO₂e | 128–282 kgCO₂e/m² |
| v0.2 IFC (CLT 432 m³), on 4,188 m² | 504–1,106 tCO₂e | 120–264 kgCO₂e/m² |
| **v0.2 IFC, on model area 3,456 m²** | **504–1,106 tCO₂e** | **146–320 kgCO₂e/m²** |

Biogenic carbon stored: ~528 tCO₂e (was ~675), reported separately, never netted. Foundations scope is a placeholder. Missing modules: A4, A5, B, C, D, insulation, MEP, finishes. Passive design, PV and rainwater reuse as brief §7–8.

## 22. Code Compliance Requirements

Jurisdiction **UNKNOWN**; no clause is cited. Once known, the code specialist must identify: building code and occupancy classification (assembly); construction type limits for mass timber of this height and area; seismic standard and hazard maps; concrete, steel, timber, masonry and geotechnical standards; fire code (sprinklers, compartments, egress); accessibility; energy; planning. Index of common frameworks: `data/codes_standards.csv` (Eurocodes, ASCE/ACI/AISC/NDS, NBC Canada, UK Approved Documents). One country's code is never applied in another.

## 23. Risk Register

| Risk | Probability | Consequence | Severity | Evidence | Mitigation | Verification |
|---|---|---|---|---|---|---|
| Torsional response from north-only cores | High (it is the current layout) | Large south-edge drift, glazing failure, column damage | **High** | CALC: e/B 24 %, amp 1.34 | CR-003 south lateral elements | L3 3-D model with flexible diaphragm |
| U-shaped CLT diaphragm overstressed / too flexible | High | Wing-tip drift, connection failure, loss of support | **High** | JUDGMENT + geometry FACT | Collectors, chords, CR-003, drag struts | L3 model; connection design |
| Program does not fit the building (C-01) | Certain | Redesign, cost and schedule | **High** | SIMULATION: 3,456 vs 4,188 m² | CR-001 decision | Updated IFC area audit |
| Unknown ground (liquefaction, soft soils) | Unknown | Foundation redesign, differential settlement | **High** until investigated | UNKNOWN | Site investigation (§5) | Geotechnical report |
| Hazard higher than cores can take elastically | Unknown | Need for ductile design or isolation | Medium–High | CALC: V/W = 0.86 Sa | Capacity design; consider isolation | L4–L5 analysis |
| Hall-wall columns buckle (L/i ≈ 84) | Medium | Hall wall instability | Medium | CALC | Larger/built-up sections, bracing to lattice | Buckling check per timber code |
| Fire in exposed-timber assembly hall | Medium | Life safety | **High** | JUDGMENT | Sprinklers, smoke control, char design, encapsulation where required | Fire strategy, code check |
| Timber wetting during construction | Medium | Decay, swelling, delay | Medium | JUDGMENT | Weather protection, moisture monitoring | Moisture readings before enclosure |
| Construction-stage instability of wings | Medium | Collapse during erection | **High** | Load path L1 | Temporary bracing plan | Temporary works design check |
| Carbon claims overstated in published material | Occurred | Credibility | Medium | SIMULATION: CLT −31 % | CR-002, page and brief updated | Re-run reconcile on each change |
| Fire following earthquake | Low–Medium | Uncontrolled fire with impaired sprinklers | High | JUDGMENT | Braced sprinkler mains, gas shut-off | MEP seismic restraint review |

## 24. Failure-Mode Analysis (red team)

**F1 — Torsional overload of the south bays**
CAUSE: all lateral stiffness on the north edge. MECHANISM: plan rotation about a stiffness centre at y ≈ 4 m; south edge deflects 1.34× average (rigid diaphragm), more with a flexible one. CONSEQUENCE: glazing failure over an assembly hall exit route; drift-induced damage to timber connections at the south. DETECTION: L3 model; accidental torsion analysis. MITIGATION: CR-003. RESIDUAL RISK: low if adopted, high if not.

**F2 — Diaphragm tear at the re-entrant corners**
CAUSE: U-shaped CLT floor with 37.5 % opening. MECHANISM: wings act as cantilevers off the north strip; stress concentrates at the inner corners (8, 8) and (32, 8). CONSEQUENCE: panel connection failure, separation of wing from cores, loss of lateral support to the wings. DETECTION: diaphragm forces in L3 model. MITIGATION: chords/collectors at the notch, CR-003 elements in each wing, stronger diaphragm (CLT–concrete composite) locally. RESIDUAL: medium until connections are tested or designed to a code.

**F3 — Gravity-column failure by deformation incompatibility**
CAUSE: timber columns and connections designed for gravity only. MECHANISM: they must follow core-plus-torsion drifts; brittle connection splitting or bearing loss. CONSEQUENCE: local collapse of floor bays. DETECTION: drift demands from L3–L5 vs connection rotation capacity. MITIGATION: drift-tolerant connections, positive bearing, test data. RESIDUAL: low–medium.

**F4 — Core shear failure before flexural yielding**
CAUSE: squat cores (H/L ≈ 1.7) attract high shear; elastic web stress 1.2 MPa at 0.8 g. MECHANISM: diagonal tension or sliding shear instead of ductile flexure. CONSEQUENCE: brittle loss of lateral resistance. DETECTION: capacity design check in L4–L5. MITIGATION: capacity-design shear, adequate web thickness and reinforcement, or base isolation. RESIDUAL: depends on hazard.

**F5 — Foundation rotation / uplift under cores**
CAUSE: large overturning moments concentrated at two corners. MECHANISM: rocking, uplift, differential settlement against the light frame. CONSEQUENCE: tilt, redistribution, cracking. DETECTION: geotechnical data + SSI model. MITIGATION: size foundations for overstrength moments, piles if needed. RESIDUAL: UNKNOWN until site investigation.

**F6 — Liquefaction or lateral spreading**
CAUSE: unknown ground. MECHANISM: loss of bearing during shaking. CONSEQUENCE: settlement, tilt, broken services. DETECTION: CPT/SPT + groundwater. MITIGATION: ground improvement or piles to competent strata. RESIDUAL: UNKNOWN.

**F7 — Fire in the hall**
CAUSE: exposed timber, high occupancy. MECHANISM: fire spread on timber surfaces, smoke filling a 9.7 m volume. CONSEQUENCE: life safety. DETECTION: fire strategy and egress modelling. MITIGATION: sprinklers, smoke extract, char-designed members, protected escape routes in cores. RESIDUAL: low–medium with code compliance.

**F8 — Progressive collapse of the hall roof**
CAUSE: diagrid relies on node continuity and few perimeter supports. MECHANISM: loss of one node or column → redistribution beyond capacity. CONSEQUENCE: roof collapse onto 400 people. DETECTION: notional removal analysis (L3/L7). MITIGATION: redundant ribs, robust nodes, tie forces. RESIDUAL: medium until analysed.

**F9 — Construction-stage instability**
CAUSE: wings without lateral elements before decks and collectors are complete; diagrid before closure. MECHANISM: sway or buckling under wind or construction loads. CONSEQUENCE: collapse during erection. DETECTION: temporary works design. MITIGATION: erection sequence, temporary bracing, shoring towers. RESIDUAL: low with competent temporary works.

**F10 — Pounding**: neighbours UNKNOWN; set separation once the site is known.

## 25. Independent Engineering Review

Reviewer stance: try to break it. Findings, ranked:

1. **Critical — lateral configuration (F1/F2).** Not acceptable as drawn. CR-003 required before further design.
2. **High — internal contradictions.** Program vs geometry (C-01); take-off vs geometry (C-02); section drawing places the hall roof at 9.7 m while the brief text says "~17 m" overall (true only for the pergola/canopy). Previously published carbon figures were too favourable on a per-area basis. Fixed in brief and page; poster carries no carbon numbers.
3. **High — all hazard, soil and code inputs UNKNOWN.** Conclusions about adequacy are impossible; only configuration conclusions are robust, because they hold for any hazard.
4. **Medium — models are Level 2.** Rigid diaphragm and fixed base are both unconservative for torsion and period respectively in this building; L3 model required.
5. **Medium — placeholder member sizes in IFC and take-off.** Glulam volume (301.8 m³) matches the earlier take-off only by coincidence of placeholders; do not quote it as a quantity.
6. **What was checked and passed:** cantilever modal model vs closed form (exact) and vs OpenSeesPy (< 0.1 %); effective masses sum to 1; demands scale linearly; symmetric layout gives zero eccentricity; IFC geometry within footprint, metres, analytic volumes, vertical beam depth. 28 automated tests.
7. **Not checked:** connections, diaphragm forces, fire design, vibration, wind on canopy, foundations, MEP, accessibility, egress numbers.

## 26. Calculations Still Required

Diaphragm forces, chords and collectors; accidental torsion; core flexure–shear capacity design; foundation overturning and uplift; column buckling (hall wall L/i ≈ 84); joist shear, bearing, LTB; floor vibration (assembly loading); fire resistance (char) of all exposed members; connection design (timber, steel nodes); diagrid stability (global buckling, snow and wind asymmetric cases); cantilever entry structure; wind pressures to code; non-structural anchorage forces; settlement and bearing (after investigation); egress capacity; energy, daylight and overheating; whole-life carbon A–D.

## 27. Tests / Simulations Still Required

Site investigation (§5) incl. Vs profile; L3 3-D OpenSeesPy model with flexible CLT diaphragm and SSI springs; response spectrum (once hazard known); core pushover; notional-removal analysis of the diagrid; connection tests or approved design values for CLT-to-core and diagrid nodes; fire modelling and egress simulation; daylight and annual energy simulation (to verify the façade claims, which are toy-model only); wind tunnel only if canopy form demands it.

## 28. Professional Approvals Required

Licensed architect and structural engineer of record in the jurisdiction; geotechnical engineer (investigation and report); fire engineer; MEP engineer; independent structural/peer review (likely required for an assembly building of this type); building control/permit authority; planning authority; inspections during construction by the authority and the engineer of record.

## 29. Recommended Next Engineering Step

1. **Client and architect decide CR-001 (area) and CR-003 (south lateral elements).** No further structural work is worth doing on the current layout.
2. **Provide the location.** It unlocks codes, hazard, wind, soils scope.
3. Then build the **L3 3-D model** (OpenSeesPy) with flexible diaphragm, run the PROTOCOL §4 verification, and update this report to v0.2.

---
*Change records: `reports/CR-001-area-reconciliation.md`, `reports/CR-002-takeoff-and-carbon.md`, `reports/CR-003-south-lateral-elements.md`. Template: `reports/change-record-template.md`.*

---

## Addendum A (2026-10-04): open-source stack examples

All results reproducible with `python -m pytest -q architecture/tests` (32 tests across the repo).

- **IDS** (`bim/requirements_ids.py`, IfcTester): the first run showed no element declared `LoadBearing` or `FireRating`. The model now carries both; `FireRating` is honestly `UNKNOWN - fire strategy pending`. 5/5 specifications pass; a bare column fails as it should. **SIMULATION (verified)**
- **Gmsh + CalculiX** (`models/calculix_beam/run_beam.py`): joist deflection, isotropic FE 17.07 mm vs Timoshenko 17.12 mm; orthotropic timber FE 18.63 mm vs 18.88 mm; equilibrium exact. Shear deformation adds ~12 % in timber → joist at L/424, still within L/350. Knife-edge supports add 3.5 mm of local crushing: a bearing-perpendicular-to-grain check is required at supports (§26). **SIMULATION (verified)**
- **pymoo** (`calculations/optimise_lateral.py`): minimum south lateral elements for e/B ≤ 0.05, edge amplification ≤ 1.10, Ω ≥ 1.20 (ASSUMED limits) are ~0.29 × core stiffness at the south edge; brute-force grid agrees. The optimum has zero margin on e/B, so **CR-003 keeps 0.5 × core at y = 28 m** (amp 1.008, e/B 0.011, Ω 1.38). **CALCULATION + JUDGMENT**
- **Gap confirmed:** no open-source tool performs code member checks; see skill `bld-member-design-checks`.
