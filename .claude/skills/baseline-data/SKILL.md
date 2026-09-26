---
name: baseline-data
description: Build or extend Nepal's verified baseline — attempt API retrieval, ingest official tables manually with provenance, and report pending items. Use for Phase 2 data work or when reports/baseline shows PENDING items.
---

# Baseline data

1. `python -m src.cli baseline --online` — tries the cross-check series in `src/data/requirements.py`.
   Failures are recorded, not hidden, and the requirement stays PENDING.
2. For Nepal-official primary sources, download the publication, extract the table to a
   `period,value` CSV (state fiscal-year labelling in `notes`), write a metadata JSON, and run
   `python -m src.cli ingest-csv data.csv meta.json`.
3. Add a new requirement to `src/data/requirements.py` (variable, unit code, owner subagent,
   primary source, optional API series) before collecting a new series.
4. `python -m src.cli validate` checks every observation for missing-source problems and duplicates;
   conflicts between sources are listed for investigation, not resolved automatically.
5. Ask Agent 15A to verify retrieved values (status `verified` requires `verified_by`).
6. `python -m src.cli report` updates `reports/baseline/baseline_report.md` and `data_gaps.md`.
