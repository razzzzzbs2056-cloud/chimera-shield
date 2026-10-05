from fastapi.testclient import TestClient

from backend.main import app
from backend.routers import scan

client = TestClient(app)
GOOD = ('{"risk_score": 90, "risk_level": "CRITICAL", "is_phishing": true, '
        '"indicators": ["fake link"], "recommendation": "Delete it."}')


class Fake:
    def __init__(self, text): self.text = text
    async def complete(self, system, user, max_tokens=1024): return self.text


def post(text, monkeypatch):
    monkeypatch.setattr(scan, "get_provider", lambda: Fake(text))
    return client.post("/api/scan/email", json={"email_content": "hi"})


def test_ok_with_fenced_output(monkeypatch):
    r = post(f"```json\n{GOOD}\n```", monkeypatch)
    assert r.status_code == 200 and r.json()["risk_level"] == "CRITICAL"


def test_bad_output_is_502(monkeypatch):
    assert post("I cannot help", monkeypatch).status_code == 502
    assert post('{"risk_score": "x"}', monkeypatch).status_code == 502


def test_empty_is_400():
    assert client.post("/api/scan/email", json={"email_content": " "}).status_code == 400


def test_models_endpoint():
    r = client.get("/api/models", params={"role": "guard"})
    assert r.status_code == 200 and all(m["role"] == "guard" for m in r.json())
