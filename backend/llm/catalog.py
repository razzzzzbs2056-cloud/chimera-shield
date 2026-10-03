"""Curated catalog of open-weight models usable with ChimeraShield.

This is a starting list, not an exhaustive one: any model your server exposes
through an OpenAI-compatible API works by setting LLM_MODEL. Hugging Face ids
and Ollama tags change over time, so confirm them before pulling, and check
each license (esp. Llama/Gemma community licenses) for commercial use.
"""
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class ModelEntry:
    family: str
    hf_id: str
    ollama_tag: str | None
    params: str
    license: str
    role: str  # "triage" | "escalation" | "guard" | "classifier"
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


CATALOG: list[ModelEntry] = [
    # Small/fast: tier-1 triage
    ModelEntry("Llama", "meta-llama/Llama-3.2-3B-Instruct", "llama3.2:3b", "3B", "Llama 3.2 Community", "triage"),
    ModelEntry("Qwen", "Qwen/Qwen2.5-7B-Instruct", "qwen2.5:7b", "7B", "Apache-2.0", "triage", "Strong JSON adherence"),
    ModelEntry("Mistral", "mistralai/Mistral-7B-Instruct-v0.3", "mistral:7b", "7B", "Apache-2.0", "triage"),
    ModelEntry("Gemma", "google/gemma-2-9b-it", "gemma2:9b", "9B", "Gemma Terms", "triage"),
    ModelEntry("Phi", "microsoft/Phi-3.5-mini-instruct", "phi3.5", "3.8B", "MIT", "triage", "Runs on CPU/laptop"),
    ModelEntry("OLMo", "allenai/OLMo-2-1124-7B-Instruct", None, "7B", "Apache-2.0", "triage", "Fully open data+code; good for research reproducibility"),
    # Large: tier-2 escalation
    ModelEntry("Llama", "meta-llama/Llama-3.3-70B-Instruct", "llama3.3:70b", "70B", "Llama 3.3 Community", "escalation"),
    ModelEntry("Qwen", "Qwen/Qwen2.5-72B-Instruct", "qwen2.5:72b", "72B", "Qwen license", "escalation"),
    ModelEntry("Mistral", "mistralai/Mixtral-8x7B-Instruct-v0.1", "mixtral:8x7b", "47B MoE", "Apache-2.0", "escalation"),
    ModelEntry("DeepSeek", "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", "deepseek-r1:32b", "32B", "MIT", "escalation", "Emits <think> blocks; extract_json strips them"),
    ModelEntry("gpt-oss", "openai/gpt-oss-20b", "gpt-oss:20b", "20B", "Apache-2.0", "escalation"),
    # Safety / injection guards: run before the scanner prompt
    ModelEntry("Llama Guard", "meta-llama/Llama-Guard-3-8B", "llama-guard3:8b", "8B", "Llama 3.1 Community", "guard", "Content-safety classifier"),
    ModelEntry("Prompt Guard", "meta-llama/Llama-Prompt-Guard-2-86M", None, "86M", "Llama 4 Community", "guard", "Prompt-injection detector; not a chat model, run via transformers"),
    # Task-specific encoders: cheap baselines for the eval harness (not chat models)
    ModelEntry("BERT", "ealvaradob/bert-finetuned-phishing", None, "110M", "Apache-2.0", "classifier", "Phishing baseline; load with transformers pipeline"),
]


def find_models(role: str | None = None, max_license_restrictive: bool = False) -> list[ModelEntry]:
    out = [m for m in CATALOG if role is None or m.role == role]
    if max_license_restrictive:
        out = [m for m in out if m.license in {"Apache-2.0", "MIT"}]
    return out
