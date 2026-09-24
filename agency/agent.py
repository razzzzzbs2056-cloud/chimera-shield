"""A single agent: a role prompt, a set of tools, and a tool-use loop."""

from __future__ import annotations

import json
import logging

from agency.llm import LLM
from agency.tools import Tool

log = logging.getLogger("agency")


class Agent:
    def __init__(self, name: str, title: str, system: str, tools: list[Tool], llm: LLM, max_turns: int = 12):
        self.name = name
        self.title = title
        self.system = system
        self.tools = {t.name: t for t in tools}
        self.llm = llm
        self.max_turns = max_turns

    def run(self, task: str) -> str:
        """Work on ``task`` until the model stops calling tools; return its final report."""
        log.info("▶ %s (%s): %s", self.title, self.name, task)
        messages: list[dict] = [{"role": "user", "content": task}]
        api_tools = [t.to_api() for t in self.tools.values()]

        for _ in range(self.max_turns):
            stop_reason, content = self.llm.complete(self.name, self.system, messages, api_tools)
            messages.append({"role": "assistant", "content": content})

            if stop_reason == "refusal":
                return f"[{self.name}] declined this task."
            if stop_reason != "tool_use":
                return _text_of(content) or f"[{self.name}] finished without a report."

            results = [self._call(block) for block in content if block.get("type") == "tool_use"]
            messages.append({"role": "user", "content": results})

        return f"[{self.name}] stopped after {self.max_turns} turns without finishing."

    def _call(self, block: dict) -> dict:
        tool = self.tools.get(block["name"])
        inputs = block.get("input") or {}
        log.info("  %s → %s(%s)", self.name, block["name"], json.dumps(inputs)[:160])
        try:
            if tool is None:
                raise ValueError(f"unknown tool {block['name']!r}")
            output, is_error = tool.handler(**inputs), False
        except Exception as exc:  # report tool failures back to the model instead of crashing
            output, is_error = f"Error: {exc}", True
        result = {"type": "tool_result", "tool_use_id": block["id"], "content": str(output)}
        if is_error:
            result["is_error"] = True
        return result


def _text_of(content: list[dict]) -> str:
    return "\n".join(b["text"] for b in content if b.get("type") == "text").strip()
