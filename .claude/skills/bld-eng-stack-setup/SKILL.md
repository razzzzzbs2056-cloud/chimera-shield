---
name: bld-eng-stack-setup
description: Install and check the open-source engineering stack (OpenSeesPy, IfcOpenShell/IfcTester, Gmsh, CalculiX, pymoo, QGIS, FreeCAD, Code_Aster, EnergyPlus, Radiance) and report which tools are usable. Use at the start of any session that will run engineering analysis, or when a tool import fails.
---

# Engineering stack setup

**Rule:** a result produced by a tool that `check_stack.py` reports MISSING cannot be cited. Say the tool is unavailable instead.

## Steps
1. Python packages: `pip install -r architecture/env/requirements-engineering.txt`
   - IfcTester: if the `odfpy` wheel fails, run `pip install --no-deps ifctester xmlschema` (only the ODS reporter needs odfpy).
   - Gmsh Python API needs the system GL library: `apt-get install -y libglu1-mesa`.
2. System tools: see `architecture/env/system-packages.md` (CalculiX `calculix-ccx`, Gmsh CLI `gmsh`; QGIS, FreeCAD, Code_Aster, EnergyPlus and Radiance are large, so install them only when the task needs them).
3. Check: `python architecture/scripts/check_stack.py` writes `architecture/env/stack-status.json`.
4. Prove it works: `python -m pytest -q architecture/tests` (includes the OpenSeesPy, IDS, CalculiX and pymoo examples; they skip themselves when a tool is missing).

## Verified in this repo (2026-10)
numpy 2.4.6 · scipy 1.17.1 · openseespy 3.7.1.2 · ifcopenshell 0.9.0 · ifctester 0.9.0 · gmsh 4.15.2 · pymoo 0.6.2 · CalculiX 2.21. Not installed: QGIS, FreeCAD, Code_Aster, EnergyPlus, Radiance.

## Pitfalls seen here
- Installing several pip packages in one command: one failing wheel aborts all of them. Install separately.
- Libraries with silent unit defaults (IfcOpenShell assigns millimetres): always set units explicitly.
