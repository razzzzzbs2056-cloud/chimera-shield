---
name: run-scenario
description: Define, evidence, validate and run a NEPAL 3T geopolitical or domestic stress scenario (S01–S10 or new ones) without inventing shock magnitudes. Use when working on scenarios/ or the scenario engine.
---

# Scenario workflow

1. Scenario files live in `scenarios/{domestic,geopolitical,compound}/<ID>.yaml`. Required fields are
   listed in `src/scenario_engine/engine.py::REQUIRED_FIELDS`; `not_a_forecast: true` and
   `audits_required: ["15", "28"]` are mandatory.
2. Each shock names a channel from `src/geopolitical_model/channels.py` and a variable. `magnitude` stays
   `null` until an evidence-backed estimate exists; then list the supporting observation ids in `evidence`.
   A number without evidence is allowed only with `illustrative: true`, and results are labelled ILLUSTRATIVE.
3. Link exposures (`research/global_exposure/exposure_register.json`) via `exposure_refs`.
4. Compound scenarios list `components`; identical component shocks are counted once and conflicting
   ones are left unresolved for 16C/00C — never summed.
5. `python -m src.cli validate`, then `python -m src.cli scenarios`, `python -m src.cli audit`,
   `python -m src.cli report`.
6. Address household, regional, sectoral and fiscal impacts under `impact_dimensions`, plus responses,
   second-order effects, uncertainty and limitations. Do not assign probabilities.
