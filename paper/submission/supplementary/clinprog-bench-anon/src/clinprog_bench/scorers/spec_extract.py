"""Spec extraction scorer for T3 tasks.

Primary metric: exact-set-match for variables; F1 for derivations.
Handles both ``slot_fill`` and ``set_match`` oracle types.
"""

from __future__ import annotations

from typing import Any

from clinprog_bench.scorers import BaseScorer, Score
from clinprog_bench.scorers._utils import (
    compute_set_metrics,
    extract_content,
    parse_json_path,
    read_gold,
)

# Submission output keys for T3 tasks.
_T3_KEYS = ["extraction.json"]


class SpecExtractScorer(BaseScorer):
    """Scorer for T3 spec interpretation tasks.

    Primary metric: exact-set-match for variables; F1 for derivations.
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
        if oracle_type == "set_match":
            return self._score_set_match(task, submission, gold)
        msg = f"Unsupported oracle type: {oracle_type}"
        raise ValueError(msg)

    # ------------------------------------------------------------------
    # slot_fill path
    # ------------------------------------------------------------------

    def _score_slot_fill(self, task: Any, submission: Any, gold: Any) -> Score:
        params = task.expected_outputs.oracle.params
        slots: list[str] = params.get("slots", [])

        gold_text = read_gold(gold)
        sub_text = extract_content(submission, _T3_KEYS)

        if not sub_text.strip():
            return Score(
                task_id=task.task_id,
                category=task.category,
                pass_flag=False,
                primary_metric=0.0,
                secondary_metrics={s: 0.0 for s in slots},
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

        if not slots:
            return Score(
                task_id=task.task_id,
                category=task.category,
                pass_flag=True,
                primary_metric=1.0,
            )

        # Compute per-slot F1 and overall metrics
        total_f1 = 0.0
        secondary: dict[str, float] = {}
        all_tp, all_fp, all_fn = 0, 0, 0

        for slot in slots:
            gold_vals = set(parse_json_path(gold_data, slot))
            sub_vals = set(parse_json_path(sub_data, slot))

            f1, precision, recall = compute_set_metrics(sub_vals, gold_vals)
            secondary[slot] = f1
            secondary[f"{slot}_precision"] = precision
            secondary[f"{slot}_recall"] = recall
            total_f1 += f1

            tp = len(sub_vals & gold_vals)
            fp = len(sub_vals - gold_vals)
            fn = len(gold_vals - sub_vals)
            all_tp += tp
            all_fp += fp
            all_fn += fn

        # Primary metric: average slot F1 (micro-averaged)
        macro_f1 = total_f1 / len(slots)
        micro_f1, _, _ = compute_set_metrics(set(), set())  # placeholder
        from clinprog_bench.scorers._utils import compute_f1

        micro_f1 = compute_f1(all_tp, all_fp, all_fn)

        # Use macro F1 as primary, micro F1 as secondary
        primary = macro_f1
        secondary["micro_f1"] = micro_f1

        # Determine exact match
        exact_match = all(
            set(parse_json_path(gold_data, slot))
            == set(parse_json_path(sub_data, slot))
            for slot in slots
        )
        secondary["exact_match"] = float(exact_match)

        return Score(
            task_id=task.task_id,
            category=task.category,
            pass_flag=primary >= 0.5,
            primary_metric=primary,
            secondary_metrics=secondary,
        )

    # ------------------------------------------------------------------
    # set_match path
    # ------------------------------------------------------------------

    def _score_set_match(self, task: Any, submission: Any, gold: Any) -> Score:
        params = task.expected_outputs.oracle.params
        expected_set: list[str] = params.get("expected_set", [])
        match_mode: str = params.get("match_mode", "exact")

        gold_text = read_gold(gold)
        sub_text = extract_content(submission, _T3_KEYS)

        if not sub_text.strip():
            return Score(
                task_id=task.task_id,
                category=task.category,
                pass_flag=False,
                primary_metric=0.0,
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

        gold_set = set(expected_set) if expected_set else set()

        # Try to extract items from submission
        sub_set: set[str] = set()
        for field in ("variables", "domains", "items"):
            items = sub_data.get(field)
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        name = item.get("variable_name") or item.get("domain_code")
                        if name:
                            sub_set.add(str(name))
                    elif isinstance(item, str):
                        sub_set.add(item)

        # Also extract from gold if expected_set is empty
        if not gold_set:
            for field in ("variables", "domains", "items"):
                items = gold_data.get(field)
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            name = item.get("variable_name") or item.get("domain_code")
                            if name:
                                gold_set.add(str(name))

        f1, precision, recall = compute_set_metrics(sub_set, gold_set)

        if match_mode == "exact":
            primary = 1.0 if sub_set == gold_set else f1
        elif match_mode == "superset":
            primary = 1.0 if gold_set.issubset(sub_set) else f1
        else:
            primary = f1

        return Score(
            task_id=task.task_id,
            category=task.category,
            pass_flag=primary >= 0.5,
            primary_metric=primary,
            secondary_metrics={
                "f1": f1,
                "precision": precision,
                "recall": recall,
            },
        )


__all__ = ["SpecExtractScorer"]
