---
name: bld-fe-gmsh-calculix
description: Component-level finite-element analysis with Gmsh (meshing) and CalculiX (solver): stresses, deflections, connections, orthotropic timber, contact. Use when a beam, node, plate or connection needs more than a hand calculation and the question is local, not global.
---

# Gmsh + CalculiX

**Example in repo:** `architecture/models/calculix_beam/run_beam.py`: 8 m glulam joist 240 × 680 mm, service UDL 22.8 kN/m, transfinite hex mesh (C3D8I), isotropic and orthotropic timber.
Results: isotropic FE 17.07 mm vs Timoshenko 17.12 mm (0.3 %); orthotropic FE 18.63 mm vs 18.88 mm (1.3 %); load 182.4 kN = reactions 182.4 kN. Lesson: shear deformation adds ~12 % in timber (G ≈ 650 MPa), and knife-edge supports add 3.5 mm of local crushing that a real bearing check must handle separately.

## Workflow
1. Question and hand estimate first (quickcheck.py or textbook formula).
2. Geometry and mesh in Gmsh Python API: `occ.addBox` / CAD import, `setTransfiniteCurve/Surface/Volume` + `setRecombine` for hexes; read nodes/elements with `gmsh.model.mesh.getNodes/getElements` and write the `.inp` yourself (keeps node sets and ordering under control; hex8 ordering matches CalculiX C3D8).
3. Elements: C3D8I (bending with linear hexes), C3D20R (quadratic; check node ordering if exporting from Gmsh), shells S8R for plates.
4. Materials: `*ELASTIC` (isotropic) or `*ELASTIC,TYPE=ENGINEERING CONSTANTS` (E1,E2,E3,ν12,ν13,ν23,G12,G13 / G23) for timber; align axis 1 with the grain (`*ORIENTATION` if not global x).
5. Loads as consistent nodal loads or `*DLOAD`; supports that match reality (bearing plates, not knife edges, when local stress matters).
6. Run `ccx -i job`; parse `job.dat` (`*NODE PRINT`, `*EL PRINT`) or view `job.frd` in CalculiX GraphiX / ParaView (via converters).

## Verify
Reactions = applied loads · result vs hand formula · mesh convergence (halve element size until change < 2 %; the repo test runs a coarse and a fine mesh) · local artefacts identified (support crushing, load singularities) · sensitivity to material constants (timber G and E⊥ vary widely).

## Limits
Linear elastic unless you add nonlinear material/contact. No code checks. Timber connection behaviour needs test-based or code values, not elastic FE alone.
