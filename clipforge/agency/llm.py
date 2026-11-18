"""Thin Claude wrapper. Every agent has a deterministic fallback, so the agency
keeps running (in "heuristic mode") when no credential is configured or a call fails."""
import logging
import os
from typing import TypeVar

from pydantic import BaseModel

from . import config

log = logging.getLogger("clipforge.llm")
T = TypeVar("T", bound=BaseModel)
_client = None


def enabled() -> bool:
    if config.USE_LLM == "off":
        return False
    if config.USE_LLM == "on":
        return True
    return bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN"))


def _get_client():
    global _client
    if _client is None:
        import anthropic
        _client = anthropic.Anthropic()
    return _client


def structured(system: str, prompt: str | list, schema: type[T], effort: str = "medium") -> T | None:
    """Ask Claude for output validated against `schema` (`prompt` may be a list of content
    blocks, e.g. an image plus text). Returns None on any failure."""
    if not enabled():
        return None
    import anthropic
    try:
        resp = _get_client().beta.messages.parse(
            model=config.ANTHROPIC_MODEL,
            max_tokens=16000,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            output_format=schema,
            output_config={"effort": effort},
            # If a safety classifier declines, the API retries on a fallback model.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        if resp.stop_reason == "refusal":
            log.warning("Claude declined request (%s)", getattr(resp.stop_details, "category", None))
            return None
        return resp.parsed_output
    except anthropic.APIConnectionError as e:
        log.warning("Claude unreachable: %s", e)
    except anthropic.RateLimitError:
        log.warning("Claude rate limited; using heuristic fallback")
    except anthropic.APIStatusError as e:
        log.warning("Claude API error %s: %s", e.status_code, e.message)
    except Exception as e:  # validation/parsing problems
        log.warning("Claude response unusable: %s", e)
    return None
