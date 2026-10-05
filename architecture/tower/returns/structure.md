# Division 3 Structural Engineering: 30-storey residential tower, concept and preliminary sizing

Focus: Statics / Reinforced Concrete / Post-Tensioned Concrete / Core / Column / Slab / Shear Wall. Analysis hierarchy Level 1-2: load path plus hand calculations written as a script. CONCEPT ONLY. Not for construction. A licensed engineer must carry out the analysis before any size is fixed (PROTOCOL §8).

Script: `architecture/tower/calcs/structure_gravity.py` -> `architecture/tower/data/structure.json`. Tests: `architecture/tests/test_tower_structure.py` (9 passed).

## INPUTS USED

- FACT (project basis, `architecture/tower/basis.json`): 30 storeys above grade and 2 basements. Ground storey is 4.5 m, typical storeys are 3.1 m, roof slab is at 94.4 m and the rooftop plant is 5.0 m. Floor plate 30 x 24 m (720 m2). Central core 12 x 8 m. Residential live load 1.5-2.0 kPa, corridor 3.0 kPa, roof 1.5 kPa, SDL 1.0 kPa, partitions 0.5 kPa, facade 6.0 kN/m. All of these load values are ASSUMPTION ranges in the basis itself.
- FACT (repo data pack, `architecture/data/materials.csv`): Concrete C40/50 has fck = 40 MPa, E = 35 GPa and density 2450 kg/m3.
- FACT (repo data pack, `architecture/data/load_combinations.csv`): generic combination forms 1.35G + 1.5Q and 1.2D + 1.6L. Because the jurisdiction is unknown, both are used only as ASSUMPTION factors.
- UNKNOWN: site, jurisdiction, governing code, wind speed, seismic hazard, soil, ground water, survey. Nothing in this return depends on any of them.

## ASSUMPTIONS

Every value below is an ENGINEERING ASSUMPTION. The structural lead or licensed engineer must confirm each one once the jurisdiction and client brief are known. The full list is in the `assumptions` key of `structure.json`.

1. RC unit weight is 25 kN/m3, including rebar.
2. Live load is 2.0 kPa, the upper end of the basis range, with no live-load reduction (conservative). A 1.5 m corridor ring around the core takes 3.0 kPa. Inside the core, 60 % of the 12 x 8 m area has floor slab (the rest is lift/stair shafts), loaded at 3.0 kPa.
3. Roof slab loads: roofing SDL 1.5 kPa plus a smeared plant allowance of 2.0 kPa, with no partitions. The core-roof plant level at +5 m (z = 99.4 m) carries 5.0 kPa of tanks and lift machinery over 12 x 8 m.
4. Facade load is 6 kN/m on every suspended level L1-L30. The ground-storey facade bears on the ground slab and is excluded.
5. Load factors are the governing value of 1.35G + 1.5Q and 1.2G + 1.6Q (both generic). Column axial limit: N_Ed <= 0.45 fck Ac on the gross section. This leaves margin for moments, slenderness and seismic axial-load ductility limits. Minimum column size is 450 mm. Sizes are rounded up to 50 mm and stepped in zones L1-10, L11-20 and L21-30.
6. Core walls are 0.60 m (L1-10), 0.50 m (L11-20) and 0.40 m (L21-plant). There are 2 internal cross walls, 0.25 m thick, included in weight but not in stiffness. The core section is treated as a closed tube with openings ignored.
7. Seismic weight = dead + psi x live, with psi = 0.3 (generic; this is set by the governing code). Partitions count fully as dead load.
8. Stiffness: cracked factor 0.5 is applied to both EI and GA of the walls (generic range 0.35-0.7). Poisson's ratio 0.2. Base fixed at the ground slab, z = 0. Basement box, podium and soil-structure interaction are ignored. Flat-plate/column frame action is ignored, so the core alone resists lateral load.
9. Tributary areas use nearest-support allocation (Voronoi-type) on a 0.05 m raster. The core perimeter acts as a continuous support. Slab continuity factors are not applied, because flat-plate continuity can raise loads on columns next to edges by about 10-20 %. This is JUDGMENT.
10. Column loads are reported at the ground slab. Basement levels, B1-B2 slabs and the parking grid are not included; foundation loads must add them.

## METHOD

L1 load path (gravity and lateral):

```
GRAVITY                                         LATERAL (wind / earthquake)
PT flat plate 250 mm (two-way, no beams)        facade -> PT slab acting as a rigid diaphragm
   |                 |                                      |
   v                 v                                      v
perimeter RC columns   RC core walls (slab        RC core (12 x 8 closed tube, cantilever)
(14 no., stepped)      bears on the core)         [option B: outrigger -> perimeter columns]
   |                 |                                      |
   v                 v                                      v
ground slab / basement transfer -> foundations   basement box -> foundations (geotech UNKNOWN)
```

L2 hand calculations, as a script:

1. Grid: 14 perimeter columns. On the long faces they sit at x = 0 / 7.5 / 15 / 22.5 / 30. On the short faces they sit at y = 0 / 8 / 16 / 24, which lines up with the core faces. There are no interior columns: the core is 9 m (X) and 8 m (Y) from the facade, so the PT plate can span directly.
2. Slab thickness from span/depth. The governing span is core face to facade = 9.0 m. Textbook PT flat-plate L/d is 35-45, giving 200-257 mm, and 250 mm (L/36) was selected. A non-PT RC flat plate at L/d 26-30 would need 300-346 mm. These ratios are JUDGMENT and textbook values, not code clauses.
3. Tributary areas use raster nearest-support allocation. Facade lengths use nearest column along the perimeter.
4. Takedown, level by level: slab G + facade + column self-weight for each column; walls + core interior floors + core tributary slab for the core. Column sizes are iterated to convergence, since self-weight depends on size. The `quickcheck.factored_load_ec` function provides the 1.35G + 1.5Q value.
5. Seismic weight per level: floor loads, plus half of the storey-below and storey-above verticals, plus psi Q. The lower half of the ground storey goes to the base.
6. Lateral sanity check: cantilever flexibility with stepped EI(z) and GA(z), delta_ij = ∫ (zi-s)(zj-s)/EI ds + ∫ 1/GA ds, with 31 lumped masses and an eigenvalue solve of F M. The method is verified against the closed forms T = 2π/1.875² √(m̄L⁴/EI) (flexure), T = 4L√(m̄/GA) (shear), the tip-mass case and the Dunkerley bound (tests).

## CALCULATIONS

All values are CALCULATION from `structure_gravity.py`, verified by `test_tower_structure.py`.

- Area loads: typical G = 0.25 x 25 + 1.0 + 0.5 = 7.75 kPa and Q = 2.0 / 3.0 kPa. Roof G = 6.25 + 1.5 + 2.0 = 9.75 kPa and Q = 1.5 kPa.
- Tributary areas (sum = 624.0 m2 = 720 - 96, tested):

| Column | Trib. area (m2) | Facade (m) | G base (kN) | Q base (kN) | N_Ed (kN) | Size L1-10 / L11-20 / L21-30 (m) | N_Ed/(Ac fck) |
|---|---|---|---|---|---|---|---|
| Corner C (x4) | 15.00 | 7.75 | 5,804 | 893 | 9,174 | 0.75 / 0.60 / 0.45 | 0.41 |
| Short-face edge E_0_8 (x4), governing | 34.55 | 8.00 | 11,273 | 2,055 | 18,301 | 1.05 / 0.85 / 0.60 | 0.41 |
| Long-face edge E_7.5_0 (x4) | 30.50 | 7.50 | 9,964 | 1,815 | 16,173 | 0.95 / 0.80 / 0.55 | 0.45 |
| Long-face centre E_15_0 (x2) | 27.81 | 7.50 | 9,273 | 1,655 | 15,000 | 0.95 / 0.75 / 0.55 | 0.42 |
| Core | 248.2 + 57.6 interior | - | 127,484 | 22,097 | 205,249 | t = 0.60 / 0.50 / 0.40 | 7.9 MPa avg on 25.96 m2 |

- Hand check of E_0_8, typical level: G = 7.75 x 34.55 + 6 x 8.0 + 1.05² x 3.1 x 25 (L1-10 zone) = 267.8 + 48.0 + 85.4 = 401 kN, and Q ≈ 2.0 x 34.55 = 69 kN. Thirty levels of tapering column give G = 11,273 kN. The factored value 1.35 x 11,273 + 1.5 x 2,055 = 18,301 kN governs over the LRFD-form result of 16,816 kN. Required Ac = 18,301 / (0.45 x 40,000) = 1.017 m2, so b = 1.008 m, rounded up to 1.05 m.
- Equilibrium (tested to 1e-6): Σcolumns + core gives G = 254,192 kN and Q = 44,457 kN, equal to an independent whole-floor sum. The core carries 50 % of G.
- Core section (closed tube, gross). I_x is about the x-axis and resists sway in Y. I_y resists sway in X.

| Zone | t (m) | A (m2) | I_x (m4) | I_y (m4) | A_shear X / Y (m2) |
|---|---|---|---|---|---|
| L1-10 | 0.60 | 22.56 | 229.0 | 438.2 | 14.4 / 9.6 |
| L11-20 | 0.50 | 19.00 | 197.6 | 375.6 | 12.0 / 8.0 |
| L21-plant | 0.40 | 15.36 | 163.6 | 309.0 | 9.6 / 6.4 |

- Cracked base stiffness: EI_X = 7.67e9 kNm2, EI_Y = 4.01e9 kNm2, GA_X = 1.05e8 kN, GA_Y = 0.70e8 kN (E = 35,000 MPa, factor 0.5).
- Seismic weight per level (kN), L1 ... L30, plant: 9,962; 9,296 (L2-9); 9,005; 8,713 (L11-19); 8,423; 8,133 (L21-29); 9,559 (roof slab with plant); 2,452 (plant level). Masses in t are W/9.81 (sum tested).
- Hand check of period, Y direction: m̄ ≈ 27,053 t / 94.4 m = 287 t/m and EI ≈ 0.5 x 35e6 x 197.6 = 3.46e9 kNm2 (mid zone). T_f = 1.787 √(287 x 94.4⁴ / 3.46e9) = 4.6 s. The script gives 4.48 s (flexure only) and 4.55 s (flexure + shear), which agree.

## RESULTS

- System (JUDGMENT): the reference scheme is Option A, an RC core with 14 perimeter RC columns and a 250 mm PT flat plate. Option B (add an outrigger/belt) is the identified upgrade path. Option C (steel/composite) is not recommended for the reference scheme.

| Criterion | A: RC core + columns + PT flat plate | B: A + outrigger/belt at plant level (+ mid-height) | C: RC core + steel/composite floors |
|---|---|---|---|
| Span efficiency | 9 m flat plate, 250 mm, flat soffit | same | 9 m beams + deck, about 0.6 m floor zone |
| Weight / seismic mass | slab dead 6.25 kPa; W ≈ 265 MN | ≈ A + outrigger walls | slab ≈ 3.3 kPa; W roughly 25-30 % lower (JUDGMENT) |
| Lateral | core alone; slender in Y (H/d = 11.8) | engages columns; lower drift and core moment | core alone, lighter |
| Fire | inherent (cover); PT tendon cover critical | same | applied protection needed |
| Vibration / acoustics | good (mass) | good | light floors need checking (residential) |
| Carbon | high cement content; GGBS blend can mitigate | + outrigger concrete | higher steel A1-A3 per materials.csv |
| Buildability / cost | repetitive table/jump forms; PT specialist; cost UNKNOWN | outrigger floor complexity; shortening | fast erection; cost UNKNOWN |

- Grid: see `grid` in `structure.json` (14 columns, symmetric). The slab is a 250 mm PT flat plate, span/depth 36.
- Base column sizes (C40/50, gross N_Ed <= 0.45 fck Ac): corners 750 mm square (N_Ed 9.2 MN). The governing edge column (short face, y = 8/16) is 1,050 mm square (N_Ed 18.3 MN). Long-face edges are 950 mm (16.2 / 15.0 MN). All step down to 450-600 mm at L21-30. Blade columns, for example 600 x 1,750 mm, are an architectural alternative with equal area. JUDGMENT: C60 at the base would bring the governing column to about 950 mm.
- Core walls: 0.40-0.60 m range, stepped 0.60 / 0.50 / 0.40 m. The average factored gravity stress at the base is 7.9 MPa, which is low. Wall thickness will be set by lateral demand, shear and coupling beams, not gravity.
- W (seismic weight above ground, dead + 0.3 Q) = 265,389 kN, i.e. 27,053 t over 31 levels (`mass_t_per_level`, length 31). That is about 12.3 kPa per floor, plausible for RC residential (JUDGMENT). Total unfactored gravity at the ground slab is G 254.2 MN and Q 44.5 MN.
- Level heights z (m): 4.5, 7.6, ..., 94.4 (L30 roof slab), 99.4 (plant).
- T1_sanity_s = 4.55 s, Y direction, cracked 0.5, core alone. Other values: X is 3.30 s cracked; with gross section, Y is 3.22 s and X is 2.34 s. T2 (Y) is 0.84 s. CALCULATION, labelled SANITY. It is an upper-bound-type estimate, because the frame action of slab and columns, internal walls, the basement and the facade are all ignored. The earthquake division owns the dynamic analysis.
- Stiffness for wind scaling (cracked, core alone): roof-slab deflection is 3.02 mm (Y) and 1.59 mm (X) per 1 kN/m of uniform lateral line load. Illustrative only: 30 kN/m in Y gives about 91 mm, roughly H/1040. The wind division owns the pressures.

## CODE / STANDARD

- Jurisdiction is UNKNOWN, so no code clauses are cited or applied.
- Load-factor forms come from `architecture/data/load_combinations.csv` (EN 1990 6.10 form and ASCE 7 LRFD form). They are used as ENGINEERING ASSUMPTIONS and must be verified against the current code of the stated jurisdiction.
- Span/depth ratios, cracked-stiffness factor, psi = 0.3 and the 0.45 fck axial limit are textbook or generic practice values. Verify against the current code.
- Mechanics: textbook beam theory (Euler-Bernoulli + Timoshenko shear flexibility, cantilever eigenvalue 1.875104).

## UNCERTAINTIES

- Loads use the upper-bound live load (2.0 kPa) with no reduction, so the column loads are conservative by roughly 5-8 %. If the code requires higher corridor or balcony loads, or heavier facades (for example precast at 10+ kN/m), they would rise. Facade load sensitivity: +1 kN/m adds about 240 kN to a 30-storey edge column.
- Tributary method: Voronoi allocation does not capture flat-plate continuity or PT balanced-load redistribution. Edge columns next to the first interior support (the core) can carry 10-20 % more, and the core correspondingly less. An L3 FE plate model is needed.
- Columns: the 0.45 fck limit is a placeholder. Real sizes depend on the seismic axial-load ratio limits of the code, biaxial moments from slab edge/corner unbalanced moment, slenderness, and fire.
- Period: ±30-40 % (cracked factor 0.35-0.7, openings, coupling beams, frame action, basement flexibility, SSI with soil UNKNOWN). The gross-to-cracked range is 3.2-4.5 s in Y.
- Core geometry: a closed tube with openings ignored overstates stiffness. Coupled-wall behaviour across door openings is unquantified. Core position and layout come from the architecture division and may change.
- Basement/podium: unknown whether the tower columns continue straight down or need transfer to the parking grid.

## FAILED CHECKS

Not checked (cannot be done at L2 or lacks data). None of these may be presented as passing:
- Punching shear at edge and corner columns (high unbalanced moment). The flat-plate shear reinforcement and column-head detail are NOT CHECKED.
- PT design: tendon layout, balanced load, precompression, losses, SLS deflection (long-term), cracking, vibration. NOT CHECKED.
- Differential axial shortening between core and columns (elastic, creep, shrinkage) over 30 storeys, and its effect on slabs and facade. NOT CHECKED.
- Lateral design: drift, acceleration (occupant comfort), core flexure/shear capacity, coupling beams, overturning and tension at the core base. All need the UNKNOWN wind and seismic hazard. NOT CHECKED.
- Outrigger option B: not sized and NOT CHECKED.
- Transfer at the podium/basement (parking grid versus tower grid) and the basement retaining walls. NOT CHECKED.
- Fire resistance (cover and tendon cover for the required rating), robustness/disproportionate collapse (column-loss alternate path in the flat plate, structural integrity tendons/bars through columns), and connection ductility. All NOT CHECKED beyond the L1 statement that the core and the PT plate with integrity reinforcement give an alternate load path.
- Foundations: loads at ground only, and the soil is UNKNOWN. NOT CHECKED.
- Independent verification (PROTOCOL §10, agent B + `verify_compare.py`) has not been run yet.
- Flag: T1_sanity of 4.55 s and core slenderness H/d of 11.8 in Y mean the 12 x 8 m core alone is likely flexible for a 94 m tower. This is JUDGMENT. Drift and wind comfort may govern, and if they do, Option B or a larger/stiffer core becomes necessary.

## RECOMMENDATIONS

1. Adopt Option A as the reference scheme for the wave-2 earthquake and wind divisions. Use `structure.json` for z, masses, EI(z) and GA(z) by zone, and report results for both the cracked (0.5) and the gross case.
2. Keep Option B (outrigger/belt at the roof plant level, plus a possible mid-height outrigger) as a pre-planned upgrade. Ask architecture now whether a plant/refuge floor can be reserved at about L15. Also consider lengthening the core in Y (8 m to 10 m) or adding perimeter shear walls on the short faces.
3. Run an L3 linear FE model of the floor plate (OpenSeesPy or Gmsh + CalculiX) with PT equivalent loads to refine column reactions, punching, and the edge/corner column moments.
4. Run an L3 3D frame/wall model including slab-column frame action and coupling beams. Compare its period with this sanity value; a difference above 30 % should be investigated.
5. Commission the independent check (agent B, a different method such as an FE plate takedown) and compare it with `verify_compare.py`.
6. Do a shortening study (staged construction, creep) before freezing the facade joints and outrigger connections.
7. Ask the client for the jurisdiction, the geotechnical investigation and the basement parking grid. Several of the failed checks depend on these.

## REQUIRED HUMAN REVIEW

- A licensed structural engineer in the project jurisdiction must review the system choice, every ASSUMPTION listed above, the load factors and the code basis. No size in this return is a design size.
- The geotechnical engineer must review the foundation loads, basement box and SSI assumptions once the site investigation exists.
- A PT specialist / designer must review the slab thickness, punching and tendon layout.
- The structural lead (`bld-design-lead`) must review and accept the recommendation to carry Option B as a contingency and the core-slenderness flag before wave 2 freezes the lateral model.
