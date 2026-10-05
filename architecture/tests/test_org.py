"""The agent organisation (org.json), the generated ORG.md and the .claude/agents files must agree."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AG = ROOT / ".claude" / "agents"
sys.path.insert(0, str(ROOT / "architecture" / "tools"))
import build_org  # noqa: E402

ORG = json.loads((ROOT / "architecture" / "org.json").read_text())
FILES = {p.stem for p in AG.glob("bld-*.md")}
STAFF = {s[0] for s in ORG["director"]["staff"]}
DIVS = {d["agent"] for d in ORG["divisions"]}
SUPPORT = set(ORG["support_only"]) | {s for d in ORG["divisions"] for s in d.get("support", [])}
ALL = {ORG["director"]["agent"]} | STAFF | set(ORG["leads"]) | DIVS | SUPPORT


def read(name): return (AG / f"{name}.md").read_text()


def test_every_agent_file_is_in_the_org_and_vice_versa():
    assert FILES == ALL, {"files not in org": FILES - ALL, "org agents without files": ALL - FILES}


def test_frontmatter_and_managed_block():
    for n in FILES:
        s = read(n)
        assert re.match(r"---\nname: " + re.escape(n) + r"\ndescription: .+\ntools: .+\nmodel: \w+\n---\n", s), n
        if n != "bld-director":
            assert s.count("ORG-START") == 1 and s.count("ORG-END") == 1, n
            assert s.count("**Role:**") == 1, n


def test_reporting_lines_match_org():
    for d in ORG["divisions"]:
        if "engine" not in d:
            assert f"**Reports to:** `{d['lead']}`" in read(d["agent"]), d["agent"]
    for s in STAFF | set(ORG["leads"]):
        assert "**Reports to:** `bld-director`" in read(s), s


def test_specialists_carry_the_return_format():
    for n in DIVS | SUPPORT:
        s = read(n)
        pos = [s.find("\n" + h + "\n") for h in ORG["return_format"]]
        assert all(p > 0 for p in pos) and pos == sorted(pos), n
    fire = read("bld-fire-life-safety")
    assert all(v in fire for v in ORG["fire_verdicts"]) and "--fire" in fire


def test_requested_divisions_and_roles_exist():
    names = {d["name"] for d in ORG["divisions"]}
    assert {d["n"] for d in ORG["divisions"]} >= set(range(2, 26))
    for role in ["Architecture", "Structural Engineering", "Earthquake Engineering", "Geotechnical Engineering", "Foundation Engineering",
                 "Civil / Site Engineering", "Mechanical / HVAC", "Electrical Engineering", "Hydraulic / Plumbing", "Fire Engineering",
                 "Façade Engineering", "Building Physics", "Sustainability", "Acoustics", "Lighting / Daylight", "Wind Engineering",
                 "Flood / Stormwater", "Transportation / Parking", "Accessibility", "BIM", "Quantity Surveyor", "Construction Engineering",
                 "Planning", "Materials", "Codes", "Risk / Reliability", "Independent Verification", "Engineering Critic", "Optimisation", "Building Energy"]:
        assert role in names, role
    assert len(STAFF) == 10 and len(ORG["return_format"]) == 10


def test_org_md_is_current():
    assert (ROOT / "architecture" / "ORG.md").read_text() == build_org.render_md(write=False)


def test_specialists_can_run_the_validator():
    # the return format must be self-validated, which needs a shell (lesson L8 in architecture/memory/lessons.md)
    for n in DIVS | SUPPORT:
        tools = re.search(r"^tools: (.*)$", read(n), re.M).group(1)
        assert "Bash" in tools, n
