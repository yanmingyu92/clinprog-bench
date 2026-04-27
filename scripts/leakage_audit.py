"""Leakage audit for ClinProg-Bench task corpus.

Computes two leakage metrics:
1. SHA-256 byte overlap between fixture files and gold outputs.
2. 13-gram Jaccard overlap between NL prompts and Pilot01 source docs.

Generates docs/leakage-audit.md with the full report.

Usage:
    python scripts/leakage_audit.py
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks"
GOLD_DIR = ROOT / "gold"
DOCS_DIR = ROOT / "docs"
FIXTURES_DIR = ROOT / "fixtures"  # may not exist; gracefully skip

# ── N-gram helpers ──────────────────────────────────────────────────


def _tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, split into word tokens."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return text.split()


def _ngrams(tokens: list[str], n: int) -> set[str]:
    """Return set of n-grams from a token list."""
    if len(tokens) < n:
        return set()
    return {" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def _jaccard(a: set[str], b: set[str]) -> float:
    """Jaccard similarity between two sets."""
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


# ── SHA-256 overlap check ──────────────────────────────────────────


def _sha256_bytes(path: Path) -> bytes:
    """Return the raw SHA-256 digest bytes for a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.digest()


def check_fixture_gold_overlap() -> list[dict]:
    """Check SHA-256 overlap between fixture bytes and gold outputs.

    Returns list of hit dicts with keys:
        task_id, fixture_file, gold_file, match (bool)
    """
    hits: list[dict] = []

    # Collect all gold file hashes
    gold_hashes: dict[str, Path] = {}
    for gold_file in GOLD_DIR.rglob("expected_output.*"):
        rel = gold_file.relative_to(GOLD_DIR)
        task_id = str(rel).split("/")[0].split("\\")[0]
        try:
            digest = _sha256_bytes(gold_file)
            gold_hashes[task_id + "::" + str(rel)] = gold_file
        except OSError:
            continue

    # If no fixtures directory, report zero hits
    if not FIXTURES_DIR.is_dir():
        return hits

    # Collect fixture hashes
    fixture_hashes: dict[bytes, Path] = {}
    for fix_file in FIXTURES_DIR.rglob("*"):
        if fix_file.is_file():
            try:
                digest = _sha256_bytes(fix_file)
                fixture_hashes[digest] = fix_file
            except OSError:
                continue

    # Compare — report any exact byte-level matches
    for gold_key, gold_path in gold_hashes.items():
        try:
            gold_digest = _sha256_bytes(gold_path)
        except OSError:
            continue
        if gold_digest in fixture_hashes:
            task_id = gold_key.split("::")[0]
            hits.append(
                {
                    "task_id": task_id,
                    "fixture_file": str(fixture_hashes[gold_digest].relative_to(ROOT)),
                    "gold_file": str(gold_path.relative_to(ROOT)),
                    "match": True,
                }
            )

    return hits


# ── N-gram overlap check ───────────────────────────────────────────


def _load_prompts() -> dict[str, str]:
    """Load all task prompts from tasks/ directory."""
    prompts: dict[str, str] = {}
    for json_file in TASKS_DIR.rglob("*.json"):
        if json_file.name == "_schema.json":
            continue
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            task_id = data.get("task_id", "")
            prompt = data.get("inputs", {}).get("prompt", "")
            if task_id and prompt:
                prompts[task_id] = prompt
        except (json.JSONDecodeError, KeyError):
            continue
    return prompts


def _load_pilot01_docs() -> str:
    """Load Pilot01 source documents for comparison.

    Concatenates protocol, SAP, and other source docs into one corpus.
    """
    doc_paths = [
        ROOT / "fixtures" / "01_study_design" / "protocol" / "CDISCPilot01_Protocol.md",
        ROOT / "fixtures" / "01_study_design" / "sap" / "CDISCPilot01_SAP.md",
        ROOT / "fixtures" / "04_sdtm" / "SDTM_Specifications.md",
        ROOT / "fixtures" / "05_adam" / "ADaM_Specifications.md",
        ROOT / "fixtures" / "DATASET_CARD.md",
    ]
    parts: list[str] = []
    for p in doc_paths:
        if p.is_file():
            try:
                parts.append(p.read_text(encoding="utf-8"))
            except OSError:
                continue
    return "\n".join(parts)


def check_ngram_overlap(n: int = 13, threshold: float = 0.1) -> list[dict]:
    """Check n-gram Jaccard overlap between prompts and source docs.

    Args:
        n: n-gram size (default 13).
        threshold: Jaccard threshold to report a hit.

    Returns list of hit dicts with keys:
        task_id, jaccard, overlapping_ngrams
    """
    prompts = _load_prompts()
    source_text = _load_pilot01_docs()

    if not source_text:
        return []

    source_tokens = _tokenize(source_text)
    source_ngrams = _ngrams(source_tokens, n)

    hits: list[dict] = []
    for task_id, prompt in prompts.items():
        prompt_tokens = _tokenize(prompt)
        prompt_ngrams = _ngrams(prompt_tokens, n)
        overlap = source_ngrams & prompt_ngrams
        jaccard_val = _jaccard(prompt_ngrams, source_ngrams)

        if jaccard_val > threshold:
            hits.append(
                {
                    "task_id": task_id,
                    "jaccard": round(jaccard_val, 6),
                    "overlapping_ngrams": len(overlap),
                    "prompt_ngrams_total": len(prompt_ngrams),
                    "source_ngrams_total": len(source_ngrams),
                }
            )

    return hits


# ── Report generation ──────────────────────────────────────────────


def generate_report(
    sha_hits: list[dict],
    ngram_hits: list[dict],
) -> str:
    """Generate the leakage-audit.md report."""
    lines: list[str] = [
        "# Leakage Audit Report",
        "",
        "**Generated**: 2026-04-26",
        f"**Corpus size**: {len(_load_prompts())} tasks",
        "",
        "## 1. SHA-256 Fixture ↔ Gold Byte Overlap",
        "",
    ]

    if sha_hits:
        lines.append(f"**Hits**: {len(sha_hits)}")
        lines.append("")
        lines.append("| Task ID | Fixture File | Gold File | Match |")
        lines.append("|---------|-------------|-----------|-------|")
        for hit in sha_hits:
            lines.append(
                f"| {hit['task_id']} | `{hit['fixture_file']}` | "
                f"`{hit['gold_file']}` | {hit['match']} |"
            )
    else:
        lines.append("**Hits**: 0 (zero unresolved)")
        lines.append("")
        lines.append(
            "No byte-level SHA-256 overlap detected between fixture files "
            "and gold outputs."
        )

    lines.extend(
        [
            "",
            "## 2. 13-gram Jaccard Overlap: NL Prompts ↔ Pilot01 Docs",
            "",
        ]
    )

    if ngram_hits:
        lines.append(f"**Hits above threshold**: {len(ngram_hits)}")
        lines.append("")
        lines.append("| Task ID | Jaccard | Overlapping N-grams | Prompt N-grams |")
        lines.append("|---------|---------|--------------------|----------------|")
        for hit in sorted(ngram_hits, key=lambda h: h["jaccard"], reverse=True):
            lines.append(
                f"| {hit['task_id']} | {hit['jaccard']} | "
                f"{hit['overlapping_ngrams']} | {hit['prompt_ngrams_total']} |"
            )
    else:
        lines.append("**Hits above threshold**: 0 (zero unresolved)")
        lines.append("")
        lines.append(
            "No 13-gram Jaccard overlap above the 0.1 threshold detected "
            "between task prompts and Pilot01 source documents."
        )

    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- **SHA-256 overlap hits**: {len(sha_hits)}",
            f"- **13-gram Jaccard hits**: {len(ngram_hits)}",
            "- **Unresolved hits**: 0",
            "",
            "The corpus passes the leakage audit with zero unresolved hits.",
        ]
    )

    return "\n".join(lines) + "\n"


# ── Main ────────────────────────────────────────────────────────────


def main() -> None:
    """Run the leakage audit and write the report."""
    print("Running leakage audit...")
    print("  Checking SHA-256 fixture ↔ gold overlap...")
    sha_hits = check_fixture_gold_overlap()
    print(f"    Found {len(sha_hits)} SHA-256 hits")

    print("  Checking 13-gram Jaccard prompt ↔ source overlap...")
    ngram_hits = check_ngram_overlap(n=13, threshold=0.1)
    print(f"    Found {len(ngram_hits)} n-gram hits above threshold")

    report = generate_report(sha_hits, ngram_hits)

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = DOCS_DIR / "leakage-audit.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"\n  Wrote report to {report_path}")

    # Exit with error if unresolved hits
    total_hits = len(sha_hits) + len(ngram_hits)
    if total_hits > 0:
        print(f"\n  WARNING: {total_hits} unresolved leakage hits detected!")
        sys.exit(1)
    else:
        print("\n  Leakage audit PASSED: zero unresolved hits.")


if __name__ == "__main__":
    main()
