---
name: bld-model-verification
description: Verify any structural, geotechnical or BIM model before its results are used (geometry, units, boundary conditions, loads, mass, mesh, equilibrium, modes, period, drift, hand-calc comparison, sensitivity). Use whenever a model or script result will appear in a report.
---

# Model verification

Run every check in `architecture/PROTOCOL.md` §4 and record PASS/FAIL with evidence:
1. **Geometry**: bounding box and key dimensions vs drawings.
2. **Units**: check library defaults (IfcOpenShell defaults to mm; OpenSees has no units).
3. **Boundary conditions** represent the real supports.
4. **Loads** and **mass**: totals equal hand totals.
5. **Mesh**: refine until results change < 2–5 %.
6. **Equilibrium**: reactions = applied loads.
7. **Modes/period/drift**: physically plausible; compare to closed forms.
8. **Hand calculation** of at least one governing result.
9. **Sensitivity**: vary each uncertain input (cracking, mass, stiffness, damping, soil springs).
Write the test into `architecture/tests/` so the check runs forever. A result that fails any check is labelled "SIMULATION (unverified)".
