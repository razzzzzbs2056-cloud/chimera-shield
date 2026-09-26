"""Append-only, hash-chained audit ledger.

Each record stores the SHA-256 of the previous record, so any edit,
deletion or reordering of an earlier record is detected by `verify()`.
The ledger has no update or delete API: an auditor who changes their view
appends a new record that references the earlier one (`supersedes`).
No other agent — including the orchestrator (00) and the Global
Intelligence Director (16) — writes to it; they can only read it.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from src.common import REPORTS_DIR, sha256_obj, utc_now

LEDGER_PATH = REPORTS_DIR / "audits" / "audit_ledger.jsonl"
VERDICTS = ("VERIFIED", "CONDITIONAL", "UNVERIFIED", "INCONSISTENT")
AUDITORS = {"15": "Independent Domestic Audit", "28": "Independent Geopolitical Red Team"}
GENESIS = "0" * 64


@dataclass
class AuditRecord:
    auditor: str  # "15" or "28"
    subagents: list[str]
    subject_id: str
    subject_sha256: str
    verdict: str
    reasons: list[str]
    checks: list[dict]
    kind: str = "audit"  # audit | dissent
    conditions: list[str] = field(default_factory=list)
    supersedes: str | None = None
    created_at: str = field(default_factory=utc_now)
    prev_hash: str = GENESIS
    record_hash: str = ""

    def body(self) -> dict:
        d = asdict(self)
        d.pop("record_hash")
        return d


class LedgerError(RuntimeError):
    pass


class AuditLedger:
    def __init__(self, path: Path = LEDGER_PATH):
        self.path = path

    def records(self) -> list[AuditRecord]:
        if not self.path.exists():
            return []
        with open(self.path, encoding="utf-8") as fh:
            return [AuditRecord(**json.loads(line)) for line in fh if line.strip()]

    def append(self, rec: AuditRecord) -> AuditRecord:
        if rec.auditor not in AUDITORS:
            raise LedgerError(f"only independent auditors {sorted(AUDITORS)} may write to the ledger")
        if rec.verdict not in VERDICTS:
            raise LedgerError(f"invalid verdict {rec.verdict!r}")
        if not rec.reasons:
            raise LedgerError("auditors must state specific reasons for every verdict")
        if rec.kind not in ("audit", "dissent"):
            raise LedgerError("kind must be 'audit' or 'dissent'")
        existing = self.records()
        rec.prev_hash = existing[-1].record_hash if existing else GENESIS
        rec.record_hash = sha256_obj(rec.body())
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(rec), ensure_ascii=False, sort_keys=True) + "\n")
        return rec

    def verify(self) -> list[str]:
        """Return problems; empty list means the chain is intact."""
        problems, prev = [], GENESIS
        for i, rec in enumerate(self.records()):
            if rec.prev_hash != prev:
                problems.append(f"record {i}: prev_hash does not match preceding record")
            if sha256_obj(rec.body()) != rec.record_hash:
                problems.append(f"record {i}: content hash mismatch (record altered)")
            prev = rec.record_hash
        return problems

    def latest_for(self, subject_id: str) -> dict[str, AuditRecord]:
        """Most recent record per auditor for one subject."""
        out: dict[str, AuditRecord] = {}
        for rec in self.records():
            if rec.subject_id == subject_id:
                out[rec.auditor] = rec
        return out
