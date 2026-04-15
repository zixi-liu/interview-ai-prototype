# LaTeX build: Scale Collapse, Model Disagreement, and False Precision

NeurIPS 2024 style (preprint mode, non-anonymous) — ready for arXiv submission.

## Files

- `main.tex` — manuscript source
- `references.bib` — BibTeX database
- `main.bbl` — pre-built bibliography (included so arXiv does not need to rerun bibtex)
- `neurips_2024.sty` — NeurIPS 2024 LaTeX class
- `figures/*.pdf` — all 7 figures (vector PDFs)
- `main.pdf` — compiled 16-page output

## Build locally

```
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

Requires `texlive-latex-base`, `texlive-latex-recommended`, `texlive-latex-extra`, `texlive-fonts-recommended`, `texlive-science`.

## arXiv submission

Upload a tarball containing:
- `main.tex`, `main.bbl`, `neurips_2024.sty`, `references.bib`
- `figures/` directory

arXiv will recompile with TeX Live; the included `main.bbl` ensures no bibtex rerun is required.
