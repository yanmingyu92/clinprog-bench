"""Documentation scorer for T4 tasks.

Primary metric: slot-fill exact-match rate over text content.
Secondary metric: regex style-lint score (formatting conventions).
"""

from __future__ import annotations

import re
from typing import Any

from clinprog_bench.scorers import BaseScorer, Score
from clinprog_bench.scorers._utils import (
    extract_content,
    normalize_text,
    read_gold,
)

# Submission output keys for T4 tasks.
_T4_KEYS = ["document.md", "document.sas", "document.txt"]


class DocScorer(BaseScorer):
    """Scorer for T4 documentation tasks.

    Primary metric: slot-fill exact-match rate.
    Secondary: regex style-lint score.
    """

    def score(
        self,
        task: Any,
        submission: Any,
        gold: Any,
    ) -> Score:
        oracle_type = task.expected_outputs.oracle.type
        if oracle_type == "slot_fill":
            return self._score_slot_fill(task, submission, gold)
        msg = f"Unsupported oracle type: {oracle_type}"
        raise ValueError(msg)

    # ------------------------------------------------------------------
    # slot_fill path
    # ------------------------------------------------------------------

    def _score_slot_fill(self, task: Any, submission: Any, gold: Any) -> Score:
        params = task.expected_outputs.oracle.params
        slots: list[str] = params.get("slots", [])
        match_mode: str = params.get("match_mode", "exact")

        gold_text = read_gold(gold)
        sub_text = extract_content(submission, _T4_KEYS)

        if not sub_text.strip():
            return Score(
                task_id=task.task_id,
                category=task.category,
                pass_flag=False,
                primary_metric=0.0,
                secondary_metrics={s: 0.0 for s in slots} | {"style_lint": 0.0},
            )

        total = len(slots)
        if total == 0:
            return Score(
                task_id=task.task_id,
                category=task.category,
                pass_flag=True,
                primary_metric=1.0,
                secondary_metrics={"style_lint": self._style_lint(sub_text)},
            )

        matched = 0
        secondary: dict[str, float] = {}

        for slot in slots:
            gold_vals = self._extract_text_slot(gold_text, slot)
            sub_vals = self._extract_text_slot(sub_text, slot)
            if self._compare_slot_values(gold_vals, sub_vals, match_mode):
                matched += 1
                secondary[slot] = 1.0
            else:
                secondary[slot] = 0.0

        rate = matched / total
        secondary["style_lint"] = self._style_lint(sub_text)

        return Score(
            task_id=task.task_id,
            category=task.category,
            pass_flag=rate >= 0.5,
            primary_metric=rate,
            secondary_metrics=secondary,
        )

    # ------------------------------------------------------------------
    # Text slot extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_text_slot(text: str, slot: str) -> set[str]:
        """Extract slot values from text content.

        Handles both array slots (``field[].subfield``) and scalar slots
        (``field_name``).
        """
        # Array-style slot: tables[].title, etc.
        if "[" in slot:
            return DocScorer._extract_array_slot(text, slot)

        # Scalar slot: use the slot name as a hint for extraction
        return DocScorer._extract_scalar_slot(text, slot)

    @staticmethod
    def _extract_array_slot(text: str, slot: str) -> set[str]:
        """Extract array-style slot values from text."""
        # Parse slot: "tables[].title" -> look for table titles
        match = re.match(r"(\w+)\[\]\.(\w+)", slot)
        if not match:
            return set()

        _parent = match.group(1)
        child = match.group(2)
        values: set[str] = set()

        # Common patterns in clinical documentation
        if child == "title":
            # "Table XX-XX.XX: Title" or "## Title" patterns
            for m in re.finditer(
                r"(?:Table\s+[\d.-]+|##)\s*[:.]?\s*(.+?)(?:\n|$)",
                text,
                re.IGNORECASE,
            ):
                val = m.group(1).strip()
                if val:
                    values.add(normalize_text(val))

        elif child == "population":
            for m in re.finditer(r"Population[:\s]+(.+?)(?:\n|$)", text, re.IGNORECASE):
                val = m.group(1).strip()
                if val:
                    values.add(normalize_text(val))

        elif child in ("row_categories", "row_categories[]"):
            # Look for bullet-point or dash-list items
            for m in re.finditer(r"[-*]\s+(.+?)(?::?\s*$|\n)", text, re.MULTILINE):
                val = m.group(1).strip()
                if val:
                    values.add(normalize_text(val))

        elif child == "data_source":
            for m in re.finditer(
                r"(?:Dataset|Data Source)[:\s]+(.+?)(?:\n|$)",
                text,
                re.IGNORECASE,
            ):
                val = m.group(1).strip()
                if val:
                    values.add(normalize_text(val))

        else:
            # Generic: look for "child: value" patterns
            pattern = rf"{child}[:\s]+(.+?)(?:\n|$)"
            for m in re.finditer(pattern, text, re.IGNORECASE):
                val = m.group(1).strip()
                if val:
                    values.add(normalize_text(val))

        return values

    @staticmethod
    def _extract_scalar_slot(text: str, slot: str) -> set[str]:
        """Extract scalar slot value from text."""
        # Convert slot name to searchable patterns
        # e.g. "define_xml_version" -> "Define-XML Version"
        label = slot.replace("_", " ").replace("-", " ").strip()

        # Try various patterns
        patterns = [
            # Bold key: **Label**: Value
            rf"\* *\*{re.escape(label)}\* *\*[:\s]+(.+?)(?:\n|$)",
            # Key: Value (in list)
            rf"^- {re.escape(label)}[:\s]+(.+?)(?:\n|$)",
            # Key: Value (standalone)
            rf"{re.escape(label)}[:\s]+(.+?)(?:\n|$)",
            # Numbered value pattern: "(N): Value"
            rf"{re.escape(label)}[^:\n]*?:\s*(\d+)",
        ]

        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if m:
                val = m.group(1).strip()
                if val:
                    return {normalize_text(val)}

        # Try extracting numbers associated with the label
        m = re.search(rf"{re.escape(label)}[^:\n]*?[:\s]+(\S+)", text, re.IGNORECASE)
        if m:
            return {normalize_text(m.group(1))}

        return set()

    # ------------------------------------------------------------------
    # Slot comparison
    # ------------------------------------------------------------------

    @staticmethod
    def _compare_slot_values(
        gold_vals: set[str],
        sub_vals: set[str],
        match_mode: str,
    ) -> bool:
        """Compare extracted slot value sets."""
        if not gold_vals:
            return True  # Nothing to match

        if match_mode == "exact":
            return gold_vals == sub_vals
        if match_mode == "superset":
            return gold_vals.issubset(sub_vals)
        return gold_vals == sub_vals

    # ------------------------------------------------------------------
    # Style lint
    # ------------------------------------------------------------------

    @staticmethod
    def _style_lint(text: str) -> float:
        """Compute a style-lint score (0..1) based on formatting rules.

        Checks:

        - No trailing whitespace on lines.
        - Consistent header usage.
        - No bare URLs (should be markdown links).
        - No excessively long lines (> 120 chars).
        """
        if not text.strip():
            return 0.0

        lines = text.split("\n")
        total_checks = 0
        passed_checks = 0

        # Check 1: No trailing whitespace
        for line in lines:
            if line.rstrip() != line and line.strip():
                # Has content + trailing whitespace
                pass
            else:
                passed_checks += 1
            total_checks += 1

        # Check 2: Header structure (has at least one ## header)
        has_headers = bool(re.search(r"^#{1,6}\s+\S", text, re.MULTILINE))
        total_checks += 1
        if has_headers:
            passed_checks += 1

        # Check 3: No bare URLs
        bare_urls = re.findall(r"(?<!\()https?://\S+", text)
        total_checks += 1
        if not bare_urls:
            passed_checks += 1

        # Check 4: Line length (proportion under 120)
        long_lines = sum(1 for line in lines if len(line) > 120)
        total_checks += 1
        if long_lines == 0:
            passed_checks += 1

        return passed_checks / total_checks if total_checks > 0 else 1.0


__all__ = ["DocScorer"]
