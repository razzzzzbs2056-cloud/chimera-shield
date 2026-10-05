# CR-003 — Add lateral elements at the south ends of the floor wings

| Field | Entry |
|---|---|
| Status | **proposed — required before further structural design** |
| WHAT CHANGED | Two lateral elements at about (4, 28) m and (44, 28) m: small cores, CLT/RC shear walls, or braced bays, each ~half a core's stiffness |
| WHY | Cores only at the north edge: e = 7.6 m (24 % of plan depth), Ω = 1.09, south-edge displacement 1.34× average (CALCULATION, `calculations/seismic_screen.py`). With the new elements: e = 0.4 m, Ω = 1.38, amplification 0.99 |
| REQUESTED BY | `bld-seismic-engineer`, `bld-red-team-reviewer` |
| STRUCTURAL IMPACT | Removes torsional irregularity, shortens diaphragm spans in both wings, gives the wings their own lateral support during erection |
| COST IMPACT | Adds two elements and foundations; reduces drift-related façade and connection cost; not a value-engineering candidate |
| CODE IMPACT | Likely removes a torsional irregularity classification (verify in the applicable seismic code) |
| REQUIRED REANALYSIS | seismic_screen.py (scheme B becomes base case), L3 model, foundations, architecture plans, IFC |
