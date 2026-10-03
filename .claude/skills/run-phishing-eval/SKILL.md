---
name: run-phishing-eval
description: Evaluate ChimeraShield detection quality (precision/recall, calibration, confidence intervals) on a labeled email set for one or more models. Use when changing a prompt or model, or asked "does it work / how accurate is it".
---

# Run a phishing detection evaluation

Owner: `detection-scientist`. Method is defined in `docs/chimera/06-system-design.md` §6.

1. **Data**: labeled emails as JSONL `{"id","email_content","sender","subject","label": 0|1,"source","category"}` in `eval/data/`. Include hard negatives (legit urgent invoices, password resets) and an injection set. Dedupe; split by time; never tune on the test split. Record license/provenance per source.
2. **Run** each candidate (`LLM_PROVIDER`/`LLM_MODEL`, temperature 0) over the test split through `get_provider()`. Run 3 times to measure nondeterminism. Cache raw outputs.
3. **Baselines** always included: URL/header heuristics, TF-IDF + logistic regression, and `ealvaradob/bert-finetuned-phishing` from the catalog.
4. **Report**: precision, recall, F1, PR-AUC, FPR at 90% recall, per-category table, parse-failure rate, p50/p95 latency, $/1k scans (or GPU-hours). All with 95% bootstrap CIs.
5. **Calibration**: reliability diagram + ECE for `risk_score`.
6. **Write** `docs/chimera/eval-reports/<date>-<model>.md`: setup (model id, commit, seed), results, failure examples, limitations. Do not claim anything the CIs don't support.
