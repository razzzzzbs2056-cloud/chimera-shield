# The Chimera Pavilion — Design Brief (concept stage)

A community and cultural pavilion: a hybrid ("chimera") of ancient mass and living lightness.
Status: **concept / feasibility**. Numbers marked *(tool)* come from `tools/quickcheck.py`; everything else is an assumption to be verified.

> **Not for construction.** Requires a site-specific geotechnical investigation, local code review, and design by licensed architects and engineers.

## 1. Concept

**Idea.** Three beings in one body: a **stone-like heart** (two reinforced-concrete cores and a brick-and-rammed-earth plinth, heavy, cool, fire-safe, anchoring the building to the ground), a **timber skeleton** (glulam grid and CLT floors, warm, tactile, carbon-storing), and a **bright skin** (a copper-and-glass veil whose pattern thins where people look out and thickens where the sun is harshest).

**Reference logic.** The roof lattice borrows from the way leaves, dragonfly wings and diatom shells reach large spans with thin ribs: a diagrid of curved glulam ribs meeting at cast-steel nodes, so the ceiling reads as a canopy of branches. The façade pattern is a gradient of perforation derived from the solar exposure of each panel (a form that is also a shading calculation).

**Experience sequence.** Arrive under a deep cantilever → compressed, dim, earthen threshold → release into a sunlit double-height hall under the lattice → climb a daylit timber stair that frames the city → the roof garden at the top, open sky.

**Proportion system.** 8.0 m structural module; hall = 3 × 8 by 3 × 8 m cells (24 × 24 m); façade rhythm 1.0 m (fins at 1 m centres, panel 2 × 4 m); floor heights follow a 1 : 0.76 ratio between ground (5.5 m) and upper (4.2 m) floors.

## 2. Site (assumed — replace with the real site)

Temperate climate, mildly seismic, medium-dense sand over stiff clay, level 2 ha urban plot, long axis east–west. Climate row: `data/climate_zones.csv` (Temperate). Ground values: `data/soils.csv`.

## 3. Program (`data/space_program.csv`)

About 4,190 m² GFA: main hall 600 (400 people), foyer/cafe 420, galleries 480, maker studios 360, learning 280, library 260, offices 160, back of house 230, toilets 168, plant 230 (5.5 %), circulation 1,000 (24 %), plus a 420 m² roof terrace.

## 4. Geometry

- Footprint: 6 × 4 bays of 8 m = **48 × 32 m (1,536 m²)**; 3 floors + roof terrace, ~17 m high.
- The hall occupies the ground-floor south-central 3 × 3 bays and rises through the first floor (void ≈ 576 m²), which accounts for the gap between 3 × 1,536 and the 4,190 m² program.

```
PLAN L0 (not to scale)                    SECTION A-A (north → south)
N ↑  8 m grid, 6 x 4 bays
┌───┬───┬───┬───┬───┬───┐                       lattice canopy ╱╲╱╲╱╲╱╲        ← roof 17 m
│ C │ W │ W │ W │ M │ C │  C = core                      ┌────────────┐ roof terrace
├───┼───┴───┴───┤   │   │  W = workshops           ───────┤ L2 learning │ 4.2 m
│ F │   HALL    │ B │ T │  F = foyer/cafe          ───────┤ L1 gallery  │ 4.2 m  hall void
│   │  24x24 m  │   │   │  M = maker, B = back     ┌──────┘  HALL      └───┐
│ ▒ │           │   │ C │  T = toilets/plant       │ plinth: brick+earth  │ 5.5 m
└───┴───────────┴───┴───┘  ▒ = entry cantilever    └──── raft on piles? ──┘ (see §10)
```

## 5. Structure (`bld-structural-engineer`)

**System.** Hybrid: RC cores resist lateral loads and house stairs, lifts and shafts; a glulam post-and-beam grid at 8 × 8 m carries CLT floors; the hall roof is a 24 × 24 m glulam diagrid on steel nodes. Alternatives considered: all-steel (lighter connections, higher carbon, needs fireproofing), all-concrete (cheapest to build, highest carbon, heaviest foundations).

**Load path.** CLT deck → secondary glulam beams at 4 m → primary glulam beams (8 m) → glulam columns → RC raft/pile cap → ground. Lateral: floor diaphragms → RC cores → foundation.

**Design loads** (`data/live_loads.csv`, Eurocode style, EN 1990 6.10): dead 1.7 kPa (150 mm CLT 0.7 + screed/finishes/services 1.0); live 4.0 kPa (assembly); factored 1.35G + 1.5Q.

**Primary beam pre-size** *(tool)*: span 8 m, 4 m tributary → w_ULS 33.2 kN/m, M = 265 kNm; f_m,d = 0.8·24/1.25 = 15.4 MPa; required depth 657 mm → **GL24h 240 × 680 mm**; SLS deflection 16.8 mm = **L/476** (limit L/300 used by the tool; project limit L/350 after finishes per `data/deflection_limits.csv`).

**Fire (indicative hand check).** 60 min, char 0.65 mm/min → 39 mm per exposed face; residual 162 × 641 mm on three-sided exposure; reduced fire load ≈ 0.49 of ULS; capacity with k_fi·f_m,k ≈ 306 kNm vs ≈ 130 kNm demand → passes with margin at this level of approximation. Detailed char and connection fire design remain open.

**Not yet checked:** shear and bearing, lateral-torsional stability, creep, floor vibration (people-induced; assembly floors are vibration-critical, f₁ > 8 Hz), connections, diaphragm design, seismic load, column slenderness, canopy buckling and snow drift.

## 6. Envelope and materials (`data/materials.csv`, `bld-materials-scientist`)

Wall: 450 mm rammed-earth/brick plinth to 1.2 m; above it a timber frame with wood-fibre insulation, U ≈ 0.15–0.20 W/m²K (Temperate row); copper-and-glass veil with perforation gradient; glazing 30–40 % of wall, U ≈ 0.8–1.2 W/m²K; roof U ≈ 0.10–0.15; ETFE or glass rooflights over the hall for ~5 % daylight openings. Copper patinates to green within decades; it is fully recyclable. Embodied-carbon numbers are ranges because EPDs vary by manufacturer.

## 7. Services (`data/mep_benchmarks.csv`, `bld-mep-engineer`)

Passive first: stack-ventilated hall (lattice cavity as exhaust), exposed CLT and earth plinth as thermal mass, night purge. Active: air-to-water heat pump with low-temperature radiant slabs, demand-controlled ventilation with heat recovery (8–15 L/s per person), PV on the south roof, rainwater harvesting for toilets and irrigation, sprinklers and smoke extract in the hall. Space: plant ≈ 5.5 % GFA, risers ≈ 2 %, floor-to-floor 4.2 m (0.7 structure + 0.5 services + 3.0 clear). Two lifts + 3 stairs; accessible step-free route to every level.

## 8. Sustainability and scientific value

**Embodied carbon (A1–A3, structure + glazing + copper only), corrected by CR-002:** v0.2 IFC take-off gives 504–1,106 tCO₂e = **146–320 kgCO₂e/m²** on the 3,456 m² floor area the geometry actually provides (the earlier 128–282 figure used an overstated CLT area). Insulation, MEP, finishes, A4, A5, B and C are **not** included, so this is a floor, not a result. **Biogenic carbon in timber: ~528 tCO₂e**, reported separately. The program (4,188 m²) does not fit the geometry: see CR-001 and `reports/engineering-report-v0.1.md`.

**Research questions** (what the building can teach):
1. How much whole-life carbon does a timber-concrete hybrid save against an all-concrete and an all-steel baseline of identical program, with ranges from EPD variance? (method: EN 15978 modules A–D, Monte Carlo over `materials.csv` ranges)
2. Does the solar-driven perforation gradient reduce cooling load without breaking daylight targets? (method: annual daylight and energy simulation, compare against uniform façade)
3. Do exposed-timber and earth thermal masses reduce peak indoor temperature under future climate files? (method: dynamic thermal simulation, and monitored data after occupation)
4. Are people-induced vibrations acceptable on 8 m timber floors at 4 kPa assembly loading? (method: modal analysis plus on-site measurement)
Instrumentation plan: embedded moisture sensors in timber, temperature, CO₂, energy sub-metering, open data for post-occupancy evaluation.

## 9. Code, safety and accessibility (`bld-code-compliance`)

Assembly occupancy with ~400 in the hall: egress needs at least 2 exits, with exit width and travel distance per the local code (verify). Exposed timber must meet the structural-fire-resistance required for the building height and use; encapsulation may be required by some jurisdictions. Step-free access, accessible toilets on every floor, tactile and visual wayfinding. Codes index: `data/codes_standards.csv`.

## 10. Construction (`bld-construction-manager`)

Sequence: enabling → piling/raft → RC cores slip-form (they provide stability early) → glulam frame erected with temporary bracing → CLT decks laid and **weather-protected immediately** (moisture is the main timber risk) → roof lattice assembled on the ground in sections and craned into place → envelope → services → fit-out → commissioning. Prefabrication of CLT and glulam to ±2 mm tolerance. Foundations are shown as a raft on piles pending soil data: bearing values in `data/soils.csv` are presumptive only.

## 11. Cost and programme (`bld-cost-planner`)

Cost shares per element: `data/cost_model.csv`. Absolute rates are intentionally blank (enter local prices); concept-stage accuracy ±30 %, contingency 10–20 %. Programme: about 30–40 months from brief to handover (`data/programme_phases.csv`). Biggest cost risks: bespoke lattice nodes, ground conditions, glazing/copper spread.

## 12. Drawings to produce (`bld-concept-designer`)

Site plan; plans L0–L3; two sections; four elevations; axonometric of structure; lattice node detail; façade pattern diagram; daylight study; render views: dawn arrival, hall at noon, roof garden at dusk.

## 13. Assumptions and open items

Site, soils, climate and jurisdiction are assumed. Loads follow Eurocode conventions but no national annex was applied. Material numbers are typical, not manufacturer data. Open: seismic and wind load, geotechnical report, fire strategy, cost rates, vibration, acoustic design of the hall, planning approval.

## 14. Decision log

| # | Decision | Reason | Revisit if |
|---|---|---|---|
| D1 | Timber–concrete hybrid | Lower embodied carbon than all-concrete; cores give stability and fire robustness | Local timber supply or code limits it |
| D2 | 8 m grid | Efficient glulam spans, fits hall 3 × 3 bays | Program changes |
| D3 | Lattice roof, not trusses | Lighter and expressive; shares the concept | Cost or buckling checks fail |
| D4 | Presumptive foundations only | No ground data | Site investigation arrives |
| D5 | CR-002 implemented: take-off and carbon corrected from IFC | Hand take-off overstated CLT | Geometry changes |
| D6 | CR-001 and CR-003 proposed: area gap; south lateral elements to fix torsion | Engineering report v0.1 | Client decision |
