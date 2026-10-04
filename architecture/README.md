# Architecture & Construction Pack

Agents, skills, data and tools for designing and engineering buildings, kept separate from the ChimeraShield app.

| Piece | Where |
|---|---|
| Agents (`bld-*`, lead = `bld-director`) | `.claude/agents/` |
| Skills (`bld-*`) | `.claude/skills/` |
| Design brief: *The Chimera Pavilion* | `design-brief.md` |
| Reference data (12 CSVs) | `data/` |
| Art: philosophy + interactive concept page | `art/` (live page: https://claude.ai/artifact/LzZ4CjjUCeCNzjWLxutW8m) |
| Poster: *Perforated Light* (PNG + PDF, philosophy, source) | `art/poster/` |
| Calculators (beam sizing, embodied carbon) | `tools/quickcheck.py` |
| Engineering protocol (evidence tags, verification, safety rule) | `PROTOCOL.md` |
| Engineering report v0.1 (29 sections), change records, risk register | `reports/` |
| Seismic screening (hand model + OpenSeesPy check), take-off reconciliation | `calculations/` |
| IFC4 coordination model + audit (IfcOpenShell) | `bim/` |
| Tool cards, data sources, failure precedents | `references/` |
| Stack check, pinned environment, system tool notes | `scripts/check_stack.py`, `env/` |
| FE example (Gmsh + CalculiX), optimisation (pymoo), IDS rules | `models/`, `calculations/optimise_lateral.py`, `bim/requirements_ids.py` |
| World precedents: 65 landmark buildings, principles, lessons → actions, interactive atlas (https://claude.ai/artifact/9SZzsYiHdoWwEv8ZCHmmqH) | `references/world-precedents.*`, `art/precedent-atlas.html` |
| Tests | `tests/` (`python -m pytest -q architecture/tests`) |

Start with `claude --agent bld-director`.

## Data files
`materials` (mechanical, thermal, carbon, biogenic, fire) · `live_loads` · `load_combinations` · `deflection_limits` · `soils` · `mep_benchmarks` · `climate_zones` · `codes_standards` · `space_program` · `cost_model` · `programme_phases` · `quantity_takeoff`.

## Honest limits
Values are typical and indicative, from general engineering knowledge, and have not been checked against current code editions or manufacturer EPDs. Costs have no absolute prices. Use for concept and feasibility only; stamped design by licensed professionals is required before construction.
