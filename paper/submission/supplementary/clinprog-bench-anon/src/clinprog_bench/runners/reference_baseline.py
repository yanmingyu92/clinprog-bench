"""Reference baseline adapter (rule-based, no LLM).

Produces deterministic, category-appropriate outputs so the scorer
layer can be validated independently of any LLM.  Three reruns with
the same inputs produce bit-identical results.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from clinprog_bench.runners import BaseAdapter, Submission

if TYPE_CHECKING:
    from pathlib import Path

    from clinprog_bench.schema import TaskSpec


class ReferenceBaseline(BaseAdapter):
    """Rule-based reference baseline that produces deterministic outputs.

    For each category the baseline returns the simplest valid structure
    that satisfies the submission format contract (see
    ``runners/contract.md``).  No external state, no randomness, no
    LLM calls -- pure string templates.
    """

    agent_name = "reference-baseline"

    def run(self, task: TaskSpec, workspace: Path) -> Submission:
        """Return a deterministic submission for *task*."""
        outputs = self._generate_outputs(task)
        return Submission(
            task_id=task.task_id,
            agent_name=self.agent_name,
            outputs=outputs,
        )

    # ------------------------------------------------------------------
    # Category-specific deterministic output generation
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_outputs(task: TaskSpec) -> dict[str, str]:
        """Produce deterministic outputs based on task category."""
        category = task.category
        output_kind = task.expected_outputs.kind

        if category == "T1":
            return ReferenceBaseline._t1_output(output_kind, task)
        if category == "T2":
            return ReferenceBaseline._t2_output()
        if category == "T3":
            return ReferenceBaseline._t3_output()
        if category == "T4":
            return ReferenceBaseline._t4_output()
        if category == "T5":
            return ReferenceBaseline._t5_output()
        return {}

    @staticmethod
    def _t1_output(kind: str, task: TaskSpec) -> dict[str, str]:
        """T1 code generation: minimal program skeleton."""
        if kind == "sas_program":
            code = (
                f"/* Reference baseline for {task.task_id} */\n"
                "libname raw 'path/to/raw' access=readonly;\n"
                "libname out 'path/to/output';\n"
                "proc sort data=raw.src; by USUBJID; run;\n"
            )
            return {"main.sas": code}
        if kind == "r_program":
            code = (
                f"# Reference baseline for {task.task_id}\n"
                "library(dplyr)\n"
                "df <- read.csv('input.csv')\n"
            )
            return {"main.R": code}
        if kind == "python_program":
            code = (
                f"# Reference baseline for {task.task_id}\n"
                "import pandas as pd\n"
                "df = pd.read_csv('input.csv')\n"
            )
            return {"main.py": code}
        return {}

    @staticmethod
    def _t2_output() -> dict[str, str]:
        """T2 code review: empty issues list."""
        return {"review.json": json.dumps({"issues": []})}

    @staticmethod
    def _t3_output() -> dict[str, str]:
        """T3 spec extraction: empty variables list."""
        return {"extraction.json": json.dumps({"variables": []})}

    @staticmethod
    def _t4_output() -> dict[str, str]:
        """T4 documentation: minimal text."""
        return {"document.md": ""}

    @staticmethod
    def _t5_output() -> dict[str, str]:
        """T5 debugging: empty patch."""
        return {"patch.diff": ""}


__all__ = ["ReferenceBaseline"]
