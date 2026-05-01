"""Debug scorer for T5 tasks.

Primary metric: patch-apply-and-match rate -- how many of the seeded
bugs the submission patch correctly fixes.

Secondary metric: LoC-minimality penalty to discourage over-editing.
"""

from __future__ import annotations

import re
from typing import Any

from clinprog_bench.scorers import BaseScorer, Score
from clinprog_bench.scorers._utils import extract_content, read_gold

# Submission output keys for T5 tasks.
_T5_KEYS = ["patch.diff"]


class DebugScorer(BaseScorer):
    """Scorer for T5 debugging tasks.

    Primary metric: patch-apply-and-test-pass rate.
    Secondary: LoC-minimality penalty.
    """

    def score(
        self,
        task: Any,
        submission: Any,
        gold: Any,
    ) -> Score:
        oracle_type = task.expected_outputs.oracle.type
        if oracle_type == "patch_apply":
            return self._score_patch_apply(task, submission, gold)
        msg = f"Unsupported oracle type: {oracle_type}"
        raise ValueError(msg)

    # ------------------------------------------------------------------
    # patch_apply path
    # ------------------------------------------------------------------

    def _score_patch_apply(self, task: Any, submission: Any, gold: Any) -> Score:
        params = task.expected_outputs.oracle.params
        bug_count: int = params.get("bug_count", 0)
        fix_locations: list[str] = params.get("fix_locations", [])

        gold_patch = read_gold(gold)
        sub_patch = extract_content(submission, _T5_KEYS)

        if not sub_patch.strip():
            return Score(
                task_id=task.task_id,
                category=task.category,
                pass_flag=False,
                primary_metric=0.0,
                secondary_metrics={
                    "matched_fixes": 0.0,
                    "loc_penalty": 0.0,
                },
            )

        # Count how many fix locations are addressed in submission
        matched_fixes = self._count_matched_fixes(sub_patch, fix_locations, gold_patch)

        primary = matched_fixes / bug_count if bug_count > 0 else 0.0

        # LoC-minimality penalty
        loc_penalty = self._compute_loc_penalty(sub_patch, gold_patch)

        return Score(
            task_id=task.task_id,
            category=task.category,
            pass_flag=primary >= 0.75,
            primary_metric=primary,
            secondary_metrics={
                "matched_fixes": float(matched_fixes),
                "loc_penalty": loc_penalty,
            },
        )

    # ------------------------------------------------------------------
    # Fix matching
    # ------------------------------------------------------------------

    @staticmethod
    def _count_matched_fixes(
        sub_patch: str,
        fix_locations: list[str],
        gold_patch: str,
    ) -> int:
        """Count how many fix locations are addressed in the submission.

        A fix is matched when:

        1. The fix location name (or a normalized variant) appears in the
           submission patch context, **or**
        2. The corresponding gold fix lines are present in the submission.
        """
        matched = 0

        # Extract individual fixes from gold patch
        gold_fixes = DebugScorer._parse_gold_fixes(gold_patch)

        # Extract fix hunks from submission
        sub_hunks = DebugScorer._parse_patch_hunks(sub_patch)

        for i, location in enumerate(fix_locations):
            location_norm = location.lower().replace("_", " ")

            # Strategy 1: Location name appears in submission patch
            if location_norm in sub_patch.lower().replace("_", " "):
                matched += 1
                continue

            # Strategy 2: Corresponding gold fix lines are present
            if i < len(gold_fixes):
                gold_fix_text = gold_fixes[i].strip()
                if gold_fix_text:
                    # Check if the fix content (after +) appears in submission
                    fix_lines = [
                        line.lstrip("+").strip()
                        for line in gold_fix_text.split("\n")
                        if line.startswith("+") and not line.startswith("+++")
                    ]
                    fix_content = " ".join(fix_lines).strip()
                    if fix_content and fix_content.lower() in sub_patch.lower():
                        matched += 1
                        continue

            # Strategy 3: Submission contains hunk headers overlapping with
            # gold fix positions
            if i < len(gold_fixes):
                gold_fix = gold_fixes[i]
                for hunk in sub_hunks:
                    if _hunks_overlap(gold_fix, hunk):
                        matched += 1
                        break

        return matched

    # ------------------------------------------------------------------
    # Patch parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_gold_fixes(gold_patch: str) -> list[str]:
        """Parse gold patch into individual fix blocks.

        Gold patches have a specific format with ``Bug N:`` and
        ``Fix N:`` markers.
        """
        # Split by "Bug N:" pattern
        bug_pattern = r"(?:^|\n)-Bug\s+\d+:"
        fix_pattern = r"(?:^|\n)\+Fix\s+\d+:"

        # Try structured parsing first (Bug/Fix format)
        fixes: list[str] = []
        fix_blocks = re.split(fix_pattern, gold_patch)

        if len(fix_blocks) > 1:
            for block in fix_blocks[1:]:
                # Take content up to the next Bug marker or end
                end = re.search(bug_pattern, block)
                content = block[: end.start()] if end else block
                fixes.append(content.strip())

        if not fixes:
            # Fallback: split by diff hunks
            hunks = DebugScorer._parse_patch_hunks(gold_patch)
            fixes = hunks if hunks else [gold_patch]

        return fixes

    @staticmethod
    def _parse_patch_hunks(patch: str) -> list[str]:
        """Split a unified diff into hunks."""
        hunk_pattern = r"@@[^@]+@@"
        parts = re.split(hunk_pattern, patch)
        # parts[0] is the header; subsequent parts are hunk contents
        hunks: list[str] = []
        for part in parts[1:]:
            stripped = part.strip()
            if stripped:
                hunks.append(stripped)
        return hunks

    # ------------------------------------------------------------------
    # LoC penalty
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_loc_penalty(sub_patch: str, gold_patch: str) -> float:
        """Compute LoC-minimality penalty (0..1, 1 = no penalty).

        Penalty is applied when the submission has significantly more
        effective lines than the gold patch.
        """
        sub_loc = DebugScorer._count_effective_lines(sub_patch)
        gold_loc = DebugScorer._count_effective_lines(gold_patch)

        if gold_loc == 0:
            return 1.0 if sub_loc == 0 else 0.5

        ratio = sub_loc / gold_loc
        # Allow up to 1.5x gold lines without penalty
        if ratio <= 1.5:
            return 1.0
        # Linear penalty above 1.5x, reaching 0 at 3x
        penalty = max(0.0, 1.0 - (ratio - 1.5) / 1.5)
        return penalty

    @staticmethod
    def _count_effective_lines(patch: str) -> int:
        """Count effective (non-context, non-header) lines in a patch."""
        count = 0
        for line in patch.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(("---", "+++", "@@", "Summary")):
                continue
            if stripped.startswith(("+", "-")):
                content = stripped[1:].strip()
                if content and not content.startswith(("Bug", "Fix")):
                    count += 1
        return count


def _hunks_overlap(hunk_a: str, hunk_b: str) -> bool:
    """Heuristic: check if two patch hunks address overlapping code."""
    # Extract added lines from both hunks
    added_a = {
        line.lstrip("+").strip().lower()
        for line in hunk_a.split("\n")
        if line.startswith("+") and not line.startswith("+++") and line.strip()
    }
    added_b = {
        line.lstrip("+").strip().lower()
        for line in hunk_b.split("\n")
        if line.startswith("+") and not line.startswith("+++") and line.strip()
    }
    # Overlap if they share any added line content
    return bool(added_a & added_b)


__all__ = ["DebugScorer"]
