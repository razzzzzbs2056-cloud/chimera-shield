# Seismic screening return: Chimera Pavilion (division 4, pipeline run)

## INPUTS USED
- Design basis: levels 5.5 / 9.7 / 13.9 m; two 8 x 8 m RC box cores, 0.4 m walls (design-brief.md, seismic_screen.py)
- Quantity take-off v0.1 (data/quantity_takeoff.csv) for seismic mass; materials.csv for densities and E

## ASSUMPTIONS
- [A] Cracked stiffness factor 0.5; seismic mass = dead + 0.3 x live; masses split equally to levels
- [A] Fixed base (no soil-structure interaction); rigid diaphragm for plan torsion
- [A] No hazard, site class or code applied: jurisdiction UNKNOWN

## METHOD
- Agent A: lumped-mass cantilever, flexure + shear flexibility, eigen solution (numpy)
- Simulation: same model in OpenSeesPy (ElasticTimoshenkoBeam, fullGenLapack)
- Results interpretation: plausibility checks listed under RESULTS
- Agent B (independent): Rayleigh quotient from the static deflection under an assumed inertial pattern (z/H)^1.5
- Independence: B uses a different method but the same input functions as A (method independence only); input data still need an independent check
- Agent C: tools/verify_compare.py with tolerances {"default": {"rel": 0.05}, "T1_s": {"rel": 0.1}}

## CALCULATIONS
- Agent A: T1 = 0.1237 s; W = 22296 kN; mode-1 mass ratio = 0.861
- OpenSees: T1 = 0.1237 s
- Agent B: T1 = 0.1237 s; W = 22296 kN; mode-1 mass ratio = 0.854
- Plan torsion (cores only): e/B = 0.24, edge amplification = 1.34

## RESULTS
- Comparator decision: PROCEED
- PASS: effective masses sum to 1
- PASS: T1 in plausible range for a squat core building (0.03-1.0 s)
- PASS: periods ordered T1 > T2 > T3
- PASS: shear deformation lengthens period
- PASS: OpenSees T1 within 1 % of hand model
- Configuration: torsionally irregular as drawn (CR-003 proposed); demand per unit Sa only

## CODE / STANDARD
- None applied: jurisdiction UNKNOWN. Method follows general structural dynamics (textbook level), not a code procedure.

## UNCERTAINTIES
- B and A share inputs, so a wrong input would agree in both
- Cracking factor (T1 0.09-0.18 s across 1.0-0.25), soil flexibility, diaphragm flexibility of CLT floors, mass distribution

## FAILED CHECKS
None

## RECOMMENDATIONS
- Adopt CR-003 before further seismic design; build the L3 3-D model with flexible diaphragms
- Obtain the site hazard and site class before any demand or capacity statement

## REQUIRED HUMAN REVIEW
- A licensed structural/earthquake engineer must review the model, assumptions and every conclusion before use
