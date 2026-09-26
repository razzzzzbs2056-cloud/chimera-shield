import importlib

from fastapi.testclient import TestClient

from backend import config
from backend.routers import scan


def test_key_only_in_dotenv_reaches_anthropic_client(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("ANTHROPIC_API_KEY=sk-from-dotenv-test\n")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    config.load_environment(str(env_file))
    client = scan.get_anthropic_client()
    assert client.api_key == "sk-from-dotenv-test"


def test_cors_allows_only_configured_origins(monkeypatch):
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://app.example.test")
    import backend.main as main

    main = importlib.reload(main)
    try:
        c = TestClient(main.app)
        headers = {"Access-Control-Request-Method": "POST"}
        ok = c.options("/api/scan/email", headers={**headers, "Origin": "https://app.example.test"})
        bad = c.options("/api/scan/email", headers={**headers, "Origin": "https://evil.example"})
        assert ok.headers.get("access-control-allow-origin") == "https://app.example.test"
        assert bad.status_code == 400
        assert "access-control-allow-origin" not in bad.headers
    finally:
        monkeypatch.delenv("ALLOWED_ORIGINS")
        importlib.reload(main)


def test_docs_disabled_in_production(monkeypatch):
    monkeypatch.setenv("ENV", "production")
    import backend.main as main

    main = importlib.reload(main)
    try:
        assert TestClient(main.app).get("/docs").status_code == 404
    finally:
        monkeypatch.delenv("ENV")
        importlib.reload(main)
