# Division 24 Engineering Critic: 30-storey residential tower, Sydney (attack on waves 1-3)

Focus: all fourteen critic questions. This division does not design anything. It attacks the design. Agreement between divisions is not treated as evidence of correctness. CONCEPT-STAGE critique only. It is not certified engineering (PROTOCOL §8). Where a check needs a code value, the value is UNKNOWN or labelled "verify against current code". No clause is quoted.

## INPUTS USED

- FACT (project record): `architecture/PROTOCOL.md`, `architecture/tower/BRIEF.md`, `architecture/tower/basis.json` v2 (Sydney, lot UNKNOWN, 30 storeys, 2 basements at 3.3 m, 4.5 m ground storey, 3.1 m typical, 94.4 m roof slab + 5 m plant, 30 x 24 m plate, central 12 x 8 m core).
- FACT (division returns and data, as they stood on 2026-10-05):
  - `returns/structure.md` + `data/structure.json`: 14 perimeter columns, no interior columns, 250 mm PT flat plate, 9.0 m governing span, closed-tube core (openings ignored), cracked factor 0.5, fixed at ground, T1 = 4.548 s (Y) / 3.304 s (X).
  - `returns/seismic.md` + `data/seismic.json`: OpenSees stick, θ max 0.093 (Y), Bredt J = 454/392/324 m4, T_θ = 1.283 s, edge amplification 1.015.
  - `returns/wind.md` + `data/wind.json`: 45 m/s case, Y sway: V_b = 11.56 MN, M_b = 640.5 MNm, top 431 mm, interstorey 1/173 at storey 28, V_cr = 44 m/s (St 0.12), comfort 23 milli-g.
  - `returns/foundation.md` + `data/foundation.json`: D = 8.6 m, core 1558 kPa vs 239 kPa elsewhere, uplift-free if M < 1780 MNm, stage-0 flotation ratio 0.95 at full head.
  - `returns/geotechnical.md` + `data/geotechnical.json`: no ground data, excavation 8-10 m assumed.
  - `returns/architecture.md` + `data/architecture.json`: option A core layout (21 rectangles), 4 lifts, 2 stairs, lobby 9-21 x 10.8-13.2 "opens to the corridor at both ends (x = 9 and x = 21)".
  - `returns/codes.md` + `data/codes.json` (updated to NSW during this review): NCC 2022 Vol One; secondary-source hazard values Region A, V500 = 45 m/s, Z = 0.08. All are low confidence and none was read in the standard.
  - `returns/fire.md` + `data/fire.json` (produced in parallel; reviewed as found): stair doors assumed at (9, 9.4) and (21, 14.6); stairs 5.5 x 2.8 m with "about 1.2 m per flight".
  - `returns/verification-structure.md` and `verification/*.json`, `verify_structure_B.py`.
- UNKNOWN: lot, terrain, ground model, groundwater, parking requirement, façade system, balcony intent, lodgement date, approval route. Nothing in this return depends on an invented value for any of these.

## ASSUMPTIONS

All are critic ENGINEERING ASSUMPTIONS, used only to size the attacks. The responsible division must confirm or replace each one.
1. Coupling lintels over the 2.4 m lobby openings: depth 0.7-1.0 m (3.1 m storey minus an opening head of 2.1-2.4 m), thickness equal to the core wall, cracked stiffness 0.15-0.30 Ig (JUDGMENT, generic range). Walls are at 0.5, as in Division 3.
2. Punching: effective depth d = 0.20 m for the 250 mm PT plate. The capacity is an ACI-type non-prestressed form, φ·0.33√f'c with φ = 0.75, giving 1.57 MPa. It is used as a textbook-order yardstick, not a code check (verify against AS 3600). No PT vertical-component or precompression benefit is taken, because edge and corner columns usually get little. Exterior moment transfer is 0.26 M0 (textbook direct-design order, JUDGMENT). For corners, a 0.7 non-coincidence factor is applied to the biaxial term.
3. Column-loss load: 1.0G + 0.4Q (generic accidental-combination order, verify).
4. SSI: rocking stiffness of an equivalent circular surface raft, K_r = 8GR³/(3(1-ν)) with ν = 0.3 and R = 14.5 m (equal I to 30 x 24 m). Embedment and piles are ignored, which makes this an upper bound on rotation. Soil shear modulus is a PARAMETER (20, 50, 200, 1000 MPa), not a value for the site.
5. Shortening: elastic only, E = 35 GPa, G-only axial stress. The creep multiplier is (1 + φ) with φ = 2-2.5 (textbook order).
6. Codes' secondary values (V500 = 45 m/s, Z = 0.08) are used only as a labelled reference case. They are not FACT.

## METHOD

Re-ran:
- `python -m pytest -q architecture/tests -k tower`: 51 passed, 58 deselected (4.3 s).
- In a scratch copy of the repo, re-ran `structure_gravity.py`, `seismic_tower.py`, `wind_tower.py`, `foundation_tower.py`, `architecture_options.py` and `verification/verify_structure_B.py`. All exited 0. `git status` showed no change to any stored data file, so the stored JSON is reproducible from the scripts. Reproducibility does not prove correctness.

Read: every file listed under INPUTS USED, line by line for the numbers quoted.

Independent critic calculations (CALCULATION). These are scratch scripts outside the repo, and every equation is restated under CALCULATIONS:
1. Core section with the architects' openings. I did a pixel integration (0.02 m) of the 12 x 8 m tube cut by the two 2.4 m lobby openings at y = 10.8-13.2 in the webs x = 9 and x = 21, then computed the properties of each half.
2. Coupled-wall 2D frame for Y sway. It has two stepped Timoshenko wall sticks at the half-centroids (lever arm 6.65-6.80 m), rigid arms, and 2 lintels per level of clear span 2.4 m. It uses a rigid diaphragm and a fixed base, and solves for deflection, eigen period and lintel shear. Validation: with rigid lintels the model returns 3.26 mm per kN/m and T = 4.58 s, against Division 3's 3.02 mm and 4.548 s. The residual is from the shear area of 11.2t vs 16t, which is acceptable for a ratio study.
3. Punching stress at edge (E_0_8) and corner (C_0_0) columns, typical floor, top zone and base zone.
4. Core-base flange stress and tension under wind Y (core alone, as Division 3 assumes).
5. SSI rocking: added roof drift and lengthened T1 (T_ssi = T·√(1 + k·h_eff²/K_r), k = M1·ω², h_eff = 0.7H).
6. Differential elastic shortening of E_0_8 versus the core.
7. Gravity stability of the Y core if the lintels fail: q_cr = 7.84·EI/L³ for a cantilever under distributed axial load (textbook).
8. Consistency hunt across all returns: core space, grid, jurisdiction status, the independence of the verifier.

## CALCULATIONS

All CALCULATION unless tagged. Units: m, kN, MPa, s.

**C1. Core with the drawn openings (architecture.json `typical_floor`, Lift lobby 9-21 x 10.8-13.2).**

| Zone t (m) | I_x closed tube (m4) | I_x of one half (m4) | Two halves uncoupled (m4) | Ratio | Lever arm between halves (m) |
|---|---|---|---|---|---|
| 0.6 | 229.0 | 5.07 | 10.1 | 4.4 % | 6.65 |
| 0.5 | 197.6 | 4.40 | 8.8 | 4.5 % | 6.72 |
| 0.4 | 163.6 | 3.67 | 7.3 | 4.5 % | 6.80 |

The openings sit at mid-depth of both 8 m webs, i.e. on the neutral axis for Y bending, where shear flow is largest. Fire's assumed stair doors at (9, 9.4) and (21, 14.6) cut the same webs again. They leave about a 0.9 m pier between the stair door and the lobby opening on x = 9 (JUDGMENT, door positions are ASSUMPTION in fire.md).

**C2. Coupled-wall Y response (per 1 kN/m uniform load; T1 with structure.json masses).**

| Lintel depth / stiffness | Top deflection (mm per kN/m) | vs rigid-lintel 3.26 | T1_Y (s) | Max lintel shear at 45 m/s, Y (kN) | Stress V/(b·0.8h) (MPa) |
|---|---|---|---|---|---|
| 0.7 m / 0.15 Ig | 5.61 | +72 % | 6.26 | 1,778 (level 8) | 5.3 |
| 0.7 m / 0.30 Ig | 4.49 | +38 % | 5.53 | n/a | n/a |
| 1.0 m / 0.15 Ig | 4.29 | +32 % | 5.39 | n/a | n/a |
| 1.0 m / 0.30 Ig | 3.79 | +16 % | 5.01 | 2,105 (level 4) | 4.4 |
| lintels lost (≈0) | 71.3 | x22 | 21.3 | n/a | n/a |

The wind shear is scaled so that the base shear is 11.56 MN (wind.json 45 m/s, 30 m face, cracked). The load is uniform, not the wind profile. For reference, an order of 0.83√f'c ≈ 5.2 MPa is a commonly quoted ceiling for diagonally reinforced coupling beams (ACI-type form, verify against AS 3600). At 55 m/s the shears scale by about 1.6 (wind.json 18.6/11.56), giving 7-8.5 MPa.

**C3. Y-direction gravity stability if the lintels fail.** EI_halves (base zone, cracked) = 2 x 5.07 x 0.5 x 35e6 = 1.77e8 kNm2. Then q_cr = 7.84 x 1.77e8 / 99.4³ ≈ 1,430 kN/m. Actual gravity is q = W/H = 265,389/99.4 ≈ 2,670 kN/m, so q/q_cr ≈ 1.9. If the internal lobby walls (2 x 12 m, 0.2-0.25 m, with lift-door openings) act as second flanges, I_half rises to about 10-14 m4 (JUDGMENT), and q/q_cr ≈ 0.7-0.9. The perimeter flat-plate frame (seismic VARIANT, 6.0-6.6e4 kN/m per storey) gives P/(k·h) = 265,389/(6.3e4 x 3.1) ≈ 1.36, so it cannot stabilise the tower alone either. Result: Y-direction stability of the tower depends on the lobby lintels.

**C4. Torsion.** Seismic used the Bredt closed-tube J. The lintels are the only closure of the cell. If the effective J is 5-10 % of Bredt, then T_θ = 1.283/√(0.05...0.10) = 4.1-5.7 s, which equals or exceeds T1_X = 3.30 s and is near T1_Y. The perimeter-frame torsional stiffness, Σk·r² ≈ 6.3e4 x (12² + 15²) ≈ 2.3e7 kNm/rad per storey, is about 2 % of the Bredt core value of 1.07e9, so the frame cannot restore separation.

**C5. Punching (typical floor, w_u = 1.35 x 7.75 + 1.5 x 2.0 = 13.46 kPa, facade 1.35 x 6 kN/m).**

| Column (zone size) | V_u (kN) | b0 (m) | v direct (MPa) | v incl. moment transfer (MPa) | / 1.57 MPa |
|---|---|---|---|---|---|
| E_0_8 top (0.60 m) | 530 | 2.20 | 1.20 | 3.03 | 1.9 |
| E_0_8 base (1.05 m) | 530 | 3.55 | 0.75 | 1.42 | 0.9 |
| C_0_0 top (0.45 m) | 265 | 1.10 | 1.20 | 4.75 | 3.0 |
| C_0_0 base (0.75 m) | 265 | 1.70 | 0.78 | 2.31 | 1.5 |

Hand check, E_0_8 top: V_u = 13.46 x 34.545 + 1.35 x 6 x 8 = 465 + 65 = 530 kN. b0 = 2(0.6 + 0.1) + (0.6 + 0.2) = 2.2 m. v = 530/(2.2 x 0.2) = 1,205 kPa. The column sizes were set only by axial stress (structure.md assumption 5). The smallest columns sit at L21-30, the same storeys where wind and seismic both find the maximum interstorey drift (storey 27-28; wind.json `max_interstorey_level_index` 28, seismic storey 28).

**C6. Core base under wind Y (core alone).** Z_x = I_x/4 = 57.3 m3, and 0.9G/A = 0.9 x 127,484/22.56 = 5.1 MPa.

| V (m/s) | M_b (MNm) | M/Z (MPa) | Net at windward flange (MPa) | Flange tension T ≈ M/7.4 - 0.45G (MN) | As at 435 MPa (mm2) | % of 12 x 0.6 flange |
|---|---|---|---|---|---|---|
| 35 | 355 | 6.2 | -1.1 | ≈ 0 | 0 | 0 |
| 45 | 640 | 11.2 | -6.1 | 29 | 67,000 | 0.9 |
| 55 | 1,030 | 18.0 | -12.9 | 82 | 188,000 | 2.6 |

Elastic seismic overturning per g (Y mode 1) is 11,429 MNm, which equals the 45 m/s wind moment at Sa(T1) = 640/11,429 = 0.056 g.

**C7. SSI rocking (Y, 45 m/s wind moment 640 MNm, k = M1·ω² with M1 = 0.614 x 27,053 t, h_eff = 69.6 m).**

| G_soil PARAMETER (MPa) | K_r (kNm/rad) | Added roof drift (mm) | T1_Y (s) | V_cr at St 0.12 (m/s) |
|---|---|---|---|---|
| 20 | 2.3e8 | 275 | 5.87 | 34.1 |
| 50 | 5.8e8 | 110 | 5.12 | 39.1 |
| 200 | 2.3e9 | 28 | 4.70 | 42.6 |
| 1000 | 1.2e10 | 6 | 4.58 | 43.7 |

**C8. Differential shortening, E_0_8 vs core (G only).**
- Base stresses are 10.2 MPa in the column vs 4.9 MPa in the core.
- Elastic shortening to the roof is 20.3 mm (column) vs 7.8 mm (core), a difference of 12.5 mm.
- With creep, x(1 + φ) = 3-3.5, giving about 37-44 mm before any construction-stage compensation.
- Over the 9 m span this is a slope of about 1/200-1/240 if uncompensated.

**C9. Column loss (accidental 1.0G + 0.4Q per floor).**
- E_0_8 lost: 343 kN per floor to redistribute, and the free edge becomes a 16 m span (C_0_0 to E_0_16).
- C_0_0 lost: 175 kN per floor, and the corner becomes a two-way cantilever reaching 12.0 m diagonally to the core corner (9, 8).

**C10. Core space check (architecture.json rectangles minus wall thickness).**
- Outer core walls are 0.6 m (L1-10), and internal shaft walls are assumed at 0.2 m.
- Lift 1 and Lift 2 clear size: (2.5 - 0.2) x (2.8 - 0.6 - 0.1) = 2.3 x 2.1 m.
- Lift 3 (corner) clear size: (2.5 - 0.6 - 0.1) x 2.1 = 1.8 x 2.1 m.
- Stair 1 clear size: 4.8 x 2.1 m. Two flights then get about 1.0 m each, against fire.md's assumed 1.2 m.
- Lobby clear depth: 2.4 - 0.2 = 2.2 m between facing lift doors.
- Lift handling with one car out (routine maintenance in a 30-storey building): 3 x 15.55/696 = 6.7 %, below the architects' own 7 % target.

**C11. Internal core walls (load omission).**
- The architects' layout has about 40.8 m of internal walls per storey: 2 x 12 m lobby walls plus 6 shaft partitions of 2.8 m.
- Structure and B model only 2 x 6.8 m = 13.6 m, so about 27 m per storey is missing.
- At 0.2-0.25 m x 3.1 m x 25 kN/m3 that is 420-530 kN per storey, i.e. +4.5-6.5 % of storey W (8,133-9,962 kN), all of it on the core.

## RESULTS

Ranked findings. Severity = Probability (1-5) x Consequence (1-5). Each finding is written as CAUSE · MECHANISM · CONSEQUENCE · DETECTION · MITIGATION · RESIDUAL RISK.

**R1 (Severity 20). The governing core stiffness rests on an assumption the drawn plan contradicts. Collapse-relevant.**
- CAUSE: Structure, seismic, wind, verification A and B, and the seismic hand model all model the core as a closed 12 x 8 m tube with openings ignored (structure.md assumption 6). Architecture draws a lift lobby running the full 12 m through the core and opening to the corridor at x = 9 and x = 21. Fire adds stair doors in the same webs.
- MECHANISM: In Y (the governing direction) the core becomes two channels coupled only by 2.4 m-span lintels on the neutral axis.
  - Uncoupled I is 4.4 % of the modelled value (C1).
  - With realistic lintels, T1_Y is 5.0-6.3 s instead of 4.55 s, and deflection rises by +16 to +72 % (C2).
  - The lintels then take 1.8-2.1 MN each at 45 m/s, about 4.4-5.3 MPa, which is at or above a practical ceiling. At 55 m/s it is 7-8.5 MPa.
  - Lintel failure removes coupling. The core alone is then unstable or near-unstable under its own gravity in Y (q/q_cr ≈ 0.7-1.9, C3).
  - Torsion: Bredt J is invalid without the lintels, and T_θ could move to 4-6 s (C4). That makes torsional irregularity credible (UNKNOWN until modelled), and seismic's 1.015 amplification is not supported.
- CONSEQUENCE: Every lateral result in seismic.md and wind.md is unconservative for Y: drift, comfort, vortex lock-in speed, θ and the gust factor. In the extreme, brittle lintel failure leads to loss of lateral stability.
- DETECTION: An L3 shell/wall model of the actual core with openings, lintels and internal walls. Compare its T1_Y with 4.55 s. A > 30 % difference triggers investigation per structure.md recommendation 4. My estimate is +10 to +38 %.
- MITIGATION (owner: architecture with structure; options only, not a design): close the lobby ends (no through-passage at the webs), move the corridor connections to the flanges away from the neutral axis, deepen the lintels or use full-storey link walls, enlarge the core in Y, or adopt Option B or perimeter walls. Then re-run every lateral division.
- RESIDUAL RISK: Even with closed webs, lift and stair doors remain. Coupling-beam ductility and detailing in jump-form are a construction risk.

**R2 (Severity 20). Punching at the upper perimeter and corner columns, coinciding with peak drift.**
- CAUSE: Columns are sized for axial load only, down to 450/600 mm at L21-30. The 250 mm plate has a 9 m span, and no punching check was done (structure FAILED CHECKS).
- MECHANISM: Direct plus moment-transfer shear reaches about 1.9x (edge) and about 3.0x (corner) a no-shear-reinforcement yardstick at the top zone (C5). The base zone is 0.9-1.5x. The maximum interstorey drift (storey 27-28) lands on these same connections. Drift adds rotation demand to connections already above a high gravity-shear ratio (about 0.76 from direct shear alone).
- CONSEQUENCE: Brittle punching, then slab drop, then impact on the floor below. This is the classic flat-plate progressive (pancake) collapse. It could be triggered under ULS wind drift alone (1/173 at 45 m/s, cracked, before the R1 increase), not only by earthquake.
- DETECTION: L3 plate FE with PT equivalent loads (structure recommendation 3), a punching check per AS 3600 including moment transfer, and a drift-compatibility check of the gravity frame.
- MITIGATION: Shear studs or rails, larger upper columns or column capitals, edge beams or thickened edge strips, integrity (structural-integrity) bars or tendons through columns, and limiting drift (R1).
- RESIDUAL RISK: Workmanship of stud placement, penetrations near columns (R12), and loss of PT.

**R3 (Severity 16). Overturning load path at the core base and into the foundation is inconsistent between divisions.**
- CAUSE: Structure gives all lateral load to the core alone. Foundation evaluates overturning as a rigid 30 x 24 raft carrying the whole building (N = 356 MN, uplift only if M > 1,780 MNm).
- MECHANISM: The core carries G = 127.5 MN on a 12 x 8 m footprint. At 45 m/s the windward flange is in net tension of 6.1 MPa, with T ≈ 29 MN. At 55 m/s T ≈ 82 MN (C6). That tension must be lapped at the base and anchored into a raft (2.0 m assumed) or into piles concentrated under the core, which is foundation's own recommendation. Those piles would then see tension. Seismic overturning matches the 45 m/s wind at Sa(T1) = 0.056 g.
- CONSEQUENCE: Under-reinforced core base, lap-splice failure in the hinge zone, raft punching or bending under the core, and pile pull-out or uplift. All are brittle or hard to repair.
- DETECTION: Core-base section analysis with real axial and moment, raft FE on springs, a pile-group analysis with tension, and a check that the foundation and structure use the same M at the same level.
- MITIGATION: Engage the perimeter columns (outrigger or perimeter walls), thicken or deepen the raft under the core, use tension piles or anchors, and stagger the laps.
- RESIDUAL RISK: Depends on ground (UNKNOWN) and the wind basis (secondary V500 = 45 m/s).

**R4 (Severity 15). Wind serviceability: vortex lock-in and comfort get worse once R1 and SSI are included.**
- CAUSE: Wind uses T1_Y = 4.55 s from the closed tube on a fixed base.
- MECHANISM:
  - At T = 5.0-6.3 s (C2) or 5.1-5.9 s on soft ground (C7), V_cr = 24/(T x 0.12) ≈ 32-40 m/s, below the 44 m/s used.
  - Lock-in then sits inside frequent winds at the secondary V500 = 45 m/s.
  - The gust factor rises, comfort (already 23 milli-g against about 10-15) worsens, and P-Delta (θ 0.09, +10 % drift) is absent from the wind drift.
  - The frequency drops to 0.16-0.20 Hz, i.e. at or below the 0.2 Hz dynamic trigger that codes.md reports (secondary).
- CONSEQUENCE: Occupant discomfort or unsaleability, façade and partition damage, and fatigue in the lintels.
- DETECTION: HFFB wind tunnel with real surroundings on the corrected stiffness.
- MITIGATION: Stiffen Y (R1 options), aerodynamic shaping (wind.md recommendation 4), and auxiliary damping if the tunnel shows an exceedance.
- RESIDUAL RISK: Damping is unmeasured (1-2.5 %).

**R5 (Severity 15). The core does not fit its programme once the wall thickness is counted, and the core will change.**
- CAUSE: Architecture tiles the 12 x 8 m outer dimension with rooms and ignores the 0.4-0.6 m walls.
- MECHANISM:
  - Clear lift shafts are 2.3 x 2.1 m and 1.8 x 2.1 m, stairs are 2.1 m wide (about 1.0 m per flight, against fire's 1.2 m), and the lobby is 2.2 m deep (C10).
  - The firefighting lift has no lobby of its own: it opens into a lobby that is open to the ring at both ends, while fire recommends a dedicated lobby.
  - With 4 lifts, one car out gives 6.7 % handling capacity.
- CONSEQUENCE: The core must grow or be re-planned. That changes stiffness, mass, the openings, the column positions and all wave-2 results. The verdicts in fire 2e/2f also rest on the wrong clear widths.
- DETECTION: A lift-manufacturer shaft check, a drawn stair section, and fire engineer review.
- MITIGATION: Architecture and structure reconcile the core (larger core or relocated stairs) before any wave-2 model is frozen.
- RESIDUAL RISK: Programme rework.

**R6 (Severity 12). The verification is not independent of the error that matters.**
- CAUSE: `structure_inputs_for_B.json` states that it "deliberately excludes Agent A's results". It nevertheless contains A's column sizes (an A result), the closed-tube core box, the cracked factor and fixed base, and every load. Seismic agent B uses A's masses. Wind and foundation have no B at all.
- MECHANISM: Six agreements (structure A, B, seismic A, B, hand model, closed form) all inherit the same closed-tube and fixed-base input. N_Ed_corner agrees to 4e-6, which B itself says confirms arithmetic only.
- CONSEQUENCE: PROCEED is recorded for a model that is conceptually wrong in Y (R1).
- DETECTION: This review.
- MITIGATION: Give B the architects' plan, not A's idealisation. Give B no member sizes. Require a different idealisation (shell model with openings), not just a different algorithm.
- RESIDUAL RISK: Common-mode errors in loads remain until code values are read.

**R7 (Severity 12). Differential shortening between core and columns.**
- CAUSE: Columns run at about 10 MPa and the core at about 5 MPa (G only).
- MECHANISM: Elastic differential is 12.5 mm at the roof, and about 37-44 mm long-term before compensation (C8). A slope of about 1/200 across 9 m imposes moments at the slab-core joint and tilts floors. Option B outriggers would lock these strains in as large forces.
- CONSEQUENCE: Cracking at the core face, partition and façade-joint distress, lift-rail alignment problems, and outrigger overstress.
- DETECTION: Staged-construction creep analysis (structure recommendation 6) and survey monitoring during the build.
- MITIGATION: Pre-camber or level compensation, delayed outrigger connection, and joints sized for the movement.
- RESIDUAL RISK: Creep parameters of the actual mix are UNKNOWN.

**R8 (Severity 12). Podium, basement and backstay unknown; the fixed-base load path is not demonstrated.**
- CAUSE: Fixity is taken at the ground slab, and the basement and parking are not modelled. The 30 x 24 footprint gives roughly 15-20 spaces per level (JUDGMENT) for 232 apartments, so the basement probably extends beyond the tower and needs a ramp through the ground slab (UNKNOWN; parking requirement not supplied).
- MECHANISM: Backstay shear reversal into the ground diaphragm and basement walls, with diaphragm cuts at ramps. Any transfer of the tower grid to a parking grid is NOT CHECKED. The 4.5 m ground storey is acceptable for the core but is a soft frame storey (seismic flag ii).
- CONSEQUENCE: An overloaded ground diaphragm or core below grade. This is a hidden transfer.
- DETECTION: Basement/podium model with soil springs.
- MITIGATION: Keep the ramp out of the backstay load path, add collectors, and keep the tower columns continuous to the raft.
- RESIDUAL RISK: UNKNOWN until the parking brief exists.

**R9 (Severity 12). Water entry.**
- Basement: stage-0 flotation ratio 0.95 at the full 8.6 m head (foundation.json). Lift pits sit 1-2 m below B2 (JUDGMENT), and the raft under the core is probably thicker, so excavation exceeds both the 8.6 m and the 8-10 m assumptions. Wall-raft and jump-form construction joints need attention.
- PT anchor pockets at the slab edge sit on the façade line: tendon corrosion if wet.
- Façade stack joints must absorb drift (1/173 ULS, more per R1) plus shortening (R7).
- Roof plant penetrations, 2 risers of 4.2 m2 serving 232 apartments, and the sprinkler system.
- Ground-floor thresholds against street flooding (flood UNKNOWN).
- DETECTION: Hydrogeology, façade movement-joint schedule, and water testing.
- MITIGATION: Tension piles or ballast for stage 0, drained or tanked basement decision, and protected anchorages.

**R10 (Severity 12). Construction stage.**
- Core jump-form ahead of the floors: the slab-to-core connection carries about 83 kN/m factored shear (C: 248.2 m2 x 13.46 kPa / 40 m) plus hogging continuity through cast-in couplers. Misplaced couplers make the joint simply supported, which pushes 10-20 % more load to the edge columns (R2).
- Lintel diagonal bars (R1) are hard to fix in jump-form.
- PT stressing is restrained by the stiff core and large base columns, causing cracking at core corners and column shear (pour strips or release details needed).
- Back-propping loads exist and are omitted. Tower-crane ties and the jump-form wind loads act on young core concrete.
- Stage-0 flotation (R9).
- DETECTION: Temporary-works design and check, and coupler survey before each pour.
- RESIDUAL RISK: Workmanship.

**R11 (Severity 10). Column loss / robustness.**
- No alternate-path check exists.
- Losing E_0_8 needs 343 kN per floor redistributed across a 16 m free edge. Losing a corner leaves a 12 m diagonal cantilever (C9). In both cases the remaining neighbours already fail the punching yardstick (R2).
- Credible triggers: vehicle impact in basement parking or at the ground-floor retail frontage, and fire.
- DETECTION: Alternate-path analysis with integrity tendons and bars through the columns.
- MITIGATION: Integrity reinforcement, impact protection, key-element design of the ground and basement columns.
- RESIDUAL RISK: Corner loss is likely to remain the weakest case.

**R12 (Severity 12). Human misuse.**
- Owners core-drilling or fixing into the PT plate and cutting tendons (sudden local loss).
- Service penetrations within the punching perimeter of columns.
- Roof and balcony overloading (planters, spas, pools) against 1.5-2.0 kPa.
- A gym in the ground retail (heavy weights, impact).
- Heavier EVs in the basement and EV battery fires.
- Stair doors propped open (both stairs share one ring corridor and one core).
- Over-occupancy and short-term letting pushing lift demand past the 7 % target.
- Drilling into lintels for services.
- DETECTION / MITIGATION: Tendon-location marking and a strata by-law, a penetration-control zone at columns, posted load limits, door hold-open on fire release only.
- RESIDUAL RISK: Owner-corporation enforcement over 50 years.

**R13 (Severity 10). Fire.**
- No fire resistance level (FRL) has been set and PT tendon cover is NOT CHECKED (fire 5a).
- Tendons lose prestress at elevated temperature (textbook order 350-450 °C, JUDGMENT).
- Restrained thermal expansion of a 30 x 24 m plate pushes the small upper perimeter columns sideways, a brittle column-shear mode (JUDGMENT).
- Both stairs are inside one core with a 2 % margin on the non-code separation reference (fire 2e). The firefighting lift has no lobby (R5).
- Basement car-park fire (EV) sits under the ground diaphragm (R8).
- DETECTION: Structural fire analysis by a specialist.
- MITIGATION: Cover per AS 3600 FRL tables (verify), spalling control, separate stairs (fire recommendation 2).
- RESIDUAL RISK: Façade fire spread (fire 5b) UNKNOWN.

**R14 (Severity 10). Earthquake beyond design level.**
- Sydney hazard Z = 0.08 is secondary and low confidence. JUDGMENT: low-to-moderate seismicity, so wind likely governs core flexure. Higher modes on the plateau govern upper-storey shear.
- Beyond design: the brittle chain is lintel shear failure (R1), then loss of coupling, θ rising from 0.09 towards instability (C3), punching under drift (R2), and pancake collapse.
- Lap splices at the core base under tension (R3).
- The high axial ratio of columns under ULS gravity (0.41-0.45 fck) limits their drift capacity.
- DETECTION: Pushover or NLTHA once the hazard is primary-sourced, with the real core.
- MITIGATION: Ductile diagonal lintels, capacity-design shear, punching studs, integrity steel.
- RESIDUAL RISK: Higher-mode wall shear amplification is not quantified.

**R15 (Severity 10). Assumptions that could cause collapse (summary).**
1. Closed-tube core (R1).
2. Columns sized by axial load only, ignoring punching and drift (R2).
3. Core-alone overturning on a "rigid whole raft" (R3).
4. Fixed base with no backstay check (R8).
5. Tributary loads without continuity (+10-20 % edge, structure.md uncertainties).
6. E_7.5_0 at 0.448 against the 0.45 fck limit: any load growth (C11 internal walls +4.5-6.5 % on the core; a precast façade +1 kN/m adds 240 kN) breaks it.

**R16 (Severity 9). Omitted loads.**
- Internal core walls about 27 m per storey (C11).
- Building maintenance unit (BMU) on the roof.
- Sprinkler and fire-water tanks: if at the roof, 5.0 kPa over the core may be low (UNKNOWN).
- Construction and back-propping loads.
- Cross-wind, torsional and corner wind cases (wind.md assumption 10).
- Wind P-Delta.
- Earth and hydrostatic pressure on basement walls.
- Vertical and accidental-torsion seismic.
- Restraint (PT shortening, thermal, shrinkage).
- Ground and basement live loads (about 1-2 % of total, small).
- Balconies: none in option A. Sydney apartments usually have them (JUDGMENT, planning UNKNOWN). Adding them changes façade load, mass, waterproofing and thermal bridging.

**R17 (Severity 9). After 50 years.**
- Creep shortening and deflection (R7).
- Lintel stiffness degrading under wind cycles, which lengthens T and worsens comfort over time.
- Sealant life about 15-25 years (JUDGMENT): façade seals must be replaceable.
- PT anchorage corrosion (R9). Carbonation and chloride (coastal exposure UNKNOWN until the lot is fixed).
- Differential settlement under the 6.5x core pressure (ground UNKNOWN).
- Lift modernisation downtime with only 4 cars.

**Contradictions between divisions (FACT, file and number):**
1. Core: structure, seismic and wind use a closed tube (structure.md assumption 6). Architecture opens the lobby at x = 9 and x = 21 (architecture.md RESULTS), and fire places stair doors in the same webs.
2. Grid: architecture "Interior columns sit at the outer corners of the corridor ring … Maximum bay 7.5 x 8 m … RC flat slab". Structure: "There are no interior columns … 9 m … PT 250 mm".
3. Internal core walls: structure/B use "2 internal cross walls … spanning Y" (13.6 m). Architecture has 2 x 12 m lobby walls along X plus 6 partitions (about 40.8 m). A Y-spanning cross wall would also block the through-lobby.
4. Y stiffness: wind fails drift and comfort, finds vortex lock-in inside the range, and says the tunnel is "not required at feasibility". Seismic gives θ ≈ 0.09 and recommends an upgrade. Structure still carries Option A as the reference. Codes reports a 0.2 Hz dynamic trigger that T1 = 4.55 s (0.22 Hz) nearly reaches, and the R1 periods (0.16-0.20 Hz) cross.
5. Option B "outrigger at plant level": the plant storey is 12 x 8 m over the core only (structure.json `plant (core roof)`), so there is no floor to carry outrigger arms to the columns. Architecture keeps all 29 residential floors identical, with no plant or refuge floor reserved.
6. Overturning: foundation uses a rigid whole raft with N = 356 MN, while structure uses core-alone lateral resistance (R3).
7. Depth: foundation D = 8.6 m, geotech 8-10 m. Lift pits and a thickened core raft are not in either.
8. Stairs: fire assumes about 1.2 m per flight in a 2.8 m shaft; with 0.6 m walls the clear width is 2.1 m (C10).
9. Jurisdiction status: basis v2, fire and codes are Sydney/NSW. Structure, seismic, wind, foundation, geotechnical and architecture returns still say jurisdiction or site UNKNOWN and have not been re-run against the codes' reference case (45 m/s, Z = 0.08, secondary). Geotechnical still states "structure.json does not exist".
10. Verification: `structure_inputs_for_B.json` claims to exclude A's results but includes A's column sizes.
11. Wind drift omits the P-Delta effect that seismic quantified (θ 0.09, T +4.3 %).

## CODE / STANDARD

- Jurisdiction per basis v2 is NSW, Australia. Codes.md names NCC 2022 Vol One, AS/NZS 1170.0/.1/.2, AS 1170.4 (edition conflict) and AS 3600. None of these texts was read by this division or by codes (secondary evidence only). No clause is quoted. Every yardstick used here is a textbook or generic form and must be verified against the current code:
  - the punching 0.33√f'c form;
  - the 0.83√f'c coupling-beam ceiling;
  - the 0.26 M0 moment transfer;
  - the 1.0G + 0.4Q accidental combination;
  - H/500 and 10-15 milli-g.
- Mechanics are textbook: coupled shear walls (frame analogy), cantilever buckling under distributed axial load (q_cr = 7.84 EI/L³), circular-footing rocking stiffness, elastic shortening.
- Requirement class of every number here: ENGINEERING ASSUMPTION.

## UNCERTAINTIES

- Lintel depth, door head heights and actual opening positions are not drawn. The R1 stiffness loss ranges from +16 % to x22 depending on them.
- Internal lobby and shaft walls could raise the half-core I by about 2-3x (JUDGMENT). That would reduce, but not remove, R1.
- Punching ratios are sensitive to d, the moment-transfer fraction and PT balanced load (±30-50 %). The corner ratio of about 3 has margin for that. The edge ratio of about 1.9 is less certain.
- The coupled-wall model uses a uniform load profile rather than the wind profile, and a reduced web shear area (11.2t vs 16t). Its rigid-lintel validation is within 8 % on deflection and 1 % on period.
- SSI uses an equivalent circular surface raft. Embedment and piles would reduce rotation. G_soil is a PARAMETER: Sydney ground (often sandstone/shale, JUDGMENT, lot UNKNOWN) may be at the stiff end.
- Hazard values are secondary (codes.md, low confidence).
- The fire return arrived during this review. Its stair-door positions are ASSUMPTION in fire.md.

## FAILED CHECKS

Critic attacks that produced a failure against the stated yardstick (not code verdicts):
- Closed-tube core assumption: FAILED against the drawn architecture (C1, R1). Y stiffness is overstated and the stability margin depends on unmodelled lintels.
- Lintel shear at 45 m/s: 4.4-5.3 MPa, at or above the about 5.2 MPa yardstick. At 55 m/s it fails (C2).
- Punching yardstick: FAILED at the top-zone edge (about 1.9) and corner (about 3.0) columns and the base-zone corner (about 1.5) (C5).
- Core-base tension at 45 and 55 m/s: net tension present (C6). It is not addressed by structure or foundation.
- Core space: lift shafts and stairs too small once walls are counted (C10).
- Verification independence: FAILED. Shared inputs include A's member sizes (R6).
- Cross-division consistency: 11 contradictions listed under RESULTS.

Could not be checked (UNKNOWN):
- the real core layout (doors, lintels);
- PT design;
- fire resistance levels (FRL);
- façade system and joints;
- ground and groundwater;
- parking and basement extent;
- primary-source wind and seismic values;
- cross-wind and torsional wind response;
- higher-mode wall shear;
- the nonlinear collapse margin;
- the Option B geometry.
The scratch critic scripts are outside the repo and have no tests. The numbers are reproducible from the equations under CALCULATIONS.

## RECOMMENDATIONS

1. Stop: do not treat the PROCEED decisions in verification-structure.md or seismic.md as clearing the lateral system. The common input (closed tube) is contradicted by the plan (R1, R6).
2. Architecture + structure (`bld-design-lead`): reconcile the core before wave 2 is rerun. Cover wall thickness, lift and stair clear sizes, the firefighting lobby, the through-lobby openings, door positions and internal walls. Issue one drawn core plan as the single input to every division.
3. Structure: build an L3 wall/shell model with openings and lintels. Re-run the period, drift, θ, torsion (actual J) and lintel shear. Do the punching check with moment transfer at every perimeter column, including drift compatibility. Do the core-base tension and lap design. Check integrity steel and column loss. Run a staged shortening analysis. Include the internal-wall weight.
4. Wind and seismic: re-run on the corrected stiffness with SSI parameters. Add P-Delta to the wind drift. Run the 45 m/s and Z = 0.08 reference case, labelled secondary. Wind should state whether f1 < 0.2 Hz triggers the tunnel.
5. Foundation: carry the core-alone M, N and V at founding level. Check tension piles under the core. Revise the depth for lift pits and the core raft thickening. Check stage-0 flotation at the measured head.
6. Verification (Division 25): repeat B with independent geometry from the architects' plan and no A member sizes, using a different idealisation.
7. Fire: recheck stair widths with the true clear dimensions, plus the firefighting lobby, the PT fire resistance level (FRL) and thermal-expansion effects on the upper columns.
8. Client: parking requirement, basement extent, balcony intent, façade type, the lot.
9. Add to the operations manual: tendon-location records, penetration control at columns, posted roof and balcony load limits.

**Risk register (ranked by severity; P and C on 1-5)**

| Risk | Probability | Consequence | Severity | Evidence | Mitigation | Verification |
|---|---|---|---|---|---|---|
| R1 Core openings: Y stiffness, lintel shear, stability, torsion | 4 | 5 | 20 | architecture.json lobby 9-21 x 10.8-13.2; C1 I 229→10.1 m4; C2 T1_Y 5.0-6.3 s, lintel 4.4-5.3 MPa; C3 q/q_cr 0.7-1.9 | Close webs or deepen lintels, enlarge core in Y, Option B or perimeter walls | L3 shell model with openings; T1 within 30 % of the revised value |
| R2 Punching at upper edge/corner columns under drift | 4 | 5 | 20 | C5 ratios 1.9 / 3.0; drift peak at storey 28 (wind.json, seismic.md) | Studs, larger top columns, edge strips, integrity steel, drift limit | Plate FE + AS 3600 punching + drift-compatibility check |
| R3 Core-base tension and foundation overturning model mismatch | 4 | 4 | 16 | C6: 29 MN (45 m/s), 82 MN (55 m/s); foundation.md 1,780 MNm on a whole raft | Engage columns, tension piles, raft thickening, staggered laps | Core-base section + raft/pile SSI model with the same M |
| R4 Vortex lock-in / comfort worse with R1 + SSI | 5 | 3 | 15 | wind.json V_cr 44 m/s, 23 milli-g; C2/C7 V_cr 32-40 m/s; codes 0.2 Hz trigger | Stiffen Y, shaping, damping | HFFB wind tunnel on the corrected model |
| R5 Core programme does not fit; core will change | 5 | 3 | 15 | C10 shafts 2.3x2.1 / 1.8x2.1 m, stair 2.1 m; fire.md 1.2 m/flight; 6.7 % HC5 with one lift out | Re-plan or enlarge the core, firefighting lobby | Lift-manufacturer and fire-engineer sign-off |
| R6 Verification not independent (shared closed tube, A sizes, masses) | 4 | 3 | 12 | structure_inputs_for_B.json contains size_by_zone_m; seismic B shares masses | Independent geometry and idealisation for B | Re-run A/B/C with the architects' plan |
| R7 Differential shortening core vs columns | 4 | 3 | 12 | C8 12.5 mm elastic, 37-44 mm long term | Compensation, delayed outrigger, joints | Staged creep analysis + survey monitoring |
| R8 Basement/podium/backstay and parking transfer unknown | 3 | 4 | 12 | structure.md assumption 8/10; foundation D 8.6 m; parking UNKNOWN | Continuous columns, ramp outside backstay, collectors | Basement model with soil springs |
| R9 Water entry (basement, lift pits, PT pockets, façade joints) | 4 | 3 | 12 | foundation.json flotation 0.95; R1/R7 movements | Tension piles/ballast, waterproofing strategy, joint design | Piezometers, façade water tests |
| R10 Construction (couplers, PT restraint, propping, stage 0) | 3 | 4 | 12 | slab-core shear about 83 kN/m; no temporary-works basis | Temporary-works design, pour strips, coupler survey | Independent temporary-works check |
| R12 Human misuse (tendon cutting, penetrations, overload) | 3 | 4 | 12 | PT plate 250 mm; R2 ratios | Tendon records, by-laws, penetration zones | Strata manual audit |
| R11 Column loss / disproportionate collapse | 2 | 5 | 10 | C9 343 kN/floor, 16 m edge, 12 m corner | Integrity reinforcement, impact protection, key elements | Alternate-path analysis |
| R13 Fire (PT tendons, thermal push on columns, stairs in one core) | 2 | 5 | 10 | fire.md 5a, 2e (2 % margin) | FRL cover, spalling control, stair separation | Structural fire analysis, fire engineer review |
| R14 Earthquake beyond design (brittle chain) | 2 | 5 | 10 | seismic θ 0.093; C3; column axial 0.41-0.45 fck | Ductile lintels, capacity design, studs | Pushover/NLTHA on the real core, primary hazard |
| R15 Column axial limit margin (E_7.5_0 0.448 vs 0.45) | 4 | 2 | 8 | structure.json base_stress_ratio; C11 +4.5-6.5 % core weight | Resize after load update | Re-run structure_gravity.py |
| R16 Omitted loads (internal walls, BMU, tanks, cross-wind, propping) | 3 | 3 | 9 | C11; wind.md assumption 10 | Add load cases | Load schedule review |
| R17 50-year: creep, lintel degradation, seals, corrosion, settlement | 3 | 3 | 9 | R7; foundation core 6.5x pressure | Maintenance plan, monitoring | Periodic structural inspection |

## REQUIRED HUMAN REVIEW

- A licensed structural engineer (registered design practitioner, NSW) must adjudicate R1-R3 before any lateral result is used. In particular, the closed-tube assumption against the drawn core, the lintel and stability finding, and punching at the upper columns.
- A PT specialist: punching, integrity tendons, stressing restraint, fire cover.
- The geotechnical engineer: SSI range, tension piles, flotation, revised excavation depth.
- A wind engineer and tunnel laboratory: lock-in and comfort on the corrected stiffness.
- A fire engineer and NSW certifier: stair clear widths, firefighting lobby, PT in fire.
- A lift consultant: shaft sizes and handling capacity with one car out.
- `bld-safety-qa-lead`: decide whether the PROCEED decisions stand given R6.
- This critique is a concept-stage aid by an AI agent. It is not certified engineering and makes no approval or construction-ready statement.
