# `paper/` — ScaleRAG-TS manuscript

Everything the paper needs is in this folder. Upload the whole folder to Overleaf,
or build locally; nothing outside it is referenced.

```
main.tex        the entire manuscript (preamble, all 5 sections, all 3 tables)
references.bib  25 entries
figures/        architecture.pdf + fig1_motivation.pdf … fig6_sensitivity.pdf
                architecture.drawio — editable source for architecture.pdf
svjour3.cls     Springer journal class, v3.2
svglov3.clo     the class's default layout option file (loaded by svjour3)
spmpsci.bst     Springer maths/CS BibTeX style
main.pdf        last local build (11 pages)
```

## Build

```sh
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

Verified on TeX Live 2026: **0 overfull hboxes, 0 overfull vboxes, 0 undefined
references, 0 undefined citations, 0 LaTeX warnings, 0 BibTeX warnings**,
25/25 bibliography entries, 11 pages.

## Author block

The author block is anonymised. The same study is under anonymous review
elsewhere and this repository is public, so a named block on a near-identically
titled manuscript would defeat that anonymity. A generic camera-ready template
sits directly beneath it in `main.tex`; the real values are deliberately not
kept in this file, because a commented-out address is still greppable.

## Prior art in Related Work

Section 2 now credits three papers that between them cover the individual
ingredients of the method, and says so explicitly rather than claiming the
operation as new. RAFT subtracts a level offset from the query and from every
retrieved patch and restores the query's offset. RAID normalises a retrieved
trajectory by its own mean and standard deviation before mapping the aggregate
onto a target scale, though it predicts those target statistics with a trained
network because it addresses cold start. kNN-MTS augments a frozen forecaster
with a retrieval branch carrying no trainable parameters and the same convex
blend. What the literature does not contain is the composition, and that is
what the paper claims. See `docs/literature-verification.md` for the checks
behind these statements.

## Why the class files are vendored here

`svjour3.cls` is **not** in CTAN or TeX Live, and it is **not** in Overleaf's
default TeX tree either — Springer distributes it only inside its own author
template. A project that just says `\documentclass{svjour3}` therefore fails on
Overleaf with `File 'svjour3.cls' not found`. Keeping the class, its `.clo`, and
the `.bst` alongside `main.tex` makes the project build anywhere.

Provenance: taken from <https://github.com/latextemplates/svjour> (`svjour3.cls`
v3.2, `svglov3.clo`, `spmpsci.bst`), which mirrors Springer's distribution
unmodified. The files are Springer's and are intended for use when preparing a
submission to a Springer journal — which is exactly what this folder is.

## Layout notes

The class is `twocolumn`, so a column is only ~235 pt wide.

- **All three tables use `table*`** and all figures use `figure*`, spanning the
  full spread. This is not cosmetic: at `\columnwidth` the internal axis labels
  of `fig3`–`fig6` rendered at roughly 5 pt cap-height, below Springer's minimum.
  At `\textwidth` they land at 9–11 pt.
- The preamble sets `\emergencystretch=1em` plus a short `\hyphenation` list and
  loads `microtype`. That is what takes the manuscript from 34 overfull hboxes
  (worst 25 pt of ink in the margin) to zero, at the cost of two barely-loose
  lines (worst underfull badness 1184). It changes no content.

## Known issue

`figures/architecture.pdf` is 1248 × 634 pt. Scaled to `\textwidth` that is a
factor of 0.39, which puts its internal labels at **~3.2–3.9 pt** — too small to
read in print. Fixing it requires re-laying out `figures/architecture.drawio`
into a taller aspect ratio (target ≈ 4:3) with larger node fonts and re-exporting
to PDF; scaling the existing export cannot help, because the problem is the
diagram's aspect ratio, not its resolution.
