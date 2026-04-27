# Audit Log — ClinProg-Bench Seed Corpus (Phase 2.2)

> This document records the dual-reviewer audit of the 20-task stratified random subset
> (4 tasks per category) required for Phase 2.2 sign-off.

## Audit Parameters

| Parameter | Value |
|-----------|-------|
| **Subset size** | 20 tasks (4 per category: T1–T5) |
| **Selection method** | Stratified random sampling (seed: 20260426) |
| **Required agreement** | Cohen's kappa >= 0.8 |
| **Reviewers** | R01 (Guanlong Ren), R02 (Jason Zhang), R03 (Xiyang Xu) |
| **Audit date** | _pending_ |

## Reviewer Assignment

| Category | Tasks | Assigned Reviewers |
|----------|-------|--------------------|
| T1 (Code Generation) | 4 | R01 + R02 |
| T2 (Code Review) | 4 | R02 + R03 |
| T3 (Spec Extraction) | 4 | R01 + R03 |
| T4 (Documentation) | 4 | R01 + R02 |
| T5 (Debugging) | 4 | R02 + R03 |

## Review Package Contents

### T1 — Code Generation (4 tasks)

| task_id | Title | Kind | Oracle Type |
|---------|-------|------|-------------|
| T1.1.sdtm_dm_gen.001 | Generate SAS program to create SDTM DM domain | sas_program | slot_fill |
| T1.1.sdtm_lb_gen.001 | Generate SAS program to create SDTM LB domain | sas_program | slot_fill |
| T1.2.adam_adae_gen.001 | Generate R program to derive ADAE from SDTM | r_program | slot_fill |
| T1.2.adam_adadas_gen.001 | Generate R program to derive ADADAS | r_program | slot_fill |

### T2 — Code Review (4 tasks)

| task_id | Title | Kind | Oracle Type |
|---------|-------|------|-------------|
| T2.1.r_dm_review.001 | Review R program for DM domain creation | json | set_match |
| T2.2.val_quality_review.001 | Quality review of validation output | json | confusion_matrix |
| T2.2.val_treatment_review.001 | Treatment assignment review | json | confusion_matrix |
| T2.2.val_doc_checklist.001 | Validation documentation checklist | json | confusion_matrix |

### T3 — Spec Extraction (4 tasks)

| task_id | Title | Kind | Oracle Type |
|---------|-------|------|-------------|
| T3.1.sdtm_dm_extract.001 | Extract SDTM DM variable metadata | json | set_match |
| T3.1.sdtm_domain_list.001 | List all SDTM domains from define.xml | json | set_match |
| T3.1.sdtm_ex_extract.001 | Extract SDTM EX variable metadata | json | set_match |
| T3.2.adam_adae_extract.001 | Extract ADAE derivation logic | json | set_match |

### T4 — Documentation (4 tasks)

| task_id | Title | Kind | Oracle Type |
|---------|-------|------|-------------|
| T4.1.tlf_demo_doc.001 | Demographics table documentation | text | slot_fill |
| T4.1.tlf_ae_doc.001 | AE table documentation | text | slot_fill |
| T4.2.dataset_card_doc.001 | Dataset card documentation | text | slot_fill |
| T4.3.study_synopsis.001 | Study synopsis documentation | text | slot_fill |

### T5 — Debugging (4 tasks)

| task_id | Title | Kind | Oracle Type |
|---------|-------|------|-------------|
| T5.2.adam_adadas_debug.001 | Debug ADADAS derivation logic | patch | patch_apply |
| T5.2.adam_adsl_debug.001 | Debug ADSL derivation errors | patch | patch_apply |
| T5.3.tlf_demo_debug.001 | Debug demographics table program | patch | patch_apply |
| T5.3.tlf_primary_debug.001 | Debug primary efficacy table | patch | patch_apply |

---

## Review Protocol

Each reviewer independently evaluates each task on these criteria:

1. **Correctness**: Does the gold output correctly solve the task?
2. **Completeness**: Does the gold output cover all required elements?
3. **Accuracy**: Are labels, values, and formatting precise?
4. **Specification alignment**: Does the output match the referenced spec?

### Per-Task Verdict

- **PASS**: Gold output meets all criteria
- **PASS-MINOR**: Gold output has minor issues that don't affect evaluation
- **FAIL**: Gold output has substantive errors requiring revision

---

## Review Results

### Per-Task Evaluations

<!-- Template — fill in during audit

#### T1.1.sdtm_dm_gen.001

| Criterion | R01 | R02 | Agree? |
|-----------|-----|-----|--------|
| Correctness | | | |
| Completeness | | | |
| Accuracy | | | |
| Spec alignment | | | |
| **Verdict** | | | |

Notes:

End template -->

_Results to be filled in during audit._

---

## Inter-Rater Agreement

### Agreement Matrix

| | R01: PASS | R01: PASS-MINOR | R01: FAIL |
|---|-----------|-----------------|-----------|
| **R02: PASS** | | | |
| **R02: PASS-MINOR** | | | |
| **R02: FAIL** | | | |

### Cohen's Kappa Calculation

```python
# Will be computed after all reviews are submitted
# Required: kappa >= 0.8
from sklearn.metrics import cohen_kappa_score
# r01_verdicts = [...]
# r02_verdicts = [...]
# kappa = cohen_kappa_score(r01_verdicts, r02_verdicts)
```

**Result**: _pending_

---

## Disagreement Resolution Log

| Task ID | Reviewer A | Reviewer B | Disagreement | Resolution | Resolved by |
|---------|-----------|-----------|--------------|------------|-------------|
| _none yet_ | | | | | |

---

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Reviewer R01 | Guanlong Ren | _pending_ | _pending_ |
| Reviewer R02 | Jason Zhang | _pending_ | _pending_ |
| Reviewer R03 | Xiyang Xu | _pending_ | _pending_ |
| Operator | Yanming Yu | _pending_ | _pending_ |

**Phase 2.2 Status**: AWAITING REVIEWER AUDIT
