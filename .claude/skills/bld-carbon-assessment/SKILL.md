---
name: bld-carbon-assessment
description: Estimate embodied carbon (A1-A3) and biogenic carbon from a quantity take-off using the architecture pack's materials data, with ranges and stated scope. Use when comparing structural or material options.
---

# Embodied carbon assessment

1. Edit/copy `architecture/data/quantity_takeoff.csv` (unit must be `m3` or `kg`; material names must match `materials.csv`).
2. Run `python architecture/tools/quickcheck.py` or call `embodied_carbon(path)`.
3. Report low–high ranges, kgCO₂e/m² GFA, and the biogenic figure separately, never netted against emissions.
4. State scope: which modules (A1–A3 only here) and which elements are missing (insulation, MEP, finishes).
5. For option comparison, build identical-program baselines (all-concrete, all-steel, hybrid), and replace `materials.csv` ranges with product EPDs where available.
