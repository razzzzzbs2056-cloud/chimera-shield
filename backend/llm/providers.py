"""LLM providers.

One Anthropic provider plus one OpenAI-compatible provider. The latter covers
essentially every way of serving open-source models: Ollama, vLLM, llama.cpp
server, LM Studio, TGI, SGLang, Hugging Face Inference, OpenRouter, Together,
Groq, Fireworks, etc. Pick one with env vars (see .env.example).
"""
import asyncio
import os

import httpx

from backend.llm.base import LLMError, LLMProvider

# name -> (base_url, api_key_env or None for keyless local servers)
PRESETS: dict[str, tuple[str, str | None]] = {
    "ollama": ("http://localhost:11434/v1", None),
    "vllm": ("http://localhost:8001/v1", None),
    "llamacpp": ("http://localhost:8080/v1", None),
    "lmstudio": ("http://localhost:1234/v1", None),
    "tgi": ("http://localhost:8080/v1", None),
    "sglang": ("http://localhost:30000/v1", None),
    "huggingface": ("https://router.huggingface.co/v1", "HF_TOKEN"),
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    "together": ("https://api.together.xyz/v1", "TOGETHER_API_KEY"),
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY"),
    "fireworks": ("https://api.fireworks.ai/inference/v1", "FIREWORKS_API_KEY"),
    "openai_compat": ("", "LLM_API_KEY"),  # custom: set LLM_BASE_URL
}

DEFAULT_ANTHROPIC_MODEL = "claude-opus-4-6"


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, model: str, api_key: str | None):
        import anthropic

        self.model = model
        self._client = anthropic.Anthropic(api_key=api_key)

    async def complete(self, system: str, user: str, max_tokens: int = 1024) -> str:
        def call():
            return self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )

        try:
            msg = await asyncio.to_thread(call)
        except Exception as e:  # SDK raises many types; surface one
            raise LLMError(f"anthropic call failed: {type(e).__name__}") from e
        parts = [b.text for b in msg.content if getattr(b, "type", "") == "text"]
        if not parts:
            raise LLMError("anthropic returned no text content")
        return "".join(parts)


class OpenAICompatProvider(LLMProvider):
    def __init__(self, name: str, model: str, base_url: str, api_key: str | None,
                 timeout: float = 60.0, transport: httpx.AsyncBaseTransport | None = None):
        self.name = name
        self.model = model
        self._url = base_url.rstrip("/") + "/chat/completions"
        self._headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self._timeout = timeout
        self._transport = transport

    async def complete(self, system: str, user: str, max_tokens: int = 1024) -> str:
        body = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as c:
                r = await c.post(self._url, json=body, headers=self._headers)
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"] or ""
        except (httpx.HTTPError, KeyError, IndexError, ValueError) as e:
            raise LLMError(f"{self.name} call failed: {type(e).__name__}") from e


def get_provider(env: dict | None = None) -> LLMProvider:
    """Build the provider from env: LLM_PROVIDER, LLM_MODEL, LLM_BASE_URL, LLM_API_KEY."""
    env = os.environ if env is None else env
    provider = env.get("LLM_PROVIDER", "anthropic").lower()
    model = env.get("LLM_MODEL", "")

    if provider == "anthropic":
        return AnthropicProvider(model or DEFAULT_ANTHROPIC_MODEL, env.get("ANTHROPIC_API_KEY"))

    if provider not in PRESETS:
        raise LLMError(f"Unknown LLM_PROVIDER '{provider}'. Options: anthropic, {', '.join(PRESETS)}")
    if not model:
        raise LLMError("LLM_MODEL is required for open-source providers (e.g. 'llama3.3' for ollama)")
    base_url, key_env = PRESETS[provider]
    base_url = env.get("LLM_BASE_URL") or base_url
    if not base_url:
        raise LLMError("LLM_BASE_URL is required for provider 'openai_compat'")
    api_key = env.get("LLM_API_KEY") or (env.get(key_env) if key_env else None)
    return OpenAICompatProvider(provider, model, base_url, api_key)
