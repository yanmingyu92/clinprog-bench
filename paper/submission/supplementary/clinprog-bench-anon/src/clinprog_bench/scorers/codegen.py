"""Code generation scorer for T1 tasks.

Supports two oracle types:

- ``slot_fill`` -- heuristic feature extraction from source code,
  comparing structural elements (variables, MedDRA hierarchy,
  seriousness logic, date handling) between submission and gold.
- ``dataset_diff`` -- engine-agnostic XPT / dataset comparison via
  ``pandas.testing.assert_frame_equal`` after sorting by primary key.
  Optionally uses ``pyreadstat`` for richer SAS transport-file parsing.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from clinprog_bench.scorers import BaseScorer, Score
from clinprog_bench.scorers._utils import (
    extract_content,
    read_gold,
    resolve_gold_path,
)

# Submission output keys for T1 tasks (in priority order).
_T1_KEYS = ["main.sas", "main.R", "main.py"]


class CodegenScorer(BaseScorer):
    """Scorer for T1 code generation tasks.

    Primary metric: slot-match rate for ``slot_fill`` oracle; dataset
    equivalence flag for ``dataset_diff`` oracle.
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
        if oracle_type == "dataset_diff":
            return self._score_dataset_diff(task, submission, gold)
        msg = f"Unsupported oracle type: {oracle_type}"
        raise ValueError(msg)

    # ------------------------------------------------------------------
    # slot_fill path
    # ------------------------------------------------------------------

    def _score_slot_fill(self, task: Any, submission: Any, gold: Any) -> Score:
        params = task.expected_outputs.oracle.params
        slots: list[str] = params.get("slots", [])
        match_mode: str = params.get("match_mode", "exact")

        gold_content = read_gold(gold)
        sub_content = extract_content(submission, _T1_KEYS)

        if not sub_content.strip():
            return Score(
                task_id=task.task_id,
                category=task.category,
                pass_flag=False,
                primary_metric=0.0,
                secondary_metrics={s: 0.0 for s in slots},
            )

        total = len(slots)
        if total == 0:
            return Score(
                task_id=task.task_id,
                category=task.category,
                pass_flag=True,
                primary_metric=1.0,
            )

        matched = 0
        secondary: dict[str, float] = {}

        for slot in slots:
            gold_vals = self._extract_slot(gold_content, slot)
            sub_vals = self._extract_slot(sub_content, slot)
            if self._compare_slot(gold_vals, sub_vals, match_mode):
                matched += 1
                secondary[slot] = 1.0
            else:
                secondary[slot] = 0.0

        rate = matched / total
        return Score(
            task_id=task.task_id,
            category=task.category,
            pass_flag=rate >= 0.5,
            primary_metric=rate,
            secondary_metrics=secondary,
        )

    # ------------------------------------------------------------------
    # dataset_diff path
    # ------------------------------------------------------------------

    def _score_dataset_diff(self, task: Any, submission: Any, gold: Any) -> Score:
        params = task.expected_outputs.oracle.params
        primary_key: list[str] = params.get("primary_key", [])
        tolerance: float = params.get("tolerance", 0.0)

        gold_path = resolve_gold_path(gold)
        sub_content = extract_content(submission, _T1_KEYS)

        # Try to locate submission dataset file
        sub_path: Path | None = None
        if isinstance(submission, Path) and submission.is_file():
            sub_path = submission
        elif isinstance(submission, str) and Path(submission).is_file():
            sub_path = Path(submission)

        if sub_path is None or not sub_content.strip():
            return Score(
                task_id=task.task_id,
                category=task.category,
                pass_flag=False,
                primary_metric=0.0,
                secondary_metrics={"error": 1.0},
            )

        try:
            import pandas as pd

            gold_df = self._read_dataset(gold_path)
            sub_df = self._read_dataset(sub_path)

            if gold_df is None or sub_df is None:
                return Score(
                    task_id=task.task_id,
                    category=task.category,
                    pass_flag=False,
                    primary_metric=0.0,
                )

            # Sort by primary key for deterministic comparison
            if primary_key:
                gold_df = gold_df.sort_values(primary_key).reset_index(drop=True)
                sub_df = sub_df.sort_values(primary_key).reset_index(drop=True)

            # Structural checks
            row_match = len(gold_df) == len(sub_df)
            col_match = set(gold_df.columns) == set(sub_df.columns)

            value_match = False
            if row_match and col_match:
                try:
                    sub_df = sub_df[gold_df.columns]  # align column order
                    pd.testing.assert_frame_equal(
                        gold_df,
                        sub_df,
                        check_exact=(tolerance == 0),
                        atol=tolerance,
                        rtol=tolerance,
                    )
                    value_match = True
                except AssertionError:
                    value_match = False

            primary = 1.0 if value_match else 0.0
            return Score(
                task_id=task.task_id,
                category=task.category,
                pass_flag=value_match,
                primary_metric=primary,
                secondary_metrics={
                    "row_count_match": float(row_match),
                    "column_match": float(col_match),
                    "value_match": float(value_match),
                },
            )
        except ImportError:
            return Score(
                task_id=task.task_id,
                category=task.category,
                pass_flag=False,
                primary_metric=0.0,
                secondary_metrics={"error": 1.0},
            )

    # ------------------------------------------------------------------
    # Dataset reading helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _read_dataset(path: Path) -> Any:
        """Read an XPT / SAS dataset; return a DataFrame or None."""
        try:
            import pandas as pd

            suffix = path.suffix.lower()
            if suffix in (".xpt", ".sas7bdat"):
                return pd.read_sas(
                    path, format="xpt" if suffix == ".xpt" else "sas7bdat"
                )
            if suffix == ".csv":
                return pd.read_csv(path)
            return pd.read_sas(path)
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Slot extraction from source code
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_slot(code: str, slot: str) -> set[str]:
        """Extract a set of values for *slot* from *code*."""
        slot_lower = slot.lower().rstrip("[]")

        if slot_lower in (
            "required_variables",
            "grouping_variables",
            "analysis_variables",
        ):
            return CodegenScorer._extract_variables(code)
        if "meddra" in slot_lower or "hierarchy" in slot_lower:
            return CodegenScorer._extract_meddra_fields(code)
        if "seriousness" in slot_lower or "flag_logic" in slot_lower:
            return CodegenScorer._extract_seriousness_criteria(code)
        if "date" in slot_lower:
            return CodegenScorer._extract_date_formats(code)
        if "primary_key" in slot_lower:
            return CodegenScorer._extract_by_variables(code)
        if "derivation" in slot_lower or "logic" in slot_lower:
            return CodegenScorer._extract_derivation_keywords(code)
        if "filter" in slot_lower:
            return CodegenScorer._extract_filter_keywords(code)
        # Generic fallback: extract uppercase identifiers
        return CodegenScorer._extract_identifiers(code)

    @staticmethod
    def _extract_variables(code: str) -> set[str]:
        """Extract variable names from SAS/R source code."""
        variables: set[str] = set()

        # SAS KEEP statement
        for m in re.finditer(r"\bkeep\s+([^;]+);", code, re.IGNORECASE):
            for var in re.findall(r"\b([A-Za-z_]\w{0,31})\b", m.group(1)):
                if var.upper() not in _SAS_KEYWORDS:
                    variables.add(var.upper())

        # SAS LENGTH statement
        for m in re.finditer(r"\blength\s+([^;]+);", code, re.IGNORECASE):
            for var in re.findall(r"\b([A-Za-z_]\w{0,31})\b", m.group(1)):
                if var.upper() not in _SAS_KEYWORDS:
                    variables.add(var.upper())

        # R: select(), mutate(), rename() -- variable names as bare words
        for var in re.findall(r"\b([A-Z][A-Z0-9_]{1,30})\b", code):
            variables.add(var)

        return variables

    @staticmethod
    def _extract_meddra_fields(code: str) -> set[str]:
        """Extract MedDRA hierarchy fields present in code."""
        meddra_fields = {"AELLT", "AEDECOD", "AEHLT", "AEHLGT", "AEBODSYS"}
        found: set[str] = set()
        for field in meddra_fields:
            if re.search(rf"\b{field}\b", code, re.IGNORECASE):
                found.add(field)
        return found

    @staticmethod
    def _extract_seriousness_criteria(code: str) -> set[str]:
        """Extract seriousness criteria referenced in code."""
        criteria = {
            "AESCAN",
            "AESCONG",
            "AESDEATH",
            "AESHOSP",
            "AESLIFE",
            "AESOD",
        }
        found: set[str] = set()
        for crit in criteria:
            if re.search(rf"\b{crit}", code, re.IGNORECASE):
                found.add(crit)
        return found

    @staticmethod
    def _extract_date_formats(code: str) -> set[str]:
        """Extract date-format identifiers from code."""
        formats: set[str] = set()
        # SAS informats/formats
        for fmt in re.findall(r"(is8601\w+)", code, re.IGNORECASE):
            formats.add(fmt.lower())
        # R date functions
        for func in re.findall(r"\b(as\.Date|ymd|ISOdate|parse_date_time)\b", code):
            formats.add(func)
        return formats

    @staticmethod
    def _extract_by_variables(code: str) -> set[str]:
        """Extract BY-statement variables from SAS or R code."""
        by_vars: set[str] = set()
        # SAS: by USUBJID ...
        for m in re.finditer(r"\bby\s+([^;]+)", code, re.IGNORECASE):
            for var in re.findall(r"\b([A-Za-z_]\w{0,31})\b", m.group(1)):
                by_vars.add(var.upper())
        # R: group_by(var1, var2)
        for m in re.finditer(r"group_by\s*\(([^)]+)\)", code, re.IGNORECASE):
            for var in re.findall(r"\b([A-Za-z_]\w{0,31})\b", m.group(1)):
                by_vars.add(var.upper())
        return by_vars

    @staticmethod
    def _extract_derivation_keywords(code: str) -> set[str]:
        """Extract derivation-related keywords."""
        keywords: set[str] = set()
        for kw in re.findall(
            r"\b(retain|merge|set|if\s+first\.|lag|dif|sum\s+of)\b", code, re.IGNORECASE
        ):
            keywords.add(kw.lower().strip())
        return keywords

    @staticmethod
    def _extract_filter_keywords(code: str) -> set[str]:
        """Extract filter-related conditions."""
        filters: set[str] = set()
        # SAS: where / subsetting if
        for m in re.finditer(r"\bwhere\s+([^;]+)", code, re.IGNORECASE):
            filters.add(m.group(1).strip().lower())
        # R: filter(condition)
        for m in re.finditer(r"\bfilter\s*\(([^)]+)\)", code, re.IGNORECASE):
            filters.add(m.group(1).strip().lower())
        return filters

    @staticmethod
    def _extract_identifiers(code: str) -> set[str]:
        """Fallback: extract all uppercase identifiers."""
        return set(re.findall(r"\b([A-Z][A-Z0-9_]{1,30})\b", code))

    # ------------------------------------------------------------------
    # Slot comparison
    # ------------------------------------------------------------------

    @staticmethod
    def _compare_slot(
        gold_vals: set[str],
        sub_vals: set[str],
        match_mode: str,
    ) -> bool:
        """Compare two sets of slot values respecting *match_mode*."""
        if match_mode == "exact":
            return gold_vals == sub_vals
        if match_mode == "superset":
            return gold_vals.issubset(sub_vals)
        # Default: exact
        return gold_vals == sub_vals


# SAS keywords to exclude from variable extraction.
_SAS_KEYWORDS = frozenset(
    {
        "KEEP",
        "DROP",
        "RENAME",
        "LABEL",
        "LENGTH",
        "FORMAT",
        "INFORMAT",
        "ATTRIB",
        "ARRAY",
        "BY",
        "WHERE",
        "IF",
        "THEN",
        "ELSE",
        "AND",
        "OR",
        "NOT",
        "IN",
        "OUTPUT",
        "RETURN",
        "DO",
        "END",
        "SET",
        "MERGE",
        "UPDATE",
        "MODIFY",
        "PUT",
        "FILE",
        "RUN",
        "QUIT",
        "DATA",
        "PROC",
        "LIBNAME",
        "FIRST",
        "LAST",
        "CHAR",
        "NUM",
        "BEST",
        "DOLLAR",
    }
)


__all__ = ["CodegenScorer"]
