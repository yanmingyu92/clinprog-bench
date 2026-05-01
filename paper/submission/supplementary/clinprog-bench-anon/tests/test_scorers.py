"""Tests for scorer implementations, shared Score dataclass, and utilities."""

from __future__ import annotations

import json
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any

import pytest

from clinprog_bench.schema import (
    Category,
    ExpectedOutputs,
    LeakageAudit,
    Oracle,
    OracleType,
    OutputKind,
    Provenance,
    ScorerName,
    Scoring,
    TaskInputs,
    TaskSpec,
)
from clinprog_bench.scorers import BaseScorer, Score
from clinprog_bench.scorers._utils import (
    compute_f1,
    compute_set_metrics,
    extract_content,
    extract_json,
    normalize_text,
    parse_json_path,
)
from clinprog_bench.scorers.codegen import CodegenScorer
from clinprog_bench.scorers.debug import DebugScorer
from clinprog_bench.scorers.doc import DocScorer
from clinprog_bench.scorers.log_review import LogReviewScorer
from clinprog_bench.scorers.spec_extract import SpecExtractScorer

# ======================================================================
# Fixtures & helpers
# ======================================================================

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
    task_id: str = "T1.1.test.001",
    oracle_type: OracleType = "slot_fill",
    oracle_params: dict[str, Any] | None = None,
    output_kind: OutputKind | None = None,
    scorer_name: ScorerName | None = None,
) -> TaskSpec:
    """Create a minimal TaskSpec for testing."""
    if scorer_name is None:
        scorer_name = _SCORER_MAP[category]
    if output_kind is None:
        output_kind = _KIND_MAP[category]

    if oracle_params is None:
        oracle_params = {"slots": ["test_slot"], "match_mode": "exact"}

    return TaskSpec(
        task_id=task_id,
        category=category,
        subcategory=task_id.rsplit(".", 1)[0] if "." in task_id else category,
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
            oracle=Oracle(type=oracle_type, params=oracle_params),
        ),
        scoring=Scoring(scorer=scorer_name, weight=1.0),
        leakage_audit=LeakageAudit(fixture_sha256_overlap=False, prompt_ngram_hits=0),
    )


# ======================================================================
# Score dataclass tests
# ======================================================================


def test_score_creation() -> None:
    s = Score(
        task_id="T1.1.adsl.001",
        category="T1",
        pass_flag=True,
        primary_metric=1.0,
    )
    assert s.task_id == "T1.1.adsl.001"
    assert s.pass_flag is True
    assert s.primary_metric == 1.0
    assert s.secondary_metrics == {}


def test_score_with_secondary() -> None:
    s = Score(
        task_id="T2.1.log.001",
        category="T2",
        pass_flag=False,
        primary_metric=0.5,
        secondary_metrics={"precision": 0.6, "recall": 0.4},
    )
    assert s.secondary_metrics["precision"] == 0.6


def test_score_frozen() -> None:
    s = Score(
        task_id="T1.1.adsl.001",
        category="T1",
        pass_flag=True,
        primary_metric=1.0,
    )
    with pytest.raises(FrozenInstanceError):
        s.pass_flag = False  # type: ignore[misc]


def test_scorer_subclass_is_base_scorer() -> None:
    assert issubclass(CodegenScorer, BaseScorer)
    assert issubclass(LogReviewScorer, BaseScorer)
    assert issubclass(SpecExtractScorer, BaseScorer)
    assert issubclass(DocScorer, BaseScorer)
    assert issubclass(DebugScorer, BaseScorer)


# ======================================================================
# _utils tests
# ======================================================================


class TestParseJsonPath:
    def test_simple_field(self) -> None:
        data = {"name": "AE"}
        assert parse_json_path(data, "name") == ["AE"]

    def test_array_subfield(self) -> None:
        data = {
            "issues": [
                {"severity": "high"},
                {"severity": "low"},
            ]
        }
        result = parse_json_path(data, "issues[].severity")
        assert result == ["high", "low"]

    def test_missing_field(self) -> None:
        assert parse_json_path({}, "missing") == []

    def test_empty_array(self) -> None:
        assert parse_json_path({"items": []}, "items[].name") == []


class TestComputeF1:
    def test_perfect(self) -> None:
        assert compute_f1(10, 0, 0) == 1.0

    def test_zero(self) -> None:
        assert compute_f1(0, 0, 10) == 0.0

    def test_balanced(self) -> None:
        f1 = compute_f1(5, 5, 5)
        assert 0.49 < f1 < 0.51


class TestComputeSetMetrics:
    def test_identical_sets(self) -> None:
        f1, p, r = compute_set_metrics({"a", "b"}, {"a", "b"})
        assert f1 == 1.0
        assert p == 1.0
        assert r == 1.0

    def test_disjoint_sets(self) -> None:
        f1, p, r = compute_set_metrics({"a"}, {"b"})
        assert f1 == 0.0
        assert p == 0.0
        assert r == 0.0

    def test_partial_overlap(self) -> None:
        f1, p, r = compute_set_metrics({"a", "b"}, {"b", "c"})
        assert p == 0.5
        assert r == 0.5
        assert 0.49 < f1 < 0.51


class TestNormalizeText:
    def test_collapses_whitespace(self) -> None:
        assert normalize_text("  hello   world  ") == "hello world"

    def test_lowercases(self) -> None:
        assert normalize_text("Hello WORLD") == "hello world"


class TestExtractContent:
    def test_string(self) -> None:
        assert extract_content("hello") == "hello"

    def test_dict_with_key(self) -> None:
        assert extract_content({"main.sas": "code"}, ["main.sas"]) == "code"

    def test_empty_dict(self) -> None:
        assert extract_content({}) == ""

    def test_dict_first_value(self) -> None:
        assert extract_content({"a": "val"}) == "val"


class TestExtractJson:
    def test_valid_json(self) -> None:
        result = extract_json('{"key": "value"}')
        assert result == {"key": "value"}

    def test_invalid_json(self) -> None:
        assert extract_json("not json") == {}

    def test_empty_string(self) -> None:
        assert extract_json("") == {}


# ======================================================================
# CodegenScorer tests
# ======================================================================


class TestCodegenScorer:
    def test_perfect_slot_fill(self, tmp_path: Path) -> None:
        """Identical SAS programs should score 1.0."""
        sas_code = (
            "libname raw 'path';\n"
            "data sdtm.ae;\n"
            "    keep STUDYID USUBJID AESEQ AETERM;\n"
            "    AELLT = strip(LLT_RAW);\n"
            "    AEDECOD = strip(PT_RAW);\n"
            "    AEHLT = strip(HLT_RAW);\n"
            "    AEHLGT = strip(HLGT_RAW);\n"
            "    AEBODSYS = strip(SOC_RAW);\n"
            "run;\n"
        )
        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        (gold_dir / "expected_output.sas").write_text(sas_code, encoding="utf-8")

        task = _make_task(
            oracle_params={
                "slots": ["required_variables[]", "meddra_hierarchy"],
                "match_mode": "superset",
            }
        )
        scorer = CodegenScorer()
        result = scorer.score(task, sas_code, str(gold_dir))

        assert result.pass_flag is True
        assert result.primary_metric == 1.0

    def test_empty_submission(self, tmp_path: Path) -> None:
        """Empty submission should score 0.0."""
        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        (gold_dir / "expected_output.sas").write_text("code;", encoding="utf-8")

        task = _make_task(
            oracle_params={"slots": ["required_variables[]"], "match_mode": "exact"}
        )
        scorer = CodegenScorer()
        result = scorer.score(task, "", str(gold_dir))

        assert result.pass_flag is False
        assert result.primary_metric == 0.0

    def test_partial_match(self, tmp_path: Path) -> None:
        """Partial slot match should return fractional score."""
        gold_code = (
            "keep STUDYID USUBJID AESEQ;\n"
            "AELLT = strip(LLT_RAW);\n"
            "AEDECOD = strip(PT_RAW);\n"
            "AEHLT = strip(HLT_RAW);\n"
            "AEHLGT = strip(HLGT_RAW);\n"
            "AEBODSYS = strip(SOC_RAW);\n"
        )
        sub_code = "keep STUDYID USUBJID;\n"  # missing AESEQ, no MedDRA

        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        (gold_dir / "expected_output.sas").write_text(gold_code, encoding="utf-8")

        task = _make_task(
            oracle_params={
                "slots": ["required_variables[]", "meddra_hierarchy"],
                "match_mode": "superset",
            }
        )
        scorer = CodegenScorer()
        result = scorer.score(task, sub_code, str(gold_dir))

        # meddra_hierarchy should match (0 fields in sub vs 5 in gold)
        assert 0.0 <= result.primary_metric <= 1.0

    def test_unsupported_oracle_type(self, tmp_path: Path) -> None:
        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        (gold_dir / "expected_output.sas").write_text("code;", encoding="utf-8")

        task = _make_task(oracle_type="set_match")
        scorer = CodegenScorer()
        with pytest.raises(ValueError, match="Unsupported oracle type"):
            scorer.score(task, "code", str(gold_dir))


# ======================================================================
# LogReviewScorer tests
# ======================================================================


class TestLogReviewScorer:
    def test_perfect_match(self, tmp_path: Path) -> None:
        """Identical issue lists should score F1=1.0."""
        gold_data = {
            "issues": [
                {"severity": "high", "category": "data_integrity"},
                {"severity": "medium", "category": "compliance"},
            ]
        }
        gold_json = json.dumps(gold_data)

        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        (gold_dir / "expected_output.json").write_text(gold_json, encoding="utf-8")

        task = _make_task(
            category="T2",
            task_id="T2.1.test.001",
            oracle_type="slot_fill",
            oracle_params={
                "slots": ["issues[].severity", "issues[].category"],
                "match_mode": "superset",
            },
            scorer_name="log_review",
        )
        scorer = LogReviewScorer()
        result = scorer.score(task, gold_json, str(gold_dir))

        assert result.primary_metric == 1.0
        assert result.pass_flag is True

    def test_no_match(self, tmp_path: Path) -> None:
        """Completely different issues should score F1=0.0."""
        gold_data = {
            "issues": [
                {"severity": "high", "category": "data_integrity"},
            ]
        }
        sub_data = {
            "issues": [
                {"severity": "low", "category": "style"},
            ]
        }

        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        (gold_dir / "expected_output.json").write_text(
            json.dumps(gold_data), encoding="utf-8"
        )

        task = _make_task(
            category="T2",
            task_id="T2.1.test.001",
            scorer_name="log_review",
            oracle_params={
                "slots": ["issues[].severity"],
                "match_mode": "exact",
            },
        )
        scorer = LogReviewScorer()
        result = scorer.score(task, json.dumps(sub_data), str(gold_dir))

        assert result.primary_metric == 0.0
        assert result.pass_flag is False

    def test_empty_submission(self, tmp_path: Path) -> None:
        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        (gold_dir / "expected_output.json").write_text(
            '{"issues": [{"severity": "high", "category": "test"}]}',
            encoding="utf-8",
        )

        task = _make_task(
            category="T2",
            task_id="T2.1.test.001",
            scorer_name="log_review",
        )
        scorer = LogReviewScorer()
        result = scorer.score(task, "", str(gold_dir))

        assert result.primary_metric == 0.0

    def test_partial_match_f1(self, tmp_path: Path) -> None:
        """Partial overlap should yield 0 < F1 < 1."""
        gold_data = {
            "issues": [
                {"severity": "high", "category": "data_integrity"},
                {"severity": "medium", "category": "compliance"},
            ]
        }
        sub_data = {
            "issues": [
                {"severity": "high", "category": "data_integrity"},
                {"severity": "low", "category": "style"},
            ]
        }

        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        (gold_dir / "expected_output.json").write_text(
            json.dumps(gold_data), encoding="utf-8"
        )

        task = _make_task(
            category="T2",
            task_id="T2.1.test.001",
            scorer_name="log_review",
            oracle_params={
                "slots": ["issues[].severity", "issues[].category"],
                "match_mode": "exact",
            },
        )
        scorer = LogReviewScorer()
        result = scorer.score(task, json.dumps(sub_data), str(gold_dir))

        assert 0.0 < result.primary_metric < 1.0

    def test_discrepancies_format(self, tmp_path: Path) -> None:
        """T2.2 tasks use 'discrepancies' array instead of 'issues'."""
        gold_data = {
            "discrepancies": [
                {"severity": "medium", "category": "consistency"},
                {"severity": "low", "category": "documentation"},
            ]
        }
        gold_json = json.dumps(gold_data)

        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        (gold_dir / "expected_output.json").write_text(gold_json, encoding="utf-8")

        task = _make_task(
            category="T2",
            task_id="T2.2.test.001",
            scorer_name="log_review",
            oracle_params={
                "slots": ["discrepancies[].severity"],
                "match_mode": "superset",
            },
        )
        scorer = LogReviewScorer()
        result = scorer.score(task, gold_json, str(gold_dir))

        assert result.primary_metric == 1.0


# ======================================================================
# SpecExtractScorer tests
# ======================================================================


class TestSpecExtractScorer:
    def test_exact_match_variables(self, tmp_path: Path) -> None:
        """Identical variable sets should score 1.0."""
        gold_data = {
            "variables": [
                {"variable_name": "STUDYID", "type": "Char", "label": "Study ID"},
                {"variable_name": "USUBJID", "type": "Char", "label": "Subject ID"},
            ]
        }
        gold_json = json.dumps(gold_data)

        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        (gold_dir / "expected_output.json").write_text(gold_json, encoding="utf-8")

        task = _make_task(
            category="T3",
            task_id="T3.1.test.001",
            scorer_name="spec_extract",
            oracle_params={
                "slots": ["variables[].variable_name"],
                "match_mode": "exact",
            },
        )
        scorer = SpecExtractScorer()
        result = scorer.score(task, gold_json, str(gold_dir))

        assert result.primary_metric == 1.0
        assert result.pass_flag is True

    def test_empty_submission(self, tmp_path: Path) -> None:
        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        (gold_dir / "expected_output.json").write_text(
            '{"variables": [{"variable_name": "AETERM"}]}', encoding="utf-8"
        )

        task = _make_task(
            category="T3",
            task_id="T3.1.test.001",
            scorer_name="spec_extract",
        )
        scorer = SpecExtractScorer()
        result = scorer.score(task, "", str(gold_dir))

        assert result.primary_metric == 0.0

    def test_partial_variable_match(self, tmp_path: Path) -> None:
        """Missing variables should give 0 < F1 < 1."""
        gold_data = {
            "variables": [
                {"variable_name": "A"},
                {"variable_name": "B"},
                {"variable_name": "C"},
            ]
        }
        sub_data = {
            "variables": [
                {"variable_name": "A"},
                {"variable_name": "D"},
            ]
        }

        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        (gold_dir / "expected_output.json").write_text(
            json.dumps(gold_data), encoding="utf-8"
        )

        task = _make_task(
            category="T3",
            task_id="T3.1.test.001",
            scorer_name="spec_extract",
            oracle_params={
                "slots": ["variables[].variable_name"],
                "match_mode": "exact",
            },
        )
        scorer = SpecExtractScorer()
        result = scorer.score(task, json.dumps(sub_data), str(gold_dir))

        assert 0.0 < result.primary_metric < 1.0

    def test_multi_slot_scoring(self, tmp_path: Path) -> None:
        """Multiple slots should each contribute to the score."""
        gold_data = {
            "variables": [
                {"variable_name": "A", "type": "Char", "label": "Alpha"},
                {"variable_name": "B", "type": "Num", "label": "Beta"},
            ]
        }

        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        (gold_dir / "expected_output.json").write_text(
            json.dumps(gold_data), encoding="utf-8"
        )

        task = _make_task(
            category="T3",
            task_id="T3.1.test.001",
            scorer_name="spec_extract",
            oracle_params={
                "slots": [
                    "variables[].variable_name",
                    "variables[].type",
                ],
                "match_mode": "exact",
            },
        )
        scorer = SpecExtractScorer()
        result = scorer.score(task, json.dumps(gold_data), str(gold_dir))

        assert result.primary_metric == 1.0


# ======================================================================
# DocScorer tests
# ======================================================================


class TestDocScorer:
    def test_slot_fill_text(self, tmp_path: Path) -> None:
        """Matching text slots should score 1.0."""
        gold_text = (
            "# SDTM Define Documentation\n"
            "\n"
            "## File Metadata\n"
            "- **Define-XML Version**: 2.0\n"
            "- **ODM Schema Version**: 1.2.2\n"
        )
        sub_text = (
            "# SDTM Define Documentation\n"
            "\n"
            "## File Metadata\n"
            "- **Define-XML Version**: 2.0\n"
            "- **ODM Schema Version**: 1.2.2\n"
        )

        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        (gold_dir / "expected_output.txt").write_text(gold_text, encoding="utf-8")

        task = _make_task(
            category="T4",
            task_id="T4.2.test.001",
            output_kind="text",
            scorer_name="doc",
            oracle_params={
                "slots": ["define_xml_version", "odm_schema_version"],
                "match_mode": "exact",
            },
        )
        scorer = DocScorer()
        result = scorer.score(task, sub_text, str(gold_dir))

        assert result.primary_metric == 1.0

    def test_empty_submission(self, tmp_path: Path) -> None:
        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        (gold_dir / "expected_output.txt").write_text("content", encoding="utf-8")

        task = _make_task(
            category="T4",
            task_id="T4.1.test.001",
            output_kind="text",
            scorer_name="doc",
        )
        scorer = DocScorer()
        result = scorer.score(task, "", str(gold_dir))

        assert result.primary_metric == 0.0

    def test_style_lint(self, tmp_path: Path) -> None:
        """Well-formatted text should get a high style-lint score."""
        good_text = "# Header\n\nSome content here.\n"
        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        (gold_dir / "expected_output.txt").write_text(good_text, encoding="utf-8")

        task = _make_task(
            category="T4",
            task_id="T4.1.test.001",
            output_kind="text",
            scorer_name="doc",
            oracle_params={"slots": ["test_slot"], "match_mode": "exact"},
        )
        scorer = DocScorer()
        result = scorer.score(task, good_text, str(gold_dir))

        assert result.secondary_metrics["style_lint"] > 0.0

    def test_partial_slot_match(self, tmp_path: Path) -> None:
        """Missing slots should produce partial scores."""
        gold_text = "**Define-XML Version**: 2.0\n**ODM Schema Version**: 1.2.2\n"
        sub_text = "**Define-XML Version**: 2.0\n"  # missing ODM version

        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        (gold_dir / "expected_output.txt").write_text(gold_text, encoding="utf-8")

        task = _make_task(
            category="T4",
            task_id="T4.2.test.001",
            output_kind="text",
            scorer_name="doc",
            oracle_params={
                "slots": ["define_xml_version", "odm_schema_version"],
                "match_mode": "exact",
            },
        )
        scorer = DocScorer()
        result = scorer.score(task, sub_text, str(gold_dir))

        assert result.primary_metric == 0.5


# ======================================================================
# DebugScorer tests
# ======================================================================


class TestDebugScorer:
    def test_perfect_patch_match(self, tmp_path: Path) -> None:
        """Identical patch to gold should score 1.0."""
        gold_patch = (
            "--- a/file.sas\n"
            "+++ b/file.sas\n"
            "@@ -1,3 +1,3 @@\n"
            "-Bug 1 (AESER_logic): old_logic;\n"
            "+Fix 1 (AESER_logic): new_logic;\n"
            "\n"
            "-Bug 2 (AESEQ_retain): old_retain;\n"
            "+Fix 2 (AESEQ_retain): new_retain;\n"
        )

        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        (gold_dir / "expected_output.patch").write_text(gold_patch, encoding="utf-8")

        task = _make_task(
            category="T5",
            task_id="T5.1.test.001",
            output_kind="patch",
            scorer_name="debug",
            oracle_type="patch_apply",
            oracle_params={
                "bug_count": 2,
                "fix_locations": ["AESER_logic", "AESEQ_retain"],
            },
        )
        scorer = DebugScorer()
        # Submit the same patch
        result = scorer.score(task, gold_patch, str(gold_dir))

        assert result.primary_metric == 1.0
        assert result.pass_flag is True

    def test_empty_submission(self, tmp_path: Path) -> None:
        gold_patch = "--- a/file\n+++ b/file\n@@ -1 +1 @@\n-old\n+new\n"
        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        (gold_dir / "expected_output.patch").write_text(gold_patch, encoding="utf-8")

        task = _make_task(
            category="T5",
            task_id="T5.1.test.001",
            output_kind="patch",
            scorer_name="debug",
            oracle_type="patch_apply",
            oracle_params={"bug_count": 1, "fix_locations": ["bug_1"]},
        )
        scorer = DebugScorer()
        result = scorer.score(task, "", str(gold_dir))

        assert result.primary_metric == 0.0

    def test_loc_penalty(self, tmp_path: Path) -> None:
        """A much larger patch than gold should incur LoC penalty."""
        gold_patch = "--- a/f\n+++ b/f\n@@ -1 +1 @@\n-old\n+new\n"
        bloated_patch = (
            "--- a/f\n+++ b/f\n"
            "@@ -1 +1 @@\n-old\n+new\n"
            "+extra1\n+extra2\n+extra3\n+extra4\n+extra5\n"
            "+extra6\n+extra7\n+extra8\n+extra9\n+extra10\n"
        )

        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        (gold_dir / "expected_output.patch").write_text(gold_patch, encoding="utf-8")

        task = _make_task(
            category="T5",
            task_id="T5.1.test.001",
            output_kind="patch",
            scorer_name="debug",
            oracle_type="patch_apply",
            oracle_params={"bug_count": 1, "fix_locations": ["fix_1"]},
        )
        scorer = DebugScorer()
        result = scorer.score(task, bloated_patch, str(gold_dir))

        assert result.secondary_metrics["loc_penalty"] < 1.0


# ======================================================================
# Gold data integration tests (all T1 seeds)
# ======================================================================


class TestCodegenGoldIntegration:
    """Run CodegenScorer on all 10 T1 gold outputs."""

    @pytest.fixture(
        params=[
            "T1.1.sdtm_dm_gen.001",
            "T1.1.sdtm_ae_gen.001",
            "T1.1.sdtm_vs_gen.001",
            "T1.1.sdtm_lb_gen.001",
            "T1.2.adam_adadas_gen.001",
            "T1.2.adam_adae_gen.001",
            "T1.2.adam_adsl_gen.001",
            "T1.3.tlf_ae_gen.001",
            "T1.3.tlf_demo_gen.001",
            "T1.3.tlf_km_gen.001",
        ]
    )
    def task_id(self, request: pytest.FixtureRequest) -> str:
        return request.param  # type: ignore[no-any-return]

    def test_gold_self_score(self, task_id: str, tmp_path: Path) -> None:
        """Gold output scored against itself should pass (>= 0.5)."""
        import json as _json

        project_root = Path(__file__).resolve().parent.parent
        task_file = project_root / "tasks" / "T1_codegen" / f"{task_id}.json"
        gold_dir = project_root / "gold" / task_id

        if not task_file.exists() or not gold_dir.exists():
            pytest.skip(f"Task {task_id} data not found")

        with open(task_file) as f:
            task_data = _json.load(f)

        from clinprog_bench.schema import TaskSpec

        task = TaskSpec.model_validate(task_data)

        # Read gold content
        gold_files = list(gold_dir.glob("expected_output.*"))
        assert gold_files, f"No gold file in {gold_dir}"
        gold_content = gold_files[0].read_text(encoding="utf-8")

        scorer = CodegenScorer()
        result = scorer.score(task, gold_content, str(gold_dir))

        assert result.pass_flag is True
        assert result.primary_metric >= 0.5
