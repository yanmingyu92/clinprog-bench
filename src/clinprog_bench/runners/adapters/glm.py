"""Zhipu GLM chat adapter (OpenAI-compatible BigModel endpoint)."""

from __future__ import annotations

import os

from clinprog_bench.runners.adapters._base import LLMAdapterBase, http_post_json


class GLMAdapter(LLMAdapterBase):
    """Single-turn GLM baseline (Zhipu BigModel / Z.ai OpenAI-compatible API)."""

    agent_name = "glm-4.5"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        endpoint: str | None = None,
        timeout: float = 90.0,
        max_tokens: int = 4096,
        max_retries: int = 3,
    ) -> None:
        key = api_key or os.environ.get("GLM5_API_KEY") or os.environ.get("GLM_API_KEY")
        if not key:
            msg = "GLM5_API_KEY not set; pass api_key= or export the env var."
            raise RuntimeError(msg)
        self._key = key
        self._model = model or os.environ.get("GLM_MODEL", "glm-4.5")
        self._endpoint = endpoint or os.environ.get(
            "GLM_ENDPOINT",
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        )
        self._timeout = timeout
        self._max_tokens = max_tokens
        self._max_retries = max_retries
        self.agent_name = self._model

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


__all__ = ["GLMAdapter"]
