---
name: bld-structural-precheck
description: Quick preliminary structural sizing and sanity check of a beam/floor in the architecture pack (bending, deflection, fire residual section). Use when a span, load or material changes in the design brief.
---

# Structural pre-check

1. Read loads from `architecture/data/live_loads.csv`, combinations from `load_combinations.csv`, limits from `deflection_limits.csv`.
2. Run `size_timber_beam(span_m, trib_width_m, dead_kpa, live_kpa, ...)` from `architecture/tools/quickcheck.py` (or extend it for steel/concrete with a test).
3. Do the hand check and show inputs, formulas and results. Compare with the tool.
4. List what is NOT checked (shear, LTB, vibration, connections, fire, seismic).
5. Update `design-brief.md` §5 only with numbers you actually computed. Run `python -m pytest -q architecture/tests`.
