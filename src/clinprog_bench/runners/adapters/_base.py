"""Shared helpers for single-turn LLM adapters (stdlib-only)."""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from typing import TYPE_CHECKING

from clinprog_bench.runners import BaseAdapter, Submission

if TYPE_CHECKING:
    from pathlib import Path

    from clinprog_bench.schema import TaskSpec


_RETRY_STATUSES = {429, 500, 502, 503, 504}

OUTPUT_KEY_BY_KIND: dict[str, str] = {
    "sas_program": "main.sas",
    "r_program": "main.R",
    "python_program": "main.py",
    "json": "review.json",
    "patch": "patch.diff",
    "text": "document.md",
}

CATEGORY_INSTRUCTIONS: dict[str, str] = {
    "T1": "Return ONLY the source code. No prose, no markdown fence.",
    "T2": (
        'Return ONLY a JSON object of the form {"issues": [{"line": int, '
        '"severity": "error|warning|info", "category": str, "message": str}]}.'
    ),
    "T3": (
        'Return ONLY a JSON object of the form {"variables": [...]} or '
        '{"<slot>": [...]} matching the prompt. No prose.'
    ),
    "T4": "Return ONLY the requested document text. No JSON, no code fence.",
    "T5": (
        "Return ONLY a unified diff (``--- a/<file>``\\n``+++ b/<file>``\\n"
        "``@@ ...``). No prose, no fence."
    ),
}

SYSTEM_PROMPT = (
    "You are a senior clinical statistical programmer. Produce outputs "
    "that satisfy CDISC SDTM/ADaM conventions and the ClinProg-Bench "
    "submission contract."
)


def inline_fixtures(task: TaskSpec, workspace: Path, budget: int) -> str:
    parts: list[str] = []
    remaining = budget
    for rel in task.inputs.fixtures:
        if remaining <= 0:
            break
        path = (workspace / rel).resolve()
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            continue
        snippet = text[:remaining]
        parts.append(f"### {rel}\n```\n{snippet}\n```")
        remaining -= len(snippet)
    return "\n\n".join(parts) if parts else "(no readable fixtures inlined)"


def strip_code_fence(text: str) -> str:
    s = text.strip()
    m = re.match(r"^```[a-zA-Z0-9_+-]*\n(.*?)\n```$", s, flags=re.DOTALL)
    if m:
        return m.group(1).strip("\n")
    return s


def build_user_message(task: TaskSpec, workspace: Path, fixture_budget: int) -> str:
    instr = CATEGORY_INSTRUCTIONS[task.category]
    fixtures = inline_fixtures(task, workspace, fixture_budget)
    return (
        f"Task ID: {task.task_id}\n"
        f"Category: {task.category} ({task.subcategory})\n"
        f"Title: {task.title}\n\n"
        f"## Instruction\n{task.inputs.prompt}\n\n"
        f"## Output format\n{instr}\n\n"
        f"## Fixture excerpts (truncated)\n{fixtures}\n"
    )


def http_post_json(
    endpoint: str,
    payload: dict,
    headers: dict[str, str],
    timeout: float,
    max_retries: int,
) -> dict:
    """POST JSON, retry on transient errors, return parsed JSON body."""
    body = json.dumps(payload).encode("utf-8")
    full_headers = {"Content-Type": "application/json", **headers}
    for attempt in range(max_retries + 1):
        try:
            req = urllib.request.Request(
                endpoint, data=body, headers=full_headers, method="POST"
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in _RETRY_STATUSES and attempt < max_retries:
                time.sleep(2.0 * (2**attempt))
                continue
            raise
        except urllib.error.URLError:
            if attempt < max_retries:
                time.sleep(2.0 * (2**attempt))
                continue
            raise
    return {}


class LLMAdapterBase(BaseAdapter):
    """Common scaffolding for single-turn LLM baselines."""

    agent_name: str = "llm-adapter"
    fixture_budget_kb: int = 8

    def run(self, task: TaskSpec, workspace: Path) -> Submission:
        out_key = OUTPUT_KEY_BY_KIND[task.expected_outputs.kind]
        user = build_user_message(task, workspace, self.fixture_budget_kb * 1024)
        t0 = time.monotonic()
        text, meta = self._chat(SYSTEM_PROMPT, user)
        wall = f"{time.monotonic() - t0:.2f}"
        return Submission(
            task_id=task.task_id,
            agent_name=self.agent_name,
            outputs={out_key: strip_code_fence(text)},
            metadata={"wall_time_seconds": wall, **meta},
        )

    def _chat(self, system: str, user: str) -> tuple[str, dict[str, str]]:
        raise NotImplementedError
