# ClinProg-Bench — NeurIPS D&B 2026 paper source

## Build

```bash
# 1. Download NeurIPS 2024 style (replace with 2026 release when published):
#    https://media.neurips.cc/Conferences/NeurIPS2024/Styles.zip
#    Extract `neurips_2024.sty` into this directory.

# 2. Build:
make            # produces main.pdf
make watch      # continuous rebuild
make clean
```

## Layout

```
paper/
├── main.tex              # entry point; \input{}s sections/
├── refs.bib              # bibliography (~12 entries; expand during lit review)
├── Makefile              # latexmk wrapper
└── sections/
    ├── abstract.tex
    ├── intro.tex
    ├── related.tex
    ├── dataset.tex       # mirrors DATA_CARD.md, summary form
    ├── benchmark.tex     # runner contract + scorers
    ├── baselines.tex     # placeholder rows; populated after B3 run
    ├── limitations.tex
    ├── ethics.tex
    └── checklist.tex     # NeurIPS D&B author checklist
```

## TODOs flagged in source

- `abstract.tex`: tighten to 200 words after baselines table is final.
- `intro.tex`: add 1–2 motivating examples.
- `related.tex`: expand each paragraph to 2–3 sentences with citations.
- `baselines.tex`: replace placeholder rows after B3 smoke run completes.
- `checklist.tex`: emit `croissant.json` before camera-ready.

## Status

v0.1.0 paper skeleton (2026-04-27). Sections compile against `neurips_2024.sty`.
Numbers cited (250 tasks, 79 tests, 0 leakage hits, DOI) are sourced from
`../DATA_CARD.md` and the v0.1.0 release artifacts.
