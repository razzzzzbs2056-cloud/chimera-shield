# Running the platform

```bash
pip install -r requirements.txt
python -m pytest
python -m src.cli first-run          # add --offline to skip network attempts
```

Orchestration loop (Agent 00 or a human operator):

```bash
python -m src.cli plan               # state/plan.md — dependency waves in batches of max_parallel
python -m src.cli next               # tasks ready now
python -m src.cli brief 10C          # prompt for a Claude Code agent
python -m src.cli start 10C
python -m src.cli complete 10C research/findings/10/10C-t1.json
python -m src.cli status
```

`state/run_state.json` persists task status so an interrupted run resumes where it stopped. Commit `state/`
to carry progress across ephemeral environments. Claude Code can dispatch ready tasks in parallel with the
Agent tool; platform limits decide how many actually run at once.

Human approvals (`state/approvals.json`) are recorded only by named humans via
`src.orchestrator.approvals.record_approval`; code paths that act outside the repository call
`require_approval` first.
