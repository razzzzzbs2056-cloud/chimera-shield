"""Build precedent-atlas.html from references/world-precedents.csv (single source of truth).

Run:  python architecture/art/build_atlas.py
"""
import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV = HERE.parent / "references" / "world-precedents.csv"
THEMES = {
    "Structure": {"structure", "long-span", "tensile", "lattice", "diagrid", "tube", "lateral", "efficiency", "cantilever", "bracing"},
    "Earthquake": {"seismic", "isolation", "damping"},
    "Timber": {"timber", "CLT", "glulam", "LVL", "gridshell", "hybrid"},
    "Shells & form-finding": {"shell", "form-finding", "geometry", "gridshell"},
    "Façade & light": {"facade", "perforation", "mashrabiya", "light"},
    "Climate": {"climate", "passive", "biomimetic", "green", "sustainability", "ventilation"},
    "Earth, brick & craft": {"earth", "brick", "craft", "community", "vernacular"},
    "Space, services & pavilions": {"pavilion", "space", "material", "services", "flexibility", "roof", "minimal", "module", "acoustics"},
    "Ground & water": {"foundation", "water", "site"},
    "Houses": {"house", "residential"},
    "Cautionary": {"failure-lesson", "cost-lesson", "maintenance", "fire"},
}


def year_num(y: str):
    y = y.strip()
    m = re.search(r"(\d+)(st|nd|rd|th)", y)
    if m and "century" in y:
        return (int(m.group(1)) - 1) * 100 + 50
    m = re.search(r"\d{3,4}", y)
    if m:
        return int(m.group(0))
    return None


def load():
    rows = list(csv.DictReader(open(CSV, newline="")))
    for r in rows:
        r["tags"] = [t for t in r["tags"].split(";") if t]
        r["year_num"] = year_num(r["year"])
        r["era"] = next((t for t in ("historic", "modern", "contemporary") if t in r["tags"]), "")
        r["themes"] = [k for k, v in THEMES.items() if v & set(r["tags"])]
    return rows


def build() -> Path:
    rows = load()
    html = (HERE / "precedent-atlas.template.html").read_text()
    data = json.dumps(rows, ensure_ascii=False).replace("</", "<\\/")
    out = HERE / "precedent-atlas.html"
    out.write_text(html.replace("/*__DATA__*/[]", data).replace("/*__THEMES__*/[]", json.dumps(list(THEMES))))
    return out


def build_gallery() -> Path:
    """Houses gallery: same CSV, so cards and atlas never disagree."""
    rows = load()
    html = (HERE / "houses-gallery.template.html").read_text()
    out = HERE / "houses-gallery.html"
    out.write_text(html.replace("/*__DATA__*/[]", json.dumps(rows, ensure_ascii=False).replace("</", "<\\/")))
    return out


if __name__ == "__main__":
    print(build(), len(load()), "precedents")
    print(build_gallery())
