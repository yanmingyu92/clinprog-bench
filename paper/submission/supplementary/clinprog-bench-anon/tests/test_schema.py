"""Tests for task schema validation."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

if TYPE_CHECKING:
    from pathlib import Path

from clinprog_bench.schema import (
    CATEGORY_SCORER_MAP,
    TaskSpec,
    validate_task_file,
    validate_tasks_dir,
)


def _sample_task_data(**overrides: object) -> dict[str, object]:
    """Build a minimal valid task JSON dict, with optional overrides."""
    base: dict[str, object] = {
        "task_id": "T1.1.adsl.001",
        "category": "T1",
        "subcategory": "T1.1",
        "title": "Derive ADSL TRT01PN from DM.ARM",
        "complexity": "simple",
        "license": "CC-BY-4.0",
        "provenance": {
            "seed_repo": "anonymous/eSubmission-Benchmark",
            "seed_commit": "a" * 40,
            "derivation_script": "scripts/build_T1.1.py",
            "human_authors": ["R01"],
            "human_reviewers": ["R02"],
        },
        "inputs": {
            "fixtures": ["fixtures/04_sdtm/datasets/dm.xpt"],
            "spec": "fixtures/05_adam/ADaM_Specifications.xlsx#ADSL",
            "prompt": "Generate SAS code that produces ADSL.TRT01PN",
        },
        "expected_outputs": {
            "kind": "sas_program",
            "gold_path": "gold/T1.1.adsl.001/",
            "oracle": {
                "type": "dataset_diff",
                "params": {"primary_key": ["USUBJID"], "tolerance": 0},
            },
        },
        "scoring": {"scorer": "codegen", "weight": 1.0},
        "leakage_audit": {"fixture_sha256_overlap": False, "prompt_ngram_hits": 0},
    }
    base.update(overrides)
    return base


def test_valid_task_spec() -> None:
    data = _sample_task_data()
    spec = TaskSpec.model_validate(data)
    assert spec.task_id == "T1.1.adsl.001"
    assert spec.category == "T1"
    assert spec.scoring.scorer == "codegen"


def test_invalid_task_id_pattern() -> None:
    data = _sample_task_data(task_id="invalid_id")
    with pytest.raises(ValidationError, match="task_id"):
        TaskSpec.model_validate(data)


def test_invalid_category() -> None:
    data = _sample_task_data(
        category="T6", scoring={"scorer": "codegen", "weight": 1.0}
    )
    with pytest.raises(ValidationError, match="category"):
        TaskSpec.model_validate(data)


def test_category_scorer_mismatch() -> None:
    data = _sample_task_data(scoring={"scorer": "debug", "weight": 1.0})
    with pytest.raises(ValidationError, match="requires scorer"):
        TaskSpec.model_validate(data)


def test_invalid_seed_commit() -> None:
    provenance: dict[str, object] = {
        "seed_repo": "test/repo",
        "seed_commit": "not-a-sha",
        "derivation_script": "scripts/test.py",
        "human_authors": ["R01"],
        "human_reviewers": ["R02"],
    }
    data = _sample_task_data(provenance=provenance)
    with pytest.raises(ValidationError, match="seed_commit"):
        TaskSpec.model_validate(data)


def test_empty_authors_rejected() -> None:
    provenance: dict[str, object] = {
        "seed_repo": "test/repo",
        "seed_commit": "a" * 40,
        "derivation_script": "scripts/test.py",
        "human_authors": [],
        "human_reviewers": ["R02"],
    }
    data = _sample_task_data(provenance=provenance)
    with pytest.raises(ValidationError, match="human_authors"):
        TaskSpec.model_validate(data)


def test_oracle_type_enum() -> None:
    outputs: dict[str, object] = {
        "kind": "sas_program",
        "gold_path": "gold/test/",
        "oracle": {"type": "invalid_oracle", "params": {}},
    }
    data = _sample_task_data(expected_outputs=outputs)
    with pytest.raises(ValidationError):
        TaskSpec.model_validate(data)


def test_difficulty_tag_optional() -> None:
    data = _sample_task_data()
    assert "difficulty_tag" not in data
    spec = TaskSpec.model_validate(data)
    assert spec.difficulty_tag is None


def test_validate_task_file(tmp_path: Path) -> None:
    task_file = tmp_path / "T1.1.adsl.001.json"
    task_file.write_text(json.dumps(_sample_task_data()))
    spec = validate_task_file(task_file)
    assert spec.task_id == "T1.1.adsl.001"


def test_validate_tasks_dir_empty(tmp_path: Path) -> None:
    tasks = validate_tasks_dir(tmp_path)
    assert tasks == []


def test_validate_tasks_dir_with_files(tmp_path: Path) -> None:
    for i in range(1, 4):
        task_id = f"T1.1.adsl.{i:03d}"
        data = _sample_task_data(task_id=task_id)
        (tmp_path / f"{task_id}.json").write_text(json.dumps(data))

    tasks = validate_tasks_dir(tmp_path)
    assert len(tasks) == 3
    assert tasks[0].task_id == "T1.1.adsl.001"
    assert tasks[2].task_id == "T1.1.adsl.003"


def test_validate_tasks_dir_skips_schema_file(tmp_path: Path) -> None:
    (tmp_path / "_schema.json").write_text("{}")
    (tmp_path / "T1.1.adsl.001.json").write_text(json.dumps(_sample_task_data()))
    tasks = validate_tasks_dir(tmp_path)
    assert len(tasks) == 1


def test_all_categories_mapped() -> None:
    expected = {"T1", "T2", "T3", "T4", "T5"}
    assert set(CATEGORY_SCORER_MAP.keys()) == expected


@pytest.mark.parametrize(
    ("category", "scorer"),
    [
        ("T1", "codegen"),
        ("T2", "log_review"),
        ("T3", "spec_extract"),
        ("T4", "doc"),
        ("T5", "debug"),
    ],
)
def test_category_scorer_map(category: str, scorer: str) -> None:
    assert CATEGORY_SCORER_MAP[category] == scorer  # type: ignore[index]
