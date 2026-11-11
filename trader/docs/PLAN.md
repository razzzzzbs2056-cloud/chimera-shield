# Plan: six phases, each with a gate

| Phase | Deliverable | Gate to pass | Status (2026-11-10) |
|---|---|---|---|
| 1. Spec | `docs/SPEC.md` | Owner's five answers recorded | Done |
| 2. Architecture | `docs/ARCHITECTURE.md` | Every hard limit lives in code, none in a model | Done |
| 3. Plan | This file, `PROGRESS.md` | Phases have tests and a gate | Done |
| 4. Test-first build | `src/`, `tests/` | All tests green, lint clean | Done: 114 tests |
| 5. Review | Walk-forward versus BTC, final self-challenge, live paper pass on real data | Results reported as they are | Done: baseline does not beat BTC |
| 6. Ship | Docker image, Compose, runbook, branch pushed | Container healthy, restarts after a crash | Paper runtime verified in a container; production deploy needs owner approval |

## Next gates (owner decides)
| Step | Needs | Gate |
|---|---|---|
| A. Paper trading with the Haiku REFLEX | `ANTHROPIC_API_KEY` on the host | 30 days and at least 100 resolved decisions |
| B. Calibration review | Step A data | Brier score better than the base-rate forecast, out of sample |
| C. OKX demo trading | OKX demo keys | Testnet checklist in `docs/RUNBOOK.md` passes |
| D. Live, small | Trade-only keys, IP allowlist, written approval | Steps A to C passed, policy promoted to `live` by name |
