---
name: bld-opensees-modelling
description: Build, verify and run OpenSeesPy models (modal, linear static, response spectrum, pushover, time-history, soil-structure springs, isolation) following the analysis hierarchy. Use when a structural or earthquake question needs more than a hand calculation.
---

# OpenSeesPy modelling

**Example in repo:** `architecture/calculations/seismic_screen.py` → `verify_with_opensees()` (lumped-mass cantilever, elastic Euler-Bernoulli and Timoshenko beams). Its periods match the hand model to < 0.1 %; test `test_opensees_agrees_with_hand_model`.

## Before modelling
- State the question and the lowest analysis level that answers it (PROTOCOL.md §3). Do not run L5/L6 to impress.
- Fix a unit system and write it at the top of the script (this repo: kN, m, t, s). OpenSees has no units.

## Build
1. `ops.wipe(); ops.model("basic", "-ndm", 2|3, "-ndf", 3|6)`.
2. Nodes, `fix` supports. Restrain DOFs that carry no mass when using eigen on small lumped models, or use `ops.eigen("-fullGenLapack", n)`; the default ARPACK solver fails on very small systems ("could not build an Arnoldi factorization").
3. Elements: `elasticBeamColumn` (bending only), `ElasticTimoshenkoBeam` (bending + shear: use for squat walls/cores), `forceBeamColumn` with fibre sections for nonlinear frames; shells for walls only when needed.
4. Masses at nodes (`ops.mass`), consistent with the gravity load case used for P-delta.
5. Damping: Rayleigh or modal, state the ratio and the modes it is anchored to.
6. Ground motions: jurisdiction-consistent selection and scaling; record the source (e.g. PEER NGA) and scaling method.

## Verify (all, recorded in the report)
Geometry and units · boundary conditions · total mass vs hand total · reactions = applied loads · mode shapes plausible · T1 vs closed form or simplified model · drift plausible · convergence and time-step study (nonlinear) · sensitivity of cracking, damping, mass, soil springs. Put the comparison into `architecture/tests/`.

## Limits
OpenSees performs no code checks and will converge to wrong answers when material models, damping or BCs are wrong. Results are SIMULATION and need a licensed engineer's review for design.
