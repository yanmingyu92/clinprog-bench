"""Task schema definitions and validation for ClinProg-Bench."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, Field, model_validator

if TYPE_CHECKING:
    from pathlib import Path


TASK_ID_PATTERN = r"^T[1-5]\.[1-9][0-9]?\.[a-z0-9_]+\.[0-9]{3}$"
SHA40_PATTERN = r"^[0-9a-f]{40}$"

OracleType = Literal[
    "dataset_diff",
    "set_match",
    "confusion_matrix",
    "patch_apply",
    "slot_fill",
]
OutputKind = Literal[
    "sas_program", "r_program", "python_program", "json", "patch", "text"
]
Category = Literal["T1", "T2", "T3", "T4", "T5"]
Complexity = Literal["simple", "mixed", "complex"]
ScorerName = Literal["codegen", "log_review", "spec_extract", "doc", "debug"]

CATEGORY_SCORER_MAP: dict[Category, ScorerName] = {
    "T1": "codegen",
    "T2": "log_review",
    "T3": "spec_extract",
    "T4": "doc",
    "T5": "debug",
}


class Provenance(BaseModel):
    """Provenance metadata linking a task to its public seed substrate."""

    seed_repo: str
    seed_commit: str = Field(pattern=SHA40_PATTERN)
    derivation_script: str
    human_authors: list[str] = Field(min_length=1)
    human_reviewers: list[str] = Field(min_length=1)


class TaskInputs(BaseModel):
    """Input specification for a benchmark task."""

    fixtures: list[str] = Field(min_length=1)
    spec: str
    prompt: str


class Oracle(BaseModel):
    """Oracle configuration for automated evaluation."""

    type: OracleType
    params: dict[str, object] = Field(default_factory=dict)


class ExpectedOutputs(BaseModel):
    """Expected output specification."""

    kind: OutputKind
    gold_path: str
    oracle: Oracle


class Scoring(BaseModel):
    """Scoring configuration for a task."""

    scorer: ScorerName
    weight: float = Field(ge=0.0, le=1.0)


class LeakageAudit(BaseModel):
    """Leakage audit results for a task."""

    fixture_sha256_overlap: bool
    prompt_ngram_hits: int = Field(ge=0)


class TaskSpec(BaseModel):
    """Complete specification for a single benchmark task.

    Every task JSON file under ``tasks/`` must validate against this model.
    """

    task_id: str = Field(pattern=TASK_ID_PATTERN)
    category: Category
    subcategory: str
    title: str
    complexity: Complexity
    difficulty_tag: str | None = None
    license: str = "CC-BY-4.0"
    provenance: Provenance
    inputs: TaskInputs
    expected_outputs: ExpectedOutputs
    scoring: Scoring
    leakage_audit: LeakageAudit

    @model_validator(mode="after")
    def _validate_category_scorer(self) -> TaskSpec:
        expected_scorer = CATEGORY_SCORER_MAP[self.category]
        if self.scoring.scorer != expected_scorer:
            msg = (
                f"Category {self.category} requires scorer "
                f"'{expected_scorer}', got '{self.scoring.scorer}'"
            )
            raise ValueError(msg)
        return self


def validate_task_file(path: Path) -> TaskSpec:
    """Validate a single task JSON file and return the parsed TaskSpec.

    Args:
        path: Path to a ``.json`` task file.

    Returns:
        Validated ``TaskSpec`` instance.

    Raises:
        pydantic.ValidationError: If the file does not conform to the schema.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    with open(path) as f:
        data: dict[str, object] = json.load(f)
    return TaskSpec.model_validate(data)


def validate_tasks_dir(tasks_dir: Path) -> list[TaskSpec]:
    """Validate all task JSON files in a directory tree.

    Skips ``_schema.json`` at any depth.

    Args:
        tasks_dir: Path to the ``tasks/`` directory.

    Returns:
        Sorted list of validated ``TaskSpec`` objects.
    """
    tasks: list[TaskSpec] = []
    for json_file in sorted(tasks_dir.rglob("*.json")):
        if json_file.name == "_schema.json":
            continue
        tasks.append(validate_task_file(json_file))
    return tasks


__all__ = [
    "Category",
    "CATEGORY_SCORER_MAP",
    "Complexity",
    "ExpectedOutputs",
    "LeakageAudit",
    "Oracle",
    "OracleType",
    "OutputKind",
    "Provenance",
    "ScorerName",
    "Scoring",
    "SHA40_PATTERN",
    "TASK_ID_PATTERN",
    "TaskInputs",
    "TaskSpec",
    "validate_task_file",
    "validate_tasks_dir",
]
