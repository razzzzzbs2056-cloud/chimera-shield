import asyncio

import httpx
import pytest

from backend.llm import LLMError, extract_json, find_models, get_provider
from backend.llm.providers import OpenAICompatProvider


def test_extract_json_plain_fenced_prose_and_think():
    assert extract_json('{"a": 1}') == {"a": 1}
    assert extract_json('```json\n{"a": 2}\n```') == {"a": 2}
    assert extract_json('Sure! Here you go: {"a": {"b": "}"}} hope it helps') == {"a": {"b": "}"}}
    assert extract_json('<think>{"a": 0}</think>{"a": 3}') == {"a": 3}


def test_extract_json_failure():
    with pytest.raises(LLMError):
        extract_json("no json here")


def test_provider_selection():
    assert get_provider({"ANTHROPIC_API_KEY": "x"}).name == "anthropic"
    p = get_provider({"LLM_PROVIDER": "ollama", "LLM_MODEL": "qwen2.5:7b"})
    assert p.name == "ollama" and p._url == "http://localhost:11434/v1/chat/completions"
    with pytest.raises(LLMError):
        get_provider({"LLM_PROVIDER": "ollama"})  # model missing
    with pytest.raises(LLMError):
        get_provider({"LLM_PROVIDER": "openai_compat", "LLM_MODEL": "m"})  # base url missing
    with pytest.raises(LLMError):
        get_provider({"LLM_PROVIDER": "nope", "LLM_MODEL": "m"})


def test_openai_compat_roundtrip_and_error():
    def handler(req: httpx.Request):
        return httpx.Response(200, json={"choices": [{"message": {"content": '{"ok": true}'}}]})

    ok = OpenAICompatProvider("t", "m", "http://x/v1", None, transport=httpx.MockTransport(handler))
    assert asyncio.run(ok.complete("s", "u")) == '{"ok": true}'

    bad = OpenAICompatProvider("t", "m", "http://x/v1", None,
                               transport=httpx.MockTransport(lambda r: httpx.Response(500)))
    with pytest.raises(LLMError):
        asyncio.run(bad.complete("s", "u"))


def test_catalog_roles():
    assert find_models("triage") and find_models("escalation") and find_models("guard")
    assert all(m.license in {"Apache-2.0", "MIT"} for m in find_models(max_license_restrictive=True))
