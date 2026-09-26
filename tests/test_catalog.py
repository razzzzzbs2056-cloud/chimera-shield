"""Architecture: 29 agents, 111 subagents, complete definitions, acyclic dependencies."""
import json

import pytest

from src.agents.catalog import (EXPECTED_AGENTS, EXPECTED_SUBAGENTS, enriched_agents, load_catalog,
                                subagent_dependencies, topo_order, validate_catalog)
from src.agents.generate import stale_files
from src.common import ROOT
from src.research.sources import SourceCatalog

AGENT_FIELDS = ["id", "role", "mission", "responsibilities", "permitted_tools", "data_access", "depends_on",
                "deliverables", "reporting_format", "escalation_rules", "validation_requirements"]


@pytest.fixture(scope="module")
def cat():
    return load_catalog()


def test_catalog_valid(cat):
    assert validate_catalog(cat, SourceCatalog()) == []


def test_counts(cat):
    assert len(cat["agents"]) == EXPECTED_AGENTS == 29
    assert sum(len(a["subagents"]) for a in cat["agents"]) == EXPECTED_SUBAGENTS == 111
    assert [a["id"] for a in cat["agents"]] == [f"{i:02d}" for i in range(29)]


def test_division_structure(cat):
    div_a = [a for a in cat["agents"] if a["division"] == "A"]
    assert all(len(a["subagents"]) == 3 for a in div_a) and len(div_a) == 16
    assert all(len(a["subagents"]) == (3 if a["id"] == "16" else 5) for a in cat["agents"] if a["division"] == "B")


def test_generated_json_complete():
    agents = json.loads((ROOT / "config" / "agents.json").read_text())["agents"]
    subs = json.loads((ROOT / "config" / "subagents.json").read_text())["subagents"]
    assert len(agents) == 29 and len(subs) == 111
    for a in agents:
        for f in AGENT_FIELDS:
            assert a.get(f) not in (None, "") or f == "depends_on", (a["id"], f)
    for s in subs:
        assert s["instructions"]["questions"] and s["evidence_requirements"]["data_required"]
        assert s["output_schema"]["properties"]["specific"]["required"]


def test_generated_files_in_sync_with_catalog():
    assert stale_files() == []
    assert len(list((ROOT / ".claude" / "agents").glob("nepal3t-*.md"))) == 29
    assert len(list((ROOT / "src" / "agents" / "specs").glob("*.md"))) == 111


def test_dependencies_acyclic_and_respect_audit_order(cat):
    deps = subagent_dependencies(cat)
    order = topo_order(deps)
    pos = {n: i for i, n in enumerate(order)}
    for sub in ("15A", "15B", "15C"):
        assert all(pos[d] < pos[sub] for d in deps[sub])
        assert "01C" in deps[sub] and "14A" in deps[sub]
    assert all(d.startswith(tuple(f"{i}" for i in range(16, 28))) for d in deps["28A"])
    assert {"15A", "28A"} <= set(deps["00C"])


def test_cycle_detection():
    with pytest.raises(ValueError):
        topo_order({"a": ["b"], "b": ["a"]})


def test_independence_and_safety(cat):
    agents = {a["id"]: a for a in enriched_agents(cat)}
    assert agents["15"]["independent"] and agents["28"]["independent"]
    assert any("Agent 28" in f for f in agents["16"]["data_access"]["forbidden"])
    assert agents["19"]["safety_note"] and agents["27"]["safety_note"]
    for aid in ("15", "28"):
        assert "Edit" not in agents[aid]["permitted_tools"]


def test_source_catalog_covers_hierarchy():
    cat = SourceCatalog()
    for sid in ("nso_nepal", "nrb", "mof_nepal", "imf_weo", "wb_wdi", "adb_nepal", "ilostat", "unctadstat", "wto",
                "iea", "icimod"):
        assert sid in cat
    assert cat.get("nso_nepal").tier == 1 and cat.get("icimod").tier == 6
