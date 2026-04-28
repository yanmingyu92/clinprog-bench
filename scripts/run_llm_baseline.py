"""Run an LLM baseline on a (stratified) subset of ClinProg-Bench.

Usage:
    uv run python scripts/run_llm_baseline.py \
        --adapter deepseek --per-category 5 --seed 20260427

Requires:
    DEEPSEEK_API_KEY exported, or a key=value line in either
    ./.env or ../.env (the bench-program/.env file).

Outputs:
    docs/leaderboard/results-<agent>-<YYYYMMDD>.json
    docs/leaderboard/submissions/<agent>/<YYYYMMDD>/<task_id>.json
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from collections import defaultdict
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from clinprog_bench.runners import BaseAdapter, Submission  # noqa: E402
from clinprog_bench.runners.reference_baseline import ReferenceBaseline  # noqa: E402
from clinprog_bench.schema import TaskSpec, validate_tasks_dir  # noqa: E402
from clinprog_bench.scorers.codegen import CodegenScorer  # noqa: E402
from clinprog_bench.scorers.debug import DebugScorer  # noqa: E402
from clinprog_bench.scorers.doc import DocScorer  # noqa: E402
from clinprog_bench.scorers.log_review import LogReviewScorer  # noqa: E402
from clinprog_bench.scorers.spec_extract import SpecExtractScorer  # noqa: E402

_SCORERS = {
    "codegen": CodegenScorer(),
    "log_review": LogReviewScorer(),
    "spec_extract": SpecExtractScorer(),
    "doc": DocScorer(),
    "debug": DebugScorer(),
}


def _load_dotenv() -> None:
    """Best-effort .env loader (no python-dotenv dep)."""
    for candidate in (REPO_ROOT / ".env", REPO_ROOT.parent / ".env"):
        if not candidate.is_file():
            continue
        for line in candidate.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


def _stratified_sample(
    tasks: list[TaskSpec], per_category: int, seed: int
) -> list[TaskSpec]:
    rng = random.Random(seed)
    by_cat: dict[str, list[TaskSpec]] = defaultdict(list)
    for t in tasks:
        by_cat[t.category].append(t)
    out: list[TaskSpec] = []
    for cat in sorted(by_cat):
        bucket = sorted(by_cat[cat], key=lambda t: t.task_id)
        rng.shuffle(bucket)
        out.extend(bucket[:per_category])
    return out


def _build_adapter(name: str) -> BaseAdapter:
    if name == "reference":
        return ReferenceBaseline()
    if name == "deepseek":
        from clinprog_bench.runners.adapters.deepseek import DeepSeekAdapter

        return DeepSeekAdapter()
    if name == "glm":
        from clinprog_bench.runners.adapters.glm import GLMAdapter

        return GLMAdapter()
    if name == "claude":
        from clinprog_bench.runners.adapters.claude import ClaudeAdapter

        return ClaudeAdapter()
    msg = f"Unknown adapter: {name}"
    raise SystemExit(msg)


def _score(task: TaskSpec, sub: Submission) -> dict[str, object]:
    scorer = _SCORERS[task.scoring.scorer]
    gold_dir = REPO_ROOT / task.expected_outputs.gold_path
    score = scorer.score(task, sub, gold_dir)
    return {
        "task_id": score.task_id,
        "category": score.category,
        "pass": score.pass_flag,
        "primary": score.primary_metric,
        "secondary": score.secondary_metrics,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--adapter", default="deepseek")
    p.add_argument("--per-category", type=int, default=5)
    p.add_argument("--seed", type=int, default=20260427)
    p.add_argument("--tasks-dir", type=Path, default=REPO_ROOT / "tasks")
    p.add_argument("--out-dir", type=Path, default=REPO_ROOT / "docs" / "leaderboard")
    args = p.parse_args()

    _load_dotenv()
    adapter = _build_adapter(args.adapter)
    all_tasks = validate_tasks_dir(args.tasks_dir)
    sample = _stratified_sample(all_tasks, args.per_category, args.seed)

    run_date = date.today().strftime("%Y%m%d")
    sub_dir = args.out_dir / "submissions" / adapter.agent_name / run_date
    sub_dir.mkdir(parents=True, exist_ok=True)

    scores: list[dict[str, object]] = []
    t_start = time.monotonic()
    for i, task in enumerate(sample, 1):
        try:
            sub = adapter.run(task, REPO_ROOT)
        except Exception as exc:  # adapter must not crash the harness
            print(f"[{i}/{len(sample)}] {task.task_id}  ERROR  {exc}", flush=True)
            sub = Submission(task_id=task.task_id, agent_name=adapter.agent_name)
        result = _score(task, sub)
        scores.append(result)
        (sub_dir / f"{task.task_id}.json").write_text(
            json.dumps(
                {
                    "task_id": sub.task_id,
                    "agent_name": sub.agent_name,
                    "outputs": sub.outputs,
                    "metadata": sub.metadata,
                    "score": result,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(
            f"[{i}/{len(sample)}] {task.task_id}  "
            f"primary={result['primary']:.3f}  pass={result['pass']}",
            flush=True,
        )

    by_cat: dict[str, list[float]] = defaultdict(list)
    for r in scores:
        by_cat[str(r["category"])].append(float(r["primary"]))
    cat_means = {c: sum(v) / len(v) for c, v in by_cat.items()}
    macro = sum(cat_means.values()) / len(cat_means) if cat_means else 0.0

    summary = {
        "agent_name": adapter.agent_name,
        "run_date": run_date,
        "seed": args.seed,
        "per_category": args.per_category,
        "n_tasks": len(sample),
        "wall_time_seconds": round(time.monotonic() - t_start, 2),
        "macro_score": round(macro, 4),
        "category_means": {c: round(m, 4) for c, m in cat_means.items()},
        "results": scores,
    }
    out_file = args.out_dir / f"results-{adapter.agent_name}-{run_date}.json"
    out_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nMacro: {macro:.4f}  ({len(sample)} tasks)  -> {out_file}")


if __name__ == "__main__":
    main()
