---
name: bld-freecad-parametric
description: Parametric geometry, drawings and IFC exchange in FreeCAD (headless FreeCADCmd scripts, BIM and FEM workbenches). Use for parametric grids, massing, repetitive components, 2D drawing sheets, or a CalculiX front-end with a GUI.
---

# FreeCAD parametric

**Status here:** not installed. The coordination IFC is generated with IfcOpenShell (`architecture/bim/make_ifc.py`); use FreeCAD when drawings or interactive parametric editing are needed.

## Workflow
1. Keep parameters in one place (a spreadsheet object or a Python dict mirrored from `design-brief.md`: grid 8 m, levels, hall 24 × 24 m).
2. Script geometry with `FreeCADCmd script.py`: Part/BIM objects (Wall, Structure, Floor), named by element type and grid reference.
3. Export IFC4 (BIM workbench) and validate it with `bld-ifc-ids-validation` before anyone uses it.
4. Drawings: TechDraw pages for plans/sections from the 3D model; dimensions from model geometry, never typed.
5. FEM workbench can drive CalculiX for quick component checks; still verify per `bld-fe-gmsh-calculix`.

## Verify
Round-trip the IFC (FreeCAD → IfcOpenShell audit): counts, volumes, storeys, units; dimensions on drawings match parameters.

## Limits
Large assemblies get slow; IFC export fidelity depends on object types. Drawings from FreeCAD are not certified documents.
