import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from tests.test_runtime import CFG, make_runner
from trader.config import Config
from trader.web.server import build_payload, make_handler, tail_jsonl


def test_payload_before_the_service_has_ever_run(tmp_path):
    cfg = Config(**{**CFG, "data_dir": str(tmp_path)})
    p = build_payload(cfg, tmp_path, tmp_path / "policies")
    assert p["status"]["health"] == "not_started" and p["account"]["equity"] == 1000.0
    assert p["positions"] == [] and p["trades"] == [] and p["nightly"] is None
    assert p["setups"][0]["symbol"] == "AAA/USDT" and p["setups"][0]["action"] is None
    assert p["limits"]["kill_drawdown"] == 0.15


def test_payload_reflects_a_real_pass_and_goes_stale(tmp_path):
    r, data = make_runner(tmp_path)
    r.run_once()
    cfg = Config(**{**CFG, "data_dir": str(tmp_path)})
    p = build_payload(cfg, tmp_path, tmp_path / "policies", now=data.now + 5)
    assert p["status"]["health"] == "ok" and p["status"]["mode"] == "paper"
    pos = p["positions"][0]
    assert pos["symbol"] == "AAA/USDT" and pos["side"] == "long" and pos["risk_at_stop"] <= 20.0 + 1e-6
    assert p["account"]["open_positions"] == 1 and 0 < p["account"]["leverage"] <= 1.01  # 1x cap, then fees
    assert p["account"]["equity"] == pytest.approx(r.core.account.equity(r.marks))
    s = p["setups"][0]
    assert s["action"] == "enter" and s["confidence"] == 0.93 and s["quality"] == 3
    assert len(p["equity_curve"]) == 1 and p["decisions"][0]["symbol"] == "AAA/USDT"
    late = build_payload(cfg, tmp_path, tmp_path / "policies", now=data.now + 3600)
    assert late["status"]["health"] == "stale"


def test_payload_surfaces_kill_pause_and_halt(tmp_path):
    r, data = make_runner(tmp_path)
    r.run_once()
    r.core.account.kill_latched, r.core.account.kill_reason = True, "drawdown 15.2%"
    r.core.global_pause, r.core.halt_reason = True, "reconciliation mismatch"
    r.save()
    cfg = Config(**{**CFG, "data_dir": str(tmp_path)})
    notices = build_payload(cfg, tmp_path, tmp_path / "p", now=data.now)["notices"]
    text = " ".join(n["text"] for n in notices)
    assert "Kill switch" in text and "Halted" in text and "paused" in text
    assert [n["level"] for n in notices][:2] == ["critical", "critical"]


def test_tail_skips_partial_and_corrupt_lines(tmp_path):
    p = tmp_path / "x.jsonl"
    p.write_text('{"a":1}\n{"a":2}\n{"a":')  # the last line is still being written
    assert tail_jsonl(p, 10) == [{"a": 1}, {"a": 2}]
    assert tail_jsonl(p, 1) == [] or tail_jsonl(p, 2)[-1] == {"a": 2}
    assert tail_jsonl(tmp_path / "missing.jsonl", 5) == []


@pytest.fixture
def server(tmp_path):
    r, _ = make_runner(tmp_path)
    r.run_once()
    cfg = Config(**{**CFG, "data_dir": str(tmp_path)})
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(cfg, tmp_path, tmp_path / "policies"))
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def _open(url, method="GET"):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # never route localhost via a proxy
    return opener.open(urllib.request.Request(url, method=method, data=b"{}" if method != "GET" else None), timeout=5)


def test_server_serves_page_and_state_with_safe_headers(server):
    page = _open(server + "/")
    body = page.read().decode()
    assert page.status == 200 and "Trader dashboard" in body and "api/state" in body
    assert "default-src 'none'" in page.headers["Content-Security-Policy"]
    assert page.headers["X-Frame-Options"] == "DENY" and page.headers["Cache-Control"] == "no-store"
    state = json.loads(_open(server + "/api/state").read())
    assert state["status"]["health"] in ("ok", "stale") and state["positions"][0]["symbol"] == "AAA/USDT"
    assert _open(server + "/healthz").read() == b"ok"


def test_server_is_read_only_and_serves_nothing_else(server):
    for method in ("POST", "PUT", "DELETE", "PATCH"):
        with pytest.raises(urllib.error.HTTPError) as e:
            _open(server + "/api/state", method)
        assert e.value.code == 405
    for path in ("/state.json", "/../.env", "/.env", "/api/resume", "/journal/decisions.jsonl"):
        with pytest.raises(urllib.error.HTTPError) as e:
            _open(server + path)
        assert e.value.code == 404


def test_page_never_builds_html_from_data():
    from trader.web.server import _page
    html = _page().decode()
    assert "innerHTML" not in html and "document.write" not in html and "eval(" not in html
    html = html.replace("http://www.w3.org/2000/svg", "")
    assert "http://" not in html and "https://" not in html  # the page calls nothing outside itself


def test_page_script_is_valid_javascript(tmp_path):
    import shutil
    import subprocess

    from trader.web.server import _page
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not installed")
    html = _page().decode()
    js = tmp_path / "page.js"
    js.write_text(html[html.index("<script>") + 8:html.index("</script>")])
    r = subprocess.run([node, "--check", str(js)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[:400]
