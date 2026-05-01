"""Runner modules for ClinProg-Bench."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from clinprog_bench.schema import TaskSpec


@dataclass(frozen=True)
class Submission:
    """Immutable record of an agent's submission for one task."""

    task_id: str
    agent_name: str
    outputs: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, str] = field(default_factory=dict)


class BaseAdapter(ABC):
    """Abstract base class for agent adapters.

    An adapter wraps an agent (or baseline) so it can participate in the
    benchmark evaluation pipeline.
    """

    agent_name: str

    @abstractmethod
    def run(self, task: TaskSpec, workspace: Path) -> Submission:
        """Execute the agent on a single task.

        Args:
            task: The task specification.
            workspace: Path to a writable workspace directory with fixtures.

        Returns:
            A ``Submission`` containing the agent's outputs.
        """
        ...


__all__ = ["BaseAdapter", "Submission"]
