# CR-001 — Reconcile program area with geometry

| Field | Entry |
|---|---|
| Status | **proposed — needs client/architect decision** |
| WHAT CHANGED | Nothing yet. Options: (a) reduce program by ~730 m²; (b) add an L1 gallery ring inside the hall; (c) floor over part of the hall at L2 with a long-span structure |
| WHY | IFC model from the brief's geometry gives 3,456 m² GFA vs 4,188 m² program (−17.5 %) — SIMULATION, verified (`bim/make_ifc.py`, `tests/test_bim.py`) |
| REQUESTED BY | `bld-bim-coordinator`, `bld-red-team-reviewer` |
| STRUCTURAL IMPACT | (a) none; (b) adds mass and a second diaphragm level inside the void, may help collectors; (c) 24 m span floor at 4 kPa: heavy, changes hall roof concept |
| COST IMPACT | (a) lowest; (c) highest |
| CODE IMPACT | Occupant load and egress change with area |
| REQUIRED REANALYSIS | make_ifc.py, takeoff_reconcile.py, seismic_screen.py (mass), egress |
