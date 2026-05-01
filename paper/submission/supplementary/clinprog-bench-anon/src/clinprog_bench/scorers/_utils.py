"""Shared utilities for scorer modules."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def resolve_gold_path(gold: str | Path) -> Path:
    """Resolve gold parameter to the actual gold output file."""
    p = Path(gold)
    if p.is_file():
        return p
    if p.is_dir():
        candidates = sorted(p.glob("expected_output.*"))
        if candidates:
            return candidates[0]
    raise FileNotFoundError(f"No gold output found at {gold}")


def read_gold(gold: str | Path) -> str:
    """Read gold output file content as UTF-8 string."""
    return resolve_gold_path(gold).read_text(encoding="utf-8")


def extract_content(submission: Any, keys: list[str] | None = None) -> str:
    """Extract string content from a submission of any supported type.

    Handles: str, Path, dict, or Submission-like objects with an
    ``outputs`` attribute.
    """
    if isinstance(submission, str):
        return submission
    if isinstance(submission, Path):
        return submission.read_text(encoding="utf-8")
    if isinstance(submission, dict):
        if keys:
            for key in keys:
                if key in submission:
                    val: str = submission[key]
                    return val
        if submission:
            first_val: str = next(iter(submission.values()))
            return first_val
        return ""
    # Duck-type for Submission dataclass
    outputs = getattr(submission, "outputs", None)
    if isinstance(outputs, dict):
        if keys:
            for key in keys:
                if key in outputs:
                    out_val: str = outputs[key]
                    return out_val
        if outputs:
            out_first: str = next(iter(outputs.values()))
            return out_first
    return ""


def extract_json(submission: Any, keys: list[str] | None = None) -> dict[str, Any]:
    """Extract and parse JSON content from a submission."""
    content = extract_content(submission, keys)
    if not content.strip():
        return {}
    try:
        result: dict[str, Any] = json.loads(content)
        return result
    except (json.JSONDecodeError, TypeError):
        return {}


def parse_json_path(data: dict[str, Any], path: str) -> list[str]:
    """Extract values from JSON using simple path notation.

    Supported patterns:

    - ``"field"`` -- simple field lookup.
    - ``"field[].subfield"`` -- iterate array and collect sub-field values.
    - ``"field1.field2"`` -- nested field lookup.
    """
    parts = path.split(".")
    current: Any = data

    for i, part in enumerate(parts):
        if current is None:
            return []
        if part.endswith("[]"):
            field_name = part[:-2]
            if isinstance(current, dict) and field_name in current:
                current = current[field_name]
                if isinstance(current, list):
                    remaining = ".".join(parts[i + 1 :])
                    if remaining:
                        results: list[str] = []
                        for item in current:
                            if isinstance(item, dict):
                                sub_results = parse_json_path(item, remaining)
                                results.extend(sub_results)
                        return results
                    return [str(item) for item in current]
            return []
        else:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return []

    if current is None:
        return []
    if isinstance(current, list):
        return [str(item) for item in current]
    return [str(current)]


def normalize_text(text: str) -> str:
    """Normalize text: lowercase, collapse whitespace, strip."""
    return re.sub(r"\s+", " ", text.strip().lower())


def compute_f1(tp: int, fp: int, fn: int) -> float:
    """Compute F1 score from confusion matrix counts."""
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    if (precision + recall) == 0.0:
        return 0.0
    return 2.0 * precision * recall / (precision + recall)


def compute_set_metrics(pred: set[str], gold: set[str]) -> tuple[float, float, float]:
    """Compute (F1, precision, recall) for two string sets."""
    tp = len(pred & gold)
    fp = len(pred - gold)
    fn = len(gold - pred)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2.0 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    return f1, precision, recall
