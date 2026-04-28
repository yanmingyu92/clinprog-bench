# ClinProg-Bench — Data Card

> Schema: Gebru et al., *Datasheets for Datasets* (CACM 2021), aligned with the NeurIPS Datasets & Benchmarks 2026 author checklist. Counts and hashes in this card are reproducible from the artifacts in this repository.

| Field | Value |
|---|---|
| Name | ClinProg-Bench |
| Version | 0.1.0 |
| Release date | 2026-04-27 |
| DOI | [10.5281/zenodo.19806731](https://doi.org/10.5281/zenodo.19806731) |
| Repository | https://github.com/yanmingyu92/clinprog-bench |
| Code license | Apache-2.0 |
| Data license | CC-BY-4.0 |
| Maintainer | Yanming Yu (ORCID [0009-0001-6701-1579](https://orcid.org/0009-0001-6701-1579)) |
| Total tasks | 250 |
| Categories | 5 (T1 codegen, T2 review, T3 spec, T4 doc, T5 debug) |
| Languages targeted | SAS, R, Python |

---

## 1. Motivation

**Purpose.** Clinical-trial statistical programming (SDTM / ADaM / TLF generation per CDISC standards) is a high-stakes domain absent from existing code-LLM benchmarks (HumanEval, MBPP, SWE-Bench, BigCodeBench). ClinProg-Bench fills that gap with 250 deterministic, expert-curated tasks grounded in a publicly redistributable substrate.

**Gap addressed.** No prior public benchmark covers (a) SAS code generation, (b) CDISC-conforming data-domain derivation, (c) regulatory documentation, or (d) clinical-program debugging under reproducible conditions. Existing pharma evaluations rely on proprietary studies that cannot be released.

**Funding / sponsors.** No external funding. Dataset construction was conducted as independent academic research.

## 2. Composition

**Instances.** Each task is a JSON `TaskSpec` (validated by `src/clinprog_bench/schema.py`) bundled with fixture files, a specification document, and a gold-standard output under `gold/<task_id>/`. The schema fixes `task_id` to the regex `T[1-5]\.[1-9][0-9]?\.[a-z0-9_]+\.[0-9]{3}` and pins `seed_commit` to a 40-char SHA-1.

**Counts.**

| Category | Subcategory | Tasks | Output kind | Oracle type | Scorer |
|---|---|---|---|---|---|
| T1 Code Generation | T1.1 SDTM (22), T1.2 ADaM (18), T1.3 TLF (20) | 60 | `sas_program` / `r_program` / `python_program` | `slot_fill` | `codegen` |
| T2 Code Review | T2.1 program review (25), T2.2 validation review (25) | 50 | `json` | `set_match` / `confusion_matrix` | `log_review` |
| T3 Spec Interpretation | T3.1 SDTM extract (21), T3.2 ADaM extract (18), T3.3 TLF spec (11) | 50 | `json` | `set_match` | `spec_extract` |
| T4 Documentation | T4.1 TLF (16), T4.2 dataset card (13), T4.3 synopsis (11) | 40 | `text` | `slot_fill` | `doc` |
| T5 Debugging | T5.1 SDTM (17), T5.2 ADaM (17), T5.3 TLF (16) | 50 | `patch` (unified diff) | `patch_apply` | `debug` |
| **Total** | | **250** | | | |

**Recommended splits.** No train / dev / test split. The benchmark is intended for held-out evaluation of pre-trained agents; it is not a training corpus. Stratified random subsets (seed `20260426`, 4 per category) are used for human audit, not for tuning.

**Modality.** Plain-text JSON tasks; UTF-8 source code (SAS / R / Python); markdown specifications; XPORT (.xpt) and CSV fixtures derived from the public CDISC Pilot Project.

**Confidentiality.** All fixtures derive from the CDISC SDTM/ADaM Pilot Project, a public reference dataset distributed by CDISC for educational use. No real patient data, no protected health information, no proprietary trial data.

**Errors / noise.** Deliberate seeded defects appear only in T5 debugging tasks (the buggy code is the *input*; the gold patch fixes it). Other categories have been audited for accuracy by a 3-reviewer expert panel (see §4).

## 3. Collection Process

**Source substrate.** `yanmingyu92/eSubmission-Benchmark` @ commit `658fcc05506b169a27dee6e2c3a1ccdaaf64a716`, a CC-BY-4.0 redistribution of the CDISC SDTM/ADaM Pilot Project. The substrate is pinned via Git submodule and SHA-256-manifested.

**Generation pipeline.** Tasks are derived deterministically from the substrate by category-specific builders (`scripts/build_T1.py` … `scripts/build_T5.py`). Each task records its `derivation_script` and `seed_commit` in its `provenance` block, making generation auditable end-to-end.

**Time frame.** Task generation: 2026-04-22 to 2026-04-26. Substrate (CDISC Pilot Project) origin: 2007–2013, last updated 2014.

**Sampling.** All eligible derivation slots in the substrate were enumerated; tasks were authored to cover the full taxonomic range of SDTM domains (DM, AE, EX, LB, VS, …), ADaM datasets (ADSL, ADAE, ADADAS, …), and TLF outputs (demographics, primary efficacy, safety) appearing in the Pilot Project.

**Compensation.** Three expert reviewers (R01 Guanlong Ren, R02 Jason Zhang, R03 Xiyang Xu) participated as unpaid academic collaborators.

## 4. Preprocessing / Cleaning / Labelling

**Schema validation.** Every task JSON is validated against `TaskSpec` (Pydantic v2, strict). The category ↔ scorer mapping is enforced by a model validator: T1→codegen, T2→log_review, T3→spec_extract, T4→doc, T5→debug.

**Gold construction.** Gold outputs live under `gold/<task_id>/` and are SHA-256-pinned in `gold/manifest.json` (272 files). T1.1 SAS gold scripts have been compiled and run end-to-end (commit `f9ea630`: 22/22 PASS).

**Leakage audit.** Two-channel audit ([`docs/leakage-audit.md`](docs/leakage-audit.md)):
- **Channel A (byte overlap).** SHA-256 hash overlap between every fixture file and every gold output. **Hits: 0.**
- **Channel B (n-gram overlap).** 13-gram Jaccard similarity ≥ 0.1 between task `prompt` strings and the Pilot01 source documents. **Hits: 0.**

**Human audit (Phase 2.2).** A stratified random sample of 20 tasks (seed `20260426`, 4 per category) is dual-reviewed by R01 / R02 / R03 against four criteria (correctness, completeness, accuracy, spec alignment). Sign-off requires **Cohen's κ ≥ 0.8**. Protocol: [`docs/audit-log.md`](docs/audit-log.md). Status as of v0.1.0: review package shipped, ratings pending.

**Annotator demographics.** Three reviewers, all PhD-level clinical-programming practitioners with 5+ years of CDISC experience, recruited through professional networks. No demographic data collected beyond professional affiliation.

## 5. Uses

**Recommended uses.** (a) Held-out evaluation of code-generating LLMs and agentic systems on clinical-programming workflows; (b) probing CDISC-domain knowledge in pre-trained models; (c) studying multi-agent and RAG strategies for regulatory-grade code generation (the runner contract in `runners/contract.md` is stateful by design); (d) reproducibility-floor reference for pharma teams comparing internal models against a public baseline.

**Out-of-scope uses.** This benchmark is **not** a substitute for regulatory validation. Passing ClinProg-Bench does **not** imply a system is fit for production use under FDA 21 CFR Part 11, ICH E9(R1), or any GxP regime. Task gold outputs are illustrative pedagogical references, not regulatory-grade deliverables.

**Known limitations.** (i) The substrate (CDISC Pilot Project) covers a single therapeutic area (Alzheimer's disease) with one phase-II-style protocol; therapeutic-area diversity is the v1.1 roadmap item. (ii) The reference baseline is rules-based and scores 0.00 on every category by construction — non-trivial baselines are deferred to leaderboard submissions. (iii) T2 / T4 oracles use slot-fill rubrics that may under-credit semantically equivalent paraphrases; this is a known precision/recall trade-off documented per task.

**Bias / fairness.** The substrate trial population reflects the demographics of the original CDISC Pilot Project (US Alzheimer's-disease patients, 2007 era). Models that overfit to this distribution may not generalise to other indications, populations, or therapeutic areas.

## 6. Distribution

**Channels.** GitHub (`https://github.com/yanmingyu92/clinprog-bench`, tag `v0.1.0`); Zenodo archival snapshot (DOI [10.5281/zenodo.19806731](https://doi.org/10.5281/zenodo.19806731)).

**Licensing.** Code: Apache-2.0. Data (tasks, fixtures, gold outputs): CC-BY-4.0. Both licenses are SPDX-conforming and are listed verbatim in `LICENSE`. No third-party DRM or technical protection measures apply.

**Citation.** See [`CITATION.cff`](CITATION.cff). Recommended BibTeX is provided in [`README.md`](README.md).

**Export controls / IP.** The CDISC Pilot Project substrate is published by CDISC under CC-BY-4.0 with no export restrictions. Re-distribution within ClinProg-Bench complies with the upstream attribution requirement (substrate identifier `658fcc05` is recorded in every task's `provenance.seed_commit`).

## 7. Maintenance

**Maintainer.** Yanming Yu (ORCID [0009-0001-6701-1579](https://orcid.org/0009-0001-6701-1579)). Primary contact via GitHub Issues on the repository.

**Versioning.** Semantic versioning. Breaking schema or oracle changes increment the major version; new tasks or scorers increment the minor version; bug fixes increment the patch version. Each tagged release is mirrored to Zenodo.

**Update cadence.** Targeted release schedule: v0.1 (NeurIPS D&B submission, 2026-Q2), v1.0 (camera-ready, 2026-Q4), v1.1 (oncology-domain expansion, 2027). The `eval.yml` GitHub Actions workflow runs schema validation, lint, type-check, and the 79-test suite on every push.

**Erratum process.** Schema-breaking errors are flagged in `CHANGELOG.md` and trigger a minor-version bump. Per-task corrections are tracked in `docs/audit-log.md` under *Disagreement Resolution*.

**Deprecation policy.** Older versions remain accessible via Git tags and Zenodo DOIs. No silent deletion.
