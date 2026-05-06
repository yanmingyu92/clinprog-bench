# Missing Fixture Files: 15 SDTM R Programs and 27 TLF Mock Templates

## Summary

When building [ClinProg-Bench](https://github.com/anonymous/clinprog-bench) on top of the `eSubmission-Benchmark` substrate (commit `658fcc05`), we identified **42 fixture file paths** referenced by benchmark tasks that do not exist in the repository. These fall into two categories:

1. **15 SDTM domain-creator R programs** — placeholder programs referenced by T2.1 (review) and T5.1 (debug) tasks
2. **27 TLF mock template Markdown files** — shell templates referenced by T1.3 (code generation), T4.1 (documentation), and T5.3 (debug) tasks

## Request

We would like the maintainers to either:

- **(A)** Author these missing files and include them in a future release, **or**
- **(B)** Mark their scope explicitly (e.g., "not planned for v1.0", "would accept PRs"), so that downstream consumers can document the coverage gap accurately.

## Category 1: Missing SDTM Domain-Creator R Programs

All located under `programs/` in the SDTM section. Currently only 5 programs exist (`create_ae.R`, `create_dm.R`, `create_sdtm_spec.R`, `create_vs.R`, `path.R`).

| # | Missing File | Referenced By |
|---|---|---|
| 1 | `create_ae_v2.R` | T5.1.sdtm_ae_v2_debug.010 |
| 2 | `create_cm.R` | T2.1.cm_review.002, T5.1.sdtm_cm_debug.002 |
| 3 | `create_dm_v2.R` | T5.1.sdtm_dm_v2_debug.009 |
| 4 | `create_ds.R` | T2.1.ds_review.003, T5.1.sdtm_ds_debug.003 |
| 5 | `create_ex.R` | T2.1.ex_review.004, T5.1.sdtm_ex_debug.004 |
| 6 | `create_lb.R` | T2.1.lb_v2_review.009, T2.1.supplb_review.015 |
| 7 | `create_lb_v2.R` | T5.1.sdtm_lb_v2_debug.011 |
| 8 | `create_mh.R` | T2.1.mh_review.005, T5.1.sdtm_mh_debug.005 |
| 9 | `create_qs.R` | T2.1.qs_review.006, T5.1.sdtm_qs_debug.006 |
| 10 | `create_sc.R` | T2.1.sc_review.007, T5.1.sdtm_sc_debug.007 |
| 11 | `create_suppae.R` | T5.1.sdtm_suppae_debug.014 |
| 12 | `create_suppdm.R` | T5.1.sdtm_suppdm_debug.013 |
| 13 | `create_supplb.R` | T5.1.sdtm_supplb_debug.015 |
| 14 | `create_sv.R` | T2.1.sv_review.008, T5.1.sdtm_sv_debug.008 |
| 15 | `create_vs_v2.R` | T5.1.sdtm_vs_v2_debug.012 |

**Suggested content:** Each program should create the corresponding SDTM domain from raw data, following the pattern established by the existing `create_ae.R` and `create_dm.R`. Programs suffixed `_v2` should contain intentional seeded defects (distinct from the v1 versions) for the debug task category.

## Category 2: Missing TLF Mock Template Files

All located under `mock_templates/` in the TLF section. Currently 7 mock templates exist (covering primary endpoint, demographics, AE overview, AE by SOC/PT, efficacy ANCOVA, KM plot, and a README).

### Sub-category 2a: Hyphenated Naming (15 files)

Used by T1.3 (code generation) and T4.1 (documentation) tasks.

| # | Missing File | Table/Figure ID | Topic | Referenced By |
|---|---|---|---|---|
| 1 | `f_mock_14-5-02_forest.md` | 14-5.02 | Forest plot | T1.3.tlf_forest_gen.048 |
| 2 | `t_mock_14-1-01_screen.md` | 14-1.01 | Screening | T1.3.tlf_screen_gen.046, T4.1.tlf_screen_doc.011 |
| 3 | `t_mock_14-1-02_deviation.md` | 14-1.02 | Protocol deviations | T1.3.tlf_protocol_dev_gen.047 |
| 4 | `t_mock_14-1-04_medhist.md` | 14-1.04 | Medical history | T1.3.tlf_medhist_gen.044, T4.1.tlf_medhist_doc.010 |
| 5 | `t_mock_14-2-01_disposition.md` | 14-2.01 | Disposition | T1.3.tlf_disposition_gen.037, T4.1.tlf_disposition_doc.003 |
| 6 | `t_mock_14-2-02_conmed.md` | 14-2.02 | Concomitant medications | T1.3.tlf_conmed_gen.038, T4.1.tlf_conmed_doc.004 |
| 7 | `t_mock_14-2-03_exposure.md` | 14-2.03 | Exposure | T1.3.tlf_exposure_gen.041, T4.1.tlf_exposure_doc.007 |
| 8 | `t_mock_14-2-04_visit.md` | 14-2.04 | Visit compliance | T1.3.tlf_visit_comp_gen.049 |
| 9 | `t_mock_14-3-02_cfb.md` | 14-3.02 | Change from baseline | T1.3.tlf_cfb_gen.040, T4.1.tlf_cfb_doc.006 |
| 10 | `t_mock_14-3-03_responder.md` | 14-3.03 | Responder analysis | T1.3.tlf_responder_gen.042, T4.1.tlf_responder_doc.008 |
| 11 | `t_mock_14-4-03_safety.md` | 14-4.03 | Safety summary | T1.3.tlf_safety_sum_gen.050, T4.1.tlf_safety_sum_doc.012 |
| 12 | `t_mock_14-4-04_severity.md` | 14-4.04 | AE by severity | T1.3.tlf_ae_severity_gen.051, T4.1.tlf_ae_severity_doc.013 |
| 13 | `t_mock_14-6-01_lab_summary.md` | 14-6.01 | Lab summary | T1.3.tlf_lab_summary_gen.039, T4.1.tlf_lab_summary_doc.005 |
| 14 | `t_mock_14-6-02_shift.md` | 14-6.02 | Lab shift table | T1.3.tlf_shift_gen.043, T4.1.tlf_shift_doc.009 |
| 15 | `t_mock_14-6-03_ecg.md` | 14-6.03 | ECG | T1.3.tlf_ecg_gen.045 |

### Sub-category 2b: Underscore Naming (12 files)

Used by T5.3 (debug) tasks. Note: some of these overlap logically with the hyphenated variants above (same table ID, different naming convention). We recommend consolidating to a single naming convention.

| # | Missing File | Table/Figure ID | Topic | Referenced By |
|---|---|---|---|---|
| 1 | `t_mock_14_1_04.md` | 14-1.04 | Medical history | T5.3.tlf_medhist_debug.010 |
| 2 | `t_mock_14_2_01.md` | 14-2.01 | Disposition | T5.3.tlf_disposition_debug.003 |
| 3 | `t_mock_14_2_02.md` | 14-2.02 | Concomitant medications | T5.3.tlf_conmed_debug.008 |
| 4 | `t_mock_14_2_03.md` | 14-2.03 | Exposure | T5.3.tlf_exposure_debug.009 |
| 5 | `t_mock_14_3_01.md` | 14-3.01 | Primary endpoint | T5.3.tlf_primary_v2_debug.011 |
| 6 | `t_mock_14_3_02.md` | 14-3.02 | Change from baseline | T5.3.tlf_cfb_debug.004 |
| 7 | `t_mock_14_3_03.md` | 14-3.03 | Responder analysis | T5.3.tlf_responder_debug.006 |
| 8 | `t_mock_14_4_01.md` | 14-4.01 | AE overview | T5.3.tlf_ae_overview_debug.002 |
| 9 | `t_mock_14_4_04.md` | 14-4.04 | AE by severity | T5.3.tlf_ae_severity_v2_debug.012 |
| 10 | `t_mock_14_5_02.md` | 14-5.02 | Forest plot | T5.3.tlf_forest_debug.013 |
| 11 | `t_mock_14_6_01.md` | 14-6.01 | Lab summary | T5.3.tlf_lab_summary_debug.005 |
| 12 | `t_mock_14_6_02.md` | 14-6.02 | Lab shift table | T5.3.tlf_shift_table_debug.007 |

**Suggested content:** Each mock template should follow the format established by existing templates (e.g., `t_mock_14-3-01_primary_endpoint.md`): table/figure ID, title, population, columns, row structure, analysis description, and any footnotes. Templates suffixed `_v2` or used by debug tasks should contain intentional seeded defects.

## Naming Convention Note

The benchmark currently uses two naming conventions for mock templates:
- **Hyphenated** (`t_mock_14-2-01_disposition.md`) — used by code-generation and documentation tasks
- **Underscore** (`t_mock_14_2_01.md`) — used by debug tasks

Many of these represent the same logical template. We recommend standardizing to **one convention** (hyphenated with descriptive suffix preferred, matching the existing authored files) and updating downstream task references accordingly.

## Impact

These 42 missing files represent a **38% fixture coverage gap** in ClinProg-Bench v0.1.0 (25 of 67 unique fixture paths are authored). The benchmark runner silently skips unresolvable paths, so zero-shot baselines are unaffected, but the grounding condition is upper-bounded by this coverage gap. Authoring these files would increase fixture coverage to 100% and enable fairer evaluation of grounded clinical programming agents.

## Environment

- **Substrate commit:** `658fcc05506b169a27dee6e2c3a1ccdaaf64a716`
- **Benchmark version:** ClinProg-Bench v0.1.0 (Zenodo DOI: `withheld-for-double-blind-review`)
- **License:** CC-BY-4.0 (matching eSubmission-Benchmark)
