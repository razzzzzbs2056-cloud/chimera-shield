---
name: add-model-provider
description: Add or switch the LLM that powers ChimeraShield scans, including any open-source model (Ollama, vLLM, llama.cpp, LM Studio, TGI, Hugging Face, OpenRouter, Together, Groq). Use when asked to add a model/provider or run locally.
---

# Add or switch a model provider

Code lives in `backend/llm/` (`providers.py` presets, `catalog.py` model list, `base.py` JSON extraction).

1. **Any OpenAI-compatible server needs no code.** Set in `.env`:
   - `LLM_PROVIDER=<preset>` (see `PRESETS` in `providers.py`; use `openai_compat` + `LLM_BASE_URL` for anything else)
   - `LLM_MODEL=<name the server uses>`
   - API key env var if the preset needs one.
2. **Local quick start (Ollama):** `ollama pull qwen2.5:7b`, then `LLM_PROVIDER=ollama LLM_MODEL=qwen2.5:7b`.
3. **New preset:** add one line to `PRESETS` (`name: (base_url, key_env_or_None)`) and a case in `tests/test_llm.py`.
4. **New catalog entry:** add a `ModelEntry` in `catalog.py` with role, license and notes. Confirm the HF id/Ollama tag exists and read the license before adding.
5. **Non-OpenAI API:** subclass `LLMProvider` (implement `complete`), raise `LLMError` on any failure, wire it in `get_provider`.
6. Run `make test`. Then run the `run-phishing-eval` skill: a new model is not "supported" until it has numbers.

Open models often wrap JSON in prose or `<think>` blocks; `extract_json` handles that, so don't loosen the response schema instead.
