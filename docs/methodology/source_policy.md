# Source and evidence policy

1. **Hierarchy** (tier 1 highest): Nepal official statistics and ministries → IMF/World Bank/ADB → UN system,
   ILO, UNCTAD, WTO → foreign governments and central banks → IEA and energy authorities → ICIMOD and climate
   science → academic and reputable independent analysis. Catalog: `research/sources/source_catalog.yaml`.
2. **Provenance.** Every value is an `Observation` with source id, URL, document title (for documents),
   publication date and/or data vintage, retrieval time and method, and the SHA-256 and path of the raw file.
3. **Statuses:** `pending` (no value allowed) → `retrieved` → `verified` (checked by 15A/28A, `verified_by`
   recorded) · `disputed` · `superseded`. The store is append-only.
4. **No substitution.** When a source is inaccessible, the item stays pending with the exact data required.
   A language model's recollection of a number is not evidence.
5. **Disagreement.** `find_conflicts` lists same-variable, same-period values that differ beyond tolerance.
   Both are kept; Agent 00B records the investigation of definitions, coverage, vintage and methodology.
6. **Projections vs outturns.** IMF WEO and similar databases mix outturns and projections; notes say so and
   projections must never be reported as historical data.
7. **Catalog URLs** were recorded from general knowledge and are marked `endpoint_status: unverified` until a
   retrieval succeeds.
