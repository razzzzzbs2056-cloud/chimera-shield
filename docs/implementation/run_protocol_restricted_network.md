# Run protocol — restricted network (research round r1)

Use this protocol when the environment can search the web but cannot download from data-source hosts
(curl / WebFetch to nrb.org.np, worldbank.org, imf.org, gov.np, etc. fail).

## What an agent does for each assigned subagent task

1. Read `CLAUDE.md`, your agent definition in `.claude/agents/`, and `src/agents/specs/<ID>.md`.
   Read upstream findings in `research/findings/` for your dependencies, if present.
2. Use **WebSearch** to locate the exact primary documents that answer each question, preferring higher
   tiers of `research/sources/source_catalog.yaml` (Nepal official → IMF/WB/ADB → UN system …).
3. Record each document as a **source lead** in the finding's `source_leads` list:
   `{"url", "title", "publisher", "source_id" (catalog id if any), "contains"}` — `contains` says which
   table, series, indicator and period the document holds. Leads never carry numbers.
4. **No numbers from search snippets or memory, anywhere** — not in `claims`, `summary`, `specific` or notes.
   Search snippets are not retrieved evidence. Empirical findings are `type: "pending"`, `value: null`,
   with the exact data required. Years, fiscal-year labels, series codes and table numbers are fine.
5. You *may* record: research design and method, definitions and known methodological issues
   (e.g. fiscal vs calendar year, rebasing, coverage), labelled `assumption` items, and `challenges` to
   other agents — all without empirical numbers.
6. Fill every subagent-specific field in `specific` with a structured description of what will populate it
   and its status (`"pending"`), the method, and the lead URLs it depends on.
7. Write `research/findings/<AGENT>/<ID>-r1.json` (`task_id: "r1"`) and run
   `python -m src.cli validate-finding <file>` until it prints `valid`.
8. Do **not** run `start`/`complete`, edit config, state, reports or other agents' files, or commit.
   The orchestrator marks tasks and commits.

Once network access is available: `python -m src.cli leads --fetch` downloads every lead (raw bytes
hashed), values are extracted and ingested (`ingest-csv`), and round r2 replaces pending items with
observations.
