# ClinProg-Bench Fixtures — Attribution

The files under this `fixtures/` directory are vendored (verbatim, unmodified)
from the **eSubmission Benchmark** clinical-trial regulatory substrate, which
is itself a derivative work based on the public CDISC SDTM/ADaM Pilot Project
("Pilot01") deliverables.

## Upstream source

- **Substrate**: eSubmission Benchmark v1.0.0
- **License**: Creative Commons Attribution 4.0 International (CC-BY-4.0)
- **Substrate tree in this repository**: `bench-program/track1-pilot01/external/eSubmission-Benchmark/`
- **Substrate citation**: see `LICENSE-eSubmissionBenchmark` in this directory and the substrate's `CITATION.cff`.

## What is vendored here

26 files are vendored — only the subset referenced by `inputs.fixtures` in the
250 task specifications. Total size ≈ 682 KB. Layout mirrors the substrate one
level down:

| Path | Purpose |
|------|---------|
| `01_study_design/` | Protocol (Pilot01) and Statistical Analysis Plan |
| `03_raw_data/` | Raw-data generator R script |
| `04_sdtm/` | SDTM specification, define.xml, and create-domain R programs |
| `05_adam/` | ADaM specification and define.xml |
| `06_tlfs/` | Mock TLF templates and TLF inventory |
| `08_validation/` | Master validation plan, consistency/quality reports |
| `DATASET_CARD.md` | Substrate-level data card |

## What is **not** vendored

42 fixture references in the 250 task specifications point at files that do
not yet exist in the upstream substrate. These are tracked as v0.1.1 work
(see `paper/sections/limitations.tex`). The reference loader silently skips
unresolvable paths, so adapter behaviour is unaffected.

## Attribution

If you use this benchmark, cite both:

1. ClinProg-Bench v0.1.0 — see the repository root `CITATION.cff`.
2. eSubmission Benchmark — see `LICENSE-eSubmissionBenchmark` and the
   substrate's `CITATION.cff`.

Per CC-BY-4.0, the substrate's license text accompanies these files
(`LICENSE-eSubmissionBenchmark`); no modifications are claimed beyond
selection and relocation.
