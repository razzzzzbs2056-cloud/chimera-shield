"""Task graph over the 111 subagent tasks, with resumable run state.

The orchestrator does not call language models itself. It decides *what is
ready*, produces task briefs for Claude Code agents, validates returned
findings and records progress in state/run_state.json so work can resume
after interruption. Parallelism is expressed as dependency "waves" chunked
by `max_parallel`; nothing guarantees all tasks in a wave run at once.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.agents.catalog import load_catalog, subagent_dependencies, subagent_index, topo_order
from src.common import STATE_DIR, load_json, utc_now, write_json

STATE_PATH = STATE_DIR / "run_state.json"
TASK_STATUSES = ("pending", "in_progress", "done", "blocked", "failed")


def waves(deps: dict[str, list[str]]) -> list[list[str]]:
    """Group tasks into levels: every task's dependencies lie in earlier levels."""
    level: dict[str, int] = {}
    for n in topo_order(deps):
        level[n] = 1 + max((level[d] for d in deps[n]), default=-1)
    out: list[list[str]] = [[] for _ in range(max(level.values()) + 1)] if level else []
    for n, lv in level.items():
        out[lv].append(n)
    return [sorted(w) for w in out]


def batches(wave_list: list[list[str]], max_parallel: int) -> list[list[str]]:
    if max_parallel < 1:
        raise ValueError("max_parallel must be >= 1")
    out = []
    for w in wave_list:
        for i in range(0, len(w), max_parallel):
            out.append(w[i:i + max_parallel])
    return out


@dataclass
class RunState:
    path: Path = STATE_PATH

    def load(self) -> dict:
        if self.path.exists():
            return load_json(self.path)
        deps = subagent_dependencies(load_catalog())
        return {"created_at": utc_now(), "updated_at": utc_now(),
                "tasks": {t: {"status": "pending", "history": []} for t in sorted(deps)}}

    def save(self, state: dict) -> None:
        state["updated_at"] = utc_now()
        write_json(self.path, state)

    def set_status(self, task: str, status: str, note: str = "", output: str | None = None) -> dict:
        if status not in TASK_STATUSES:
            raise ValueError(f"invalid status {status}")
        state = self.load()
        if task not in state["tasks"]:
            raise KeyError(task)
        if status == "in_progress":
            blockers = self.unmet_dependencies(task, state)
            if blockers:
                raise ValueError(f"{task} blocked by unfinished dependencies: {blockers}")
        t = state["tasks"][task]
        t["status"] = status
        if output:
            t["output"] = output
        t["history"].append({"at": utc_now(), "status": status, "note": note})
        self.save(state)
        return state

    def unmet_dependencies(self, task: str, state: dict | None = None) -> list[str]:
        state = state or self.load()
        deps = subagent_dependencies(load_catalog())
        return [d for d in deps[task] if state["tasks"][d]["status"] != "done"]

    def ready(self) -> list[str]:
        state = self.load()
        deps = subagent_dependencies(load_catalog())
        return sorted(
            t for t, v in state["tasks"].items()
            if v["status"] == "pending" and all(state["tasks"][d]["status"] == "done" for d in deps[t])
        )

    def summary(self) -> dict:
        state = self.load()
        counts = {s: 0 for s in TASK_STATUSES}
        for v in state["tasks"].values():
            counts[v["status"]] += 1
        return counts


def task_brief(sub_id: str) -> str:
    """Prompt text an operator (or Agent 00) gives a Claude Code agent for one task."""
    cat = load_catalog()
    s = subagent_index(cat)[sub_id]
    parent = next(a for a in cat["agents"] if a["id"] == s["parent"])
    return (
        f"You are acting as NEPAL 3T subagent {sub_id} ({s['name']}) under Agent {parent['id']} "
        f"({parent['name']}).\n"
        f"Read CLAUDE.md, .claude/agents/nepal3t-{parent['id']}-{parent['slug']}.md and src/agents/specs/{sub_id}.md.\n"
        f"Complete the task, write research/findings/{parent['id']}/{sub_id}-<task>.json, validate it with "
        f"`python -m src.cli validate-finding <file>`, then mark it done with "
        f"`python -m src.cli complete {sub_id} <file>`.\n"
        "Never invent data. If sources are inaccessible, mark items pending with the exact data required."
    )
