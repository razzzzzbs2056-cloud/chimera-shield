---
name: bld-facade-art
description: Create or revise generative façade and ornament for the pavilion (seeded, sun-driven, parametric) and publish it as an interactive concept page. Use when the user asks for artistic patterns, façade design, or visual concept pages.
---

# Generative façade art

1. Read `architecture/art/algorithmic-philosophy.md` and `architecture/art/pavilion-concept.html` (the working example).
2. Decide the driving quantities (sun incidence, view, structure grid, privacy) and write the rule. Add a seed so output is reproducible.
3. Load `anthropic-skills:algorithmic-art` for method and `artifact-diagramming` for plan/section drawings; use `anthropic-skills:theme-factory` if a new palette is needed.
4. Edit the HTML (single file, no external assets beyond Google Fonts), keep both light and dark themes working, and keep it usable at 400 px width.
5. Verify headlessly (render in Chromium, check console errors and horizontal overflow), then publish with the Artifact tool, passing the existing URL to update in place.
6. Label every number as toy-model or sourced from `architecture/data/`. Never present a toy result as a simulation.
