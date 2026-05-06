# ClinProg-Bench

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19806731.svg)](https://doi.org/10.5281/zenodo.19806731)
[![License: Apache-2.0](https://img.shields.io/badge/Code-Apache--2.0-blue.svg)](LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/Data-CC--BY--4.0-lightgreen.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Croissant](https://img.shields.io/badge/Croissant-metadata-orange.svg)](croissant.json)
[![CI](https://github.com/anonymous/clinprog-bench/actions/workflows/eval.yml/badge.svg)](https://github.com/anonymous/clinprog-bench/actions/workflows/eval.yml)

**The first public benchmark for evaluating LLM and agentic systems on clinical trial statistical programming tasks.**

ClinProg-Bench provides 250 expert-curated tasks across 5 categories, grounded in the [CDISC Pilot01](https://bitbucket.cdisc.org/projects/CED/repos/sdtm-adam-pilot-project/browse) dataset and FDA Therapeutic Classification Guidelines, with deterministic scoring and a language-agnostic evaluation framework.

---

## 📊 Task Taxonomy

| Category | Name | Tasks | Output Kind | Oracle | Scorer |
|----------|------|-------|-------------|--------|--------|
| **T1** | Code Generation | 60 | SAS / R / Python program | `slot_fill` | `codegen` |
| **T2** | Code Review | 50 | JSON (issues) | `slot_fill` | `log_review` |
| **T3** | Spec Interpretation | 50 | JSON (variables) | `slot_fill` | `spec_extract` |
| **T4** | Documentation | 40 | Text | `slot_fill` | `doc` |
| **T5** | Debugging | 50 | Patch (unified diff) | `patch_apply` | `debug` |

## 🚀 Quick Start

```bash
# Install
pip install clinprog-bench

# Validate all tasks
clinprog-bench validate tasks/

# Run reference baseline
python -m clinprog_bench.runners.reference_baseline
```

## 📁 Repository Structure

```
clinprog-bench/
├── src/clinprog_bench/       # Python package
│   ├── schema.py             # Pydantic TaskSpec schema
│   ├── scorers/              # 5 scorer modules (codegen, log_review, spec_extract, doc, debug)
│   ├── runners/              # Runner contract + reference baseline
│   └── cli.py                # CLI entry point
├── tasks/                    # 250 task JSON files (T1–T5)
├── gold/                     # Gold-standard outputs + SHA-256 manifest
├── scripts/                  # Task generators, leakage audit, execution harness
├── docs/                     # Annotation guide, audit log
├── review_package/           # 20-task subset for expert review
└── tests/                    # 79 unit + integration tests
```

## 🏆 Leaderboard

Single-turn baselines on a stratified 25-task subset (5 per category, seed `20260427`). Two conditions: **+grounding** inlines vendored CDISC fixtures (≤8&nbsp;KB/req) from `fixtures/`; **zero-shot** uses prompt only. Reference baseline runs all 250 tasks.

| Agent | T1 | T2 | T3 | T4 | T5 | Avg (+grounding) | Avg (zero-shot) |
|-------|-----|-----|-----|-----|-----|-----|-----|
| DeepSeek-Chat | 0.35 | 0.00 | 0.44 | 0.56 | 0.05 | **0.28** | 0.27 |
| Claude Sonnet 4.5 | 0.25 | 0.00 | 0.44 | 0.56 | 0.00 | **0.25** | 0.26 |
| GLM-4.5 | 0.10 | 0.00 | 0.08 | 0.44 | 0.07 | **0.14**¹ | 0.22 |
| Reference Baseline (rules-only, 250/250) | 0.25 | 0.00 | 0.00 | 0.00 | 0.00 | — | 0.05 |

¹ GLM-4.5 with grounding incurred 7 upstream timeouts (scored 0); the drop is operational, not capability-bounded. See `paper/sections/baselines.tex` for analysis.

*Submit your results via pull request to join the leaderboard. Full run details and per-task submissions: [`docs/leaderboard/`](docs/leaderboard/).*

## 🔬 Design Principles

- **Language-Agnostic**: Tasks accept SAS, R, and Python solutions. Scoring uses `pyreadstat` for dataset equivalence (no proprietary SAS runtime required for the SAS-Free tier).
- **Deterministic Evaluation**: All primary metrics are code-based (F1, exact match, patch apply). No LLM-as-a-judge.
- **Public Data Only**: Built entirely on CDISC Pilot01 and PHUSE public datasets. No proprietary clinical data.
- **Stateful Runner Contract**: Designed for multi-agent and RAG-augmented workflows, not just single-turn inference.
- **Reproducible**: SHA-256 manifests for all gold outputs. Reference baseline is bit-identical across reruns.

## 📝 Evaluation Tiers

| Tier | Requirements | Who |
|------|-------------|-----|
| **SAS-Free** | Python/R only; `pyreadstat` dataset diffs | Open-source ML researchers |
| **SAS-Required** | SAS runtime for AST/compile checks | Pharma industry teams |

## 🔗 Citation

```bibtex
@dataset{yu_clinprog_bench_2026,
  author    = {Jaime Yan},
  title     = {ClinProg-Bench: A Public Benchmark for Clinical Trial Statistical Programming Automation},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.19806731},
  url       = {https://doi.org/10.5281/zenodo.19806731}
}
```

## License

- **Code**: [Apache License 2.0](LICENSE)
- **Data**: [Creative Commons Attribution 4.0 International (CC-BY-4.0)](https://creativecommons.org/licenses/by/4.0/)

## Roadmap

- **v1.1**: Complex oncology dataset expansion
- **v1.0**: NeurIPS Datasets & Benchmarks 2026 submission
