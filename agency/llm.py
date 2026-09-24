"""Model backends.

``ClaudeLLM`` calls the Claude API. ``MockLLM`` replays a scripted company so
the whole org chart can be demoed and tested offline without an API key.
Both return ``(stop_reason, content_blocks)`` where blocks are plain dicts
that can be appended to the conversation as-is.
"""

from __future__ import annotations

import itertools
from typing import Protocol

from agency.config import Config

FALLBACK_BETA = "server-side-fallback-2026-07-01"


class LLM(Protocol):
    def complete(self, agent: str, system: str, messages: list, tools: list[dict]) -> tuple[str, list[dict]]: ...


class ClaudeLLM:
    def __init__(self, config: Config):
        import anthropic

        self.client = anthropic.Anthropic()
        self.config = config

    def complete(self, agent, system, messages, tools):
        kwargs = dict(
            model=self.config.model,
            max_tokens=16000,
            system=system,
            messages=messages,
            tools=tools,
            thinking={"type": "adaptive"},
            output_config={"effort": self.config.effort},
        )
        if self.config.fallbacks:
            # If the primary model declines, the API retries on a fallback model in the same call.
            response = self.client.beta.messages.create(
                betas=[FALLBACK_BETA], extra_body={"fallbacks": "default"}, **kwargs
            )
        else:
            response = self.client.messages.create(**kwargs)
        blocks = [b.model_dump(mode="json", exclude_none=True) for b in response.content]
        return response.stop_reason, blocks


_ids = itertools.count(1)


def _tool_use(name: str, **inputs) -> dict:
    return {"type": "tool_use", "id": f"toolu_mock_{next(_ids)}", "name": name, "input": inputs}


def _text(text: str) -> dict:
    return {"type": "text", "text": text}


class MockLLM:
    """Deterministic stand-in: each agent calls its tools in a fixed order, then reports."""

    def __init__(self, config: Config):
        self.config = config

    def complete(self, agent, system, messages, tools):
        done = sum(
            1
            for m in messages
            if m["role"] == "user" and isinstance(m["content"], list)
            for b in m["content"]
            if b.get("type") == "tool_result"
        )
        task = messages[0]["content"] if isinstance(messages[0]["content"], str) else "the goal"
        script = self._script(agent, task)
        if done < len(script):
            return "tool_use", [script[done]]
        return "end_turn", [_text(f"[{agent}] Finished: {task[:120]}")]

    def _script(self, agent: str, task: str) -> list[dict]:
        company = self.config.company_name
        if agent == "ceo":
            return [
                _tool_use("delegate", agent="marketing", task=f"Build a launch campaign for: {task}"),
                _tool_use("delegate", agent="content", task="Write the launch blog post and 3 social posts from the campaign."),
                _tool_use("delegate", agent="email", task="Send the launch announcement to the beta list."),
                _tool_use("delegate", agent="engineer", task="Build a landing page for the launch."),
                _tool_use("view_board"),
            ]
        if agent == "marketing":
            return [
                _tool_use("view_board"),
                _tool_use(
                    "post_campaign",
                    title="Launch campaign",
                    audience="Small-business owners who publish content weekly",
                    channels=["blog", "linkedin", "x", "email"],
                    plan=f"Week 1 teaser, week 2 launch post + email, week 3 case study. Goal: {task}",
                ),
            ]
        if agent == "content":
            return [
                _tool_use("publish_content", title="Launch blog post", format="blog",
                          body=f"# Meet {company}\n\nAI agents that plan, write and ship your content."),
                _tool_use("publish_content", title="Launch social posts", format="social",
                          body="1/ We're live.\n2/ Your content team, powered by AI agents.\n3/ Try it free."),
            ]
        if agent == "email":
            return [
                _tool_use("send_email", to="beta@example.com", subject=f"{company} is live",
                          body="Hi there,\n\nWe just launched. Reply to get early access.\n\n— The team"),
            ]
        if agent == "engineer":
            return [
                _tool_use("write_file", path="site/index.html",
                          content=f"<!doctype html><title>{company}</title><h1>{company}</h1><p>AI content, on autopilot.</p>"),
            ]
        return []


def make_llm(config: Config) -> LLM:
    return MockLLM(config) if config.mock else ClaudeLLM(config)
