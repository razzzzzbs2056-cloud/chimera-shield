# Division 7 Wind Engineering: 30-storey residential tower, structural wind loads, response, vortex shedding, comfort

Focus: Structural Wind Loads / Along-Wind Response / Cross-Wind Response / Vortex Shedding / Facade Loading / Comfort / Wind-Tunnel Data Interpretation. Analysis level L1-L2 (hand calculation as a script). CONCEPT ONLY, not for construction. Site, terrain, jurisdiction and wind standard are UNKNOWN, so every result is parametric in the basic speed (35, 45, 55 m/s). Script: `architecture/tower/calcs/wind_tower.py` -> `architecture/tower/data/wind.json`. Tests: `architecture/tests/test_tower_wind.py` (11 passed).

## INPUTS USED

- FACT (project basis, `architecture/tower/basis.json`): 94.4 m to roof slab, 5.0 m plant above (top 99.4 m), plate 30 x 24 m, central core 12 x 8 m. Wind speed, site and jurisdiction are UNKNOWN there; results are requested for 35, 45 and 55 m/s.
- FACT (structural division, `architecture/tower/data/structure.json`, CALCULATION labelled SANITY): core-alone cantilever periods T1 (cracked, factor 0.5) = 4.55 s in Y and 3.30 s in X; gross section 3.22 s in Y and 2.34 s in X. Zone core inertia and shear area (I_x, I_y, A_shear_X/Y for L1-10, L11-20, L21-31), E = 35 GPa, Poisson 0.2, levels z, base fixed at ground. The earthquake division is refining the periods in parallel; sensitivity to period is shown.
- Axis convention (JUDGMENT, from the structure data): wind on the 30 m face blows along Y and excites the flexible Y sway (I_x = 163-229 m4, T1 = 4.55 s cracked); wind on the 24 m face blows along X (I_y, T1 = 3.30 s cracked).
- UNKNOWN: basic wind speed, averaging time and return period, terrain category, topography, neighbouring buildings, wind standard, damping, tuned-mass options, comfort criterion, plant/parapet geometry.

## ASSUMPTIONS

All are ASSUMPTION, drawn from generic textbook/standard forms; verify against the applicable wind standard. None is a clause citation.
1. Air density 1.25 kg/m3 (1.2-1.25 typical).
2. The nominal speed V (35, 45, 55 m/s) is read as a roughly 3-s gust speed at 10 m. The mean-hourly-type speed is V/1.5 (gust ratio 1.5, textbook range about 1.4-1.6). If V were already a mean speed, loads rise by about 2.25 (sensitivity run below).
3. Mean speed profile: power law V(z) = (V/1.5)(z/10)^0.20 for z >= 10 m, constant below 10 m (suburban-type terrain). No topography, shielding or channelling factors (all 1.0).
4. Turbulence intensity I(z) = 1/ln(z/z0) with z0 = 0.5 m, evaluated at z_s = 0.6H = 59.6 m (I = 0.21). Integral length L(z) = 300(z/200)^0.5 m = 164 m at z_s.
5. Net along-wind force coefficient Cf = 1.3 (windward about +0.8 plus leeward about -0.5) for a rectangular prism of plan ratio about 0.8 to 1.25; roughness, corner-shape and interference effects ignored. Plant (94.4-99.4 m) modelled as the core footprint, 12 m wide for Y wind and 8 m for X wind.
6. Dynamic response: Davenport-type gust factor G = 1 + 2 I sqrt(gB^2 B^2 + gR^2 R^2) applied uniformly to the mean pressure, gB = 3.5, gR = sqrt(2 ln(nT)) + 0.577/sqrt(2 ln(nT)) with T = 600 s, background B^2 = 1/(1 + 0.9((b + h)/L)^0.63), resonant R^2 = (pi/4 zeta) S E with a von Karman-type gust spectrum E and a size-reduction S. Critical damping zeta = 1.5 percent (strength level; no measured damping; real value could be 1-2.5 percent). First mode treated as one equivalent static load shape.
7. Serviceability wind taken as 0.7 of the basic speed (shorter return period; the real ratio depends on the code and hazard curve). Peak acceleration crude formula uses this speed.
8. Strouhal number St = 0.12 for the rectangular section, range 0.08-0.15 shown.
9. Structure: core alone resists wind, fixed at ground (z = 0), stepped EI(z) and GA(z) from structure.json, cracked factor 0.5 and gross both shown; frame action, basement and soil flexibility ignored (as in the structural division).
10. Wind loads act only above ground level z = 0 (no basement exposure). Torsion, eccentric and corner-wind load cases not evaluated.

## METHOD

1. Velocity pressure q = 0.5 rho V^2 (hand check) and the profile q(z) = 0.5 rho V(z)^2 (CALCULATION).
2. Mean along-wind line load w(z) = q(z) Cf b(z); equivalent static peak load = G w(z) (CALCULATION, Davenport-type form, textbook rank 5). Base shear and overturning moment about the ground slab by integration at 0.1 m resolution.
3. Deflection by Euler-Bernoulli plus Timoshenko shear flexibility on the stepped core section: curvature M/EI and shear strain V/GA integrated from the base. Interstorey drift ratio = (y_i - y_(i-1))/h_i including rotation. Verified against the closed form w L^4 / 8EI (tests).
4. Vortex shedding: V_cr = f1 b / St = b/(T1 St), with b the plan width across the wind. Cross-wind sway of the 30 m face wind case occurs in X (T1 = 3.30 s, b = 30 m); cross-wind sway of the 24 m face wind case occurs in Y (T1 = 4.55 s, b = 24 m). V_cr compared with the mean speed profile.
5. Comfort: crude along-wind resonant acceleration a = (2 pi/T)^2 x_mean 2 gR I R, with the mean top deflection x_mean at the serviceability speed (INDICATION only, along-wind only; no cross-wind or torsional contribution).
6. Verification: q hand values, V^2 scaling, closed-form mean base shear, cantilever closed form, V_cr formula (tests).

## CALCULATIONS

Velocity pressure at 10 m (nominal V, hand check): q = 0.5 x 1.25 x V^2 = 766 Pa (35 m/s), 1266 Pa (45), 1891 Pa (55). Hand check for 45 m/s at 94.4 m: V = (45/1.5) x (9.44)^0.2 = 30 x 1.567 = 47.0 m/s, q = 0.5 x 1.25 x 47.0^2 = 1381 Pa (script 1381 Pa). Profile q(z) uses the mean-type speed V/1.5, so q(10 m) is 562 Pa at V = 45 (nominal 1266 Pa divided by 1.5^2).

Mean-type velocity pressure q(z) [Pa] (CALCULATION):

| z (m) | 10 | 20 | 40 | 60 | 80 | 94.4 | 99.4 |
|---|---|---|---|---|---|---|---|
| V = 35 | 340 | 449 | 592 | 697 | 782 | 835 | 853 |
| V = 45 | 562 | 742 | 979 | 1152 | 1292 | 1381 | 1410 |
| V = 55 | 840 | 1109 | 1463 | 1721 | 1930 | 2063 | 2106 |

Gust factor G (cracked period, 45 m/s): 3.04 for the 30 m face case (T = 4.55 s; background B^2 = 0.56, resonant R^2 = 1.54) and 2.81 for the 24 m face case (T = 3.30 s). Period sensitivity at 45 m/s (30 m face): G = 2.72 (T = 3.18 s), 3.04 (4.55 s), 3.30 (5.91 s). 24 m face: 2.55 (2.31 s), 2.81 (3.30 s), 3.05 (4.30 s). A stiffer building attracts a lower G but a higher mean load share.

Peak equivalent static base shear V_b [MN] and overturning moment M_b [MNm] about ground, cracked stiffness (gross in brackets):

| V (m/s) | 30 m face V_b | 30 m face M_b | 24 m face V_b | 24 m face M_b |
|---|---|---|---|---|
| 35 | 6.4 (5.8) | 355 (323) | 4.8 (4.4) | 263 (243) |
| 45 | 11.6 (10.4) | 640 (576) | 8.5 (7.7) | 470 (427) |
| 55 | 18.6 (16.6) | 1030 (921) | 13.6 (12.3) | 752 (677) |

Mean (static) parts at 45 m/s: 30 m face 3.8 MN and 211 MNm; 24 m face 3.0 MN and 167 MNm. The mean part scales exactly with V^2 (tested); G does not, because the reduced frequency changes with speed. Resultant arm M_b/V_b about 55 m. For scale: building weight W = 265 MN (structure.json), so V_b/W is about 2.4 to 7 percent over the range. Sensitivity if V were already a mean speed (45 m/s, cracked): V_b = 30.2 MN and M_b = 1672 MNm (30 m face), 22.1 MN and 1221 MNm (24 m face); top deflection 1126 mm and 432 mm.

Top deflection y_top (mm, at 99.4 m), H/y ratio (H = 99.4 m), maximum interstorey drift as 1/n. Load = full basic-speed equivalent static load:

| V | 30 m face cracked | 30 m face gross | 24 m face cracked | 24 m face gross |
|---|---|---|---|---|
| 35 | 239 (H/416), 1/312 | 109 (H/915), 1/685 | 93 (H/1069), 1/805 | 43 (H/2314), 1/1743 |
| 45 | 431 (H/230), 1/173 | 194 (H/513), 1/384 | 166 (H/598), 1/450 | 76 (H/1316), 1/991 |
| 55 | 693 (H/143), 1/107 | 310 (H/321), 1/240 | 266 (H/373), 1/281 | 120 (H/830), 1/625 |

Same at the assumed serviceability speed 0.7 V (cracked, top H/y, max interstorey 1/n): 30 m face 35 m/s: H/944, 1/707; 45 m/s: H/531, 1/398; 55 m/s: H/333, 1/249. 24 m face: H/2381, H/1358, H/858 for 35, 45, 55 m/s (interstorey 1/1794, 1/1023, 1/647). Maximum interstorey drift occurs near L27-L28 (core thinning plus rotation accumulated below).

Vortex shedding V_cr = b/(T1 St), cracked stiffness. Mean speed at roof (99.4 m) for 35, 45, 55 m/s nominal: 36.9, 47.5, 58.0 m/s.

| Case | T1 (s) | b (m) | St | V_cr (m/s) | Nominal V at which V_cr is reached at the roof |
|---|---|---|---|---|---|
| Wind on 24 m face, Y sway | 4.55 | 24 | 0.08 / 0.12 / 0.15 | 66.0 / 44.0 / 35.2 | 62.5 / 41.7 / 33.3 |
| Wind on 30 m face, X sway | 3.30 | 30 | 0.08 / 0.12 / 0.15 | 113.5 / 75.7 / 60.5 | 107.6 / 71.7 / 57.4 |

Gross-section values (T1 = 3.22 s in Y) are in `wind.json`: V_cr = 62.2 m/s at St 0.12 for the 24 m face case, reached at the roof at a nominal 58.9 m/s, i.e. slightly above the range. Hand check: 24/(4.548 x 0.12) = 43.97 m/s (tested). For the 24 m face case the height at which V_cr is reached (St 0.12, cracked) is 68 m at 45 m/s nominal and 25 m at 55 m/s; at 35 m/s the roof mean speed (36.9 m/s) is below V_cr.

Comfort indication (INDICATIVE, along-wind resonant only, zeta = 1.5 percent, serviceability speed 0.7 V, cracked): 30 m face: 11.5, 23, 40 milli-g at 35, 45, 55 m/s; 24 m face: 7.5, 15, 27 milli-g. Gross section: 30 m face 8.7, 18, 32; 24 m face 5.6, 12, 21 milli-g.

## RESULTS

- CALCULATION: Equivalent static peak base shear over the parametric range 35-55 m/s is 6.4-18.6 MN (30 m face) and 4.8-13.6 MN (24 m face) for cracked stiffness; overturning moment about the ground slab 355-1030 MNm and 263-752 MNm. Gross stiffness lowers G and these by about 10 percent. These are the figures to hand to `bld-structural-engineer` as a range, with the stated G and Cf. The 30 m face wind case (flexible Y sway) governs.
- CALCULATION: Top deflection at basic-speed load is H/416 to H/143 (30 m face, cracked) and H/1069 to H/373 (24 m face, cracked). Against a commonly used order of magnitude of about H/500 for wind drift (JUDGMENT, verify against the project criterion, which is normally set at a shorter return period), the 30 m face cracked case exceeds that order at the full basic-speed load at all three speeds (H/416, H/230, H/143). At the assumed serviceability speed 0.7 V it passes at 35 and 45 m/s (H/944, H/531) and fails at 55 m/s (H/333). Interstorey drift at 0.7 V is 1/707, 1/398 and 1/249 for 35, 45, 55 m/s, against a common order of 1/400-1/500 (JUDGMENT, verify): borderline at 45 and failing at 55 m/s. The 24 m face case passes everywhere at 0.7 V.
- JUDGMENT: The core-alone system is flexible in Y (T1 about 4.5 s, H/d = 11.8). Wind drift and acceleration, not strength, are likely to govern the 30 m face direction at 45 m/s and above. Outrigger or stiffer core (structural division Option B) would shorten the period and cut deflection roughly in proportion to stiffness gain.
- CALCULATION and JUDGMENT: Vortex shedding. For wind on the 24 m face, V_cr = 44 m/s (St 0.12) for Y sway at 4.55 s, which is a roof-height mean speed reached at about 42 m/s nominal basic speed, i.e. inside the 35-55 m/s range and reached at far more frequent winds than the extreme (nominal 33-63 m/s across St 0.15-0.08). Lock-in or cross-wind resonance is therefore a CREDIBLE concern in the Y direction and cannot be dismissed. For the 30 m face wind case (X sway) V_cr = 76 m/s (60-114 over the St range) is at or above the roof speed at 55 m/s nominal (58 m/s mean at roof), so lock-in there is unlikely at the design speeds but not excluded at St 0.15. Slenderness H/sqrt(BD) = 3.7 means the cross-wind spectral peak is moderate; the total cross-wind response and base moment were NOT quantified (needs aerodynamic data).
- JUDGMENT: Occupant comfort at these periods (3.3 and 4.5 s) is important: peak acceleration indication 12-23 milli-g for the 30 m face at 45 m/s serviceability-level wind (cracked and gross), above a residential criterion of order 10-15 milli-g (10-year; JUDGMENT, verify). Cross-wind and torsion would add. Flag as a risk.
- Wind-tunnel recommendation (JUDGMENT): REQUIRED at design stage for this tower, as a high-frequency force balance (HFFB) test at least, with a pressure/cladding test if facade design is to be optimised. Reasons: flexible slender core-only system (T1 4.5 s, H/d 11.8), credible cross-wind resonance near the design range, comfort risk for residential use, unknown site context (neighbours, topography). Not required at feasibility stage to size the concept; the code static method gives the preliminary loads here. CFD with OpenFOAM is not installed here (skill bld-eng-stack-setup); CFD supplements but does not replace code methods or tunnel testing for tall buildings; use only as a pedestrian-level wind and site-screening aid after the site is known.
- Pedestrian wind and facade loading: not computed (NOT CHECKED). Qualitative risk: corner acceleration and downwash at a 99 m tower with a 4.5 m podium-level entrance; a canopy or screens at the entrance and corner chamfers/setbacks are the usual mitigation (JUDGMENT). Facade cladding pressures need local coefficients from the applicable standard or tunnel.

## CODE / STANDARD

- UNKNOWN: governing wind standard. No clause numbers are quoted. Every coefficient and form above is a generic textbook-type ASSUMPTION (rank 5, established textbook methods: power-law profile, Davenport gust-response, Strouhal shedding, Euler-Bernoulli/Timoshenko cantilever). Verify against the applicable wind standard once the jurisdiction is known, including its basic wind speed definition (averaging time, return period), terrain categories, topographic, directional and importance factors, dynamic-response procedure, drift and acceleration limits, and the conditions that mandate wind-tunnel testing for tall or flexible buildings.
- The mapping of 35/45/55 m/s to the local code basic speed is itself unknown; the model reads them as about 3-s gust speeds at 10 m.

## UNCERTAINTIES

- Speed definition: reading V as a mean speed rather than a 3-s gust changes loads by about 2.25 to 2.6 (sensitivity run). The largest single uncertainty.
- Terrain and exponent (alpha 0.20, z0 0.5 m): urban terrain would reduce speeds and loads but raise turbulence; open terrain would raise them (HIGH).
- Cf = 1.3: plausible range about 1.1-1.5 (plus or minus 15 percent on load); not a pressure-integration from distributions.
- Gust factor method: simplified single-mode and uniform-G, plus or minus 20 percent; ignores mode shape and higher modes.
- Period: structural sanity values, plus or minus 30-40 percent (cracked factor, frame action, basement, SSI). Deflection is directly proportional to 1/EI (so cracked-to-gross doubles deflection) and G moves by about 10 percent.
- Damping: 1.5 percent assumed, no measurement. Acceleration varies roughly as damping^-0.5 to damping^-1, so 1 percent vs 2.5 percent changes the indication by more than 30 percent.
- Strouhal number range 0.08-0.15 widens V_cr by a factor 1.9; the cross-wind verdict depends on St and on whether aerodynamic modifications (corners) are applied.
- Wind-load direction and torsion, interference from neighbours, topographic speed-up, and uplift/pressure distributions are not covered.
- Deflection ignores slab-column frame action and shear-wall stiffness of perimeter elements; it is therefore conservative.

## FAILED CHECKS

- Wind drift at the basic-speed load: top deflection H/416 to H/143 for the 30 m face case (cracked) fails an order-of-magnitude H/500 test (JUDGMENT, verify) at all three speeds; at 0.7 V it fails only at 55 m/s (H/333); with gross stiffness H/915 to H/321 (the 55 m/s case fails).
- Interstorey drift at 0.7 V, 30 m face cracked: 1/249 at 55 m/s against an order of 1/400-1/500 (JUDGMENT, verify) fails; 1/398 at 45 m/s is borderline.
- Comfort indication fails at 45 and 55 m/s for the 30 m face (cracked): 23 and 40 milli-g against about 10-15 milli-g (JUDGMENT, verify).
- Vortex shedding: lock-in speed V_cr (44 m/s at St 0.12, Y sway, wind on 24 m face) lies inside the design speed range; the cross-wind concern is not screened out.
- No pass-fail check against a code could be made: site and code UNKNOWN.
- Not checked: facade cladding pressures, canopy and pergola uplift, pedestrian wind comfort at corners and entrances, torsion, cross-wind and torsional base moments, fatigue, along-wind response of the plant screens.

## RECOMMENDATIONS

1. Obtain jurisdiction, site, terrain and topography; replace the parametric range with the code-based speed and category; rerun `wind_tower.py` (all inputs are constants at the top of the script).
2. Treat Y-direction stiffness as a design driver: ask `bld-structural-engineer` to evaluate Option B (outrigger/belt at the plant level and possibly mid-height), a longer core in Y (8 m to 10 m) or perimeter walls on the short faces, and report the revised EI(z), T1 and mass so wind can be rerun.
3. Commission wind-tunnel testing at the design stage (HFFB for overall loads, cross-wind and torsion, plus acceleration at the project damping; add pressure taps for the facade and entrance/pedestrian-level study). Include the real surroundings.
4. Design the plan for aerodynamic mitigation options while the architecture is still open: chamfered or recessed corners, a stepped or tapered profile, openings through plant levels; these reduce cross-wind excitation and corner acceleration.
5. Define the comfort criterion with the client (return period, residential limit) and a damping assumption with a range (1, 1.5, 2.5 percent); evaluate a tuned mass or liquid damper only if the tunnel shows an exceedance.
6. CFD (OpenFOAM, not installed here, see skill bld-eng-stack-setup) only as a supplement for pedestrian-level wind screening after the site is known and with validation; it does not replace code methods or the tunnel for this tower.
7. Use the base shear and moment ranges above as placeholder lateral loads for `bld-structural-engineer` with the explicit caveat that they are a generic parametric range.

## REQUIRED HUMAN REVIEW

- Licensed structural/wind engineer to confirm the wind standard, basic speed, terrain, load combinations and drift and acceleration criteria; none of the numbers here is a design value.
- Review of the assumed gust-ratio reading of V (3-s gust vs mean) before any number is carried into the structural model.
- Independent verification (A/B/C per PROTOCOL section 10) of the base shear and deflection by a different method; the inputs from `structure.json` are shared, so a wrong structural input would agree twice.
- Wind-tunnel laboratory scope and brief to be approved by the client's design team; peer review of tunnel results.
- Facade, canopy, pergola and pedestrian-wind design to be assessed separately once the architecture and site are fixed.
