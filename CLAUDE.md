# Repository notes

This repository holds two unrelated projects:

- `backend/`, `frontend/`, `app/`: the ChimeraShield cybersecurity MVP. See `README.md`.
- `trader/`: a crypto trading agent (paper trading by default), custom engine.
- `trader-freqtrade/`: the same rule strategy rebuilt on the open-source freqtrade bot
  (dry run by default). See `trader-freqtrade/README.md`.

## When working on `trader/` or `trader-freqtrade/`

Read `trader/PROGRESS.md` first, every session, and update it before you finish. It lists
what is done, what is blocked, and every design decision with its reason.

Rules that hold for all trading work:

- Never place live orders, move funds, or handle exchange keys with trading rights
  without the owner's explicit go-ahead in that session.
- Never print or commit a key. Secrets live only in `trader/.env` (git-ignored).
- Hard risk limits stay in code (`trader/src/trader/risk/engine.py`); no model output may
  relax them.
- Run `cd trader && .venv/bin/pytest` before committing changes there.
- For `trader-freqtrade/`: run `python -m pytest tests` in an environment with freqtrade
  installed; `config.json` must keep `dry_run: true` and empty keys.
