import json
import os
from types import SimpleNamespace

import pytest

# Deterministic settings for tests; never use a real key.
os.environ["ANTHROPIC_API_KEY"] = "test-key-not-real"
os.environ.setdefault("SCAN_RATE_LIMIT", "1000/minute")
os.environ.pop("TRIAGE_MODEL", None)
os.environ.pop("MAX_EMAIL_BYTES", None)

from fastapi.testclient import TestClient  # noqa: E402

from backend.main import app  # noqa: E402
from backend.routers import scan  # noqa: E402


def make_message(text: str, stop_reason: str = "end_turn") -> SimpleNamespace:
    return SimpleNamespace(content=[SimpleNamespace(type="text", text=text)], stop_reason=stop_reason)


class FakeMessages:
    def __init__(self) -> None:
        self.reply: SimpleNamespace | Exception = make_message(
            json.dumps(
                {
                    "risk_score": 88,
                    "risk_level": "CRITICAL",
                    "is_phishing": True,
                    "indicators": ["Urgent request to reset a password", "Link goes to a lookalike domain"],
                    "recommendation": "Delete the email and report it to your IT contact.",
                }
            )
        )
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if isinstance(self.reply, Exception):
            raise self.reply
        return self.reply


class FakeAnthropic:
    def __init__(self) -> None:
        self.messages = FakeMessages()


@pytest.fixture(autouse=True)
def _reset_state(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")
    monkeypatch.setenv("SCAN_RATE_LIMIT", "1000/minute")
    scan.limiter.reset()
    scan._client_for_key.cache_clear()
    yield
    app.dependency_overrides.clear()
    scan.limiter.reset()
    scan._client_for_key.cache_clear()


@pytest.fixture
def fake_llm() -> FakeAnthropic:
    fake = FakeAnthropic()
    app.dependency_overrides[scan.anthropic_client_dependency] = lambda: fake
    return fake


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
