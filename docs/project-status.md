# Project Status

**Project:** ScaleRAG-TS (pivoted from GraphRoute-TS — the graph-routing hypothesis
was rejected). **Phases 1–11A complete.** Method + hyperparameters frozen. The M5 test
split `d_1914–d_1941` is **consumed** (Phase 10, locked). Phase 11B (native TS-RAG on
ETTh1/ETTm1/Weather/Electricity) is **pre-registered but blocked** — decision gate not
passed; those four datasets remain untouched.

> **Repo identity note (2026-07-24, resolved 2026-07-26):** this project's local folder
> was renamed from `graphroute-ts` to `ScaleRAG-TS`, and the GitHub repository is
> `ScaleRAG-Mathematical-Scale-Restoration-TSFM`. The remote now points there and pushing
> is verified working — no pending action. See `CLAUDE.md` → "Repo identity" for detail,
> including the venv breakage the `mv` caused (stale absolute paths in `.venv/`, fixed
> 2026-07-26). The Python package (`src/graphroute_ts/`) is intentionally unchanged.

## Phase summary

| Phase | Scope | Outcome |
|-------|-------|---------|
| 1 | Environment + reproducible workspace | ✅ uv/Python 3.11, Chronos-2 cu130, hooks, skills, agents |
| 2 | Leakage-safe M5 pipeline + classical baselines (synthetic) | ✅ ingest, chronological splits, metrics/WRMSSE, Seasonal Naive + LightGBM |
| 3 | Validate pipeline on **official M5** | ✅ full-panel ingest (59M rows), leakage-audit, LightGBM WRMSSE 0.71 |
| 4 | Frozen Chronos-2 + naive retrieval | ✅/⚠️ Chronos-2 integrated; naive Euclidean retrieval *hurts* (scale mismatch) |
| 5 | Scalable scale-aware retrieval (FAISS) | ✅ scale restoration fixes it; `mean/L2/cat/k20` frozen baseline; full-panel feasible |
| 6 | Typed graph + graph-guided retrieval | ❌ frozen graph/GraphSAGE ≈ random controls |
| 7 | Learned relation-aware router (M5) | ❌ relation ≡ temporal; metadata util-corr 0.003 |
| 8 | Favorita transfer + graph kill test | ❌ rejected cross-dataset (metadata util-corr −0.063); hypothesis falsified |
| 9 | **ScaleRAG-TS** (pivot): scale-aware retrieval + gated fusion | ⚖️ best method; controlled-study framing (see below) |
| 10 | M5 held-out **test** confirmation (single locked run) | ⚖️ frozen verdict confirmed on untouched data; 0/3 pre-registered criteria met |
| 11A | Native TS-RAG feasibility on ETTm2 (dev-only) | ❌ decision gate 4/5 (condition 3 fails) → Phase 11B blocked |

## Frozen M5/Favorita result (Phase 9–10, do not re-litigate)

- **ScaleRAG_gated** = mean/L2/category/k=20 + scale restoration + learned gate.
- Full-panel validation: beats target-only Chronos-2 **+5.08%** RMSSE on M5
  (CI [4.97, 5.19]); **+0.83%** on Favorita — **regime-dependent** (helps intermittent,
  marginal on dense).
- **M5 test split `d_1914–d_1941` consumed once** (Phase 10, `M5_TEST_CONSUMED.lock`):
  confirmed **+5.49%** RMSSE over Chronos-2 (CI [5.40, 5.59]) but only **+0.69%** over
  the strongest simple baseline (LightGBM, below the 3% bar), **loses** the official
  WRMSSE to LightGBM/seasonal-naive, and is beaten by frozen Chronos-2 on
  MAE/WAPE/MASE/pinball/coverage → **0/3 pre-registered criteria met**. Do not re-run
  (harness refuses while the lock exists).
- Scale restoration is decisive (ablation: 0.7425 → 2.7884 RMSSE without it, 3.8×).
  Learned gate beats fixed fusion (~1.1%). Calibration regresses (cov80 0.69 vs Chronos
  0.79) — reported, mitigable post-hoc.
- Cross-dataset graph-routing **negative** is the secondary contribution.

## Phase 11A result (native TS-RAG feasibility, ETTm2 dev-only — do not re-litigate)

Tested whether the same scale-restoration mechanism transfers to the **official TS-RAG**
benchmark regime (context 512, horizon 64, frozen Chronos-Bolt, MSE/MAE), using **only
ETTm2** as development data.

- Official TS-RAG reproduced to **≤0.10%** of published numbers (decision-gate
  condition 1: met).
- Restored retrieval beats raw retrieval **+85.4%** MSE (CI [+85.2%, +85.6%], 7/7
  channels) — the mechanism itself transfers (condition 2: met).
- **But** the frozen restored-fusion config (scale=mean, k=20, weight=0.25, selected on
  val only) is **−0.85%** MSE vs. frozen Chronos-Bolt (CI [−1.39%, −0.28%], significantly
  *worse*) and **−2.30%** vs. official TS-RAG on ETTm2 test (condition 3: **fails**).
  ScaleRAG is also Pareto-dominated on latency (~2.4× slower for a worse result; 0
  trainable params vs. TS-RAG's 4.78 M ARM).
- **Decision gate: 4/5 conditions met → Phase 11B NOT initiated.** ETTh1, ETTm1, Weather,
  Electricity remain unopened (`docs/phase11b-preregistration.md`, frozen but not
  executed).
- Full detail: `docs/scalerag-native-dev-report.md`, `docs/tsrag-official-audit.md`,
  `docs/tsrag-ettm2-reproduction.md`, `docs/scalerag-native-{dev-results,frozen-config}.json`.

## Publication assets (current)

- `ScaleRAG_Final_Audit_Report.md` — whole-project audit prepared for NotebookLM review;
  verdict: strong "YES" for an Applied Intelligence submission, framed as a **"Mechanism &
  Regime Taxonomy"** paper (not a SOTA-accuracy claim). Key defense against the
  "self-inflicted-wound" critique (reviewers may argue scale mismatch is an artifact of
  using primitive statistical k-NN instead of neural retrieval like TS-RAG): lean on the
  Pareto/efficiency argument — 0 trainable params vs. TS-RAG's 4.78 M, and statistical
  restoration is uniquely suited to extreme sparsity (M5) where neural retrieval
  struggles; concede TS-RAG wins on dense data (ETTm2).
- **`paper/` — the single home for everything paper-related** (consolidated 2026-07-26).
  Upload this one folder to Overleaf; nothing outside it is needed.
  - `paper/main.tex` — the **whole manuscript in one file**: svjour3 twocolumn preamble,
    abstract, all five sections, and all three tables inlined as `table*` (each keeping its
    full source-provenance comment block). Figures are referenced as `figures/figN_*.pdf`;
    there are no `\input`s and no `../` paths.
  - `paper/references.bib` — 22 entries. The only `.tex`-adjacent file kept separate.
  - `paper/figures/` — 6 vector PDFs, `fig1_motivation.pdf` … `fig6_sensitivity.pdf`,
    written directly by `scripts/make_phase11a_figures.py`, plus `architecture.pdf` — the
    end-to-end pipeline diagram (Fig. 1 of the paper), authored in draw.io and kept as
    editable source alongside it in `architecture.drawio`. It is vector, fonts embedded and
    subsetted, no raster layers. Re-export from the `.drawio` with **Dark unchecked** and a
    border (the first export was dark-themed and edge-clipped).

  **Figure-design rules** (redrawn 2026-07-26; the script enforces them):
  - **One y-axis per panel — never a twin axis.** Two measures of different scale become
    small multiples. This is why `fig6` is three panels: a dual-scale plot implies a
    correlation the data does not contain.
  - **Direct end-labels** on lines rather than legend boxes parked over the data; a legend
    only where marks cannot be labelled in place (`fig3b`, where four curves converge).
  - **No trend line through incomparable populations.** `fig4` deliberately omits the
    connecting curve the earlier version drew through five different datasets on two
    different metrics — no such fit was ever estimated.
  - Solid hairline gridlines on the value axis only; top/right spines dropped.
  - Palette validated colour-blind-safe all-pairs (blue `#2a78d6` = ours/restored, orange
    `#eb6834` = raw/target-only, violet `#4a3aa7` = TS-RAG; worst deutan ΔE 13.0, worst
    normal-vision ΔE 16.3, all ≥3:1 on white).
  - **Exemplar windows are representative, not flattering.** `fig3` picks the window whose
    fused error is nearest the median; `fig1`'s selection criteria are unchanged from the
    original. Every value still traces to a locked artifact.

  - `paper/svjour3.cls`, `paper/svglov3.clo`, `paper/spmpsci.bst` — the Springer class and
    bib style, vendored because they ship with neither TeX Live nor Overleaf.
  - `paper/main.pdf` — the compiled 10-page manuscript; `paper/README.md` records the build
    command, the verification counts, and the class provenance.

  Supersedes the former `manuscript/` (5 section files) and `latex_assets/` (3 table files),
  both removed in the same commit — their content is preserved verbatim inside `main.tex`,
  including the `table` → `table*` fix so the tables span the two-column spread. No numbers
  were changed at any point. Verified 0 overfull hboxes / 0 undefined refs /
  0 undefined citations / 0 bibtex warnings / 22-of-22 citation keys matched.
  **Claims are aligned to the locked results:** the LightGBM gate is named as the sole
  trainable component (M5 is *not* parameter-free), retrieval is described as exact —
  FAISS-CPU for ETTm2, bit-identical batched-GPU for the M5 full panel, never
  "GPU-accelerated FAISS" — and a dedicated subsection reports all held-out M5 negatives
  (0/3 criteria, WRMSSE loss, +0.69% over LightGBM, coverage regression).

## Controlled synthetic affine probe (2026-07-26)

Causal validation of the scale-restoration mechanism against the "this is just
denormalization" critique, using **synthetic data only** — no M5/Favorita split is
touched and no Phase-11B dataset is opened. A query is built as an exact affine
image `x' = a·x + b` of a known donor motif, so retrieval and reconstruction can be
scored separately. 5 seeds, paired bootstrap CIs. Full detail:
`docs/affine-probe-report.md`; code `src/graphroute_ts/affine_probe.py` +
`scripts/affine_probe_run.py`.

- **Retrieval invariance:** raw-space top-1 hit rate collapses from 1.000 (control)
  to 0.176 (chance 0.083) under transform; normalised retrieval stays at 1.000.
  Δ = **+0.744**, CI95 [+0.702, +0.784].
- **Invariance alone is insufficient:** normalised retrieval without restoration
  finds the correct motif every time yet forecasts no better than the series mean
  (nmse 0.75→1.87). Restoration Δnmse = **−1.508**, CI95 [−1.71, −1.272].
- **Restoration is exactly affine-equivariant:** `znorm+restore` error is constant to
  **8.7 × 10⁻¹⁹** across the whole (a, b) grid; the residual is the noise floor.
- **Limitation found, reported not fixed (rules 9, 12):** the frozen config uses
  `scale="mean"`, which is *exactly scale*-equivariant but has **no location term**.
  Under an offset its nmse degrades 291× (0.00067 → 0.195) and hit rate falls to
  0.580. Not acted on — changing the frozen scale after seeing results would be
  test-driven tuning, and the M5 test split is consumed.
- Makes **no** end-to-end accuracy claim; the recorded negatives stand unchanged.

## Deliverables

- Code: full pipeline through Phase 11A (see `CLAUDE.md` architecture); ruff + mypy
  clean; every phase committed (branch `hf-demo`, ahead of/merged with `main` history).
- Docs (paper artifacts): `scalerag-ts-method`, `scalerag-ts-validation-report`,
  `final-experiment-report`, `ablation-report`, `calibration-analysis`,
  `threats-to-validity`, `paper-outline`, `scalerag-final-tables.json`, the Phase-10
  locked artifacts (`final-heldout-test-report`, `scalerag-heldout-test-tables`,
  `final-abstract`), and the full Phase-11A set listed above.

## Open / next (only if authorized)

- ~~Rename the GitHub repository~~ — **done 2026-07-26**; remote points at
  `ScaleRAG-Mathematical-Scale-Restoration-TSFM` and pushing is verified.
- ~~Obtain `svjour3.cls` + `spmpsci.bst`~~ — **done 2026-07-26.** The real Springer class
  (v3.2), `svglov3.clo`, and `spmpsci.bst` are now vendored in `paper/` (provenance in
  `paper/README.md`); they are in neither TeX Live nor Overleaf's default tree, which is
  what caused the `File 'svjour3.cls' not found` failure. `paper/main.pdf` is a real local
  build: **10 pages, 0 overfull hbox/vbox, 0 undefined refs, 0 undefined citations,
  0 LaTeX warnings, 0 BibTeX warnings, 22/22 entries.**
- **`figures/architecture.pdf` is illegible at print size** — 1248 × 634 pt scaled to
  `\textwidth` is a factor of 0.39, putting its labels at ~3.2–3.9 pt. Needs
  `architecture.drawio` re-laid-out to roughly 4:3 with larger node fonts, then re-exported.
  Rescaling the existing PDF cannot fix it; the problem is aspect ratio, not resolution.
- Draft the remaining paper sections around the frozen tables/figures/audit report.
- Phase 11B stays **blocked** unless the Phase-11A gate result changes — do not open the
  four final datasets to "rescue" the result (rules 2, 9, 12).
Kaggle credentials are read from the environment (see `.env.example`) and are never committed or echoed.
