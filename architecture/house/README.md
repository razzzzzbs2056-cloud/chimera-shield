# The Garden House: 3-bedroom concept

Interactive 3D model: `three-bed-house-3d.html` (live: https://claude.ai/artifact/oAp8FoRXUcPKdwmsdSXUMr).

| Item | Value |
|---|---|
| Type | Single-storey family house |
| Internal area | 150 m² (15.0 × 10.0 m), plus 25.2 m² covered terrace |
| Bedrooms | 3 (main 21.0 m² with ensuite 5.8 m² and walk-in robe 6.2 m²; bedrooms 2 and 3 13.7 m² each with built-in robes) |
| Bathrooms | Family bathroom 6.2 m², ensuite, powder room 2.7 m² |
| Living | Living and dining 33.5 m², family nook 15.0 m², kitchen 9.6 m² with island and pantry |
| Other | Entry 8.4 m², hallway 7.9 m², laundry 3.6 m² |
| Heights | 2.7 m ceilings; 25° gable roof, 0.6 m eaves |

Assumptions: flat site, street on one side, garden facing the sun (south in the northern hemisphere, north in the southern). Wall and room dimensions are concept-level. Not for construction: a real house needs a site survey, planning and building code checks, structural and energy design, and a licensed designer or architect.

Checks: `python -m pytest -q architecture/tests/test_house.py` verifies the 14 rooms tile the footprint exactly (150.0 m², no overlaps), there are 3 bedrooms, and room sizes meet basic livability thresholds.
