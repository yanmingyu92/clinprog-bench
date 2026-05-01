"""Anthropic Claude Messages-API adapter."""

from __future__ import annotations

import os

from clinprog_bench.runners.adapters._base import LLMAdapterBase, http_post_json


class ClaudeAdapter(LLMAdapterBase):
    """Single-turn Claude baseline (Anthropic Messages API)."""

    agent_name = "claude-sonnet"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        endpoint: str = "https://api.anthropic.com/v1/messages",
        anthropic_version: str = "2023-06-01",
        timeout: float = 90.0,
        max_tokens: int = 4096,
        max_retries: int = 3,
    ) -> None:
        key = (
            api_key
            or os.environ.get("CLAUDE_API_KEY")
            or os.environ.get("ANTHROPIC_API_KEY")
        )
        if not key:
            msg = "CLAUDE_API_KEY not set; pass api_key= or export the env var."
            raise RuntimeError(msg)
        self._key = key
        self._model = model or os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-5")
        self._endpoint = endpoint
        self._version = anthropic_version
        self._timeout = timeout
        self._max_tokens = max_tokens
        self._max_retries = max_retries
        self.agent_name = self._model

    def _chat(self, system: str, user: str) -> tuple[str, dict[str, str]]:
        body = http_post_json(
            self._endpoint,
            {
                "model": self._model,
                "system": system,
                "messages": [{"role": "user", "content": user}],
                "temperature": 0.0,
                "max_tokens": self._max_tokens,
            },
            {
                "x-api-key": self._key,
                "anthropic-version": self._version,
            },
            self._timeout,
            self._max_retries,
        )
        # Messages API: body["content"] is a list of {type, text} blocks.
        blocks = body.get("content", [])
        text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
        usage = body.get("usage", {})
        return text, {
            "model": self._model,
            "prompt_tokens": str(usage.get("input_tokens", 0)),
            "completion_tokens": str(usage.get("output_tokens", 0)),
        }


__all__ = ["ClaudeAdapter"]
