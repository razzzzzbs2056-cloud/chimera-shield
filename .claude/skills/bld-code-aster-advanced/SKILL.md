---
name: bld-code-aster-advanced
description: Plan and run advanced nonlinear, thermo-mechanical, modal or dynamic FE with Code_Aster (with MFront for custom material laws). Use only when CalculiX or OpenSees cannot answer the question, for example fire-exposed timber sections, concrete cracking, or coupled thermal-mechanical behaviour.
---

# Code_Aster (+ MFront)

**Status here:** not installed. Run it from the official container or Salome-Meca. Until it is installed, do not quote results.

## When it is justified
- Thermo-mechanical analysis of charring timber or heated steel nodes (fire design beyond tabulated methods).
- Concrete damage and cracking where the mechanism matters (e.g. squat core shear, anchorage zones).
- Large nonlinear models where validated element libraries matter.
Otherwise use hand methods, OpenSeesPy or CalculiX (analysis hierarchy, PROTOCOL.md §3).

## Workflow
1. Mesh in Gmsh or Salome (MED format), named groups for supports, loads and materials.
2. Command file (`.comm`): read mesh → define materials (`DEFI_MATERIAU`, or an MFront law via `DEFI_MATERIAU`/behaviour integration) → assign → boundary conditions → `STAT_NON_LINE` / `DYNA_NON_LINE` / `THER_NON_LINE` / `CALC_MODES` → post-process.
3. Run with `run_aster` (the export file lists inputs/outputs); view results in ParaView.

## Verify
Reproduce a published Code_Aster validation case with the same element/material first. Then mesh convergence, energy balance, hand comparison of the elastic stage, and calibration of any MFront law against test data (cite the tests).

## Limits
Steep learning curve; easy to produce converged nonsense. Results are SIMULATION and require a specialist reviewer.
