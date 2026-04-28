"""Adapter collection for third-party agent integrations."""

from __future__ import annotations

from clinprog_bench.runners.adapters.claude import ClaudeAdapter
from clinprog_bench.runners.adapters.deepseek import DeepSeekAdapter
from clinprog_bench.runners.adapters.glm import GLMAdapter

__all__ = ["ClaudeAdapter", "DeepSeekAdapter", "GLMAdapter"]
