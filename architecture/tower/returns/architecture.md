# Division 2 Architecture: 30-storey residential tower, concept options v1

Focus: Building Massing, Core Design, Vertical Transportation, Floor-Plan Generation, Space Planning, Daylighting.
Script: `architecture/tower/calcs/architecture_options.py` -> `architecture/tower/data/architecture.json`. Tests: `architecture/tests/test_tower_architecture.py`.

## INPUTS USED
- `architecture/tower/BRIEF.md`: residential apartments, 30 storeys above grade (FACT: brief). Site, jurisdiction, hazards, soil, budget, client: UNKNOWN.
- `architecture/tower/basis.json` v1 (ASSUMPTION, director's reference basis): 2 basements, 4.5 m ground floor, 3.1 m typical floor, 94.4 m to roof slab, 30 x 24 m plate, central 12 x 8 m core, about 8 apartments per floor, ground floor lobby/amenity/retail.
- `architecture/PROTOCOL.md` sections 1, 5, 9 and 12; `architecture/tools/pareto.py` input format.

## ASSUMPTIONS
- ASSUMPTION: ground floor is non-residential, so 29 residential floors (levels 2-30). The director must confirm.
- ASSUMPTION: all residential floors repeat the typical plate. There are no podium, setbacks or crown floors in the metrics.
- ASSUMPTION: ring corridor 1.5 m wide around the core in every option. The fire/code division must confirm the minimum width for the jurisdiction.
- ASSUMPTION: the reference footprint 30 x 24 m is the largest plate the (unknown) site allows. Option C breaks this and is flagged `fits_reference_footprint: false`.
- ASSUMPTION: occupancy is 1.5 persons per bedroom. Lifts: 1000 kg / 13-person cars, 10 passengers per up-peak trip, 2.5 m/s, 10 s lost per stop, 1.2 s per passenger transfer, 5-minute handling-capacity target 7 % of population. These are concept values. A lift consultant must confirm them, and the target must be checked against the jurisdiction's guidance (verify against current code/guide).
- JUDGMENT: proxy weights are as follows. Façade m² costs 1.5x a floor m² (cost proxy) and weighs 0.5x a floor m² (carbon proxy). Structure factors: RC flat slab 1.00/1.00, hybrid timber 1.15/0.65, PT slab 1.03/0.95, chamfered and balconied 1.08/1.05 (cost/carbon). The cost and carbon divisions must replace these.
- JUDGMENT: apartment mixes, the identity scores (1-5) and the dual-aspect counts for options without a drawn layout.

## METHOD
1. I generated five options, each optimised for one named objective (PROTOCOL section 12). All keep 30 storeys and 94.4 m to the roof slab.
2. The script computes these per-floor proxies (equations are in its docstring):
   - GFA = plate area
   - core = Lc x Wc
   - corridor = (Lc+2w)(Wc+2w) - core
   - NSA = GFA - core - corridor. This is an upper bound: envelope, party walls and columns are not deducted.
   - efficiency = NSA/GFA
   - façade/GFA = perimeter x 3.1 / GFA
   - max depth from façade to core = max((L-Lc)/2, (W-Wc)/2). This is the daylight proxy.
   - core ratio = core/GFA
   - slenderness = 94.4 / least plate dimension
   - cost and carbon proxy indices = (factor x GFA + k x façade area)/NSA, normalised to option A.
3. I drew the reference typical floor (option A) as 21 rectangles. The script self-checks the tiling, and the tests re-check it with independent code.
4. Lift check (concept estimate), conventional up-peak method. Probable stops S = N(1-(1-1/N)^P). RTT = 2 x rise/v + (S+1) t_stop + 2P t_pass, which conservatively assumes every trip reaches the top floor. HC5 per lift = 300P/RTT. Lifts required = max(2, ceil(0.07 x population / HC5)).
5. I ran a Pareto comparison with `tools/pareto.py` using `objective_senses`: cost_proxy_index min, carbon_proxy_index min, nsa_total_m2 max, max_depth_facade_to_core_m min, identity_score max.

## CALCULATIONS
All values are CALCULATION unless marked otherwise. Per typical floor, except totals (x29 residential floors; GFA above grade x30).

| Metric | A cheapest | B lowest carbon | C max NSA | D best daylight | E identity |
|---|---|---|---|---|---|
| Plate (m) | 30 x 24 rect | 30 x 24 rect | 34 x 26 rect | 27 x 21 rect | 30 x 24, 4.5 m chamfers |
| Core (m), position | 12 x 8 central | 12 x 8 central | 13 x 8 central | 12 x 8 central | 12 x 8 central |
| GFA/floor (m²) | 720.0 | 720.0 | 884.0 | 567.0 | 679.5 |
| Core / corridor (m²) | 96 / 69 | 96 / 69 | 104 / 72 | 96 / 69 | 96 / 69 |
| NSA/floor (m²) | 555.0 | 555.0 | 708.0 | 402.0 | 514.5 |
| Efficiency NSA/GFA | 0.771 | 0.771 | 0.801 | 0.709 | 0.757 |
| Façade m² per m² GFA | 0.465 | 0.465 | 0.421 | 0.525 | 0.445 |
| Max depth façade-to-core (m) | 9.0 | 9.0 | 10.5 | 7.5 | 9.0 |
| Max apartment depth (m) | 7.5 | 7.5 | 9.0 | 6.0 | 7.5 |
| Core area ratio | 0.133 | 0.133 | 0.118 | 0.169 | 0.141 |
| Apartments/floor (mix, JUDGMENT) | 8 (2x1B, 4x2B, 2x3B) | 8 (same) | 10 (2x1B, 6x2B, 2x3B) | 6 (2x1B, 4x2B) | 8 (2x1B, 4x2B, 2x3B) |
| Apartments total | 232 | 232 | 290 | 174 | 232 |
| NSA total (m²) | 16,095 | 16,095 | 20,532 | 11,658 | 14,920.5 |
| Dual-aspect share | 0.50 | 0.50 | 0.40 | 0.667 | 0.50 |
| Slenderness H/B | 3.93 | 3.93 | 3.63 | 4.50 | 3.93 |
| Cost proxy index | 1.000 | 1.088 | 0.942 | 1.145 | 1.048 |
| Carbon proxy index | 1.000 | 0.716 | 0.906 | 1.114 | 1.051 |
| Identity score (JUDGMENT) | 1 | 3 | 1 | 2 | 5 |
| Lifts required / provided | 4 / 4 | 4 / 4 | 4 / 4 | 2 / 3 | 4 / 4 |
| Stairs | 2 | 2 | 2 | 2 | 2 |

Option E perimeter = 2(30-9) + 2(24-9) + 4 x 4.5 x sqrt(2) = 97.46 m. Area = 720 - 2 x 4.5² = 679.5 m².

Lift check, reference option A (CALCULATION, concept estimate):
- Population = (2x1.5 + 4x3.0 + 2x4.5) persons/floor x 29 floors = 24 x 29 = 696 persons.
- Demand = 0.07 x 696 = 48.7 persons per 5 minutes.
- Rise = 4.5 + 28 x 3.1 = 91.3 m. N = 29, P = 10, so S = 29(1 - (28/29)^10) = 8.58 stops.
- RTT = 2 x 91.3/2.5 + 9.58 x 10 + 2 x 10 x 1.2 = 73.0 + 95.8 + 24.0 = 192.9 s.
- HC5 per lift = 3000/192.9 = 15.55 persons. Lifts needed = 48.7/15.55 = 3.13, so **4 lifts**.
- With 4 lifts: interval 48.2 s, HC5 = 8.9 % of population.
- C: 30 persons/floor, 870 total, 4 required, HC5 7.15 %, interval 48.2 s.
- D: 15 persons/floor, 435 total, 2 required, 3 provided for redundancy (JUDGMENT), interval 64.3 s.

## RESULTS
**Reference typical floor (option A).** x runs east 0..30 m and y runs north 0..24 m. 21 rectangles tile 720 m² exactly. This is CALCULATION, checked by the script and the tests.

| Name | Type | x0 | y0 | x1 | y1 | Area m² |
|---|---|---|---|---|---|---|
| A01 SW corner | 2B | 0 | 0 | 7.5 | 9 | 67.5 |
| A02 W | 1B | 0 | 9 | 7.5 | 15 | 45.0 |
| A03 NW corner | 2B | 0 | 15 | 7.5 | 24 | 67.5 |
| A04 N | 3B | 7.5 | 17.5 | 22.5 | 24 | 97.5 |
| A05 NE corner | 2B | 22.5 | 15 | 30 | 24 | 67.5 |
| A06 E | 1B | 22.5 | 9 | 30 | 15 | 45.0 |
| A07 SE corner | 2B | 22.5 | 0 | 30 | 9 | 67.5 |
| A08 S | 3B | 7.5 | 0 | 22.5 | 6.5 | 97.5 |
| Corridor S / N | corridor | 7.5 | 6.5 / 16 | 22.5 | 8 / 17.5 | 22.5 each |
| Corridor W / E | corridor | 7.5 / 21 | 8 | 9 / 22.5 | 16 | 12.0 each |
| Stair 1 | stair | 9 | 8 | 14.5 | 10.8 | 15.4 |
| Lift 1, Lift 2 (firefighting candidate) | lift | 14.5 / 17 | 8 | 17 / 19.5 | 10.8 | 7.0 each |
| Riser 1 | riser | 19.5 | 8 | 21 | 10.8 | 4.2 |
| Lift lobby | lobby | 9 | 10.8 | 21 | 13.2 | 28.8 |
| Lift 3, Lift 4 | lift | 9 / 11.5 | 13.2 | 11.5 / 14 | 16 | 7.0 each |
| Riser 2 | riser | 14 | 13.2 | 15.5 | 16 | 4.2 |
| Stair 2 | stair | 15.5 | 13.2 | 21 | 16 | 15.4 |

Floor totals:
- Apartments: 555 m². Core: 96 m². Corridor: 69 m².
- Every apartment touches the ring corridor. The lobby opens to the corridor at both ends (x = 9 and x = 21).
- Stairs sit on opposite corners of the core. Stair 1 opens from the south/west corridor and Stair 2 from the north/east corridor.

**Shared structural grid (JUDGMENT, for `bld-structural-engineer` to verify):**
- x = 0 / 7.5 / 15 / 22.5 / 30. y = 0 / 8 / 16 / 24. Maximum bay 7.5 x 8 m.
- Interior columns sit at the outer corners of the corridor ring. Core walls sit on x = 9/21 and y = 8/16.

**Concept (JUDGMENT):**
- The idea is a "quiet lantern": a calm, repetitive and efficient plate. Every apartment is no more than 7.5 m deep, so daylight reaches the back wall. Corner units are dual aspect.
- Identity budget goes into the ground floor (4.5 m) and the crown, not into every floor.
- Option E spends that budget on the whole shaft instead. Its chamfered corners shorten the façade (0.445 vs 0.465 m² per m² GFA) at a cost of 40.5 m² of plate per floor.

**Pareto:**
- With all five options, every option is non-dominated.
- Best per objective: cost C, carbon B, NSA C, daylight D, identity E.
- If the 30 x 24 m footprint is a hard limit, remove C. A then becomes the lowest-cost option, and A, B, D and E remain non-dominated.
- Finding (CALCULATION on JUDGMENT weights): the cost proxy per m² of NSA falls as the plate grows, because the core is diluted. The larger plate C is about 6 % cheaper per m² of NSA than A, but its plan is 1.5 m deeper. So "cheapest" depends on whether the footprint is fixed.

**Recommendation:** keep option A as the reference and carry B and D forward as variants (JUDGMENT; see RECOMMENDATIONS).

## CODE / STANDARD
- Jurisdiction is UNKNOWN, so no code clause is cited or applied (PROTOCOL sections 2 and 5).
- Corridor width, stair width, stair separation (remoteness), firefighting lift and lobby protection, accessible lift car size, apartment minimum areas and daylight criteria must all be verified against the current code once the jurisdiction is known. This is for `bld-code-compliance`.
- The lift method is a conventional up-peak round-trip estimate of the kind found in lift-traffic design guides (for example CIBSE Guide D; verify against the current edition). It is not a traffic simulation.

## UNCERTAINTIES
- Site size, orientation, setbacks and height limits are UNKNOWN. The compass labels (N/S/E/W) are plan labels only, so daylight and solar performance cannot yet be judged. Depth to core is a geometric proxy, not a SIMULATION.
- NSA is an upper-bound proxy. Real NSA after deducting envelope, party walls and columns is likely 5-10 % lower (JUDGMENT).
- The cost and carbon indices rest on JUDGMENT weights. Their ranking can flip under the real rates from the cost and carbon divisions.
- The lift count depends on occupancy (1.5 persons per bedroom) and the 7 % target. At 5 % the reference needs 3 lifts; at 8 % it still needs 4.
- Shaft sizes (2.5 x 2.8 m) and the 2.4 m lobby depth are tight for 1000 kg cars. They need lift-manufacturer data.
- Hybrid timber (B) at 94 m depends on the jurisdiction and fire strategy (UNKNOWN).
- D's slenderness of 4.5 may be governed by wind or drift, which are outside this division.

## FAILED CHECKS
- NOT RUN: this agent session had no shell tool. The script, the pytest run and the `validate_return.py` run were **not executed** by this division. `data/architecture.json` was written by hand from the script's formulas, and `test_stored_json_matches_fresh_script_run` will catch any discrepancy. The caller must run:
  - `python architecture/tower/calcs/architecture_options.py`
  - `python -m pytest -q architecture/tests/test_tower_architecture.py`
  - `python architecture/tools/validate_return.py architecture/tower/returns/architecture.md`
- C exceeds the reference footprint (34 x 26 m against 30 x 24 m). It is infeasible unless the site allows the larger plate.
- Stair remoteness may fail. The stair centres are 8.3 m apart, and the doors are about 13.1 m apart, against a 30 x 24 m plate diagonal of 38.4 m. This passes only if the jurisdiction's rule is no stricter than one third of the diagonal (12.8 m). PROFESSIONAL REVIEW REQUIRED by fire/code.
- Single-aspect units: 4 of 8 reference apartments (A02, A04, A06, A08) are single aspect. A02 faces west and A08 faces south; their real orientation is unknown, so there is an overheating or poor-daylight risk.

## RECOMMENDATIONS
- JUDGMENT: carry A forward as the reference for the structure, MEP, fire and 3D model waves.
- JUDGMENT: carry B (structure-led carbon variant) and D (daylight variant) as the alternates. Hold E as a façade/crown study, and hold C until the site area is known.
- `bld-structural-engineer`: verify 7.5 x 8 m flat-slab spans, the 12 x 8 m core stiffness for H/B 3.9 (4.5 for D), and the column positions at the corridor corners.
- `bld-mep-engineer`: confirm whether two risers of about 4.2 m² each are enough, and where rooftop and basement plant and riser offsets go.
- `bld-code-compliance`: corridor and stair widths, stair separation, firefighting lift and lobby, accessible routes.
- Lift consultant: run a traffic simulation for 4 x 1000 kg at 2.5 m/s.
- Decision manager: rerun `tools/pareto.py` once the footprint constraint is resolved and the real cost and carbon rates replace the proxies.

## REQUIRED HUMAN REVIEW
- A licensed architect must review the plan, unit sizes and accessibility once the jurisdiction is known.
- A fire engineer or building-control authority must review egress, stair remoteness and the firefighting lift.
- A lift consultant must review the lift count, car size and shaft dimensions.
- The client must confirm the apartment mix, market and the footprint limit.
- A human must run the script, tests and validator (see FAILED CHECKS) before any downstream use of `architecture.json`.
- This is concept feasibility only, not for construction (PROTOCOL section 8).
