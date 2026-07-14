# Paper Outline — ScaleRAG-TS

## Recommended title
**ScaleRAG-TS: A Controlled Study of Scale-Aware Retrieval Augmentation and
Relational Metadata for Time-Series Foundation Models.**

(Alternative, if the retrieval gain is emphasised: *"When Does Retrieval Help a
Time-Series Foundation Model? A Scale-Aware, Regime-Dependent Study with a
Cross-Dataset Graph-Routing Negative."*)

## Framing
A rigorous, pre-registered, leakage-controlled study — **not** a SOTA claim. Two
genuinely positive, honest contributions and one clean negative, all with
confidence intervals and controls across two datasets.

## Contributions (claims we can defend)
1. **Scale-aware retrieval augmentation of a frozen TSFM.** Mean-scaled matching +
   **exact scale restoration** turns naive retrieval (which *hurts*, +RMSSE) into a
   useful augmentation, improving target-only Chronos-2 by **+4.86%** RMSSE on the M5
   1k subset (CI [4.30, 5.39]) and **+5.49%** on the **locked full-panel held-out
   test** `d_1914–d_1941` (CI [+5.40, +5.59]; validation +5.08%). Scale restoration is
   the decisive component (ablation: 0.74 → 2.79 without it).
2. **Learned uncertainty-aware gated fusion.** A small gate over retrieval
   confidence/disagreement, intermittency, volume, and Chronos uncertainty routes
   each series between the TSFM and retrieval; it beats fixed-weight fusion
   (0.7173 vs 0.7252) and is the best method overall on M5.
3. **Regime-dependent benefit (novel, honest).** Retrieval augmentation helps
   strongly on **intermittent** data (M5, +4.86%) but marginally on **denser** data
   (Favorita, +0.83%); the gate adapts by deferring to Chronos where retrieval is
   unreliable.
4. **Cross-dataset relational-metadata negative.** Across M5 and Favorita — with
   non-learned and *learned* routers, shuffled-relation and random-label controls,
   and confidence intervals — **typed-relation graph routing adds no predictive
   retrieval value** beyond temporal/statistical similarity (metadata-only utility
   correlation 0.003 on M5, −0.063 on Favorita). Richer Favorita metadata does not
   help.
5. **Methodological finding.** On intermittent-retail RMSSE, **recent-mean and
   LightGBM are punishing baselines**; a foundation model + retrieval helps the
   model but does not beat them by a pre-registered margin — a cautionary result for
   the field's benchmarking.

## Claims we explicitly do NOT make
- **No SOTA / leaderboard claim.** On the **full-panel official M5 WRMSSE** (now
  computed on the held-out test), ScaleRAG (1.223) does **not** win — LightGBM (0.866)
  and Seasonal-Naive (0.870) are better. The +5.49% headline is **RMSSE-specific**.
- **No general point-accuracy win.** Frozen Chronos-2 is best on MASE/WAPE/MAE and is
  the best-calibrated forecaster; ScaleRAG's fusion under-covers and trades absolute/
  probabilistic accuracy for squared-error accuracy (all reported).
- No superiority over RAFT / TS-RAG originals (only *inspired* reimplementations
  under our protocol).
- **0 / 3 pre-registered criteria met** on the untouched test split — the negative is
  confirmed, not softened.

## Proposed section structure
1. Introduction — retrieval-augmented forecasting; the intermittent-retail challenge.
2. Related work + **protocol-comparability table** (M5 winner, AME-TS, GNBAN, RAFT,
   TS-RAG, Chronos-2) — with explicit non-comparability flags.
3. Method — ScaleRAG-TS: scale-aware retrieval, scale restoration, gated fusion,
   leakage protocol.
4. Experimental protocol — datasets, splits, metrics, paired bootstrap,
   pre-registration.
5. Results — matched baselines, cross-dataset, slices, ablations.
6. Gate & calibration analysis.
7. The graph-routing negative (M5 + Favorita, controls).
8. Threats to validity.
9. Conclusion — when retrieval helps a TSFM; a cautionary benchmarking note.

## Reproducibility statement
Full pipeline, seeds, `uv.lock`, leakage tests, and machine-readable result tables
released. The M5 test split `d_1914–d_1941` was reserved untouched during
development and **consumed exactly once** after freezing (Phase 10, commit
`d42d20e`, `M5_TEST_CONSUMED.lock`); the harness blocks further test runs. Locked
results: `docs/final-heldout-test-report.md`, `docs/scalerag-heldout-test-tables.json`,
`docs/final-abstract.md`. The full-panel run uses a GPU exact-k-NN retriever verified
bit-identical to the frozen numpy retriever (`scripts/verify_gpu_retrieval.py`).

## Next step (only if reviewers want it; secondary)
A small **adapter/LoRA** efficiency experiment on the frozen backbone — reported
separately, never used to rescue the retrieval headline (Phase 9 Part D, deferred).
