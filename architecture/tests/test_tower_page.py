"""The Sydney tower page is built from the divisions' data and reflects it."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tower"))
import build_tower_page  # noqa: E402


def test_page_embeds_current_division_data():
    html = build_tower_page.main().read_text()
    data = json.loads(re.search(r"var DATA = (\{.*?\});\n</script>", html, re.S).group(1).replace("<\\/", "</"))
    s = json.loads((ROOT / "tower" / "data" / "structure.json").read_text())
    a = json.loads((ROOT / "tower" / "data" / "architecture.json").read_text())
    assert data["structure"]["W_kN"] == s["W_kN"] and len(data["structure"]["columns"]) == len(s["columns"])
    assert data["floor"] == a["typical_floor"]
    assert data["basis"]["site"]["latitude"] == -33.87
    assert all(r["valid"] for r in data["status"] if r["state"] == "returned")   # returned rows must validate; pending rows allowed
