# ClinProg-Bench — NeurIPS 2026 E&D Track Submission Package

## Submission Checklist

Upload the following to the **E&D OpenReview portal**:
https://openreview.net/group?id=NeurIPS.cc%2F2026%2FEvaluations_and_Datasets_Track

### Required Uploads

| # | File | OpenReview Field | Size |
|---|------|-----------------|------|
| 1 | `ClinProg-Bench_submission.pdf` | Paper PDF | ~275 KB |
| 2 | `supplementary/clinprog-bench-supplementary.zip` | Supplementary Material | ~4.2 MB |
| 3 | `croissant.json` | Croissant Metadata | ~6 KB |

### OpenReview Form Settings

| Field | Value |
|-------|-------|
| Track | Evaluations & Datasets |
| Review mode | **Double-blind** |
| Dataset URL | *(withheld — full code in supplementary ZIP)* |

### Deadlines

- **Abstract**: May 4, 2026 AoE
- **Full paper + all materials**: May 6, 2026 AoE

## Package Contents

```
submission/
├── ClinProg-Bench_submission.pdf    # Main paper (11pp, anonymized)
├── croissant.json                   # MLCommons Croissant metadata (core + RAI)
├── README.md                        # This file
├── main.tex                         # LaTeX source
├── neurips_2026.sty                 # Official NeurIPS 2026 style
├── refs.bib                         # Bibliography
├── sections/                        # LaTeX section files
│   ├── abstract.tex
│   ├── intro.tex
│   ├── related.tex
│   ├── dataset.tex
│   ├── benchmark.tex
│   ├── baselines.tex
│   ├── limitations.tex
│   ├── ethics.tex
│   ├── checklist.tex                # Official 16-item NeurIPS checklist
│   └── reproducibility.tex
└── supplementary/
    ├── README.md                    # Supplementary package manifest
    └── clinprog-bench-supplementary.zip  # Anonymized benchmark (865 files)
```

## Verification

The PDF was built with `neurips_2026.sty` using `\usepackage[eandd]{neurips_2026}`.
To rebuild: `pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex`
