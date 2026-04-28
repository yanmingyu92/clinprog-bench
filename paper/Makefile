# NeurIPS D&B 2026 paper build
# Requires: latexmk, biber/bibtex, neurips_2024.sty (download separately)

PAPER := main

.PHONY: all clean watch

all: $(PAPER).pdf

$(PAPER).pdf: $(PAPER).tex sections/*.tex refs.bib
	latexmk -pdf -interaction=nonstopmode -halt-on-error $(PAPER).tex

watch:
	latexmk -pdf -pvc -interaction=nonstopmode $(PAPER).tex

clean:
	latexmk -C
	rm -f $(PAPER).bbl $(PAPER).run.xml
