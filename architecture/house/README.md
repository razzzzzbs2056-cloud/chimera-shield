# The Garden House: 3-bedroom concept

Interactive 3D model: `three-bed-house-3d.html` (live: https://claude.ai/artifact/BoSYoze2aNs1XeM1DRRFeg).

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

---

# The Lantern House: 3-storey concept

Interactive 3D model: `lantern-house-3d.html` (live: https://claude.ai/artifact/1v1kqhF6DAvrzD8DCEoMtq).

| Floor | Rooms | Area |
|---|---|---|
| Ground (+0.0) | Entry, study/guest room, library nook, guest WC, utility, kitchen, 6.4 m double-height living, dining; garden deck | 120.0 m² |
| First (+3.2) | Bedroom 2 with interior window over the living room, Bedroom 3, family bath, family lounge (sliding walls), balcony | 94.2 m² |
| Second (+6.4) | Main bedroom, ensuite, studio; 45.6 m² roof garden with pergola | 74.4 m² |
| **Total** | 3 bedrooms, study, studio, 2 bathrooms + WC, lift shaft | **288.6 m²** + 79 m² outdoor |

Design moves and their sources (see the table on the page and `references/world-precedents.csv`, tag `house`): Maison de Verre and Villa Müller (double-height glass living), Villa Savoye and Casa Barragán (ribbon windows, roof garden), Fallingwater and Robie House (balcony, deep horizontal shading), Villa Mairea (timber stair screen), Rietveld Schröder House (sliding walls), Glass House (solid service cores), Villa Rotonda (one proportion system), Moriyama House and Katsura (outdoor rooms on every level). Farnsworth House is used as a warning: big glass needs shading and ventilation.

Checks: `architecture/tests/test_lantern_house.py` (each floor tiles 120 m², 3 bedrooms, 288.56 m², stair/lift/bathrooms stack, void over living) and `test_pages_syntax.py` (all 3D pages parse).

Not for construction: needs a site, planning and code checks (stairs, guards, fire escape from upper floors), structural and energy design, and a licensed architect.
