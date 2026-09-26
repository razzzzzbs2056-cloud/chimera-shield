---
name: evidence-research
description: NEPAL 3T research workflow for any subagent task — retrieve primary sources, record observations with provenance, label facts vs assumptions, and write a schema-valid finding. Use whenever a NEPAL 3T agent researches a question.
---

# Evidence research (NEPAL 3T)

1. `python -m src.cli brief <SUBAGENT_ID>` and read `src/agents/specs/<SUBAGENT_ID>.md`.
2. Check dependencies: `python -m src.cli next` must list the task. Then `python -m src.cli start <ID>`.
3. For each question, find the primary source in priority order (`research/sources/source_catalog.yaml`).
   - Machine-readable series: use `src.data.ingest.fetch_worldbank` / `fetch_imf` (raw bytes are hashed and kept).
   - Documents (PDF/Excel from NSO, NRB, MoF, NEA…): save the table as `period,value` CSV plus a metadata
     JSON (`source_id, source_url, document_title, publication_date, variable, unit, recorded_by`) and run
     `python -m src.cli ingest-csv <csv> <meta.json>`.
   - Academic papers: cite each paper individually (authors, year, title, DOI/URL) in the finding's `source_ids`
     notes; register numbers from it as observations with `source_id: academic`.
4. If a source is unreachable: record a `pending` finding stating the exact series, source and period needed.
   Do **not** fill the gap with remembered or estimated numbers.
5. If two sources disagree beyond tolerance, keep both observations and describe the definitional,
   coverage, vintage or methodological reason in `challenges` or `data_gaps`.
6. Write `research/findings/<AGENT>/<ID>-<task>.json` with: `subagent_id, task_id, generated_at, summary,
   findings[{claim, type: fact|estimate|assumption|pending, value, unit, period, observation_ids, source_ids}],
   data_gaps, assumptions, challenges, uncertainty, specific{…required fields…}`.
7. `python -m src.cli validate-finding <file>`; fix every problem; `python -m src.cli complete <ID> <file>`.
