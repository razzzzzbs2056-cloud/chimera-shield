# trader

A two-layer crypto trading agent for OKX (spot and perpetual swaps), paper trading by default.

- **Code decides everything that matters:** thresholds, sizes, orders, stops, the kill switch.
- **A small model (the REFLEX) only judges:** on each closed candle it reads one numeric
  snapshot and returns a typed verdict. Code gates that verdict before any order.

**Status (2026-11-10):** paper runtime works on live OKX data and in Docker. The rule
baseline does **not** beat holding BTC in walk-forward tests. Nothing here is evidence of
an edge. Live trading is blocked until the owner approves. See `PROGRESS.md`.

## Quick start
```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
```
```bash
.venv/bin/pytest
```
```bash
.venv/bin/trader once
```
```bash
.venv/bin/trader dashboard
```
Then open http://localhost:8080. Docker: see `docs/RUNBOOK.md`.

## Where things are
| Path | What |
|---|---|
| `PROGRESS.md` | What is done, what is next, every decision and why. Read first |
| `docs/SPEC.md`, `docs/ARCHITECTURE.md`, `docs/PLAN.md` | Requirements, design, phases and gates |
| `docs/RESEARCH.md` | Market regime and the eight finalists |
| `docs/RUNBOOK.md` | Operating, alerts, testnet checklist, going live |
| `docs/results/` | Walk-forward results versus holding BTC |
| `config/default.yaml` | Mode, limits, costs, off-limits coins, setups |
| `policies/` | Versioned gate thresholds and the active pointer |
| `src/trader/web/` | Read-only web dashboard (`trader dashboard`, port 8080) |
| `src/trader/`, `tests/` | Code and 114 tests |
