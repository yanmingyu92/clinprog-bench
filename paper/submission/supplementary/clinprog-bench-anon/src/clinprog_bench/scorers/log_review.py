"""Log review scorer for T2 tasks.

Computes a TP / FP / FN confusion matrix by matching agent-reported
issues against gold issues using (severity, category) tuples, then
derives F1 as the primary metric.
"""

from __future__ import annotations

from typing import Any

from clinprog_bench.scorers import BaseScorer, Score
from clinprog_bench.scorers._utils import (
    compute_f1,
    extract_content,
    extract_json,
    parse_json_path,
    read_gold,
)

# Submission output keys for T2 tasks.
_T2_KEYS = ["review.json"]

# Known array field names in T2 JSON outputs.
_ISSUE_ARRAY_FIELDS = ["issues", "discrepancies", "findings"]


class LogReviewScorer(BaseScorer):
    """Scorer for T2 code review tasks.

    Primary metric: F1 over the seeded-defect set (TP, FP, FN at
    severity + category granularity).
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
        if oracle_type == "confusion_matrix":
            return self._score_confusion_matrix(task, submission, gold)
        msg = f"Unsupported oracle type: {oracle_type}"
        raise ValueError(msg)

    # ------------------------------------------------------------------
    # slot_fill path
    # ------------------------------------------------------------------

    def _score_slot_fill(self, task: Any, submission: Any, gold: Any) -> Score:
        params = task.expected_outputs.oracle.params
        slots: list[str] = params.get("slots", [])
        match_mode: str = params.get("match_mode", "superset")

        gold_text = read_gold(gold)
        sub_text = extract_content(submission, _T2_KEYS)

        if not sub_text.strip():
            return Score(
                task_id=task.task_id,
                category=task.category,
                pass_flag=False,
                primary_metric=0.0,
                secondary_metrics={"precision": 0.0, "recall": 0.0},
            )

        try:
            import json

            gold_data: dict[str, Any] = json.loads(gold_text)
            sub_data: dict[str, Any] = json.loads(sub_text)
        except (json.JSONDecodeError, TypeError):
            return Score(
                task_id=task.task_id,
                category=task.category,
                pass_flag=False,
                primary_metric=0.0,
            )

        # Extract (severity, category) tuples from gold and submission
        gold_tuples = self._extract_issue_tuples(gold_data)
        sub_tuples = self._extract_issue_tuples(sub_data)

        tp, fp, fn = self._compute_confusion(sub_tuples, gold_tuples, match_mode)
        f1 = compute_f1(tp, fp, fn)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        # Also compute per-slot match rates
        secondary: dict[str, float] = {
            "precision": precision,
            "recall": recall,
            "tp": float(tp),
            "fp": float(fp),
            "fn": float(fn),
        }

        for slot in slots:
            gold_vals = set(parse_json_path(gold_data, slot))
            sub_vals = set(parse_json_path(sub_data, slot))
            if match_mode == "superset":
                secondary[slot] = 1.0 if gold_vals.issubset(sub_vals) else 0.0
            else:
                secondary[slot] = 1.0 if gold_vals == sub_vals else 0.0

        return Score(
            task_id=task.task_id,
            category=task.category,
            pass_flag=f1 >= 0.5,
            primary_metric=f1,
            secondary_metrics=secondary,
        )

    # ------------------------------------------------------------------
    # confusion_matrix path
    # ------------------------------------------------------------------

    def _score_confusion_matrix(self, task: Any, submission: Any, gold: Any) -> Score:
        params = task.expected_outputs.oracle.params
        expected_tp: int = params.get("expected_tp", 0)
        expected_fn: int = params.get("expected_fn", 0)

        sub_data = extract_json(submission, _T2_KEYS)

        if not sub_data:
            return Score(
                task_id=task.task_id,
                category=task.category,
                pass_flag=False,
                primary_metric=0.0,
            )

        sub_tuples = self._extract_issue_tuples(sub_data)
        # In confusion_matrix mode, every reported issue counts
        reported = len(sub_tuples)
        tp = min(reported, expected_tp)
        fp = max(0, reported - expected_tp)
        fn = max(0, expected_tp - tp)
        f1 = compute_f1(tp, fp, fn)

        return Score(
            task_id=task.task_id,
            category=task.category,
            pass_flag=f1 >= 0.5,
            primary_metric=f1,
            secondary_metrics={
                "tp": float(tp),
                "fp": float(fp),
                "fn": float(fn + expected_fn),
            },
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_issue_tuples(data: dict[str, Any]) -> set[tuple[str, str]]:
        """Extract (severity, category) tuples from a review JSON."""
        tuples: set[tuple[str, str]] = set()

        for field in _ISSUE_ARRAY_FIELDS:
            items = data.get(field)
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        severity = str(item.get("severity", "")).lower().strip()
                        category = str(item.get("category", "")).lower().strip()
                        if severity and category:
                            tuples.add((severity, category))

        return tuples

    @staticmethod
    def _compute_confusion(
        sub_tuples: set[tuple[str, str]],
        gold_tuples: set[tuple[str, str]],
        match_mode: str,
    ) -> tuple[int, int, int]:
        """Compute TP, FP, FN for issue matching."""
        tp = len(sub_tuples & gold_tuples)
        fp = len(sub_tuples - gold_tuples)

        if match_mode == "superset":
            # Extra submissions are acceptable, not false positives
            fp = 0
            fn = len(gold_tuples - sub_tuples)
        else:
            fn = len(gold_tuples - sub_tuples)

        return tp, fp, fn


__all__ = ["LogReviewScorer"]
