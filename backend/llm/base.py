import json
import re
from abc import ABC, abstractmethod


class LLMError(Exception):
    """Provider call failed or returned unusable output."""


class LLMProvider(ABC):
    name: str
    model: str

    @abstractmethod
    async def complete(self, system: str, user: str, max_tokens: int = 1024) -> str:
        """Return the model's text reply."""


_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_json(text: str) -> dict:
    """Parse a JSON object from model output.

    Open-source models often wrap JSON in prose, code fences or <think> blocks,
    so strip those and fall back to the first balanced {...} object.
    """
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    candidates = [text]
    candidates += _FENCE.findall(text)
    start = text.find("{")
    while start != -1:
        depth = 0
        in_str = esc = False
        for i in range(start, len(text)):
            c = text[i]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
            elif c == '"':
                in_str = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    candidates.append(text[start:i + 1])
                    break
        start = text.find("{", start + 1)
    for cand in candidates:
        try:
            obj = json.loads(cand.strip())
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(obj, dict):
            return obj
    raise LLMError("No valid JSON object found in model output")
