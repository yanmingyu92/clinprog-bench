"""Scoring modules for ClinProg-Bench."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Score:
    """Immutable score for a single task evaluation."""

    task_id: str
    category: str
    pass_flag: bool
    primary_metric: float
    secondary_metrics: dict[str, float] = field(default_factory=dict)


class BaseScorer(ABC):
    """Abstract base class for all category scorers."""

    @abstractmethod
    def score(
        self,
        task: Any,
        submission: Any,
        gold: Any,
    ) -> Score:
        """Score a submission against the gold standard.

        Args:
            task: The TaskSpec for the task.
            submission: The agent's submission output.
            gold: Path to the gold-standard output.

        Returns:
            A Score object with evaluation results.
        """
        ...


__all__ = ["BaseScorer", "Score"]
