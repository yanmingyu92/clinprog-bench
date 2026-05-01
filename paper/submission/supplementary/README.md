# ClinProg-Bench — Supplementary Materials

## Contents

This supplementary package accompanies the NeurIPS Evaluations & Datasets 2026
submission "ClinProg-Bench: A Public Benchmark for Clinical-Trial Statistical
Programming Automation."

### 1. Benchmark Code & Data (anonymized repository snapshot)

The full benchmark is hosted on GitHub (URL withheld for double-blind review)
and archived on Zenodo (DOI withheld). For reviewer inspection, we include:

| Directory | Contents |
|-----------|----------|
| `src/clinprog_bench/` | Python package: schema, 5 scorers, runner contract, CLI |
| `tasks/` | All 250 task JSON specifications (T1–T5) |
| `gold/` | Gold-standard outputs + SHA-256 manifest |
| `fixtures/` | Vendored CDISC Pilot01 fixture subset (26 files, 682 KB) |
| `scripts/` | Task generators, leakage audit, baseline runner |
| `tests/` | 79 unit + integration tests |
| `review_package/` | 20-task audit subset + completed dual-reviewer audit log |

### 2. Key Quality Artifacts

- **`DATA_CARD.md`** — Gebru-style datasheet (provenance, composition, licensing)
- **`croissant.json`** — MLCommons Croissant machine-readable metadata
- **`docs/leakage-audit.md`** — Two-channel leakage audit report (SHA-256 + 13-gram, 0 hits)
- **`review_package/audit-log.md`** — Completed dual-reviewer audit (κ = 0.82)
- **`CITATION.cff`** — Citation metadata with Zenodo DOI

### 3. Reproducibility

```bash
# Install (Python >= 3.11)
pip install .

# Validate all tasks
clinprog-bench validate tasks/
pytest -q   # 79 tests, <1s

# Reference baseline (all 250 tasks)
python -m clinprog_bench.runners.reference_baseline
```

LLM baselines require API keys; see `scripts/run_llm_baseline.py --help`.

### 4. Licensing

- **Code**: Apache License 2.0
- **Data (tasks, gold, fixtures)**: CC-BY-4.0
- **Substrate**: CDISC Pilot01 (CC-BY-4.0)

### 5. Anonymization Note

All author-identifying information has been removed from this package.
The GitHub repository URL and Zenodo DOI are withheld for double-blind review
and will be provided for camera-ready.
