"""Sandboxed file writes: agents can only create files inside the workspace."""

from __future__ import annotations

from pathlib import Path


class Workspace:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def write(self, rel_path: str, content: str) -> Path:
        target = (self.root / rel_path).resolve()
        if not target.is_relative_to(self.root):
            raise ValueError(f"path escapes the workspace: {rel_path}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return target

    def listing(self) -> str:
        files = sorted(p.relative_to(self.root) for p in self.root.rglob("*") if p.is_file())
        return "\n".join(str(f) for f in files) or "(workspace is empty)"
