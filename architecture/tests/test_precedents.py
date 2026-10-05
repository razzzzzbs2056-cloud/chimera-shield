import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "art"))
import build_atlas  # noqa: E402

FIELDS = ["id", "name", "place", "year", "designers", "typology", "structure", "materials",
          "climate_light", "innovation", "lesson_for_pavilion", "tags"]


def test_csv_schema_and_completeness():
    rows = list(csv.DictReader(open(ROOT / "references" / "world-precedents.csv", newline="")))
    assert list(rows[0].keys()) == FIELDS
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate ids"
    for r in rows:
        for f in ("name", "place", "year", "designers", "structure", "innovation", "lesson_for_pavilion"):
            assert r[f].strip(), (r["id"], f)
        assert any(t in r["tags"].split(";") for t in ("historic", "modern", "contemporary")), r["id"]


def test_every_entry_reachable_by_a_theme_and_year_parsing():
    rows = build_atlas.load()
    assert all(r["themes"] for r in rows)
    assert build_atlas.year_num("c. 7th century") == 650
    assert build_atlas.year_num("13th–14th century") == 1250
    assert build_atlas.year_num("1882–ongoing") == 1882
    assert build_atlas.year_num("historic") is None


def test_built_page_embeds_all_entries():
    out = build_atlas.build()
    html = out.read_text()
    assert "/*__DATA__*/" not in html and html.count('"lesson_for_pavilion"') == len(build_atlas.load())


def test_gallery_houses_exist_in_library_and_have_builders():
    import re
    out = build_atlas.build_gallery()
    html = out.read_text()
    ids_in_csv = {r["id"] for r in build_atlas.load()}
    houses = re.findall(r"\{ id: '([a-z0-9-]+)', notice:", html)
    builders = set(re.findall(r"\n    '([a-z0-9-]+)': function \(g\)", html))
    assert len(houses) == 12 and set(houses) <= ids_in_csv
    assert set(houses) == builders
