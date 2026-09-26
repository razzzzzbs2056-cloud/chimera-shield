"""Source catalog access."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.common import RESEARCH_DIR, load_yaml

CATALOG_PATH = RESEARCH_DIR / "sources" / "source_catalog.yaml"


@dataclass(frozen=True)
class Source:
    id: str
    tier: int
    institution: str
    url: str | None
    covers: tuple[str, ...]
    endpoint_status: str


class SourceCatalog:
    def __init__(self, path: Path = CATALOG_PATH):
        raw = load_yaml(path)["sources"]
        self.sources = {
            sid: Source(sid, int(v["tier"]), v["institution"], v.get("url"), tuple(v.get("covers", [])),
                        v.get("endpoint_status", "unverified"))
            for sid, v in raw.items()
        }

    def __contains__(self, sid: str) -> bool:
        return sid in self.sources

    def get(self, sid: str) -> Source:
        return self.sources[sid]

    def rank(self, source_ids: list[str]) -> list[str]:
        """Order source ids by hierarchy tier (highest priority first)."""
        return sorted(source_ids, key=lambda s: (self.sources[s].tier, s))

    def ids(self) -> list[str]:
        return sorted(self.sources)
