"""DeepSeek chat-completions adapter (OpenAI-compatible)."""

from __future__ import annotations

import os

from clinprog_bench.runners.adapters._base import LLMAdapterBase, http_post_json


class DeepSeekAdapter(LLMAdapterBase):
    """Single-turn DeepSeek baseline."""

    agent_name = "deepseek-chat"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = "deepseek-chat",
        endpoint: str = "https://api.deepseek.com/chat/completions",
        timeout: float = 60.0,
        max_tokens: int = 4096,
        max_retries: int = 3,
    ) -> None:
        key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not key:
            msg = "DEEPSEEK_API_KEY not set; pass api_key= or export the env var."
            raise RuntimeError(msg)
        self._key = key
        self._model = model
        self._endpoint = endpoint
        self._timeout = timeout
        self._max_tokens = max_tokens
        self._max_retries = max_retries

    def _chat(self, system: str, user: str) -> tuple[str, dict[str, str]]:
        body = http_post_json(
            self._endpoint,
            {
                "model": self._model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.0,
                "top_p": 1.0,
                "max_tokens": self._max_tokens,
                "stream": False,
            },
            {"Authorization": f"Bearer {self._key}"},
            self._timeout,
            self._max_retries,
        )
        content = body["choices"][0]["message"]["content"] or ""
        usage = body.get("usage", {})
        return content, {
            "model": self._model,
            "prompt_tokens": str(usage.get("prompt_tokens", 0)),
            "completion_tokens": str(usage.get("completion_tokens", 0)),
        }


__all__ = ["DeepSeekAdapter"]
