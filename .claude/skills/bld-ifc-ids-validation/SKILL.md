---
name: bld-ifc-ids-validation
description: Write buildingSMART IDS information requirements and validate IFC models with IfcTester; also covers IfcOpenShell authoring rules and Bonsai for interactive editing. Use whenever an IFC model is created, received, or used to feed analysis, quantities or fire review.
---

# IFC + IDS validation

**Example in repo:** `architecture/bim/requirements_ids.py` writes `bim/pavilion.ids` and validates `chimera-pavilion-structure.ifc`. Five specifications: every column, beam, slab and wall has a material, `Pset_*Common.LoadBearing = TRUE`, a `FireRating`, and sits in a storey; storey names follow the brief. Tests check that a compliant model passes **and** a bare column fails.

## Workflow
1. Agree the requirements first: what the model must contain for its next use (analysis, quantities, fire, facilities).
2. Express them as IDS facets: `ids.Entity` (applicability), `ids.Attribute`, `ids.Property` (pset, name, data type, value or `ids.Restriction` enumeration/pattern), `ids.Material`, `ids.PartOf`, `ids.Classification`.
3. `spec.validate(ifcopenshell.open(path))`; read `spec.specifications[i].status`, `applicable_entities`, `failed_entities`.
4. Fix the model at its source (the authoring script or Bonsai), not by editing exported IFC by hand. Re-run.
5. Commit the `.ids` with the model so reviewers can repeat the check.

## IfcOpenShell authoring rules (learned here)
- Set units explicitly: `unit.assign_unit(m, units=[unit.add_si_unit(m, unit_type=t) for t in ("LENGTHUNIT","AREAUNIT","VOLUMEUNIT")])`; the default is millimetres.
- Check orientation of extruded members: beam depth must be vertical (test it from the geometry kernel's vertices).
- Use honest placeholders: `FireRating = "UNKNOWN - fire strategy pending"` passes "present" checks but stays visibly unresolved.

## Bonsai (BlenderBIM)
For people editing the model interactively; agents use IfcOpenShell scripts. Both write the same open IFC.

## Limits
IDS checks information, not engineering adequacy. A model that passes IDS can still be structurally wrong.
