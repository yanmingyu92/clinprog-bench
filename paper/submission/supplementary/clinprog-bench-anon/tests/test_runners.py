"""Tests for runner contract, adapter, and submission round-trip."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from clinprog_bench.runners import BaseAdapter, Submission

if TYPE_CHECKING:
    from pathlib import Path
from clinprog_bench.runners.reference_baseline import ReferenceBaseline
from clinprog_bench.schema import (
    Category,
    ExpectedOutputs,
    LeakageAudit,
    Oracle,
    OutputKind,
    Provenance,
    ScorerName,
    Scoring,
    TaskInputs,
    TaskSpec,
)

_SCORER_MAP: dict[Category, ScorerName] = {
    "T1": "codegen",
    "T2": "log_review",
    "T3": "spec_extract",
    "T4": "doc",
    "T5": "debug",
}

_KIND_MAP: dict[Category, OutputKind] = {
    "T1": "sas_program",
    "T2": "json",
    "T3": "json",
    "T4": "text",
    "T5": "patch",
}


def _make_task(
    category: Category = "T1",
    task_id: str = "T1.1.adsl.001",
    output_kind: OutputKind | None = None,
    scorer_name: ScorerName | None = None,
) -> TaskSpec:
    if scorer_name is None:
        scorer_name = _SCORER_MAP[category]
    if output_kind is None:
        output_kind = _KIND_MAP[category]
    subcategory = task_id.rsplit(".", 1)[0] if "." in task_id else category
    return TaskSpec(
        task_id=task_id,
        category=category,
        subcategory=subcategory,
        title="Test task",
        complexity="simple",
        provenance=Provenance(
            seed_repo="test/repo",
            seed_commit="a" * 40,
            derivation_script="scripts/test.py",
            human_authors=["R01"],
            human_reviewers=["R02"],
        ),
        inputs=TaskInputs(
            fixtures=["fixtures/test.xpt"],
            spec="spec.xlsx",
            prompt="Test prompt",
        ),
        expected_outputs=ExpectedOutputs(
            kind=output_kind,
            gold_path=f"gold/{task_id}/",
            oracle=Oracle(
                type="slot_fill", params={"slots": ["test_slot"], "match_mode": "exact"}
            ),
        ),
        scoring=Scoring(scorer=scorer_name, weight=1.0),
        leakage_audit=LeakageAudit(fixture_sha256_overlap=False, prompt_ngram_hits=0),
    )


def test_submission_creation() -> None:
    sub = Submission(
        task_id="T1.1.adsl.001",
        agent_name="test-agent",
        outputs={"main.sas": "proc sort; run;"},
    )
    assert sub.task_id == "T1.1.adsl.001"
    assert sub.agent_name == "test-agent"
    assert "main.sas" in sub.outputs


def test_reference_baseline_round_trip(tmp_path: Path) -> None:
    """Gate test: mock agent submission round-trips through the adapter."""
    task = _make_task()
    adapter: BaseAdapter = ReferenceBaseline()
    submission = adapter.run(task, tmp_path)

    assert isinstance(submission, Submission)
    assert submission.task_id == task.task_id
    assert submission.agent_name == "reference-baseline"


def test_submission_serialization(tmp_path: Path) -> None:
    """Verify a Submission can be serialized to JSON and back."""
    original = Submission(
        task_id="T1.1.adsl.001",
        agent_name="test-agent",
        outputs={"main.sas": "proc sort data=dm; by usubjid; run;"},
        metadata={"wall_time_seconds": "12.5"},
    )

    # Serialize
    serialized = json.dumps(
        {
            "task_id": original.task_id,
            "agent_name": original.agent_name,
            "outputs": original.outputs,
            "metadata": original.metadata,
        }
    )

    # Deserialize
    data = json.loads(serialized)
    restored = Submission(**data)

    assert restored.task_id == original.task_id
    assert restored.agent_name == original.agent_name
    assert restored.outputs == original.outputs
    assert restored.metadata["wall_time_seconds"] == "12.5"


def test_reference_baseline_is_base_adapter() -> None:
    assert issubclass(ReferenceBaseline, BaseAdapter)


def test_reference_baseline_deterministic(tmp_path: Path) -> None:
    """Three reruns must produce bit-identical outputs."""
    adapter = ReferenceBaseline()
    task = _make_task()

    results = [adapter.run(task, tmp_path) for _ in range(3)]
    assert all(r.outputs == results[0].outputs for r in results)


def test_reference_baseline_t2_output(tmp_path: Path) -> None:
    """T2 baseline should produce empty issues list."""
    adapter = ReferenceBaseline()
    task = _make_task(
        category="T2",
        task_id="T2.1.test.001",
        scorer_name="log_review",
    )
    sub = adapter.run(task, tmp_path)
    assert "review.json" in sub.outputs
    assert json.loads(sub.outputs["review.json"]) == {"issues": []}


def test_reference_baseline_t3_output(tmp_path: Path) -> None:
    """T3 baseline should produce empty variables list."""
    adapter = ReferenceBaseline()
    task = _make_task(
        category="T3",
        task_id="T3.1.test.001",
        scorer_name="spec_extract",
    )
    sub = adapter.run(task, tmp_path)
    assert "extraction.json" in sub.outputs
    assert json.loads(sub.outputs["extraction.json"]) == {"variables": []}


def test_reference_baseline_t5_output(tmp_path: Path) -> None:
    """T5 baseline should produce empty patch."""
    adapter = ReferenceBaseline()
    task = _make_task(
        category="T5",
        task_id="T5.1.test.001",
        output_kind="patch",
        scorer_name="debug",
    )
    sub = adapter.run(task, tmp_path)
    assert "patch.diff" in sub.outputs
    assert sub.outputs["patch.diff"] == ""
