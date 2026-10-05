---
name: bld-seismic-screening
description: Run and interpret the seismic screening model (masses, periods, modes, demand per unit Sa, plan torsion, OpenSeesPy cross-check) and extend it when the layout changes. Use for early earthquake configuration decisions.
---

# Seismic screening

1. Update inputs in `architecture/calculations/seismic_screen.py` (levels, cores, assumptions tagged [A]).
2. Run it and `python -m pytest -q architecture/tests/test_seismic_screen.py` (includes closed-form and OpenSeesPy checks).
3. Report periods with the cracking sensitivity, demand **per unit Sa** (never pick a hazard without a jurisdiction), and the torsion indicators (e/B, Ω, edge amplification) for every scheme considered.
4. State the limits: fixed base, rigid diaphragm, elastic, first mode. Escalate to an L3 3-D model when diaphragms are flexible or the plan is irregular.
5. Never call the building "earthquake proof"; state hazard and performance objective.
