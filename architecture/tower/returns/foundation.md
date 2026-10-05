## INPUTS USED
- FACT (project files): architecture/PROTOCOL.md s1, s5, s9; tower/BRIEF.md; tower/basis.json (30 x 24 m plate, 12 x 8 m core, 2 basements at 3.3 m, 30 storeys); tower/data/structure.json (G = 254.19 MN, Q = 44.46 MN at ground slab; core G 127.48 MN, Q 22.10 MN; 14 perimeter columns, largest E_0_8 service 13.33 MN; EC-form N_Ed core 205.2 MN); tower/returns/geotechnical.md and data/geotechnical.json (investigation scope).
- FACT: no geotechnical data, no site, no jurisdiction, no groundwater level (basis.json). Every soil capacity, stiffness, groundwater level and hazard is UNKNOWN.
- Wind and earthquake overturning moments: PENDING (placeholders in data/foundation.json).
- Script: architecture/tower/calcs/foundation_tower.py -> architecture/tower/data/foundation.json; tests architecture/tests/test_tower_foundation.py (7 pass).

## ASSUMPTIONS
- ASSUMPTION (structure/architecture to confirm): raft thickness 2.0 m (not designed); founding depth D = 2 x 3.3 + 2.0 = 8.6 m below ground slab level; basement floors 10 kPa per level (slab, column share, finishes); perimeter basement wall 0.4 m thick; concrete 25 kN/m3.
- ASSUMPTION: raft sizes 30 x 24 m (tower footprint, 720 m2) and 36 x 30 m (enlarged, 1080 m2, 3 m projection each side; site boundary UNKNOWN).
- ASSUMPTION (PARAMETER, not fact): soil unit weight 16, 18, 20 kN/m3 for excavation unloading; water ignored in the net-pressure figure.
- PARAMETRIC (not capacities): working load per pile 3, 5, 8, 12 MN; raft load share in a piled raft 0, 25, 50 %.
- ASSUMPTION: factored load uses EC form 1.35 G + 1.5 Q (jurisdiction UNKNOWN).

## METHOD
- L1 conceptual plus L2 hand calculation. Pressure q = N/A. Net pressure after unloading = q_gross - gamma x D (parameter). Pile count n = ceil(P / Pw). Edge pressure under overturning q = N/A +/- M/Z, Z = B L^2/6; no tension if e = M/N <= L/6. Flotation U = gamma_w x h x A, h a parameter.
- Comparison matrix is JUDGMENT unless a number is stated; the pareto tool was not run because no quantitative cost, carbon or settlement data exists to feed it.

## CALCULATIONS
All CALCULATION tags below come from foundation_tower.py (tested). Units kN, kPa, MN.
1. Superstructure service G + Q = 298.65 MN; factored 1.35G + 1.5Q = 409.84 MN.
2. Basement weight (raft + 2 floors + walls): 57.5 MN on the 30 x 24 raft; 84.3 MN on the 36 x 30 raft (ASSUMPTION-based).
3. Total service at founding: 356.2 MN (tower raft), 383.0 MN (enlarged raft).
4. Core vs perimeter: core service 149.6 MN = 50.1 % of the total on 13 % of the plan; 1558 kPa on the 96 m2 core footprint vs 239 kPa on the remaining 624 m2 (ratio 6.5).
5. Overturning sensitivity: 100 MNm adds/removes 27.8 kPa (30 x 24 raft, bending along 30 m) or 15.4 kPa (36 x 30 raft). M is PENDING.
6. Flotation, stage 0 (basement only, no tower), 30 x 24 raft: weight 57.5 MN; uplift for water head 2, 4, 6, 8.6 m above base is 14.1, 28.3, 42.4, 60.7 MN; weight/uplift ratio is 4.07, 2.04, 1.36 and 0.95, so stage 0 floats at the full 8.6 m head (code partial factors not applied).
7. Parametric pile count, load = total service at founding (n piles):

| Pw (MN per pile, PARAMETRIC) | 30 x 24 raft (356.2 MN) | 36 x 30 raft (383.0 MN) | core only (149.6 MN) | piled raft, raft carries 25 % | raft carries 50 % |
|---|---|---|---|---|---|
| 3 | 119 | 128 | 50 | 90 | 60 |
| 5 | 72 | 77 | 30 | 54 | 36 |
| 8 | 45 | 48 | 19 | 34 | 23 |
| 12 | 30 | 32 | 13 | 23 | 15 |

Group efficiency, negative skin friction, tension from overturning and seismic load are not included.

## RESULTS
Pressures (CALCULATION; basement weight is ASSUMPTION):
| Raft | superstructure service | total gross | factored (superstructure) | net after unloading, gamma 16 / 18 / 20 |
|---|---|---|---|---|
| 30 x 24 m | 415 kPa | 495 kPa | 569 kPa | 357 / 340 / 323 kPa |
| 36 x 30 m | 277 kPa | 355 kPa | 380 kPa | 217 / 200 / 183 kPa |
Net pressure of 180 to 360 kPa is a high demand for a raft (JUDGMENT; the allowable value is UNKNOWN until investigation).

Alternatives (credibility is JUDGMENT; capacities UNKNOWN):
- Isolated footings: not credible. The core takes 149.6 MN (1558 kPa over its footprint), so a footing would cover nearly the whole core and columns up to 13.3 MN need footings that merge with neighbours. Possible only on rock of very high capacity, and still a poor fit for the core. Rule-in data: rock at founding level with UCS/pressuremeter proof.
- Strip footings: not credible. Same reason; the average pressure of 415 kPa across the whole plan leaves no clear strip spacing. Rule-in data as above.
- Combined footings: not credible for the core; marginal for columns on shallow rock only. A combined footing under the core is, in effect, a raft.
- Raft (30 x 24 or enlarged): credible only if investigation shows stiff soil or weathered rock to 1.5 to 2 x B (36 to 48 m) below founding level, small hole-to-hole variation and no liquefaction. Risks: total settlement, dishing (core 6.5 x the column pressure), tilt, and a very thick raft under the core (punching and shear unknown). Enlarging to 36 x 30 m lowers net pressure by about 140 kPa and the overturning edge-pressure sensitivity from 27.8 to 15.4 kPa per 100 MNm, but needs site area (UNKNOWN).
- Piles (bored, cast in place): credible and the usual route when shallow ground is weak or a bearing layer or rock is reachable. Table above gives the count per working capacity. Differential settlement: pile spacing can be concentrated under the core, at roughly half the load in 13 % of the plan. Uplift: piles give tension capacity for flotation (to be derived). Rule-out data: no reachable competent layer, obstructions, artesian water, karst.
- Barrettes (rectangular diaphragm-wall panels): credible where very high individual capacity is needed (the core load of 149.6 MN would need few elements) and the bearing layer is deep. Treat each barrette as a pile with a high Pw (the 12 MN column of the table is a lower bound on the number needed). Rule-in data: deep competent stratum, wall-grade spoil handling, trench stability. Rule-out: boulders, cavities.
- Caissons (large-diameter shafts, hand or machine dug): credible under the core and the heavy columns where rock or dense soil is within reach; the 8 and 12 MN rows are indicative. Rule-out: high water table without sealing, loose granular soil, contamination.
- Pile-raft: credible and potentially the most economic if the raft alone meets bearing but not settlement or differential settlement; piles are placed mainly under the core. Table shows 15 to 90 piles for the raft carrying 25 to 50 %. Needs soil-structure interaction analysis and a pile load test. Rule-out: liquefiable or deep compressible layers, uncertain contact under the raft.

Cross-cutting checks:
- Differential settlement core vs columns: core pressure is 6.5 x the column-zone pressure and the stress bulbs overlap, so the core settles more; the structural division must set the tilt and differential limits (UNKNOWN). Settlement value: UNKNOWN.
- Uplift/flotation: water head UNKNOWN. Stage 0 (basement without tower) is the critical case during construction; the ratio in the JSON falls below 1 for a head near the full depth. Remedies: tension piles, anchors, ballast, staged dewatering, drainage.
- Lateral/overturning: M_wind and M_seismic are PENDING. Edge pressures from q = N/A +/- M/Z. Under the 30 x 24 raft N/A = 495 kPa, so uplift at the edge only if M/N > 5 m, i.e. M > 1780 MNm at N = 356 MN (CALCULATION from L/6 = 5 m). Seismic base shear transfer into the ground via basement walls and raft: UNKNOWN.

Comparison matrix (JUDGMENT; H = high, M = medium, L = low risk or cost; blanks are not applicable):
| Option | Settlement risk | Bearing | Uplift | Lateral/seismic | Cost | Constructability | Embodied carbon |
|---|---|---|---|---|---|---|---|
| Isolated | rule out | rule out | poor | poor | n/a | n/a | n/a |
| Strip | rule out | rule out | poor | poor | n/a | n/a | n/a |
| Combined | rule out | rule out | poor | poor | n/a | n/a | n/a |
| Raft on soil/rock | M to H | ground-dependent | needs ballast/drain | good if ground stiff | M | easy | H (thick raft) |
| Piles + pile cap | L to M | via bearing layer | tension piles | good, rake/flexure by design | M to H | M | H |
| Barrettes | L | high per element | good | good | H | M (specialist) | H |
| Caissons | L | high per element | M | good | H | M to H (water) | H |
| Pile-raft | L to M | shared | needs piles at edge | good | M | M | M |

Recommendation (conditional): carry raft, pile-raft and bored piles/barrettes in parallel. If the investigation finds uniform stiff ground or rock to depth, choose the raft (enlarged if site allows); if the raft fits bearing but exceeds settlement or tilt limits, choose pile-raft with piles under the core; if weak or liquefiable ground overlies a competent layer, choose piles or barrettes under the core and columns. Isolated, strip and combined footings are excluded at this load level, except on shallow rock proven by the investigation.

## CODE / STANDARD
- Jurisdiction UNKNOWN; no clause retrieved or quoted. Verify against current editions: EN 1997-1 and national annex, or the local equivalent (for example IBC/ASCE 7 foundations chapters, ACI 318); pile testing standards (for example ASTM D1143, D1194, D3689, D4945 or EN ISO 22477-1); local seismic code for soil-structure interaction and liquefaction.
- Load-factor form EC (1.35/1.5) is an ASSUMPTION for presentation only.
- Requirement class: BUILDING CODE / REFERENCED STANDARD, not yet determinable.

## UNCERTAINTIES
- All soil, groundwater, rock level, liquefaction and seismic hazard values: UNKNOWN.
- Raft thickness, basement weights, wall thickness and excavation depth are ASSUMPTIONS and move the gross pressure by perhaps 10 to 20 % (JUDGMENT).
- structure.json base fixity at the ground slab ignores the basement box and soil flexibility; moment and base shear at founding level are PENDING.
- Pile counts exclude group effects, negative skin friction, tension and seismic loads; pile load tests would be needed to fix any Pw.
- Enlarged raft size depends on a site boundary that is UNKNOWN.

## FAILED CHECKS
None run to a pass or fail verdict. Bearing, settlement, differential settlement, uplift, overturning and seismic checks: INSUFFICIENT INFORMATION (no soil data, no groundwater level, no overturning moment). The only exclusions made (isolated, strip, combined footings) are JUDGMENT on geometry and load level, not code checks.

## RECOMMENDATIONS
- Execute the investigation scope in tower/returns/geotechnical.md (deep boreholes to 45 to 60 m, CPTu, pressuremeter, piezometers over a hydrological year) before choosing a foundation.
- Ask the wind and earthquake divisions for N, M and base shear at founding level so the edge-pressure formula can be evaluated and the tension piles sized.
- Ask the structure division to re-run with basement box and soil springs and to set differential-settlement and tilt limits.
- Obtain the design groundwater level and check stage-0 flotation before the tower load arrives.
- Plan an instrumented pile load test and a soil-structure interaction analysis (pile-raft option); re-run foundation_tower.py with real Pw when available and use tools/pareto.py with quantity data for cost and carbon.

## REQUIRED HUMAN REVIEW
- Licensed geotechnical engineer for ground model, all capacities, settlement and uplift, and for the investigation.
- Licensed structural engineer for raft thickness, punching under the core, pile layout, load path, and settlement and tilt limits.
- Temporary-works engineer and independent checker for the excavation, retention and dewatering.
- This is a concept-level aid and not certified design. It contains no capacities, construction-ready dimensions or approvals.
