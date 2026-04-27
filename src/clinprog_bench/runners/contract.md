# Agent Runner Contract

> **Version:** 0.1.0-draft
> **Last updated:** 2026-04-26

## 1. Overview

The runner contract defines how an agent interacts with the ClinProg-Bench
evaluation pipeline. It is **language-agnostic**: agents may be written in
Python, R, SAS, or any other language, provided they conform to the workspace
protocol described below.

## 2. Workspace Protocol

### 2.1 Workspace Layout

For each task, the runner creates an isolated workspace directory:

```
workspace/
├── task.json          # The TaskSpec JSON for this task
├── fixtures/          # Symlinks to relevant fixture files
├── spec/              # Specification documents (if any)
├── output/            # Agent writes results here
├── output/metadata.json  # Optional metadata (timing, tool calls, etc.)
└── output/submission.json # Required: final submission envelope
```

### 2.2 Lifecycle

1. **Setup** — The runner creates the workspace, populates `task.json` and
   `fixtures/`, and starts a timer.
2. **Execution** — The agent reads `task.json`, accesses `fixtures/`, and
   writes its outputs into `output/`. The agent may read/write freely within
   the workspace during the allocated time window.
3. **Submission** — The agent writes `output/submission.json` with its final
   answer. The file must be valid JSON conforming to the Submission schema.
4. **Teardown** — The runner collects the submission, records timing metadata,
   and cleans up the workspace.

### 2.3 Time Limits

- Default: 300 seconds (5 minutes) per task.
- Configurable via `--timeout` CLI flag.
- If the agent exceeds the time limit, the runner treats it as an empty
  submission.

## 3. Submission Format

```json
{
  "task_id": "T1.1.adsl.001",
  "agent_name": "my-agent-v2",
  "outputs": {
    "main.sas": "proc sort data=dm; by usubjid; run; ...",
    "metadata.json": "{...}"
  },
  "metadata": {
    "wall_time_seconds": "42.3",
    "tool_call_count": "5"
  }
}
```

### 3.1 Output Keys by Category

| Category | Expected output keys | Format |
|----------|---------------------|--------|
| T1 Code Generation | `main.sas` / `main.R` / `main.py` | Source code |
| T2 Code Review | `review.json` | JSON: list of `{line, severity, category, message}` |
| T3 Spec Interpretation | `extraction.json` | JSON: variable lists / derivation predicates |
| T4 Documentation | `document.sas` / `document.md` | Filled template |
| T5 Debugging | `patch.diff` | Unified diff |

### 3.2 Metadata

The `metadata` field is informational and does not affect scoring. Agents may
log wall-clock time, number of tool calls, or other diagnostics here.

## 4. Adapter Interface (Python)

Python-based agents can subclass `BaseAdapter` from
`clinprog_bench.runners`:

```python
from pathlib import Path
from clinprog_bench.runners import BaseAdapter, Submission
from clinprog_bench.schema import TaskSpec

class MyAgent(BaseAdapter):
    agent_name = "my-agent"

    def run(self, task: TaskSpec, workspace: Path) -> Submission:
        # Read fixtures, call LLM, write outputs
        ...
        return Submission(
            task_id=task.task_id,
            agent_name=self.agent_name,
            outputs={"main.sas": generated_code},
        )
```

## 5. Multi-Agent / RAG Support

The workspace is **stateful**: agents may create intermediate files, maintain
context across tool calls, and implement multi-agent orchestration patterns
within the workspace directory during the allocated time window.

Agents that use retrieval-augmented generation (RAG) may:
- Index `fixtures/` into a vector store within the workspace.
- Maintain retrieval state between iterations.
- Cache intermediate reasoning in workspace files.

All of this happens within the workspace; the runner only reads
`output/submission.json` at the end.

## 6. Leaderboard Submission

Each leaderboard entry corresponds to a single run of an agent across all
tasks:

```
leaderboard/submissions/<agent_name>/<date>/
├── manifest.json           # Lists all task submissions
├── T1.1.adsl.001.json
├── T1.1.adsl.002.json
└── ...
```

The runner produces this directory structure automatically from the adapter
outputs.

## 7. Reproducibility Requirements

- Agents must accept a `--seed` flag and produce deterministic outputs for a
  given seed.
- Three runs with the same seed must produce bit-identical results.
- Run-to-run variance > 5 percentage points on overall score triggers an
  "unstable" flag on the leaderboard.
