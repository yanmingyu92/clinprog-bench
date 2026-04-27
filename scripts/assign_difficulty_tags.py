"""Assign difficulty_tag to all task JSONs based on complexity.

Reads every task JSON under tasks/, computes a difficulty_tag from the
complexity field and other heuristics, writes the updated JSON back,
and reports counts.

Difficulty mapping:
  simple  → easy
  mixed   → medium
  complex → hard

Usage:
    python scripts/assign_difficulty_tags.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks"

COMPLEXITY_TO_DIFFICULTY = {
    "simple": "easy",
    "mixed": "medium",
    "complex": "hard",
}


def assign_tags() -> dict[str, int]:
    """Assign difficulty_tag to all task JSONs. Returns count by tag."""
    counts: dict[str, int] = {}
    updated = 0

    for json_file in sorted(TASKS_DIR.rglob("*.json")):
        if json_file.name == "_schema.json":
            continue

        data = json.loads(json_file.read_text(encoding="utf-8"))
        complexity = data.get("complexity", "mixed")
        tag = COMPLEXITY_TO_DIFFICULTY.get(complexity, "medium")

        old_tag = data.get("difficulty_tag")
        if old_tag != tag:
            data["difficulty_tag"] = tag
            json_file.write_text(
                json.dumps(data, indent=2) + "\n",
                encoding="utf-8",
            )
            updated += 1

        counts[tag] = counts.get(tag, 0) + 1

    return {"updated": updated, "counts": counts}


def main() -> None:
    """Run the tag assignment."""
    print("Assigning difficulty_tag to all tasks...")
    result = assign_tags()
    print(f"  Updated {result['updated']} task(s)")
    print("  Tag distribution:")
    for tag, count in sorted(result["counts"].items()):
        print(f"    {tag}: {count}")
    total = sum(result["counts"].values())
    print(f"  Total: {total} tasks")


if __name__ == "__main__":
    main()
