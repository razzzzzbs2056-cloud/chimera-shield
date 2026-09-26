"""Human-approval gate for anything that leaves the repository.

Actions in `GATED_ACTIONS` raise `ApprovalRequired` unless state/approvals.json
contains a matching approval recorded by a named human. Code that performs
such an action must call `require_approval` first. Agents cannot grant
approvals: `record_approval` refuses approver names that look like agent ids.
"""

from __future__ import annotations

import re
from pathlib import Path

from src.common import STATE_DIR, load_json, sha256_obj, utc_now, write_json

APPROVALS_PATH = STATE_DIR / "approvals.json"
GATED_ACTIONS = {
    "external_write",  # posting, uploading or publishing anywhere outside this repo
    "contact_third_party",  # emails, messages, surveys, interviews
    "financial_action",  # any payment, purchase or commitment of funds
    "fieldwork",  # citizen consultation or data collection involving people
    "publish_report",  # releasing reports outside the project
}
_AGENT_LIKE = re.compile(r"^(agent[\s_-]*)?\d{2}[A-E]?$", re.IGNORECASE)


class ApprovalRequired(PermissionError):
    pass


def _load(path: Path) -> dict:
    return load_json(path) if path.exists() else {"approvals": []}


def action_key(action: str, detail: dict) -> str:
    return sha256_obj({"action": action, "detail": detail})


def record_approval(action: str, detail: dict, approver: str, path: Path = APPROVALS_PATH) -> dict:
    if action not in GATED_ACTIONS:
        raise ValueError(f"unknown gated action {action}")
    if not approver.strip() or _AGENT_LIKE.match(approver.strip()):
        raise ValueError("approvals must be recorded by a named human, not an agent")
    data = _load(path)
    entry = {"key": action_key(action, detail), "action": action, "detail": detail, "approver": approver,
             "approved_at": utc_now()}
    data["approvals"].append(entry)
    write_json(path, data)
    return entry


def require_approval(action: str, detail: dict, path: Path = APPROVALS_PATH) -> dict:
    if action not in GATED_ACTIONS:
        raise ValueError(f"unknown gated action {action}")
    key = action_key(action, detail)
    for entry in _load(path)["approvals"]:
        if entry["key"] == key:
            return entry
    raise ApprovalRequired(f"human approval required for {action}: {detail}")
