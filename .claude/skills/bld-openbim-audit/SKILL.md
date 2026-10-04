---
name: bld-openbim-audit
description: Regenerate the IFC coordination model with IfcOpenShell, audit geometry and quantities, and reconcile take-off and carbon. Use after any geometry or program change.
---

# openBIM audit

1. Edit geometry constants in `architecture/bim/make_ifc.py` to match the design brief.
2. Run `python architecture/bim/make_ifc.py` (writes the IFC and `audit.json`) and `python architecture/calculations/takeoff_reconcile.py`.
3. Run `python -m pytest -q architecture/tests/test_bim.py` (metres, footprint, analytic volumes, vertical beam depth, counts).
4. Report: element counts, volumes by material vs take-off, GFA vs program, carbon change. Any mismatch is a finding with a change record (`architecture/reports/change-record-template.md`).
5. Placeholder member sizes are ASSUMPTIONS: never quote them as quantities for pricing.
