---
name: bld-building-physics
description: Building physics with EnergyPlus (energy, thermal comfort, overheating) and Radiance (daylight, glare), including how to replace toy models such as the façade perforation estimate with simulations. Use for envelope, façade, daylight, comfort or operational-energy decisions.
---

# Building physics (EnergyPlus + Radiance)

**Status here:** not installed. The façade "sun load vs uniform veil" number on the concept page is a toy model and must not be repeated as a performance claim until this workflow runs.

## Workflow
1. Climate: EPW weather file for the nearest station; add a future-climate file for overheating checks.
2. Geometry: simplified thermal zones from the IFC (one zone per use per orientation); shading surfaces for the copper veil (as a perforated layer with measured or calculated transmittance).
3. EnergyPlus (directly, through OpenStudio, or eppy): constructions from `data/materials.csv` (U-values, thermal mass), internal gains from the program, schedules, HVAC templates (heat pump, DCV with heat recovery). Outputs: annual heating/cooling, peak loads, hours above comfort limits.
4. Radiance (or Honeybee/Ladybug as a front-end): annual daylight (sDA/ASE or the metric the local code uses), glare for the hall and galleries, with the veil modelled geometrically.
5. Compare façade options with identical everything-else: uniform veil vs sun-driven gradient (the research question in `design-brief.md` §8).

## Verify
Weather file and location correct · zone areas match the IFC · envelope U-values hand-checked · simulation of a simple shoebox against hand heat-loss · daylight model reflectances and transmittances documented · sensitivity to occupancy and infiltration.

## Limits
Simulation accuracy depends on inputs and calibration; report ranges and state the code's required method where compliance is the goal.
