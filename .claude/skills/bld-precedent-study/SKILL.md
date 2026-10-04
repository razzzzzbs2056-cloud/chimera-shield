---
name: bld-precedent-study
description: Study world-class architecture precedents for a design question (long-span timber roof, perforated façade, seismic hybrid, passive cooling, etc.), extend the precedent library, rebuild the interactive atlas, and turn lessons into owned actions. Use when the user asks about the best buildings in the world or when a design move needs precedents.
---

# Precedent study

Agent: `bld-precedent-researcher`.

## Steps
1. **Frame the question** narrowly (e.g. "how have timber gridshells over 20 m been braced and maintained?").
2. **Search the library**: `architecture/references/world-precedents.csv` (65 buildings, tags: structure, seismic, timber, gridshell, shell, facade, perforation, light, climate, passive, earth, brick, cautionary...). The atlas page filters by theme and era.
3. **Add missing precedents** with every field: id, name, place, year, designers (architect and engineer), typology, structure, materials, climate_light, innovation, lesson_for_pavilion, tags (include one era tag: historic, modern or contemporary).
4. **Verify** facts before citing (PROTOCOL.md evidence ranking). Keep the source note on the atlas until entries are verified.
5. **Analyse**: mechanism, cost or failure, transferable lesson, limits of transfer.
6. **Act**: add rows to the "Lessons → actions" table in `world-precedents.md` with an owner agent and status, and raise a change record if the design changes.
7. **Rebuild and test**: `python architecture/art/build_atlas.py`; `python -m pytest -q architecture/tests/test_precedents.py`; republish the atlas page with the Artifact tool to the same URL.

## Quality bar
Breadth across eras, cultures, climates and budgets (a mud-brick school can teach as much as a supertall). Include failures and repairs of famous buildings. No invented numbers.
