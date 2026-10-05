# Division 25 Independent Verification: tower structure (Agent B)

## INPUTS USED
- FACT: `architecture/tower/verification/structure_inputs_for_B.json`, which holds the plate (30 x 24 m), the 14 perimeter columns by zone, the core box [9,8,21,16] (12 x 8 m) with walls 0.6/0.5/0.4 m, the 0.25 m slab, all unit loads and factors, levels z = 4.5 to 99.4 m, E = 35 000 MPa, cracked factor 0.5 and Poisson's ratio 0.2.
- FACT: `architecture/PROTOCOL.md` (sections 1, 9 and 10), `architecture/tower/BRIEF.md` and `architecture/tower/basis.json`.
- I did not read any of A's files (data/structure.json, returns/structure.md, calcs/structure_gravity.py, the test file) before writing B_structure.json. I saw A_structure.json only through the comparator output, after my numbers were written.

## ASSUMPTIONS
- ASSUMPTION (B): level 30 (z = 94.4 m) is the roof slab, carrying roof SDL, 2.0 kPa plant and 1.5 kPa roof live over the full slab area. Level 31 (z = 99.4 m) is a plant roof over the core footprint only (96 m2), carrying a slab plus 5.0 kPa core plant and roof live.
- ASSUMPTION (B): perimeter columns stop at the roof slab (94.4 m). Only the core continues through the 5 m plant storey.
- ASSUMPTION (B): the ground storey is counted fully in W, G and Q. W is all dead load above the ground slab (every storey's vertical elements, including the whole ground storey) plus 0.3 x all live load, including roof live.
- ASSUMPTION (B): the core floor slab is 0.6 x 96 m2 = 57.6 m2. The corridor band is a 1.5 m ring around the core (69 m2). The residential area is 555 m2. SDL + partitions are applied over the slab area of 681.6 m2. Facade load of 6 kN/m is applied over the 108 m perimeter at levels 1 to 30.
- ASSUMPTION (B): the two 0.25 m internal core walls span the short (Y) direction. They count as weight only and are excluded from core stiffness, because their positions are not given.
- ASSUMPTION (B): the shear area is 2 x t x (outer depth parallel to sway). The cracked factor of 0.5 is applied to both E and G.

## METHOD
- The inputs were shared with Agent A through structure_inputs_for_B.json. Input errors common to both agents are therefore NOT caught by this check.
- Weights: whole-floor zoned areas x unit loads, plus self-weight of every column and core-wall segment computed storey by storey (not a per-column takedown).
- Core I: my own pixel integration of the box section on a 0.025 m grid, cross-checked against the closed-form box formula. Axis convention: I_x is about the global x axis and resists sway in Y; I_y resists sway in X.
- Periods: a Timoshenko (flexure + shear) cantilever stiffness matrix of 31 storey elements with zoned wall thickness, fixed at z = 0. Rotations are condensed out. Masses are lumped (level loads plus half of each adjacent storey) and solved as a numpy eigenproblem. A Rayleigh quotient on the static deflected shape serves as a cross-check.
- Corner column C_0_0: a half-bay tributary panel of 3.75 x 4.0 = 15 m2 plus 7.75 m of facade, using the simple-span assumption. JUDGMENT: no practical alternative method exists at concept stage, so this row is the least independent.
- Agent C: `verify_compare.py` with tol_structure.json (default rel 0.05, periods rel 0.10).

## CALCULATIONS
- CALCULATION (`architecture/tower/verification/verify_structure_B.py`): typical level G = 5930.4 kN and Q = 1489.8 kN; roof G = 7293.6 kN; plant roof G = 1080 kN. Vertical element self-weight totals 74 671.9 kN.
- CALCULATION: base core section A = 22.56 m2. I_x = (12 x 8^3 - 10.8 x 6.8^3)/12 = 229.01 m4, matching the pixel result. I_y = 438.16 m4.
- CALCULATION: corner column G = 5804.1 kN and Q = 892.5 kN. The EC form gives 1.35G + 1.5Q = 9174.2 kN; the LRFD form gives 1.2G + 1.6Q = 8392.9 kN. The EC form governs.
- CALCULATION: total modal mass is 27 135 t. Eigen periods are T_Y = 4.553 s and T_X = 3.307 s. The Rayleigh cross-check gives 4.526 s and 3.287 s, within 1%.

## RESULTS
| Key | B | A | rel diff | tol | |
|---|---|---|---|---|---|
| W_kN | 268 338 | 265 389 | 1.1% | 5% | ok |
| G_ground_kN | 255 027 | 254 192 | 0.33% | 5% | ok |
| Q_ground_kN | 44 371 | 44 457 | 0.19% | 5% | ok |
| core_I_x_base_m4 | 229.01 | 229.01 | 0.0% | 5% | ok |
| core_I_y_base_m4 | 438.16 | 438.16 | 0.0% | 5% | ok |
| N_Ed_corner_kN | 9174.2 | 9174.2 | 0.0% | 5% | ok |
| T1_Y_cracked_s | 4.553 | 4.548 | 0.11% | 10% | ok |
| T1_X_cracked_s | 3.307 | 3.304 | 0.10% | 10% | ok |

Agent C decision: **PROCEED** (all eight keys within tolerance). Files: B_structure.json and tol_structure.json in `architecture/tower/verification/`.

## CODE / STANDARD
- None applied. The jurisdiction is UNKNOWN. The load-factor forms (1.35/1.5 and 1.2/1.6) and psi = 0.3 are project ASSUMPTIONS from the inputs file, not verified code clauses. Verify against the current code once the jurisdiction is known.

## UNCERTAINTIES
- JUDGMENT: the 1.1% gap in W is consistent with a different treatment of the ground storey, roof live or plant level (e.g. A may lump only the upper half of the ground storey). It is within tolerance and was not investigated further.
- JUDGMENT: the exact agreement on N_Ed_corner (difference about 4e-6) shows that both agents used the same tributary idealisation. It confirms the arithmetic, not the method. Two-way slab continuity could raise or lower the corner reaction by about 10 to 20%, and this was not checked.
- UNKNOWN: internal core wall positions (they would add to I_y if placed off-centre), basement and soil flexibility (which would lengthen the periods), and columns and coupling in lateral stiffness (excluded by definition: core alone).

## FAILED CHECKS
None. All comparator rows passed. I did not check: column stress against the 0.45 fck limit, slab span/depth ratios, the correctness of the shared inputs themselves, or live load reduction.

## RECOMMENDATIONS
- Record PROCEED for the gravity and stiffness quantities.
- Check the corner and edge column loads with a two-way slab or FE gravity model before sizing columns, because both agents share the tributary simplification.
- The structure division should state its ground-storey and plant-level mass treatment explicitly in its return, to make the 1.1% W gap explainable.

## REQUIRED HUMAN REVIEW
A licensed structural engineer must review all load assumptions (they were shared inputs and are not independently validated), the jurisdiction-specific load factors, the cracked-section factor and the base-fixity assumption. These are feasibility-stage aids only, not certified design.
