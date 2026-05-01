# ClinProg-Bench Review Package — Phase 2.2 Dual-Reviewer Audit

## Overview

This package contains 20 tasks (4 per category, stratified random sample) selected for independent dual-reviewer audit as part of ClinProg-Bench v0.1.0 governance.

## Directory Structure

```
review_package/
├── README.md              # This file
├── audit-log.md           # Audit template — fill in during review
├── T1/                    # Code Generation (4 tasks)
│   ├── T1.1.*.json        # Task specifications
│   └── gold/              # Gold-standard expected outputs
├── T2/                    # Code Review (4 tasks)
├── T3/                    # Spec Extraction (4 tasks)
├── T4/                    # Documentation (4 tasks)
└── T5/                    # Debugging (4 tasks)
```

## Review Instructions

1. **Read** each assigned task JSON and its gold output in the `gold/` subfolder.
2. **Evaluate** on four criteria: correctness, completeness, accuracy, specification alignment.
3. **Record** a per-task verdict: PASS / PASS-MINOR / FAIL.
4. **Log** findings in `audit-log.md`.

## Verdict Definitions

| Verdict | Meaning |
|---------|---------|
| **PASS** | Gold output meets all four criteria |
| **PASS-MINOR** | Minor issues that don't affect evaluation validity |
| **FAIL** | Substantive errors requiring revision |

## Reviewer Assignments

| Category | Reviewers |
|----------|-----------|
| T1 (Code Generation) | R01 + R02 |
| T2 (Code Review) | R02 + R03 |
| T3 (Spec Extraction) | R01 + R03 |
| T4 (Documentation) | R01 + R02 |
| T5 (Debugging) | R02 + R03 |

## Timeline

- **Return deadline**: [specified in email]
- **Target agreement**: Cohen's kappa >= 0.8
- **Disagreement resolution**: brief reconciliation call if needed

## Contact

Anonymous Author — Project Manager, ClinProg-Bench
