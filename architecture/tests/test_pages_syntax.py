"""Every inline script in the published HTML pages must parse (catches e.g. a // comment swallowing a closing brace)."""
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PAGES = sorted(list((ROOT / "art").glob("*.html")) + list((ROOT / "house").glob("*.html")))


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
@pytest.mark.parametrize("page", [p for p in PAGES if not p.name.endswith(".template.html")], ids=lambda p: p.name)
def test_inline_scripts_parse(page, tmp_path):
    js = "\n".join(m.group(1) for m in re.finditer(r"<script>(.*?)</script>", page.read_text(), re.S))
    f = tmp_path / "page.js"; f.write_text(js)
    r = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[:400]
