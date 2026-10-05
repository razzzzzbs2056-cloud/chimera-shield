# Division 4 Earthquake Engineering: 30-storey residential tower, modal and per-unit-Sa dynamic analysis

Focus: Modal Analysis / Mode Shapes / Base Shear / Drift / Torsion / P-Delta / Response Spectrum (parametric only). Analysis level L4: a linear modal analysis with response-spectrum style combination. It is parametric in Sa because the hazard is UNKNOWN. CONCEPT ONLY. Not for construction. This return gives demands, not capacities. It does not state, and cannot state, a performance level for any real hazard (PROTOCOL §8).

Script: `architecture/tower/calcs/seismic_tower.py` -> `architecture/tower/data/seismic.json`. Tests: `architecture/tests/test_tower_seismic.py` (8 passed). Model: OpenSeesPy 3.7.1.2.

## INPUTS USED

- FACT (Division 3, `architecture/tower/data/structure.json`). Level heights z = 4.5, 7.6 ... 94.4 m (L30 roof slab) and 99.4 m (core-roof plant), 31 levels. Seismic mass per level is `mass_t_per_level`, which includes the roof plant. The total is 27,053 t (W = 265,389 kN, dead + 0.3 live). Gravity per level is `W_level_kN`.
- FACT (Division 3). Core section by zone (closed 12 x 8 m tube, openings ignored):

| Zone | t (m) | I_x (m4) | I_y (m4) | A_shear X / Y (m2) |
|---|---|---|---|---|
| 1-10 | 0.60 | 229.0 | 438.2 | 14.4 / 9.6 |
| 11-20 | 0.50 | 197.6 | 375.6 | 12.0 / 8.0 |
| 21-31 | 0.40 | 163.6 | 309.0 | 9.6 / 6.4 |

  Other Division 3 values: E = 35,000 MPa, Poisson 0.2 (G = 14,583 MPa), cracked factor 0.5, 14 perimeter columns with sizes by zone, and the 250 mm PT flat plate.
- FACT (Division 3 sanity values): T1 = 4.548 s (Y) and 3.304 s (X), both cracked. Gross values are 3.216 s (Y) and 2.336 s (X).
- FACT (`architecture/tower/verification/structure_inputs_for_B.json`): the core outer dimensions and wall-thickness zones used by the independent check.
- UNKNOWN: site, jurisdiction, seismic hazard (spectrum), site class, soil, governing code, importance class, ductility class.

## ASSUMPTIONS

All of these are ENGINEERING ASSUMPTIONS. The earthquake engineer of record must confirm them.

1. Base fixed at the ground slab, z = 0. This matches Division 3. The basement box, foundation and soil flexibility (SSI) are ignored. Soil is UNKNOWN; the geotechnical division must confirm.
2. The core is a stick on the plan centre (15, 12) m. Elements are elastic Timoshenko beams. Each element between levels k-1 and k takes the zone section of level k. The 0.5 cracked factor applies to EI, GA and GJ. The internal cross walls are excluded from stiffness. Openings and coupling beams are ignored, which overstates stiffness.
3. Torsional stiffness uses the Bredt closed-tube J = 4A0²t/p (454 / 392 / 324 m4 by zone). This is an upper bound: door openings make the core partly open-section, which is much softer in torsion.
4. The diaphragm is rigid in plane. Masses are lumped at 31 levels in X and Y. Rotational inertia is m(Lx²+Ly²)/12 for the 30 x 24 m plate, and the 12 x 8 m footprint at the plant level.
5. Reference model: the core alone resists lateral load, with perimeter slab-column frame action ignored. There is also a separately labelled VARIANT with frame action (item 3 under METHOD).
6. Response spectrum: elastic, 5 % damped, with no behaviour, R or q factor. Results are given per unit Sa (g). The SRSS of 3 modes assumes the same Sa for all three modes (constant-Sa assumption). A real design spectrum descends at long periods, so Sa(T1 ≈ 3.3-4.5 s) is much smaller than the plateau value. The higher modes (0.26-0.84 s) would usually sit on or near the plateau, at a much larger Sa than mode 1. The constant-Sa SRSS therefore understates the higher-mode share relative to a real spectrum. The per-mode coefficients below let any spectrum be applied.
7. P-Delta gravity is W_level (dead + 0.3 live), all on the sway system (rigid diaphragm).
8. Accidental eccentricity is 5 % of the plan dimension perpendicular to the load. This is common practice and must be verified against the code once the jurisdiction is known.

## METHOD

1. Configuration check (L1, JUDGMENT). See RESULTS.
2. Agent A: OpenSeesPy 3D stick model (`ndm 3, ndf 6`).
   - 31 `ElasticTimoshenkoBeam` elements, with geomTransf vecxz = global X. Sway in X uses I_y and A_shear_X. Sway in Y uses I_x and A_shear_Y.
   - Node 1 is fixed. Masses are in X, Y and RZ.
   - Eigen solution uses `-fullGenLapack` (all 93 mass modes).
   - Participation is computed as Γ = L/M_n and M_eff = L²/M_n per direction.
3. VARIANT (JUDGMENT, clearly labelled): perimeter flat-plate frame contribution.
   - Muto D-values for the 14 columns, with columns at 0.7 Ig and slab strips 0.35 x tributary width at 0.33 Ig.
   - Slab spans are column-to-column along the parallel faces, and facade-to-core across the perpendicular faces.
   - The frame is modelled as a second, translational-only stick tied to the core by equalDOF in X and Y.
4. Per unit Sa, for each mode n:
   - Sd = Sa·g/ω², u = Γφ·Sd, f = mΓφ·Sa·g.
   - From these: storey shear, base shear (= M_eff·Sa·g), base overturning moment Σf·z, roof (L30) displacement, and storey drift ratio Δu/h computed per mode.
   - Combination is SRSS of the first 3 modes per direction. The modes are well separated (ratio ≥ 2.4), so CQC ≈ SRSS.
5. P-Delta, two ways:
   - (a) Storey stability coefficient θ = P·Δ/(V·h) from the mode-1 and SRSS elastic results. This is independent of Sa in a linear analysis.
   - (b) OpenSees eigen solution after gravity with the PDelta transformation, θ_equiv = 1 - (T_lin/T_PΔ)². The ElasticTimoshenkoBeam in 3.7.1 did not add geometric stiffness (tested: T was unchanged). Step (b) therefore uses a matched flexure-only elasticBeamColumn pair (Linear vs PDelta).
6. Torsion screening:
   - Centre of mass vs centre of rigidity (core plus frame D-values).
   - Torsional period.
   - Static edge amplification for accidental eccentricity: 1 + e·c/r_k², with r_k = (ω_θ/ω)·r_m.
7. Verification (PROTOCOL §4/§10):
   - Hand model: exact stepped-cantilever flexibility (analytic integration) and a numpy eigen solve.
   - Closed form: uniform cantilever T_f = 2π/1.875²·√(m̄H⁴/EI) and T_s = 4H√(m̄/GA), combined by Southwell.
   - Equilibrium: static OpenSees run under the mode-1 forces.
   - Sensitivities: cracked factor 0.35 / 0.5 / 0.7 / 1.0, and mass ±10 %.
   - Agent B: a Rayleigh quotient. The sections are rebuilt from the B inputs. B deflects under the inertial pattern m·g·(z/H)^1.5 using numerical moment-area plus shear integration (20,000 steps), then takes the Rayleigh quotient on that deflection.
   - Agent C: `tools/verify_compare.py`, with tolerances T1 10 % and others 5 % (as in `pipeline.py`).

## CALCULATIONS

All values are SIMULATION (OpenSeesPy, verified) or CALCULATION. They come from `seismic.json`.

- Closed-form check (CALCULATION):
  - X: EI_avg = 6.51e9 kNm2 and GA_avg = 8.69e7 kN, with m̄ = 272 t/m. This gives T_f = 3.61 s and T_s = 0.70 s, so T = 3.68 s (+11 % vs 3.30 s).
  - Y: EI_avg = 3.42e9 and GA_avg = 5.79e7, giving T_f = 4.98 s and T_s = 0.86 s, so T = 5.05 s (+11 % vs 4.55 s).
  - The closed form runs long, as expected. Height-averaging under-weights the stiffer base zone, which dominates a cantilever, and the real mass tapers with height. The gap is within the 15 % screening tolerance.
- Hand stepped-cantilever (exact): T = 3.304 / 0.622 / 0.257 s (X) and 4.548 / 0.840 / 0.340 s (Y). OpenSees agrees to < 0.01 %, and Division 3 agrees to < 0.01 %.
- Unit check: V1 per g = M_eff × 9.81. For Y: 0.6144 × 27,053 t × 9.81 = 163,042 kN.
- Equilibrium (static OpenSees under the mode-1 forces): base reaction = applied force to 1e-9, base moment = Σf·z to 1e-9, and static roof displacement = modal roof displacement to 1e-6.
- Agent B (Rayleigh-Stodola) vs A:

| Quantity | A (OpenSees) | B (Rayleigh) | Rel. diff | Tol |
|---|---|---|---|---|
| T1 X (s) | 3.3039 | 3.3038 | 1.4e-5 | 10 % |
| T1 Y (s) | 4.5481 | 4.5480 | 1.4e-5 | 10 % |
| Mode-1 mass ratio X / Y | 0.616 / 0.614 | 0.616 / 0.615 | 0.11 % | 5 % |
| V1 per g X / Y (kN) | 163,395 / 163,042 | 163,579 / 163,226 | 0.11 % | 5 % |

  Comparator decision: **PROCEED**.
- P-Delta (Y, governing):
  - Storey θ from mode 1 is at most 0.093, at storey 16. The SRSS value is 0.093.
  - OpenSees PDelta: T1 rises from 4.480 to 4.673 s (+4.3 %), so θ_equiv = 0.081.
  - For X: θ storey max = 0.049, and OpenSees +2.2 %, θ_equiv = 0.043.
- Torsion screening:
  - The torsional period is 1.28 s (RZ mass ratio 0.81). ω_θ/ω_Y = 3.54 and ω_θ/ω_X = 2.58.
  - The edge amplification from accidental eccentricity is about 1.015 (Y loading, e = 1.5 m) and 1.018 (X loading, e = 1.2 m).

## RESULTS

**Configuration (JUDGMENT).**
- The plan is regular and doubly symmetric: a central core with 14 perimeter columns at symmetric positions. There are no re-entrant corners, transfers or floating columns in the tower as drawn.
- The flags are:
  - (i) The core is slender in Y (H/d = 11.8), and Y governs everything below.
  - (ii) The 4.5 m ground storey is taller than the 3.1 m typical storey. This creates a soft-storey risk for the frame only; the continuous core governs the lateral system.
  - (iii) Flat-plate slab-column connections are drift-sensitive (punching under imposed drift). This is a deformation-compatibility issue for the gravity frame.
  - (iv) The plant level is a small setback mass at the top (250 t). It shows no whip in the mode shapes, but the higher modes should be checked with a real spectrum.
  - (v) Core openings and coupling beams are not modelled.
  - (vi) Podium and basement transfer is unknown.
  - (vii) Pounding with neighbours is UNKNOWN (no site).

**Modal (SIMULATION, verified; core alone, cracked 0.5, fixed base).**

| Direction | T1 / T2 / T3 (s) | Mass ratio mode 1 / 2 / 3 | Sum of 3 |
|---|---|---|---|
| Y (governing) | 4.548 / 0.840 / 0.340 | 0.614 / 0.210 / 0.078 | 0.902 |
| X | 3.304 / 0.622 / 0.257 | 0.616 / 0.209 / 0.077 | 0.902 |
| Torsion RZ | 1.283 / 0.458 / 0.277 | 0.807 / 0.106 / 0.038 | 0.95 |

- The overall order is 4.55 s (Y), 3.30 s (X), 1.28 s (torsion), 0.84 s (Y2), 0.62 s (X2) and 0.46 s (RZ2). The modes are uncoupled because CM = CR.
- The first mode shape is flexural. Normalised to the plant level, it reads 0.005 / 0.07 / 0.19 / 0.35 / 0.55 / 0.76 / 1.0 at L1 / L6 / L11 / L16 / L21 / L26 / plant.
- **T1 matches the Division 3 sanity values (4.55 s Y, 3.30 s X) to < 0.01 %.** The closed form is +11 %.
- Over all modes, the effective masses sum to 1.000 in X, Y and RZ.

**Sensitivity of T1 (s).**

| Case | Y | X | Torsion |
|---|---|---|---|
| Cracked 0.35 | 5.44 | 3.95 | 1.53 |
| Cracked 0.5 | 4.55 | 3.30 | 1.28 |
| Cracked 0.7 | 3.84 | 2.79 | 1.08 |
| Gross 1.0 | 3.22 | 2.34 | 0.91 |
| Mass -10 % | 4.31 | 3.13 | 1.22 |
| Mass +10 % | 4.77 | 3.47 | 1.35 |

- T scales with √(mass) (±4.9 %) and with 1/√(cracked factor), so 0.35-0.7 spans roughly -15 / +20 %.

**VARIANT with perimeter flat-plate frame (JUDGMENT/SIMULATION, labelled).**
- Storey stiffness is about 6.0-6.6e4 kN/m in typical storeys and 7.6e5 kN/m at the fixed-base L1.
- T1 becomes 4.20 s in Y (-7.6 %) and 3.16 s in X (-4.4 %). The mass ratios are unchanged (0.62).
- The frame stiffens the tower only modestly. It cannot be relied on without punching and drift-compatibility checks.

**Demands per unit Sa (g)** (SIMULATION; elastic, core alone, Sa at the stated mode period, no R or q). W = 265.4 MN.

| Per 1.0 g | Y mode 1 | Y SRSS-3 (const. Sa) | X mode 1 | X SRSS-3 (const. Sa) |
|---|---|---|---|---|
| Base shear V (MN) | 163.0 (0.614 W) | 173.5 (0.654 W) | 163.4 (0.616 W) | 174.1 (0.656 W) |
| Base overturning M (MN·m) | 11,429 | 11,487 | 11,445 | 11,502 |
| Roof (L30) displacement (m) | 7.83 | 7.83 | 4.13 | 4.13 |
| Max storey drift ratio | 0.116 (storey 28) | 0.116 | 0.061 (storey 28) | 0.061 |

- The displacement-based quantities are better expressed per metre of spectral displacement Sd(T1), because Sd = Sa·g·(T/2π)²: 5.14 m per g in Y and 2.71 m per g in X. Per metre of Sd, roof = 1.52 m and max drift = 2.26 % in both directions.
- Per-mode coefficients per g, for use with any future spectrum, as (V MN; M MN·m; roof m; max drift):

| Mode | Y | X |
|---|---|---|
| Mode 1 | 163.0; 11,429; 7.83; 0.116 | 163.4; 11,445; 4.13; 0.061 |
| Mode 2 | 55.7; 1,124; 0.137; 0.0076 | 56.3; 1,124; 0.075; 0.0042 |
| Mode 3 | 20.6; 235; 0.012; 0.0012 | 20.7; 230; 0.007; 0.0007 |

  Combine them as √Σ(coefficient_n × Sa(T_n))².

**Illustration only** (Sa(T1) = Sa for the SRSS too; not a hazard statement):

| Sa (g) | V1 Y / X (MN) | M1 Y / X (MN·m) | Roof Y / X (m) | Max drift Y / X |
|---|---|---|---|---|
| 0.1 | 16.3 / 16.3 | 1,143 / 1,144 | 0.78 / 0.41 | 1.16 % / 0.61 % |
| 0.2 | 32.6 / 32.7 | 2,286 / 2,289 | 1.57 / 0.83 | 2.32 % / 1.22 % |
| 0.4 | 65.2 / 65.4 | 4,572 / 4,578 | 3.13 / 1.65 | 4.65 % / 2.44 % |

- JUDGMENT: these are elastic. A real spectrum would give Sa(4.5 s) far below its plateau.
- The elastic drift in Y reaches about 1 % already at Sa(T1) ≈ 0.09 g. The Y direction is drift-sensitive, consistent with Division 3's slenderness flag.
- Codes typically impose a minimum base-shear floor for long-period buildings, which may govern strength. Verify against the current code.

**P-Delta indication (CALCULATION + SIMULATION).**
- The elastic stability coefficient θ is at most 0.09 in Y (θ_equiv 0.08, with T1 elongating 4.3 %) and 0.05 in X.
- This is an indication only. Code formats amplify drift (C_d or q) and reduce shear (R or q), so the design θ depends on the code and ductility class. Y is close to commonly used thresholds (about 0.1, verify against code).
- P-Delta must be included in any design-level Y analysis.

**Torsion screening.**
- CM = (15.0, 12.0) m. CR of the core = (15, 12) m and CR of the frame = (15.0, 12.0) m, so the static eccentricity is 0 (CALCULATION).
- Torsion is not the first mode (T_θ = 1.28 s, far below T1).
- With 5 % accidental eccentricity, the static edge amplification is about 1.02. This rests on the Bredt closed-tube J; with door openings the core is much softer in torsion, which would raise the amplification. UNKNOWN until the core layout is fixed.

**Verification.** All 23 interpreter checks PASS. The comparator decision is **PROCEED**.

## CODE / STANDARD

- None applied. The jurisdiction is UNKNOWN, so no spectrum, importance factor, R/q/C_d, drift limit, θ limit, minimum base shear or accidental-eccentricity clause is used or cited. Every such value must be retrieved for the stated jurisdiction at its current edition (PROTOCOL §11). "Verify against current code."
- Methods are textbook structural dynamics only:
  - Modal superposition and SRSS.
  - Timoshenko cantilever.
  - Rayleigh quotient.
  - Muto D-value method for the frame variant.
- Requirement class of all values here: ENGINEERING ASSUMPTION.

## UNCERTAINTIES

- Hazard (UNKNOWN):
  - The spectral shape decides whether mode 1 or the higher modes govern shear. At long period Sa is small. At the plateau, modes 2-3 (0.26-0.84 s) carry a large part of the storey shear in the upper storeys.
  - The constant-Sa SRSS here is not a design spectrum result.
- Stiffness: the cracked factor gives T1 3.8-5.4 s in Y. Other unmodelled effects are core openings and coupling beams (softer), frame action (stiffer, -4 to -8 %), facade and partitions, and the basement and SSI (softer, soil UNKNOWN). Overall T1 uncertainty is about ±30 % (JUDGMENT).
- Mass is shared with Division 3, so a wrong mass would agree in A, B and the hand model. T scales with √m (±10 % mass gives ±4.9 % T).
- Torsional stiffness is an upper bound (closed tube). The real T_θ may be considerably longer, and its separation from the translational periods is not assured.
- The independence of agent B is about the method (different algorithm, sections rebuilt from the B inputs). The masses, the 0.5 factor and E are shared inputs.
- Elastic analysis only: no nonlinearity, hinge formation, higher-mode amplification of wall shear in inelastic response, or damping uncertainty.
- The frame-variant parameters (effective width, cracking) are JUDGMENT with a wide range.

## FAILED CHECKS

All 23 automated checks pass. The following are NOT CHECKED and may not be presented as passing:
- No hazard, site class or spectrum is available, so no design demand, drift-limit compliance or strength check exists.
- Core flexural, shear and coupling-beam capacity, boundary elements, and higher-mode wall shear amplification: NOT CHECKED.
- Slab-column punching under imposed drift (deformation compatibility of the PT flat plate and columns): NOT CHECKED. This is critical given an elastic drift of about 1 % at Sa(T1) ≈ 0.09 g in Y.
- Diaphragm forces, collectors and drag struts into the core, and podium/basement transfer diaphragm: NOT CHECKED.
- SSI, basement embedment, foundation rocking and the overturning uplift at the core base: NOT CHECKED (soil UNKNOWN).
- Core openings and torsional stiffness of the real core: NOT CHECKED. The Bredt J is an upper bound.
- Nonlinear (pushover or time-history) behaviour and performance-level assessment: NOT DONE. That is premature without hazard.
- Separation and pounding with neighbouring buildings: UNKNOWN (no site).
- Wind serviceability (likely to govern stiffness for a 4.5 s tower) is owned by the wind division and is NOT CHECKED here.

## RECOMMENDATIONS

1. Obtain the jurisdiction, site class and official hazard (spectrum) before any demand is used for sizing. Then re-run this script with Sa(T_n) from that spectrum, using the per-mode coefficients, CQC or SRSS, and the code's minimum base shear and drift checks.
2. Treat the Y direction as governing:
   - It is drift-sensitive, and P-Delta θ is close to 0.1.
   - Carry Division 3's Option B forward as the pre-planned upgrade: an outrigger/belt at the plant level and possibly at mid-height.
   - Alternatively, deepen the core in Y (8 m to about 10 m) or add short-face shear walls. This is a recommended architectural and structural configuration change for the architecture division.
   - Re-run the variant to quantify the gain.
3. Build an L3 3D model with wall panels and openings, coupling beams, the slab-column frame and the basement box with soil springs, once the geotechnical data exist. Compare its T1 with 4.55 s and investigate if the difference exceeds 30 %.
4. Include P-Delta in all Y-direction design-level analyses. Do not use ElasticTimoshenkoBeam with the PDelta transformation in OpenSeesPy 3.7.1 expecting geometric stiffness: it was found not to apply it. Use elasticBeamColumn, force-based elements, or explicit leaning columns.
5. Plan the detailing topics for the licensed designer (no sizes given here):
   - Core boundary elements and confinement.
   - Capacity-design shear for walls, including higher-mode amplification.
   - Ductile, diagonally reinforced coupling beams if openings couple the walls.
   - Punching shear reinforcement and integrity reinforcement at the slab-column connections for the imposed drift.
   - Collectors and diaphragm-to-core connections.
   - Lap splices outside the potential hinge zone at the core base.
   - Foundation anchorage of the core for overturning.
6. Define the intended performance levels with the client, e.g. life safety at the design event and collapse prevention at the maximum considered event, as the jurisdiction requires. No performance claim is made here, and the building must not be described as resistant to any earthquake without that hazard and assessment.

## REQUIRED HUMAN REVIEW

- A licensed structural/earthquake engineer in the project jurisdiction must review the model, boundary conditions, the cracked-stiffness and mass assumptions, and every conclusion before any use. These results are feasibility-stage aids, not a design.
- `bld-results-interpreter` and `bld-independent-verifier` should repeat the verification with independently derived masses. The agent-B check here shares the masses with A.
- The geotechnical engineer must review the fixed-base assumption once the site investigation exists.
- `bld-design-lead` must decide on the Y-direction stiffness upgrade (Option B or a deeper core) before the wave-2 lateral model is frozen.
