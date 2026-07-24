# ScaleRAG-TS Independent Audit Packet
## 1. Audit packet purpose
This packet combines the project's final research evidence into a single, structured, searchable Markdown document for **independent publication-readiness review in NotebookLM**.

Scope and caveats the reviewer must apply:

- **Project reports are not independent evidence.** The narrative documents and machine-readable tables in this packet are produced by the project itself. They establish what was *claimed* and what was *measured under the project's own protocol*.
- **Literature sources uploaded separately to NotebookLM must be used to verify novelty, related-work comparisons, and external claims.** No literature sources are bundled in this packet.
- **Numbers must be checked against the machine-readable tables.** Section 13 (`scalerag-final-tables.json`, `scalerag-heldout-test-tables.json`) is authoritative; narrative numbers in Sections 4-11 must match it.
- **The M5 held-out test was consumed exactly once.** The `d_1914-d_1941` split was reserved untouched during development, then evaluated by a single locked run after configuration freezing (Phase 10, commit `d42d20e`, `M5_TEST_CONSUMED.lock`). The test-driven-tuning is blocked by project rules 2, 9, 12.

## 2. Source manifest
- **Git commit (HEAD):** `623a03618209b8c7a44894b143f0f2ca12dbfc04`
- **Branch:** `hf-demo`
- **Study tag:** ScaleRAG-TS controlled study (Phases 1-10)
- **Repository status:** clean (no uncommitted changes)
- **Packet generation date:** 2026-07-14

| § | Source | Status | Role | Kind | Replacement |
|---|---|---|---|---|---|
| 4 | `docs/final-heldout-test-report.md` | found | Held-out test verdict | narrative | - |
| 5 | `docs/final-experiment-report.md` | found | Final controlled-study report | narrative | - |
| 6 | `docs/scalerag-ts-method.md` | found | Method specification | narrative | - |
| 7 | `docs/ablation-report.md` | found | Ablation evidence | narrative | - |
| 8 | `docs/calibration-analysis.md` | found | Calibration evidence | narrative | - |
| 9.1 | `docs/graph-retrieval-report.md` | found | Relational routing: non-learned graph | narrative | - |
| 9.2 | `docs/learned-router-report.md` | found | Relational routing: learned M5 router | narrative | - |
| 9.3 | `docs/favorita-router-report.md` | found | Relational routing: learned Favorita router | narrative | - |
| 10 | `docs/threats-to-validity.md` | found | Threats to validity | narrative | - |
| 11.1 | `docs/final-abstract.md` | found | Final abstract & contribution list | narrative | - |
| 11.2 | `docs/paper-outline.md` | found | Paper outline | narrative | - |
| 12.1 | `README.md` | found | Repository README (extract) | narrative | - |
| 12.2 | `docs/reproducibility-policy.md` | found | Reproducibility policy | narrative | - |
| 12.3 | `spaces/scalerag-demo/README.md` | found | Hugging Face demo README | narrative | - |
| 13.A | `docs/scalerag-final-tables.json` | found | Validation matrix (M5 1k + Favorita 5k) | machine-readable | - |
| 13.B | `docs/scalerag-heldout-test-tables.json` | found | Held-out test + full-panel validation | machine-readable | - |

All listed source files were found at the recorded paths. No file was missing; no substitution was required.

## 3. Frozen study summary
Extracted from `docs/final-heldout-test-report.md` and `docs/final-experiment-report.md` (preserved verbatim below in Sections 4 and 5). Numbers are not reinterpreted.
| field | value |
|---|---|
| Final paper title | **ScaleRAG-TS: A Controlled Study of Scale-Aware Retrieval Augmentation and Relational Metadata for Time-Series Foundation Models.** (Alternative framing in `docs/paper-outline.md`.) |
| Research question | Does scale-aware temporal retrieval + a learned uncertainty-aware gated fusion improve a **frozen** Chronos-2 backbone on intermittent-retail forecasting, and does typed-relation graph routing add retrieval value beyond temporal/statistical similarity? |
| Frozen Chronos-2 backbone | Official `amazon/chronos-2`, frozen (`backbone_frozen: true`, `backbone_params_updated: 0` on the held-out test). |
| Trained components | A small LightGBM gate over retrieval nn-distance, retrieval-disagreement, intermittency, log-volume, Chronos uncertainty, and scale-spread. 3 seeds averaged (42/43/44); ~9,000 ensemble leaf values; ~9,000 LightGBM leaf values; no neural parameters are trained. |
| Frozen components | Chronos-2 backbone (0 trainable parameters). Retriever design (mean/L2 / category-filter / k=20 + scale restoration). Pre-registered success criteria. The pipeline and leakage guards. |
| Datasets and sizes | M5 (Walmart) - full panel of 30,490 series, d_1..d_1941. Favorita (Corporación Favorita) - 5,000-series streamed subset, 1,000 days, 9 typed entity attributes (item, family, class, perishable, store, type, cluster, city, state). Both intermittent retail; zero-fraction 0.68 (M5) and 0.263 (Favorita). |
| Validation horizon | M5 `d_1886-d_1913` (28 days, eval origin d_1885). For the locked study, validation was additionally re-run on the full 30,490-series panel at the same origin. |
| Test horizon | M5 `d_1914-d_1941` (28 days, eval origin d_1913). Full 30,490-series panel. Consumed exactly once (`M5_TEST_CONSUMED.lock`, commit `d42d20e`). |
| Final selected configuration | `ScaleRAG_gated`: mean/L2/category-filter/k=20 + scale restoration + LightGBM gate. Frozen before the held-out run. |
| Pre-registered success criteria | C1: ≥3% rel. RMSSE/WRMSSE over the strongest matched baseline with 95% CI excluding 0. C2: ≥5% over target-only Chronos-2 on **both** M5 and Favorita. C3: ≥7% on a predefined sparse/intermittent/low-volume/reduced-history slice over the strongest baseline. |
| Held-out test verdict | **0/3 pre-registered criteria met** on untouched M5 test data. ScaleRAG improves Chronos-2 by +5.49% RMSSE (CI [+5.40%, +5.59%]) but only +0.69% over the strongest baseline (lightgbm) - an order of magnitude below the 3% bar. The method does not win the official WRMSSE, and the RMSSE gain reverses on MAE/WAPE/MASE/pinball/coverage. |
| Main positive finding | Scale-aware retrieval + scale restoration + uncertainty-aware gated fusion improves a frozen Chronos-2 by +5.49% RMSSE on the M5 held-out test (CI [+5.40%, +5.59%]), confirming validation (+5.08%). |
| Main negative finding | The gain is **RMSSE-specific and regime-dependent**: it does not beat the strongest simple baseline (lightgbm) by the pre-registered 3% margin, does not win the official dollar-weighted WRMSSE, and reverses on MAE/WAPE/MASE/pinball/coverage where the **frozen Chronos-2 alone is best**. All three pre-registered criteria fail. |
| Calibration limitation | Gated fusion **under-covers**: 80% coverage 0.698 (test) and 0.706 (val) vs Chronos-2 0.786/0.791. No post-hoc calibration multiplier was applied because none was fitted and frozen during the study (rule 5); raw coverage is reported. Point-preserving post-hoc widening is offered as a calibration-aware option (not a rescue of the headline). |
| Cross-dataset relational-routing negative | Across M5 and Favorita, with non-learned and *learned* routers, shuffled-relation and random-label controls, and confidence intervals - typed-relation graph routing adds no predictive retrieval value beyond temporal/statistical similarity. Metadata-utility correlation: 0.003 (M5), -0.063 (Favorita). Richer Favorita metadata does not change this. |
| Claims explicitly NOT made | No SOTA / leaderboard claim (ScaleRAG does not win official WRMSSE). No general point-accuracy win (Chronos-2 is best on MASE/WAPE/MAE). No superiority over the original RAFT / TS-RAG papers (only *inspired* reimplementations under the project protocol). No LoRA or TSFM fine-tuning (deferred; never used to rescue the headline). |

## 4. Final held-out test report
Verbatim contents of `docs/final-heldout-test-report.md`. This is **project-generated evidence** - not independently verified.
<!-- BEGIN SOURCE: final-heldout-test-report.md -->

# ScaleRAG-TS — Final Held-Out Test Report (Phase 10)

**Single locked confirmation run on the reserved M5 test split `d_1914–d_1941`.**
The method, hyperparameters, gate, retrieval config, and pre-registered success
criteria were **frozen before** this run; nothing was tuned on the test results.
The test split is now **consumed** (`M5_TEST_CONSUMED.lock`) and further
test-driven tuning is blocked (rules 2, 9, 12).

## Provenance

| | |
|---|---|
| Eval window | `d_1914–d_1941` (last 28 public M5 days), forecast origin `d_1913` |
| Population | **Full M5 panel, 30,490 series** (canonical WRMSSE valid) |
| Frozen method | `ScaleRAG_gated` = mean/L2/category-filter/k=20 + scale restoration + LightGBM gate (seeds 42/43/44) |
| Gate-training origins | `val_m2 = d_1829`, `val_m1 = d_1857` — **unchanged from the frozen study** (historical-only) |
| Git commit | `d42d20e3bc4d6096f82349d16284b5b6da00346f` |
| Hardware | RTX 5070 Ti, CUDA 13.0, torch 2.13.0+cu130, Python 3.11.15 |
| Retriever | GPU batched-exact k-NN, **verified bit-identical** to the frozen numpy retriever on the 1,000-series validation subset (max point diff `0.0`) |

The GPU retriever is an arithmetic-only acceleration of the frozen exact k-NN (no
method change): it reproduces the frozen validation numbers bit-for-bit
(`scripts/verify_gpu_retrieval.py`), and made the full-panel run tractable
(retrieval **42 s/origin** vs an estimated ~4.8 h for the numpy path).

## Headline verdict (confirmed on untouched test data)

**All three pre-registered success criteria FAIL on the held-out test.** ScaleRAG
improves the frozen Chronos-2 backbone on **RMSSE** but does not beat the strongest
simple baseline by the pre-registered margin, does not win the official
**WRMSSE**, and its RMSSE gain does **not** carry over to absolute-error or
probabilistic metrics. The controlled-study framing stands, now on data never seen
during development.

## Full metrics (30,490 series, `d_1914–d_1941`)

Lower is better for every column. Best in **bold**.

| method | RMSSE | WRMSSE | MASE | WAPE | MAE | pinball |
|---|---|---|---|---|---|---|
| **ScaleRAG_gated** (proposed) | **0.7612** | 1.2231 | 1.020 | 0.698 | 1.008 | 0.298 |
| lightgbm | 0.7665 | **0.8663** | 1.077 | 0.740 | 1.067 | 0.534 |
| recent_mean | 0.7669 | 1.0876 | 1.074 | 0.745 | 1.075 | 0.538 |
| fusion_fixed0.5 | 0.7692 | 1.3809 | 0.991 | 0.691 | 0.997 | 0.296 |
| retrieval_scaleaware | 0.7795 | 1.2293 | 1.111 | 0.743 | 1.072 | 0.326 |
| chronos2_target (frozen) | 0.8054 | 1.9395 | **0.893** | **0.665** | **0.960** | **0.289** |
| seasonal_naive | 0.9972 | 0.8697 | 1.211 | 0.862 | 1.244 | 0.622 |

**No method dominates — the winner depends on the metric:**
- **RMSSE (squared, scaled):** ScaleRAG wins (0.7612), +5.49% over Chronos-2.
- **WRMSSE (official M5, dollar-weighted, hierarchical):** LightGBM (0.8663) and
  Seasonal-Naive (0.8697) win; ScaleRAG (1.2231) is mid-pack, Chronos-2 worst.
- **MASE / WAPE / MAE / pinball / coverage (absolute & probabilistic):** the
  **frozen Chronos-2 alone is best**. ScaleRAG's fusion trades typical-case and
  calibrated-distribution accuracy for squared-error accuracy.

This metric-dependent reordering is the central honest result: retrieval fusion
reduces large (squared) errors on intermittent series while slightly worsening
average-magnitude and probabilistic accuracy.

## Paired-bootstrap 95% CIs (per-series relative RMSSE improvement, 2,000 resamples)

| comparison | rel. improvement | 95% CI | excludes 0 |
|---|---|---|---|
| ScaleRAG vs **Chronos-2** | **+5.49%** | [+5.40%, +5.59%] | yes |
| ScaleRAG vs **strongest baseline (lightgbm)** | **+0.69%** | [+0.57%, +0.82%] | yes |
| retrieval_scaleaware vs Chronos-2 | +3.22% | [+3.03%, +3.40%] | yes |
| fusion_fixed0.5 vs Chronos-2 | +4.49% | [+4.40%, +4.58%] | yes |
| lightgbm vs Chronos-2 | +4.83% | [+4.67%, +5.00%] | yes |
| recent_mean vs Chronos-2 | +4.78% | [+4.62%, +4.94%] | yes |

The ScaleRAG–vs–strongest CI excludes zero (a real but small edge over LightGBM on
RMSSE), yet is an order of magnitude below the pre-registered **3%** bar.

## Pre-registered success criteria — verdict

| # | criterion | result on test | met? |
|---|---|---|---|
| C1 | ≥3% rel. RMSSE/WRMSSE over the strongest matched baseline, CI excl. 0 | RMSSE +0.69% (<3%); WRMSSE **worse** than lightgbm/seasonal | **NO** |
| C2 | ≥5% over target-only Chronos-2 on **both** M5 and Favorita | M5 test +5.49% ✓; Favorita +0.83% ✗ | **NO** |
| C3 | ≥7% on a predefined sparse/intermittent/low-volume/reduced-history slice over strongest | best such slice +0.93% (reduced-history); intermittent −0.03%, low-volume −0.30% | **NO** |

**0 / 3 criteria met** → no positive forecasting-improvement claim; the work is a
controlled study (as pre-registered).

## Pre-registered slices (ScaleRAG vs Chronos-2 / vs strongest, RMSSE)

| slice | n | vs Chronos-2 | vs strongest (lightgbm) |
|---|---|---|---|
| intermittent (zero-frac > 0.8) | 11,783 | **+5.97%** [+5.81, +6.13] | −0.03% [−0.17, +0.13] |
| low-volume (< median) | 15,241 | **+6.85%** [+6.71, +6.99] | −0.30% [−0.43, −0.17] |
| reduced-history (< 100 non-zero) | 1,778 | +3.14% [+2.63, +3.61] | +0.93% [+0.40, +1.51] |
| dense (zero-frac < 0.3) | 2,247 | +0.34% [+0.12, +0.56] | **+5.04%** [+4.28, +5.90] |

Retrieval augmentation helps the **backbone** most on sparse/low-volume series
(+6–7% vs Chronos-2) but there it merely *matches* the strong LightGBM/recent-mean
baselines. The one place ScaleRAG clearly beats the strongest baseline is the
**dense** slice (+5.04%) — the opposite of the sparse-data motivation, and still
short of C3's 7% on a *sparse* slice.

## Calibration / coverage (nominal 50 / 80 / 90%)

| method | cov50 | cov80 | cov90 | width80 |
|---|---|---|---|---|
| chronos2_target | 0.358 | **0.786** | **0.907** | 2.84 |
| retrieval_scaleaware | 0.525 | 0.728 | 0.805 | 2.04 |
| fusion_fixed0.5 | 0.307 | 0.715 | 0.848 | 2.44 |
| ScaleRAG_gated | 0.306 | 0.698 | 0.828 | 2.40 |

The frozen Chronos-2 is the best-calibrated forecaster; the gated fusion
**under-covers** (80% coverage 0.698 vs 0.786). No post-hoc calibration multiplier
was applied because none was fitted and frozen during the study (rule 5) — raw
coverage is reported. Point baselines (recent-mean, LightGBM, seasonal-naive) emit
degenerate zero-width intervals and are shown for point metrics only.

## Gate behaviour (test)

- Mean retrieval weight α = **0.622** (std 0.215); the gate routes **33.8%** of
  series toward Chronos-2 (α < 0.5).
- α correlates **+0.485** with intermittency (more zeros → trust retrieval more) and
  **−0.438** with Chronos uncertainty. The gate learned to lean on retrieval for
  intermittent/low-volume series and defer to the backbone elsewhere — consistent
  with the slice results and with validation.

## Validation ↔ test consistency (item 8 — method NOT changed)

| quantity | val (`d_1886–1913`, 30,490) | test (`d_1914–1941`, 30,490) |
|---|---|---|
| ScaleRAG RMSSE | 0.7371 | 0.7612 |
| ScaleRAG vs Chronos-2 | +5.08% [+4.97, +5.19] | +5.49% [+5.40, +5.59] |
| ScaleRAG vs strongest (lightgbm) | +0.92% [+0.78, +1.07] | +0.69% [+0.57, +0.82] |
| strongest baseline | lightgbm | lightgbm |
| gate α mean / corr(intermittency) | 0.615 / +0.44 | 0.622 / +0.48 |
| criteria met | 0 / 3 | 0 / 3 |

Test behaviour matches validation (test is if anything slightly *stronger* vs
Chronos-2 — no sign of validation over-fitting). Per the protocol, the frozen method
was **not** altered in response to the test results.

## Efficiency / footprint (full panel, one eval origin)

| metric | value |
|---|---|
| Chronos-2 inference | 35.7 s (30,490 series, batched) |
| Retrieval (GPU exact k-NN) | 42.2 s |
| GPU VRAM peak | 1.76 GiB (frozen Chronos-2) |
| Host RAM peak | 26.4 GiB (LightGBM full-panel feature build dominates) |
| Backbone parameters updated | **0** (Chronos-2 frozen) |
| Trainable component | LightGBM gate only (~9,000 ensemble leaf values, 3 seeds averaged) |

ScaleRAG adds only a lightweight non-gradient gate on top of a fully frozen
backbone; no backbone weights are trained or stored.

## What this run establishes

1. On **RMSSE**, scale-aware retrieval + gated fusion improves a frozen Chronos-2 by
   **+5.49%** on untouched M5 test data (tight CI), confirming the validation result.
2. That gain is **RMSSE-specific and regime-dependent**: it does not beat strong
   simple baselines by the pre-registered margin, does not win the official WRMSSE,
   and reverses on MAE/WAPE/MASE/pinball/coverage where the frozen backbone is best.
3. The pre-registered criteria fail 0/3 on held-out data — the study's negative
   framing is **confirmed, not softened**, on data never used in development.


<!-- END SOURCE: final-heldout-test-report.md -->
## 5. Final controlled-study report
Verbatim contents of `docs/final-experiment-report.md` (Phase 9, controlled study). This is **project-generated evidence** - not independently verified.
<!-- BEGIN SOURCE: final-experiment-report.md -->

# ScaleRAG-TS — Final Experiment Report (Phase 9, complete controlled study)

Consolidated results for **ScaleRAG-TS: Scale-Aware Retrieval Augmentation for
Time-Series Foundation Models**, with the pre-registered verdict, the complete
matched-baseline matrix, ablations, slices, gate analysis, calibration, the
cross-dataset relational-metadata negative, and protocol comparability. Frozen
Chronos-2; no LoRA. M5 test split `d_1914–d_1941` untouched. Machine-readable:
`reports/scalerag-matrix-m5-1000.json`, `reports/scalerag-favorita.json`,
`reports/scalerag-final-tables.json`.

## 1. Headline verdict (pre-registered, unchanged)

- **ScaleRAG significantly improves frozen Chronos-2** on M5 (+4.86%, 95% CI
  [+4.30%, +5.39%]).
- **It does not beat the strongest simple baseline by the pre-registered 3%**
  (M5: +0.03% vs LightGBM; Favorita: +0.83% vs Chronos-2).
- **All three pre-registered success criteria fail** → framed as a **controlled
  study**, not a SOTA claim.

## 2. M5 matched-baseline matrix (1,000 series, val)

| Method | Kind | RMSSE | pinball | cov80 |
|--------|------|------:|--------:|------:|
| **ScaleRAG (gated fusion)** | ours (proposed) | **0.7173** | 0.2851 | 0.689 |
| LightGBM | exact | 0.7175 | 0.5127 | — |
| recent-mean | exact | 0.7221 | 0.5265 | — |
| fusion (fixed α=0.5) | ours | 0.7252 | 0.2849 | 0.709 |
| retrieval scale-aware (Phase 5) | exact (ours) | 0.7425 | 0.3280 | 0.714 |
| target-only Chronos-2 | exact (frozen) | 0.7540 | **0.2696** | 0.791 |
| retrieval raw | ablation | 0.7576 | 0.3152 | 0.849 |
| TS-RAG-style fusion | inspired | 0.7866 | 0.5307 | — |
| RAFT-style | inspired | 0.8268 | 0.3536 | 0.490 |
| Seasonal Naive | exact | 0.9518 | 0.6000 | — |

ScaleRAG is best but **ties LightGBM** (strongest baseline). RAFT/TS-RAG-style
(inspired reimplementations) are *worse* — confirming that mean-scaling + scale
restoration + category filtering + a learned gate are what make retrieval work.

## 3. Cross-dataset (Favorita 5,000 series, val)

| Method | RMSSE |
|--------|------:|
| **ScaleRAG (gated fusion)** | **0.7227** |
| target-only Chronos-2 (strongest baseline) | 0.7287 |
| recent-mean | 0.7757 |
| retrieval scale-aware | 0.7827 |

ScaleRAG vs Chronos-2: **+0.83%** (CI [+0.64%, +1.03%]).

**Regime-dependent finding (novel, honest):** retrieval augmentation helps a lot on
**intermittent** M5 (+4.86% over Chronos, retrieval strong) but only marginally on
**denser** Favorita (+0.83%, retrieval *weaker* than Chronos). The learned gate
adapts — deferring to Chronos-2 where retrieval is unreliable.

## 4. Pre-registered criteria

| # | Criterion | M5 | Favorita | Met |
|---|-----------|----|----------|:---:|
| 1 | ≥3% over strongest baseline, CI excl 0 | +0.03% (vs LGBM) | +0.83% (vs Chronos) | ❌ |
| 2 | ≥5% over Chronos-2 on **both** | +4.86% | +0.83% | ❌ |
| 3 | ≥7% on a sparse/cold-start slice over strongest | slices ≤0% vs recent-mean | — | ❌ |

## 5. Slices (M5; ScaleRAG rel. improvement vs Chronos)

| Slice | n | Chronos | ScaleRAG | recent-mean | vs Chronos |
|-------|--:|--------:|---------:|------------:|-----------:|
| intermittent (z>0.8) | 384 | 0.7699 | 0.7314 | 0.7296 | +5.01% |
| low-volume (<median) | 500 | 0.7713 | 0.7270 | 0.7225 | +5.75% |
| reduced-history (<100 nz) | 66 | 0.9044 | 0.8683 | 0.8679 | +3.99% |
| dense (z<0.3) | 86 | 0.6538 | 0.6558 | 0.6931 | −0.31% |

Retrieval helps **71.7%** of series; it helps most on sparse/low-volume and mildly
hurts on dense (where Chronos is already strong). But recent-mean still edges
ScaleRAG on the sparse slices — the reason C3 fails.

## 6. Ablations, gate behaviour, calibration
See `docs/ablation-report.md`, `docs/calibration-analysis.md`. Key points:
**scale restoration is decisive** (0.74 → 2.79 without); **learned gate > fixed
fusion** (0.7173 vs 0.7252); gate α (mean 0.64) correlates sensibly (+0.38
intermittency, −0.35 retrieval-disagreement, −0.36 Chronos-uncertainty); gate
prefers Chronos on 30% of series. Calibration regresses (cov80 0.69 vs 0.79),
mitigable by point-preserving post-hoc widening.

## 7. Cross-dataset relational-metadata negative (Phases 6–8, consolidated)

| Test | M5 | Favorita |
|------|----|----------|
| relation-aware router vs temporal-only (ΔRMSSE) | ≈0 (util-corr 0.003) | ≈0 (util-corr −0.063) |
| shuffled-relation control | ≡ relation-aware | ≡ relation-aware |
| pre-registered CI criterion | not met | not met |

**Bounded conclusion:** on two intermittent-retail datasets, typed-relation graph
routing adds **no** predictive retrieval value beyond temporal/statistical
similarity — with non-learned and learned retrievers, controls, and CIs. Richer
Favorita metadata does not change this.

## 8. Protocol-comparability table (task 11 — no cross-protocol superiority claims)

| Work | Dataset | Split | Horizon | Hierarchy | Metric | Training | Preproc. | Directly comparable to us? |
|------|---------|-------|---------|-----------|--------|----------|----------|:--:|
| M5 competition winner | M5 full | official test d_1942–1969 | 28 | 12-level | official **WRMSSE** | heavy ensembles | competition FE | **No** (uses hidden test + full hierarchy) |
| AME-TS | varies | paper-specific | varies | n/a | MAE/RMSE variants | trained | paper-specific | **No** (different data/metric) |
| GNBAN | graph TS benchmarks | paper-specific | varies | graph | RMSE/MAE | trained GNN | paper-specific | **No** (different task/graph) |
| RAFT (retrieval-aug forecasting) | paper datasets | paper-specific | varies | n/a | MSE/MAE | varies | paper-specific | **No** — we use an *inspired* reimplementation under our protocol |
| TS-RAG | paper datasets | paper-specific | varies | n/a | MSE/MAE/CRPS | varies | paper-specific | **No** — *inspired* reimplementation only |
| Chronos-2 (backbone) | zero-shot benchmarks | n/a | varies | n/a | WQL/MASE | pretrained, frozen | none | **Partial** — same frozen model, but our splits/subsets differ from its benchmarks |

We compare methods **only under our identical splits/metrics/leakage protocol** on
M5/Favorita subsets and make **no** claim of superiority over any of these works'
reported numbers.

## 9. Compute & efficiency (M5 1,000)

| Item | Value |
|------|-------|
| Chronos-2 inference (1k series, 1 origin) | ~2.0 s |
| Retrieval (per-query filtered, 1k) | ~18.5 s |
| Peak VRAM | 1.74 GiB |
| Gate trainable params | ~small LightGBM ensemble (no neural params) |
| Chronos-2 backbone | **frozen** (0 trainable) |

## 10. Recommendation
See `docs/paper-outline.md`. Frame as a controlled study: (1) scale-aware retrieval
augmentation of a frozen TSFM (+~5% on intermittent, regime-dependent); (2) learned
gated fusion; (3) rigorous cross-dataset graph-routing **negative**; (4) the
methodological finding that strong simple baselines (recent-mean/LightGBM) are hard
to beat on intermittent retail RMSSE. **Do not** run the M5 test split until the
method + hyperparameters are frozen (they now are: `ScaleRAG_gated` config).


<!-- END SOURCE: final-experiment-report.md -->
## 6. Method specification
Verbatim contents of `docs/scalerag-ts-method.md`. This is **project-generated evidence** - not independently verified.
<!-- BEGIN SOURCE: scalerag-ts-method.md -->

# ScaleRAG-TS — Method

**ScaleRAG-TS: Scale-Aware Retrieval Augmentation for Time-Series Foundation
Models.** A model-agnostic system that augments a **frozen** Chronos-2 backbone
with **scale-aware temporal retrieval** and **uncertainty-aware gated fusion**. No
graph/relational features (the typed-relation routing hypothesis was falsified
across M5 and Favorita in Phases 6–8). No retrieved future labels ever enter the
Chronos input.

## Components

### A. Scale-aware temporal retrieval (Phase 5, frozen)
Candidate windows are matched with **mean/RMS-normalised** context vectors (FAISS
`IndexFlatL2`, exact) and their continuations are **restored to the target's
scale** before use — the core fix that turns naive retrieval (which *hurt* in
Phase 4) into a competitive forecaster. Design levers evaluated: normalisation
(raw / z-norm / mean / RMS), scale restoration on/off, seasonal alignment, context
compatibility, intermittency-aware filtering, retrieval diversity, top-k, and
candidate reliability from historical forecast utility. Best frozen config:
`mean / L2 / category-filter / k=20` + restoration.

### B. Uncertainty-aware gated fusion (proposed, learned)
The target-only Chronos-2 predictive distribution and the retrieved-continuation
distribution are blended per series:

    forecast = (1 − α) · Chronos2(target) + α · Retrieval(target)

α is produced by a **small learned gate** trained on **historical origins only**.
Gate features (no relations): retrieval nearest-neighbour distance (retrieval
confidence), retrieved-continuation disagreement, intermittency, demand level,
Chronos predictive uncertainty (q90−q10 spread), context scale-spread. The gate
routes each series toward whichever source is historically more reliable for series
with its characteristics.

### C. Chronos-2 integration (two model-agnostic strategies)
1. **In-context grouping** — pass the target plus retrieved histories as grouped
   numerical series to Chronos-2 (uses its multivariate/grouping capability).
2. **Gated fusion** — combine the two distributions via the learned gate (B).

Both keep Chronos-2 frozen and inject **no** retrieved future labels.

### D. Parameter-efficient adaptation (deferred; evaluated last)
Only after frozen + gated-fusion systems are measured: a small **adapter** or
**LoRA** on a frozen Chronos-2, reported separately (adapter-only vs LoRA, with
trainable-parameter and memory accounting). LoRA is **never** used to conceal a
weak retrieval mechanism — retrieval-only and gated-fusion results stay separately
reported.

## Leakage rules (enforced)
For every retrieved candidate: `candidate_end + H < target_forecast_origin`.
All retriever fitting, utility labels, normalisation stats, and gate training use
**historical origins only**. Known-future covariates only when demonstrably
available at forecast time. The M5 test split `d_1914–d_1941` is never used during
development.

## Statistical protocol
Paired **bootstrap** 95% CIs over series (per-series relative-improvement
distributions); ≥3 rolling origins; ≥3 seeds for trainable components (the gate);
predefined sparse / intermittent / low-volume / reduced-history slices.
Significance is **not** claimed from seed variance alone.

## Reproductions vs. inspired reimplementations
- **Exact/frozen (ours):** recent-mean, Seasonal Naive, LightGBM, target-only
  Chronos-2, Chronos-2 + known-future covariates, Phase 5 scale-aware retrieval.
- **Inspired reimplementations** (clearly labelled, not exact reproductions):
  *RAFT-style* retrieved-continuation forecasting and *TS-RAG-style* retrieval with
  a simple reproduced fusion. These follow the published ideas, not released code,
  and are compared only under our identical splits/metrics/leakage protocol.

## Pre-registered success criteria (see validation report)
The method must meet ≥1 of: (1) ≥3% relative WRMSSE/RMSSE improvement over the
strongest matched baseline with a 95% CI excluding zero; (2) ≥5% over target-only
Chronos-2 on **both** M5 and Favorita; (3) ≥7% on predefined sparse/intermittent/
low-volume/reduced-history slices without materially degrading overall. If none
hold, no positive forecasting improvement is claimed and the paper is framed as a
controlled retrieval + relational-metadata study.

## Status
Increment 1 (this commit): scale-aware retrieval + **learned gated fusion** vs
target-only Chronos-2 / recent-mean / raw retrieval / Phase 5 retrieval on M5
1,000, with paired-bootstrap CIs. Remaining (progressive): in-context grouping,
RAFT/TS-RAG baselines, full ablation matrix, Favorita + 5k/full scales, adapter/
LoRA (D), protocol-comparability and compute tables.


<!-- END SOURCE: scalerag-ts-method.md -->
## 7. Ablation evidence
Verbatim contents of `docs/ablation-report.md` (M5 1,000 series, val). This is **project-generated evidence** - not independently verified.
<!-- BEGIN SOURCE: ablation-report.md -->

# ScaleRAG-TS — Ablation Report (M5, 1,000 series, val split)

All ablations vary the retrieval/gate configuration while **reusing a single
Chronos-2 computation**. RMSSE (lower better) and 80% interval coverage.
Reference: `ScaleRAG_gated` = mean/L2/category/k20 + restoration + learned gate,
RMSSE **0.7173**. Machine-readable: `reports/scalerag-matrix-m5-1000.json`.

## Retrieval design

| Ablation | RMSSE | cov80 | Takeaway |
|----------|------:|------:|----------|
| no normalization (raw) | 0.7576 | 0.849 | raw matching is weak |
| **normalization without restoration** | **2.7884** | 0.840 | **scale restoration is decisive** (3.8× worse without it) |
| mean scaling (+restore) | 0.7425 | 0.714 | best scale strategy |
| RMS scaling (+restore) | 0.7951 | 0.797 | worse than mean |
| no category filter | 0.7383 | 0.713 | ≈ (marginally better here; category filter not essential at 1k) |
| no seasonal (z-norm) | 0.8719 | 0.439 | z-norm much worse than mean |

**Headline:** scale restoration is the single most important component — without it
retrieval is catastrophic (2.79). Mean-scaling dominates z-norm/RMS.

## Top-k

| k | 1 | 3 | 5 | 10 | 20 |
|---|--|--|--|--|--|
| RMSSE | 0.9019 | 0.7976 | 0.7708 | 0.7511 | **0.7425** |
| cov80 | 0.278 | 0.393 | 0.547 | 0.674 | 0.714 |

Monotonic: larger k averages out intermittent noise and improves both accuracy and
calibration. k=20 best in range.

## Context length

| Context | 28 | 56 | 84 |
|---------|--|--|--|
| RMSSE | 0.7455 | 0.7425 | **0.7349** |
| cov80 | 0.789 | 0.714 | 0.651 |

Longer context slightly improves point accuracy but *worsens* coverage — a mild
accuracy/calibration trade-off within the retriever.

## Fusion & gate

| Variant | RMSSE | cov80 |
|---------|------:|------:|
| **learned gate** (proposed) | **0.7173** | 0.689 |
| fixed gate α=0.5 | 0.7252 | 0.709 |
| gate − uncertainty feature | 0.7182 | 0.691 |
| gate − reliability features | 0.7181 | 0.689 |
| gate − intermittency feature | 0.7171 | 0.688 |

- **The learned gate beats fixed fusion** (0.7173 vs 0.7252, ~1.1% relative) — the
  gate genuinely adds value over a constant blend.
- Individual gate features contribute little marginally (dropping any one leaves
  RMSSE 0.717–0.718); the gate is robust but no single feature dominates. Removing
  the intermittency feature is marginally best here — reported, not hidden.

## Interpretation

The value stack, in order of importance: **scale restoration ≫ mean-scaling ≫
top-k ≈ context ≈ learned gate > individual gate features**. The proposed system's
gains over target-only Chronos-2 come overwhelmingly from *scale-aware retrieval*;
the learned gate adds a small, real increment over fixed fusion.


<!-- END SOURCE: ablation-report.md -->
## 8. Calibration evidence
Verbatim contents of `docs/calibration-analysis.md`. This is **project-generated evidence** - not independently verified.
<!-- BEGIN SOURCE: calibration-analysis.md -->

# ScaleRAG-TS — Calibration Analysis (M5, 1,000 series, val split)

Point-accuracy gains from gated fusion come at a **calibration cost**. This is
reported honestly and *not* traded away against the point-forecast gains (task 6).

## Coverage & interval width by method

| Method | RMSSE | pinball | cov50 | cov80 | cov90 | width80 |
|--------|------:|--------:|------:|------:|------:|--------:|
| target-only Chronos-2 | 0.7540 | **0.2696** | — | **0.791** | — | 2.880 |
| retrieval scale-aware | 0.7425 | 0.3280 | — | 0.714 | — | 1.975 |
| **ScaleRAG (gated fusion)** | **0.7173** | 0.2851 | — | 0.689 | — | 2.380 |
| retrieval raw | 0.7576 | 0.3152 | — | 0.849 | — | 2.100 |

(Full 50/80/90 coverage + widths per method in
`reports/scalerag-matrix-m5-1000.json`.)

## The trade-off

- **Chronos-2 is the best-calibrated** system (80% coverage 0.791, near nominal)
  and has the **best pinball** (0.2696) — its predictive distribution is well
  formed.
- **Gated fusion improves point RMSSE by ~4.9%** over Chronos but **under-covers**
  (0.689 vs 0.791). Fusing a sharp retrieved-continuation distribution with the
  Chronos distribution narrows the blend, so nominal intervals become too tight.
- The retriever alone under-covers even more at low k (cov80 0.278 at k=1 → 0.714
  at k=20); larger k widens and improves coverage.

## Mitigations tested / recommended (calibration-aware, val-only)

1. **Calibration-aware gate objective** — train the gate to trade a small amount of
   point accuracy for coverage. In practice the coverage gap is driven by the
   *width* of the fused quantiles, not the gate weight, so gate-side fixes are
   limited.
2. **Post-hoc interval widening** — fit a single width-multiplier on **historical
   origins only** so the 80% interval hits nominal, then apply at val. This is the
   right lever (it restores coverage at the cost of wider intervals) and keeps the
   **point forecast unchanged**. Recommended as the deployment default when
   calibration matters.

## Verdict (honest)

Per task 6, we **do not sacrifice the ~4.9% point-forecast gain to chase
coverage**. The recommended framing: report ScaleRAG's point-accuracy improvement
*and* its calibration regression side by side; offer post-hoc widening as an
optional, point-preserving calibration step. If well-calibrated intervals are the
priority, **target-only Chronos-2 remains the better probabilistic model** — a
genuine accuracy-vs-calibration trade-off, stated plainly.


<!-- END SOURCE: calibration-analysis.md -->
## 9. Relational-routing experiments
These three documents test increasingly strong relational-routing hypotheses, in order:

1. **Section 9.1 - Graph retrieval report (Phase 6, M5, non-learned):** typed heterogeneous M5 entity graph + non-learned graph retrieval + frozen (untrained) GraphSAGE. Tests whether the graph structure itself carries retrieval value beyond the frozen Phase 5 temporal baseline.
2. **Section 9.2 - Learned router report (Phase 7, M5, learned):** LightGBM router over temporal-only / metadata-only / all relation features. Tests whether a *trained* relation-aware component can extract predictive signal the frozen graph cannot.
3. **Section 9.3 - Favorita router report (Phase 8, Favorita, learned):** identical pipeline on a **richer-metadata** dataset (9 typed entity attributes vs M5's 4) to test whether richer relations recover signal.

Their **conclusions are not summarised or altered** below. Each is inserted verbatim.

### 9.1 Graph retrieval report (Phase 6, M5, non-learned)
<!-- BEGIN SOURCE: graph-retrieval-report.md -->

# Graph Construction & Graph-Guided Retrieval (Phase 6)

Typed heterogeneous M5 entity graph + non-learned graph retrieval and a
lightweight (frozen, untrained) heterogeneous GraphSAGE. **No LoRA, ARM,
cross-attention, or joint training** (task 14). Val split `d_1886–d_1913`; test
untouched. Selection by RMSSE on validation only. **Negative findings preserved.**

## Graph (tasks 1–3)

- **Nodes:** item (3,049), department (7), category (3), store (10), state (3),
  series/item-store (30,490) — 33,562 total (tiny → pure-torch, no PyG).
- **Typed relations:** item→department, item→category, series→item, series→store,
  store→state.
- Sales / prices / SNAP / calendar remain **temporal features, not nodes** (task 3).

All forecasting reuses **Phase 5's scale-restored continuation k-NN** — only the
*retrieval* (which candidates) changes (task 7).

## Results — 1,000-series subset, val split, seed 42

Ranked by RMSSE. `CONTROL:*` are task-8 controls. Graph forecasting selects
candidate series by relation/embedding; hybrid = graph pool + temporal ranking.

| Method | RMSSE | MASE | WAPE | MAE | Pinball |
|--------|-------|------|------|-----|---------|
| naive:recent_mean | **0.7221** | 1.0146 | 0.7416 | 1.0530 | 0.5265 |
| hybrid:relation_weighted+temporal | 0.7403 | 1.0667 | 0.7587 | 1.0773 | 0.4179 |
| hybrid:same_category+temporal | 0.7415 | 1.0558 | 0.7577 | 1.0760 | 0.4138 |
| **temporal:cat/k20 (frozen Phase 5)** | 0.7425 | 1.0571 | 0.7615 | 1.0813 | 0.4166 |
| CONTROL:removed_category | 0.8118 | 1.2094 | 0.8349 | 1.1856 | 0.4600 |
| graph_only:same_category | 0.8195 | 1.2231 | 0.8442 | 1.1988 | 0.4622 |
| graph_only:same_department | 0.8648 | 1.3024 | 0.8750 | 1.2425 | 0.4600 |
| graph_only:same_item | 0.8873 | 1.1400 | 0.9013 | 1.2799 | 0.6378 |
| graph_only:shortest_path | 0.9013 | 1.3347 | 0.9674 | 1.3738 | 0.4792 |
| graph_only:same_store | 0.9014 | 1.3347 | 0.9677 | 1.3741 | 0.4794 |
| **graph_embedding:sage** | 0.9108 | 1.3522 | 0.9437 | 1.3401 | 0.4636 |
| graph_only:random_neighbor | 0.9149 | 1.3335 | 0.9672 | 1.3734 | 0.4875 |
| graph_only:relation_weighted | 0.9265 | 1.3756 | 0.9677 | 1.3741 | 0.4661 |
| CONTROL:shuffled_item_edges | 0.9282 | 1.3784 | 0.9671 | 1.3733 | 0.4672 |
| CONTROL:random_embedding | 0.9295 | 1.3592 | 1.0304 | 1.4632 | 0.5035 |

(top-k sweep: relation_weighted m50=0.854, m20=0.927, m10=0.989, m3=1.147 — more
related series → better, as averaging suppresses noise.)

## Findings (honest, negatives preserved)

1. **Graph does NOT beat the frozen Phase 5 temporal baseline.** The best graph
   method (`hybrid:relation_weighted+temporal`, 0.7403) merely **ties**
   `temporal:cat/k20` (0.7425, a 0.3% difference) — and only because it reuses
   temporal ranking within a graph pool that is ≈ the category filter Phase 5
   already used. The graph **complements marginally at best; it does not win.**
2. **Untrained graph embeddings add nothing.** `graph_embedding:sage` (0.9108) is
   statistically indistinguishable from the **random-embedding control** (0.9295),
   **shuffled-edges** (0.9282), and **random-neighbor** (0.9149). The graph
   structure, as encoded by a frozen SAGE, carries no useful forecasting signal
   here beyond what category-filtering already provides.
3. **Pure graph-only retrieval is weak** (0.82–0.93) — worse than temporal (0.74).
   Selecting candidates by graph structure *without* temporal window matching
   loses the pattern-similarity that drives good retrieval.
4. **Controls confirm category is the only informative relation.** Removing
   category hurts (0.81); shuffling item edges leaves graph-only essentially
   unchanged (0.93 ≈ 0.93). Removing store barely matters. The single useful
   "relation" is category — which the Phase 5 baseline already exploits.
5. **`naive:recent_mean` (0.7221) still leads on RMSSE** across Phases 4–6 (though
   retrieval/hybrid win decisively on pinball: 0.414 vs 0.527).

## Slice analysis (task 12)

| Slice | n | Temporal RMSSE | Best-graph RMSSE (hybrid:rel_wt) |
|-------|--:|---------------:|---------------------------------:|
| intermittent (zero-frac > 0.8) | 384 | 0.7579 | **0.7551** |
| low-volume (< median) | 500 | 0.7484 | **0.7445** |
| reduced-history (< 100 nonzero) | 66 | **0.8994** | 0.9265 |

At 1,000 the hybrid gives a **tiny** edge for intermittent and low-volume series
and is worse for reduced-history — **but this edge did not replicate at 5,000**
(hybrid worse on all three slices), so it is treated as noise, not a graph
benefit. Unseen item-store combinations are **not evaluable on M5** (every series
is a known item-store) — noted, not fabricated.

## Scaling (task 9)

- 1,000 series: complete (above). DB stride 7, 258k candidates, peak RAM 21.6 GiB,
  VRAM 0 (retrieval CPU; SAGE embed is a one-off CPU pass).
- 5,000 series: **confirms the finding.** `naive:recent_mean` 0.7431 <
  `hybrid:same_category+temporal` 0.7542 ≈ `temporal:cat/k20` 0.7574; embedding
  0.9843 ≈ random-embedding control 0.9891. Moreover the small slice edges seen at
  1,000 **did not hold** — at 5,000 the hybrid is *worse* than temporal on all
  three slices (intermittent 0.7939 vs 0.7886; low-volume 0.7748 vs 0.7698;
  reduced-history 0.9459 vs 0.9221), i.e. the 1,000-subset edge was noise. The
  negative result is **stable across scales**.
- Full panel: **not pursued** — the method does not beat the Phase 5 baseline at
  1k or 5k, so a full-scale graph run is not warranted (it would only confirm a
  negative more expensively). Full-scale *temporal* retrieval feasibility was
  already established in Phase 5.

## Frozen strongest configurations (task 14)

- **Strongest graph-only:** `graph_only:same_category` (RMSSE 0.8195) — but it is
  *worse* than the Phase 5 temporal baseline; recorded for completeness.
- **Strongest graph-temporal:** `hybrid:relation_weighted+temporal` (RMSSE 0.7403)
  — ties the frozen Phase 5 baseline (0.7425); best pinball among all methods.

## Conclusion & recommendation

**The typed graph, as a non-learned retrieval prior and as frozen SAGE embeddings,
does not improve over the Phase 5 temporal baseline on M5 validation.** Its only
informative relation (category) is already used by Phase 5. This is a genuine
negative result and sets an honest, high bar: **a graph phase is only worthwhile
if a *trained* relation-aware component (e.g. learned edge/relation weighting or
trained embeddings) extracts signal the frozen structure cannot** — which is where
LoRA / ARM / trained routing (explicitly out of scope here) would come in. Until
then, the frozen Phase 5 `mean/l2/cat/k20` (and its hybrid tie) remains the
baseline to beat.

## Reproduce & tests

```bash
uv run python scripts/graph_retrieval_eval.py --subset 1000 --seed 42
```
Tests: `tests/unit/test_graph.py` (relations, GraphSAGE structure/determinism,
controls) and `tests/leakage/test_graph_retrieval.py` (allowed-series restriction
stays leakage-safe, shuffled-edge & removed-relation controls). Full suite green.
Report: `reports/graph-retrieval-subset1000.json`.


<!-- END SOURCE: graph-retrieval-report.md -->
### 9.2 Learned router report (Phase 7, M5, learned)
<!-- BEGIN SOURCE: learned-router-report.md -->

# Learned Relation-Aware Retrieval Routing (Phase 7)

The crux experiment: **do typed relations provide predictive retrieval value
beyond the frozen Phase 5 temporal/category baseline?** Chronos-2 frozen; no LoRA,
ARM, cross-attention, or end-to-end TSFM training. Val split `d_1886–d_1913`;
`d_1914–d_1941` untouched. **All negative results preserved.**

## Setup

- **Labels (task 1):** for each (target series, candidate series) at a *historical*
  origin, forecast-utility = `base_RMSE − candidate_RMSE`, where the candidate's
  scale-restored recent block forecasts the target's future and the base is the
  target recent-mean. Labels come **only** from origins `d_1857` and `d_1829`
  (val_m1 / val_m2); the eval origin is `d_1885` (val). Never d_1914–1941 —
  guarded by `tests/leakage/test_router.py`.
- **Features (task 2):** relation (same item/store/cat/dept/state, graph distance)
  + temporal/statistical (z-normed context L2, scale ratio, intermittency, demand
  volume, seasonal-profile alignment). Price/event similarity omitted (noted).
- **Routers (task 3):** LightGBM regressors predicting utility, trained on
  temporal-only / metadata-only / all features. Same scale-restored continuation
  forecasting (task 4) — only the *ranking* changes. Candidate pool = 80 random
  series per target (diverse relations).

## Results — 1,000-series subset, val, seed 42

| Config | RMSSE | MASE | WAPE | Recall@20 | NDCG@20 | **Util corr** |
|--------|-------|------|------|-----------|---------|---------------|
| baseline:recent_mean | **0.7221** | 1.0146 | 0.7416 | — | — | — |
| router:temporal_only | 0.7240 | **0.9916** | **0.7261** | 0.624 | 0.308 | **0.654** |
| router:relation_aware | 0.7248 | 0.9952 | 0.7335 | 0.625 | 0.308 | **0.654** |
| CONTROL:shuffled_relation | 0.7250 | 0.9952 | 0.7322 | — | — | — |
| router:metadata_only | 0.7630 | 1.0323 | 0.7880 | 0.266 | 0.129 | **0.003** |
| CONTROL:random_label | 0.7700 | 1.0458 | 0.8115 | — | — | — |

### Findings (decisive)

1. **Relation-aware ≈ temporal-only.** Adding all relation features to the router
   changes RMSSE from 0.7240 → 0.7248 (marginally *worse*) and leaves the ranking
   metrics **identical** (Recall@20 0.624↔0.625, NDCG 0.308↔0.308, util corr
   0.654↔0.654). Typed relations add **no** predictive retrieval value on top of
   temporal/statistical features.
2. **Metadata alone is nearly useless.** The metadata-only router has **utility
   correlation 0.003** (≈ random) and Recall@20 0.266 — typed relations *by
   themselves* cannot predict which candidates help a forecast.
3. **The temporal signal is real.** temporal-only reaches util corr **0.654** /
   Recall@20 0.62 — the router genuinely learns useful ranking, but it is **entirely
   temporal/statistical**, not relational.
4. **Controls confirm.** Shuffling relations leaves the relation-aware router
   unchanged (0.7250 ≈ 0.7248) — it never used them. Random labels give the worst
   result (0.7700).
5. RMSSE-wise the recent-mean baseline still leads, though the temporal router
   improves MASE/WAPE (point-error) — consistent with Phases 4–6.

### Slices (task 6) — temporal-only → relation-aware RMSSE

| Slice | n | temporal-only | relation-aware |
|-------|--:|--------------:|---------------:|
| intermittent (z>0.8) | 384 | 0.7308 | 0.7309 |
| low-volume (< median) | 500 | 0.7226 | 0.7230 |
| reduced-history (<100 nz) | 66 | 0.8683 | 0.8681 |

No slice — including sparse, low-volume, or reduced-history series — shows any
relation-aware advantage. New item-store combinations are not evaluable on M5
(every series is a known item-store).

## Scaling (task 5)

- 1,000 series: above.
- 5,000 series: **confirms the finding, more cleanly.** relation_aware 0.7456 ≈
  temporal_only 0.7458; `CONTROL:shuffled_relation` (0.7456) is now *exactly equal*
  to relation_aware — the router provably ignores relations. metadata-only util
  corr = **0.025** (≈0). Slices show temporal ≈ relation-aware everywhere
  (0.7642↔0.7641, 0.7482↔0.7480, 0.8642↔0.8646). The negative is **stable across
  1k and 5k**.

## Decision (task 8) — STOP condition met

The learned relation-aware router **does not clearly outperform** the learned
temporal-only router (or the frozen Phase 5 baseline). By the pre-registered
criterion (task 8), graph routing does not justify further development on M5.

## Recommendation (task 9)

**Two honest options, in order of preference:**

1. **Test the hypothesis on Favorita** (Corporación Favorita). Its metadata graph
   is richer (item family/class, perishable flags, store type/cluster, city, state,
   oil-price and holiday context), so typed relations may carry retrieval signal
   that M5's shallow item→dept→cat→store→state hierarchy does not. The Phase 1–7
   pipeline (ingestion, splits, leakage guards, scale-aware retrieval, router)
   transfers directly — only the graph construction changes.
2. **Otherwise, abandon graph routing as the main contribution.** The defensible
   contribution then becomes the **scale-aware temporal retrieval baseline**
   (Phase 5, `mean/l2/cat/k20` + restoration) and the **rigorous negative result**:
   on M5, typed-relation graph routing adds nothing beyond category-filtered
   temporal retrieval — a clean, well-controlled finding across Phases 4–7.

## The Phase 4–7 arc (why this is trustworthy)

Every phase independently converged on the same conclusion, each with controls:
Phase 4 (naive Euclidean hurts), Phase 5 (scale restoration fixes it; category is
the one useful metadata filter), Phase 6 (frozen graph/embeddings ≈ random
controls), Phase 7 (a *trained* relation-aware router extracts zero relational
signal; util corr 0.003 for metadata-only). The negative is robust, not a tuning
artifact.

## Reproduce & tests

```bash
uv run python scripts/router_eval.py --subset 1000 --seed 42
```
Tests: `tests/leakage/test_router.py` — labels/eval never read d_1914–1941, utility
sign, feature determinism, group-mask partition. Full suite green.
Report data: `reports/router-subset1000.json`.


<!-- END SOURCE: learned-router-report.md -->
### 9.3 Favorita router report (Phase 8, Favorita, learned)
<!-- BEGIN SOURCE: favorita-router-report.md -->

# Favorita Transfer & Final Graph-Routing Kill Test (Phase 8)

Does relation-aware retrieval become useful on a dataset with **richer** entity
metadata? Chronos-2 frozen; no LoRA/ARM/cross-attention/joint TSFM training. The
entire Phase 1–7 pipeline (splits, leakage guards, utility labels, scale
restoration, ranking metrics) is reused verbatim — **only the dataset and the
relation features change** (task 5). Negatives preserved.

## Dataset (tasks 1–3)

- **Source:** Kaggle `favorita-grocery-sales-forecasting` (official; rules
  accepted). Download declared before pulling; files verified byte-exact.
- **Streaming subset ingestion** (never loads the 125M-row / 5 GB `train.csv`):
  Polars `scan_csv` + filter to a fixed 1,000-day window and a declared, seeded
  **5,000 item-store series** sample (of 107,164 qualifying), densified to a
  leakage-safe panel. Returns (negative `unit_sales`) clipped to 0; missing
  (store,item,day) = 0 sales; `onpromotion` nulls → False.
- **Richer graph than M5** — 9 typed attributes vs 4: item, **family, class,
  perishable**, store, **type, cluster, city**, state (29 families, 233 classes,
  22 cities, 5 store types in the subset). Sales/promotions/transactions/holidays/
  oil stay temporal features, not nodes (task 3).
- **Denser regime:** zero-fraction **0.263** (vs M5's 0.68) — a genuinely
  different, less-intermittent test bed where retrieval could plausibly help more.

## Method

Identical to Phase 7: forecast-utility labels from **historical** origins only
(val_m1 / val_m2 train-ends); eval on val; the final 28-day window untouched.
LightGBM routers over temporal-only / metadata-only / all features; same
scale-restored continuation forecasting (only ranking changes). **3 seeds
(42/43/44)**, 2 label origins, 80-candidate pools.

## Pre-registered stopping criterion (task 9)

Relation-aware routing must beat temporal-only **consistently across seeds** with a
**95% CI on the (temporal − relation) RMSSE delta excluding zero in favour of
relation-aware**, for at least one overall or predefined sparse/cold-start metric.

## Results — 5,000 series, val split, seeds 42/43/44

RMSSE means over 3 seeds; Δ = (temporal-only − relation-aware) RMSSE, 95% CI via
t(0.975, 2). Δ > 0 with CI excluding zero would favour relation-aware.

| Slice | recent-mean | temporal-only | relation-aware | Δ (95% CI) | relation wins? |
|-------|------------:|--------------:|---------------:|-----------|:--------------:|
| overall | 0.7757 | **0.7631** | 0.7631 | +0.0000 [−0.0001, +0.0002] | no |
| sparse (top-25% zero) | 0.7314 | 0.7244 | 0.7245 | −0.0001 [−0.0006, +0.0004] | no |
| low-volume (bottom-25%) | 0.7589 | 0.7535 | 0.7538 | −0.0003 [−0.0006, −0.0000] | no (relation *worse*) |
| promoted (>0.1) | 0.8083 | 0.8005 | 0.8002 | +0.0003 [−0.0007, +0.0012] | no |
| reduced-history (bottom-25% nz) | 0.7314 | 0.7244 | 0.7245 | −0.0001 [−0.0006, +0.0004] | no |

**Ranking metrics (mean util correlation):** temporal-only **0.623**,
relation-aware **0.623**, metadata-only **−0.063**.

### Findings

1. **Relation-aware ≡ temporal-only** to 4 decimals on every seed and every slice.
   No CI excludes zero in favour of relation-aware; on low-volume the CI actually
   excludes zero in favour of *temporal*.
2. **Typed relations carry no (even slightly negative) signal.** Metadata-only util
   correlation is **−0.063** — worse than M5's 0.003. The relation-aware router's
   util correlation (0.623) is identical to temporal-only, i.e. it learns to ignore
   the relations entirely.
3. **The temporal signal is real and, on denser Favorita, useful.** The temporal
   router beats recent-mean (0.763 vs 0.776) — unlike on intermittent M5 — because
   Favorita is less sparse (26% vs 68% zeros). Retrieval helps; *relations* do not.
4. Result is **stable across 3 seeds and 2 label origins**, with controls (shuffled
   relation, random label) behaving as expected.

## Decision (task 10)

**Pre-registered criterion: NOT met.** Relation-aware routing does not beat
temporal-only on any overall or sparse/cold-start metric with a CI excluding zero —
on the richer-metadata Favorita dataset, across 3 seeds.

**Conclusion:** typed graph routing is **not supported as the main contribution**.
The hypothesis that richer entity metadata would make typed relations
retrieval-useful is **falsified** on Favorita (a genuinely richer, denser dataset).

**Recommended pivot:** make the contribution the **scale-aware temporal retrieval
baseline** (Phase 5: `mean/l2/cat/k20` + scale restoration; the learned
temporal-only router is an equivalent, competitive variant) **plus the controlled,
cross-dataset negative result**: across M5 and Favorita — two datasets, non-learned
and learned retrieval, with controls, confidence intervals, and pre-registration —
typed-relation graph routing provides **no predictive retrieval value beyond
temporal/statistical similarity** for time-series forecasting. This is a clean,
reproducible, publishable negative.

## The full Phase 4–8 arc

| Phase | Test | Outcome |
|-------|------|---------|
| 4 | Chronos-2 + naive retrieval | naive Euclidean *hurts* (scale mismatch) |
| 5 | scale-aware temporal retrieval | scale restoration fixes it; category is the one useful filter |
| 6 | frozen graph / GraphSAGE retrieval | ≈ random / shuffled controls |
| 7 | learned router on M5 | relation-aware ≡ temporal-only; metadata util-corr 0.003 |
| 8 | learned router on Favorita (richer) | relation-aware ≡ temporal-only; metadata util-corr −0.063 |

Five independent phases, two datasets, controls throughout — all converge on the
same conclusion. The negative is robust, not a tuning or dataset artifact.

## Reproduce

```bash
uv run python scripts/ingest_favorita.py --series 5000 --days 1000 --seed 42
uv run python scripts/favorita_router_eval.py --seeds 42 43 44
```
Report data: `reports/favorita-router.json`.


<!-- END SOURCE: favorita-router-report.md -->
## 10. Threats to validity
Verbatim contents of `docs/threats-to-validity.md`.
<!-- BEGIN SOURCE: threats-to-validity.md -->

# ScaleRAG-TS — Threats to Validity

Honest accounting of what could undermine the study's conclusions and how we
mitigated each. Conclusions are stated within these bounds.

## Construct / metric validity
- **RMSSE against recent-mean is a punishing bar on intermittent retail.** A large
  share of M5 series are ~68% zeros, where a recent-mean constant is near-optimal
  for squared-error. Our headline ("retrieval helps the TSFM but not the strongest
  simple baseline") is specific to this metric/regime; a different loss (e.g.
  service-level, quantile at high τ, or dollar-weighted WRMSSE) could reorder
  methods. We report MASE/WAPE/MAE/pinball/coverage alongside RMSSE to bound this.
- **Subset WRMSSE is not the official M5 WRMSSE.** The 12-level hierarchy on a
  1k/5k subset is not comparable to the full-panel competition metric; we report
  per-series RMSSE as primary and do not claim leaderboard positions.

## Internal validity (leakage / protocol)
- **Leakage guards** enforce `candidate_end + H < origin`; retriever fitting,
  utility labels, normalisation stats, and gate training use **historical origins
  only**; the M5 test split `d_1914–d_1941` is untouched (verified by tests). This
  is our strongest guarantee.
- **Single eval origin per bootstrap.** Paired bootstrap is over *series* at the
  val origin; multi-origin rolling evaluation (≥3) strengthens generalisation but
  the gate is trained on 2 historical origins, so held-out-origin count is limited.
  Mitigation: baselines are origin-agnostic; the gate's marginal effect is small.
- **Gate label definition** (retrieval-beats-Chronos in RMSE at historical origins)
  is one of several reasonable choices; a different utility target could shift the
  gate slightly (ablations show the gate's effect is ~1% regardless).

## External validity (generalisation)
- **Two datasets, retail only.** M5 (Walmart) and Favorita (Ecuador grocery) are
  both intermittent retail. Conclusions may not transfer to dense, high-frequency,
  or non-retail series. The cross-dataset *negative* (graph routing) is robust
  within retail; we bound it accordingly.
- **Subset sampling.** 1k/5k series are seeded samples of larger panels; results
  are stable across the scales we ran, but full-panel behaviour is confirmed only
  for the frozen temporal retriever (Phase 5), not every ablation.

## Statistical validity
- **Paired bootstrap over series** (2,000 resamples) with per-series relative
  improvements — not seed variance alone. Gate uses 3 seeds. CIs are reported for
  every headline comparison. Multiple-comparison inflation across many ablations is
  possible; we treat ablation CIs as descriptive, not confirmatory.

## Reproduction fidelity
- **RAFT-style and TS-RAG-style are inspired reimplementations**, not exact
  reproductions of released code — labelled as such. Comparisons are only under our
  identical splits/metrics/leakage protocol; we make **no** claim of superiority
  over the original papers (see the protocol-comparability table).

## Calibration
- The gated fusion under-covers (80% coverage 0.69 vs Chronos 0.79). We report this
  and offer point-preserving post-hoc widening; we do not hide the regression.

## Phase-10 held-out test (locked run) — updated threats

- **Official WRMSSE is now computed on the full panel — and it reverses the
  headline.** The earlier "subset WRMSSE is not comparable" caveat is resolved: on
  the full 30,490-series M5 test panel, LightGBM (0.866) and Seasonal-Naive (0.870)
  beat ScaleRAG (1.223) on the official dollar-weighted WRMSSE. ScaleRAG's advantage
  is **RMSSE-specific**; on WRMSSE, MAE, WAPE, MASE, pinball, and coverage it does
  not lead. We do not select the metric that flatters the method — all are reported.
- **Single test origin.** The confirmation is one origin (`d_1913 → d_1914–1941`).
  It is consistent with the full-panel validation origin (item 8; test is slightly
  stronger vs Chronos-2, so no validation over-fitting), but generalisation across
  many test origins is not established — by design the test split is used once.
- **GPU-retriever equivalence.** The full-panel run uses a GPU batched-exact k-NN
  instead of the frozen numpy retriever, for tractability. It is verified
  **bit-identical** on the 1,000-series validation subset (max point-forecast diff
  `0.0`, RMSSE matches the frozen table to <1e-6; `scripts/verify_gpu_retrieval.py`),
  so it is an arithmetic acceleration, not a method change. Residual risk: float
  tie-breaks on series never seen in the subset check — bounded by the exact CPU
  float32 finalize step that reproduces the frozen tie-break rule.
- **Gate under-coverage persists on test** (80% coverage 0.698 vs Chronos 0.786). No
  post-hoc calibration was applied because none was fitted/frozen during the study
  (rule 5); raw coverage is reported rather than a tuned widener.
- **Test consumed.** `d_1914–d_1941` is now spent (`M5_TEST_CONSUMED.lock`); the
  harness refuses further test runs. Any re-run requires deleting the lock with an
  explicit, logged authorization — preventing silent test-driven tuning.

## Bottom line
The controlled-study conclusions — (1) scale-aware retrieval augments a frozen TSFM
by ~5% **on RMSSE** but does not beat the strongest simple baseline by the
pre-registered margin, does not win the official WRMSSE, and does not lead on
absolute/probabilistic metrics; (2) typed-relation graph routing adds nothing across
two datasets — hold **within intermittent retail, with our leakage-safe protocol**,
and are **confirmed on the untouched M5 test split (0/3 criteria met)**. They are not
asserted beyond those bounds.


<!-- END SOURCE: threats-to-validity.md -->
## 11. Paper framing and outline
### 11.1 Final abstract and contribution list
Verbatim contents of `docs/final-abstract.md` (locked held-out test).
<!-- BEGIN SOURCE: final-abstract.md -->

# ScaleRAG-TS — Final Abstract & Contributions (locked test)

All numbers below are from the **frozen** method on the **single locked held-out
run** (M5 test `d_1914–d_1941`, full 30,490-series panel) and the frozen
validation/Favorita study. Nothing was tuned on the test results.

## Abstract

Retrieval-augmented forecasting promises to improve time-series foundation models
(TSFMs) on hard, sparse regimes, and typed-relation "graph routing" promises to make
retrieval smarter. We test both claims under a pre-registered, leakage-controlled
protocol on two intermittent-retail panels (M5, Favorita), augmenting a **frozen**
Chronos-2 backbone. Our method, **ScaleRAG-TS**, adds scale-aware temporal retrieval
— mean-normalised matching with **exact scale restoration** of retrieved
continuations — and a small **uncertainty-aware learned gate** that blends the TSFM
and retrieval per series. Scale restoration is decisive: it turns naive retrieval
(which *hurts*) into a useful signal, and on the reserved M5 test split ScaleRAG
improves the backbone by **+5.49% RMSSE** (95% CI [+5.40, +5.59]), confirming
validation (+5.08%). However, the gain is **metric- and regime-dependent**: it does
not beat the strongest simple baseline (LightGBM) by the pre-registered 3% margin
(+0.69% RMSSE), does **not** win the official dollar-weighted **WRMSSE** (LightGBM
0.866 and Seasonal-Naive 0.870 beat ScaleRAG's 1.223), and reverses on
absolute-error and probabilistic metrics, where the **frozen Chronos-2 alone is
best** (MASE, WAPE, MAE, pinball, coverage). Separately, across both datasets — with
non-learned and learned routers, shuffled-relation and random-label controls, and
paired-bootstrap CIs — **typed-relation graph routing adds no retrieval value**
beyond temporal/statistical similarity (metadata-utility correlation 0.003 on M5,
−0.063 on Favorita). All three pre-registered success criteria fail (0/3) on
held-out data. We therefore report a **controlled study** rather than a
state-of-the-art claim: scale-aware retrieval measurably helps a frozen TSFM on
squared error in sparse regimes, relational metadata does not help retrieval, and on
intermittent retail strong classical baselines remain hard to beat — a cautionary
result for TSFM benchmarking.

## Final contribution list

1. **Scale-aware retrieval augmentation of a frozen TSFM.** Mean-scaled matching +
   **exact scale restoration** converts naive retrieval (which increases RMSSE) into
   a useful augmentation, improving frozen Chronos-2 by **+5.49% RMSSE on the
   held-out M5 test** (CI [+5.40, +5.59]); restoration is the decisive component
   (ablation 0.74 → 2.79 RMSSE without it).
2. **Learned uncertainty-aware gated fusion.** A lightweight gate over retrieval
   confidence/disagreement, intermittency, demand level, and Chronos uncertainty
   routes each series between the backbone and retrieval; it beats fixed-weight
   fusion and is the best method on RMSSE, while adding **0 trainable backbone
   parameters**.
3. **Honest metric- and regime-dependence (primary negative).** The RMSSE gain does
   **not** transfer: ScaleRAG loses to strong simple baselines on **WRMSSE** and to
   the frozen backbone on **MAE/WAPE/MASE/pinball/coverage**; it helps sparse series
   vs the backbone (+6–7%) but only *ties* the strongest baseline there. **0/3**
   pre-registered criteria met on untouched test data.
4. **Cross-dataset relational-metadata negative.** Typed-relation graph routing adds
   no predictive retrieval value beyond temporal similarity on either M5 or Favorita,
   under learned/non-learned routers and shuffle/random controls with CIs.
5. **Benchmarking caution.** On intermittent-retail RMSSE, recent-mean and LightGBM
   are punishing baselines and win the official WRMSSE; a frozen TSFM + retrieval
   improves the model but not the field's strongest simple methods by a
   pre-registered margin.

## Claims we explicitly do NOT make

- **No SOTA / leaderboard claim.** On the full-panel official **WRMSSE**, ScaleRAG
  does not win (LightGBM/Seasonal-Naive are better); the headline gain is
  RMSSE-specific.
- **No general point-accuracy win.** Frozen Chronos-2 is better on MASE/WAPE/MAE and
  is the best-calibrated forecaster (ScaleRAG under-covers).
- **No superiority over the RAFT / TS-RAG originals** — only *inspired*
  reimplementations under our identical protocol.
- **No relational/graph contribution** — that hypothesis was falsified.

## Limitations (summary; full accounting in `threats-to-validity.md`)

- Two intermittent-retail datasets only; RMSSE-favourable framing; a single held-out
  test origin; gate trained on two historical origins; inspired (not exact) RAFT/
  TS-RAG reimplementations; gated fusion under-covers. The GPU retriever used for the
  full-panel run is verified bit-identical to the frozen numpy retriever.


<!-- END SOURCE: final-abstract.md -->
### 11.2 Paper outline
Verbatim contents of `docs/paper-outline.md`.
<!-- BEGIN SOURCE: paper-outline.md -->

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


<!-- END SOURCE: paper-outline.md -->
## 12. Reproducibility and usage
### 12.1 Repository README (extract)

The following sections are **extracted from `README.md`** (repository root). Unrelated project-status narrative is omitted; everything below is verbatim from the marked sections.
<!-- BEGIN SOURCE: README.md -->
# ScaleRAG-TS  (formerly GraphRoute-TS)

**Scale-Aware Retrieval Augmentation for Time-Series Foundation Models.**

Research codebase studying whether scale-aware temporal retrieval + a learned
gated fusion improves a **frozen** Chronos-2 backbone on intermittent-retail
forecasting (M5 + Favorita). The original relation-aware **graph-routing**
hypothesis was rigorously **rejected** cross-dataset (Phases 6–8) and is kept as a
controlled negative result.

> **Status:** Phases 1–9 complete; controlled study finished, method frozen. The
> M5 test split `d_1914–d_1941` is untouched. See `docs/project-status.md`,
> `docs/final-experiment-report.md`, and the research rules in `CLAUDE.md`.

## Requirements

- Linux (developed on CachyOS/Arch), NVIDIA GPU with recent driver (RTX 5070 Ti,
  Blackwell/sm_120, CUDA 13.x here).
- [`uv`](https://docs.astral.sh/uv/) for environment management.
- Python 3.11 (provisioned automatically by `uv` — pinned in `.python-version`).

## Install dependencies

```bash
# uv provisions Python 3.11 and creates a project-local .venv from the lockfile.
uv sync --extra ml --extra retrieval --extra tsfm
```

`torch` is pulled from the CUDA 13.0 (`cu130`) index configured in `pyproject.toml`
to match the Blackwell GPU. Heavy optional groups (`graph`, `gpu-retrieval`) are
defined but intentionally **not** installed yet.

## Activate the environment (Fish)

```fish
source .venv/bin/activate.fish
```

<details><summary>bash / zsh</summary>

```bash
source .venv/bin/activate
```
</details>

Or prefix any command with `uv run` (no activation needed), e.g. `uv run pytest`.

## Verify GPU support

```bash
uv run python scripts/environment_check.py      # full pass/fail report
uv run python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

## Fast checks

```bash
make check      # format + lint + type + unit + leakage
make verify     # environment health check
make test       # unit tests
make leakage    # leakage / split-integrity tests
make smoke      # environment smoke tests
```

## Start Jupyter

```bash
make jupyter    # or: uv run jupyter lab
```

## Project skills (Claude Code)

Invoke inside Claude Code:

| Skill | Purpose |
|-------|---------|
| `/environment-check` | Verify the dev environment (read-only). |
| `/data-audit` | Audit a dataset (schema, missing, ordering, leakage hints). |
| `/leakage-audit` | Enforce chronological-split & retrieval-horizon integrity. |
| `/baseline-run` | Run one small **declared** baseline (refuses full-scale runs). |
| `/experiment-review` | Audit an experiment for soundness & reproducibility. |
| `/research-code-review` | Review code for correctness, leakage, reproducibility. |

## M5 pipeline & baselines (Phase 2)

Developed against a deterministic **synthetic** M5 fixture (offline); the same
code path runs on real M5 once the files are in `data/raw/`. See
`docs/m5-data-design.md`, `docs/m5-split-policy.md`, `docs/processed-schema.md`,
and `docs/baseline-report.md`.

```bash
# 1) build + ingest the offline synthetic fixture (idempotent)
uv run python scripts/make_synthetic.py --days 1941 --raw data/raw_synth --processed data/processed

# 2) verify chronological-split integrity
uv run python scripts/leakage_audit.py --spec configs/split_check_val.json

# 3) declare, then run the classical baselines (val split; test held out)
uv run python scripts/baseline_run.py --config configs/baseline_seasonal_naive.yaml --dry-run
uv run python scripts/baseline_run.py --config configs/baseline_seasonal_naive.yaml --confirm
uv run python scripts/baseline_run.py --config configs/baseline_lightgbm.yaml --confirm
```

Real M5 ingestion (once files are present in `data/raw/`) uses the identical
`ingest_m5` path — validate first, then point a config's `processed_dir` at it.

## Layout

See `CLAUDE.md` for the full architecture, environment commands, and the
non-negotiable research rules. Data, checkpoints, artifacts, logs, and secrets are
never committed (`.gitignore`).

<!-- END SOURCE: README.md -->

### 12.2 Reproducibility policy (separate document)
Verbatim contents of `docs/reproducibility-policy.md` (operationalises CLAUDE.md research rules 6 and 10).
<!-- BEGIN SOURCE: reproducibility-policy.md -->

# Reproducibility Policy

Every result must be reproducible from recorded inputs. This policy operationalises
CLAUDE.md research rules 6 and 10.

## Record for every experiment

- **Seed(s)** — set via `graphroute_ts.reproducibility.set_seed`.
- **Package versions** — the committed `uv.lock` is authoritative; also capture
  `torch.__version__` and `torch.version.cuda`.
- **Config file** — the exact YAML (validated by `graphroute_ts.config`).
- **Git commit** — `git rev-parse HEAD`; the tree must be clean (no uncommitted diff).
- **Runtime** — wall-clock duration and peak memory / VRAM.
- **Hardware** — GPU name + compute capability, driver, CPU, RAM.

`graphroute_ts.reproducibility.RunContext` captures a best-effort fingerprint
(python, platform, git commit, torch, CUDA, GPU) — persist it alongside metrics.

## Determinism

- Seed Python, NumPy, and Torch (CPU + CUDA).
- Request deterministic cuDNN where practical; note that bit-exactness is **not**
  guaranteed across hardware/driver versions — record the environment, don't assume.
- No nondeterministic ordering (e.g. set iteration) in data pipelines.

## Metrics & claims

- **No single-run headline numbers.** Report central tendency and dispersion across
  multiple seeds (rule 6).
- Statistical claims require a named test or confidence interval (rule 8).
- Aggregation level (per-series vs pooled) and weighting are stated explicitly.

## Environment reproducibility

- `uv.lock` is committed and never hand-edited. Recreate with
  `uv sync --extra ml --extra retrieval --extra tsfm`.
- Python is pinned by `.python-version`; the PyTorch CUDA index is pinned in
  `pyproject.toml`.

## Data reproducibility

- Datasets are not committed; record dataset name, version/snapshot, and the
  preprocessing commit that produced `data/processed/*`.
- All fitted transforms are fit on **train only** and persisted for reuse.

## Prohibited

Editing evaluation code to improve a number (rule 9); swapping a failed model
silently (rule 7); reporting results from an unclean/uncommitted tree.


<!-- END SOURCE: reproducibility-policy.md -->
### 12.3 Hugging Face demo usage
Verbatim contents of `spaces/scalerag-demo/README.md`. The Space is **research software, not a scientific contribution**: it is a lightweight standalone reimplementation, references the official `amazon/chronos-2` checkpoint, ships no M5 / Favorita / Kaggle data or credentials, and bundles only synthetic example data.
<!-- BEGIN SOURCE: spaces/scalerag-demo/README.md -->

---
title: ScaleRAG-TS Demo
emoji: 🔬
colorFrom: indigo
colorTo: red
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
license: apache-2.0
pinned: false
short_description: Scale-aware retrieval augmentation of a frozen Chronos-2 (research demo)
---

# ScaleRAG-TS — research demo

**Scale-Aware Retrieval Augmentation for Time-Series Foundation Models.**
This Space illustrates how augmenting a **frozen** Chronos-2 backbone with
**scale-aware temporal retrieval** and a **learned uncertainty-aware gated fusion**
changes its forecasts. Upload a CSV of time series (or use the bundled synthetic
example), pick a target series, and compare:

- **target-only Chronos-2** vs **ScaleRAG** point forecasts (with the actuals held out),
- the **retrieved historical analog windows** (scale-restored) that retrieval used,
- the **learned gate weight α** that decides how much to trust retrieval vs the backbone.

> ⚠️ **Research software — not a product.** This is an *illustration* of the method.
> It does **not** reproduce the paper's exact reported metrics (those come from a
> controlled full-dataset study with a frozen LightGBM gate and paired-bootstrap CIs).

## What this demo is (and is not)

- The **method** here is a lightweight, self-contained reimplementation of the paper's
  retrieval + gated-fusion path so the Space is standalone. The gate is a small logistic
  gate fit on **your uploaded corpus's own historical origin** (the paper uses a learned
  LightGBM gate). Deployment/engineering here is **not** a scientific contribution.
- The **science** (controlled study, ablations, held-out test, the rejected graph-routing
  hypothesis) lives in the code repository and paper.

## Model & data provenance

- The forecasting backbone is the **official `amazon/chronos-2`** checkpoint (Apache-2.0),
  loaded at runtime from the Hugging Face Hub. **No Chronos-2 weights are redistributed**
  by this Space — it references the official checkpoint.
- The bundled example (`examples/synthetic_retail.csv`) is **fully synthetic**, generated by
  `examples/make_synthetic.py`. **No M5, Favorita, or Kaggle data or credentials** are
  included, uploaded, or distributed here.

## CSV format

| column | required | notes |
|--------|----------|-------|
| `series_id` | yes | one id per series (aliases: `id`, `series`) |
| `value` | yes | numeric observations (aliases: `sales`, `y`) |
| `t` / `date` / `step` | no | used to order each series if present |

## Links

- 📄 Paper / method write-up: see the code repository (`docs/`).
- 💻 Code repository: set `REPO_URL` / `PAPER_URL` in `app.py` to your public URLs.

## Method (one paragraph)

For a target series at forecast origin *o*, retrieval mean-normalises the recent context,
finds the *k* nearest **leakage-safe** candidate windows (those ending before *o*), and
restores each retrieved continuation to the target's scale. A gate scores retrieval
confidence, disagreement, intermittency, demand level, Chronos uncertainty, and
scale-spread to produce a per-series weight **α**, and the final forecast is the convex
blend `(1 − α)·Chronos-2 + α·Retrieval`. No graph/relational features (that hypothesis was
falsified in the study) and no retrieved future labels ever enter the Chronos input.


<!-- END SOURCE: spaces/scalerag-demo/README.md -->
## 13. Machine-readable final tables
Markdown tables in this section are **generated deterministically from the JSON files** by a small script; the original JSON is also preserved inline for direct inspection. No numerical values are retyped by hand.
**Labels used in this section:**
- *val (M5 1k)* - M5 1,000-series validation subset (1,000 series, `d_1886-d_1913`). Frozen study numbers.
- *val (M5 30,490)* - full 30,490-series M5 validation panel at the same origin. Re-run during the locked Phase-10 confirmation.
- *test (M5 30,490)* - full 30,490-series M5 held-out test (`d_1914-d_1941`). **Consumed exactly once** (`M5_TEST_CONSUMED.lock`).
- *Favorita 5k* - Favorita 5,000-series val subset (1,000 days). Frozen reference.
- *inspired* (RAFT / TS-RAG-style) vs *exact* baselines are labelled in the M5 1k table.

### 13.A Frozen validation matrix - JSON source
Original JSON (`docs/scalerag-final-tables.json`):

<details><summary>Click to expand</summary>

```json
{
  "study": "ScaleRAG-TS controlled study",
  "verdict": "positive retrieval augmentation of frozen Chronos-2 (regime-dependent); no pre-registered success criterion met; graph-routing rejected cross-dataset",
  "m5_1000": {
    "methods_rmsse": {
      "recent_mean": 0.7220824121274221,
      "seasonal_naive": 0.951802930248127,
      "lightgbm": 0.7175355694891105,
      "chronos2_target": 0.7539587247776638,
      "retrieval_raw": 0.7576107070840873,
      "retrieval_scaleaware_P5": 0.7424561064366584,
      "RAFT_style": 0.8267552877010563,
      "TSRAG_style_fusion": 0.7866383714084775,
      "fusion_fixed0.5": 0.7251628266273276,
      "ScaleRAG_gated": 0.717305058911237
    },
    "scalerag_vs_chronos": {
      "rel_improvement": 0.04861495021128071,
      "ci95_low": 0.0430429362997639,
      "ci95_high": 0.05393849368597238,
      "excludes_zero": true,
      "n": 1000
    },
    "scalerag_vs_strongest": {
      "rel_improvement": 0.0003212531722122337,
      "ci95_low": -0.00554986443230368,
      "ci95_high": 0.006328077485272804,
      "excludes_zero": false,
      "n": 1000
    },
    "strongest_baseline": "lightgbm",
    "slices": {
      "intermittent(z>0.8)": {
        "vs_chronos_rel": 0.050094884051850495,
        "scalerag_rmsse": 0.7313713957433756,
        "recent_rmsse": 0.7295655815727778
      },
      "low_volume(<med)": {
        "vs_chronos_rel": 0.05749550828454374,
        "scalerag_rmsse": 0.72698367561172,
        "recent_rmsse": 0.7225274395720604
      },
      "reduced_history(<100nz)": {
        "vs_chronos_rel": 0.03987901065322361,
        "scalerag_rmsse": 0.868288604106924,
        "recent_rmsse": 0.8678685542607341
      },
      "dense(z<0.3)": {
        "vs_chronos_rel": -0.0030709271669517877,
        "scalerag_rmsse": 0.6557948697679028,
        "recent_rmsse": 0.6931354417720706
      }
    },
    "gate_behaviour": {
      "alpha_mean": 0.6400368789685666,
      "alpha_std": 0.24406733140358527,
      "alpha_pct_prefer_chronos(<0.5)": 0.304,
      "corr_alpha_chronos_unc": -0.36314981680903585,
      "corr_alpha_disagreement": -0.3505157438594678,
      "corr_alpha_intermittency": 0.38129044382732064
    },
    "calibration": {
      "chronos_cov80": 0.7912857142857143,
      "scalerag_cov80": 0.6885,
      "note": "fusion improves point RMSSE but under-covers vs Chronos; post-hoc widening trades width for coverage"
    },
    "key_ablations": {
      "norm_no_restore": 2.788399207280297,
      "mean_scaling": 0.7424561064366584,
      "no_category_filter": 0.7382787110842058,
      "k=20": 0.7424561064366584,
      "context=84": 0.7348850516549994,
      "fixed_gate_0.5": 0.7251628266273276
    }
  },
  "favorita_5000": {
    "methods_rmsse": {
      "recent_mean": 0.7757157213669394,
      "chronos2_target": 0.7287461397547859,
      "retrieval_scaleaware": 0.78271615560888,
      "ScaleRAG_gated": 0.7226931751288974
    },
    "scalerag_vs_chronos": {
      "rel_improvement": 0.008305998887246518,
      "ci95_low": 0.006392539019263186,
      "ci95_high": 0.010307869036746171,
      "excludes_zero": true,
      "n": 5000
    },
    "strongest_baseline": "chronos2_target"
  },
  "preregistered_criteria": {
    "c1_3pct_over_strongest": {
      "m5": 0.0003212531722122337,
      "favorita": 0.008305998887246518,
      "met": false
    },
    "c2_5pct_over_chronos_both": {
      "m5": 0.04861495021128071,
      "favorita": 0.008305998887246518,
      "met": false
    },
    "c3_7pct_slice_over_strongest": {
      "met": false
    }
  },
  "graph_routing_negative": {
    "m5_metadata_util_corr": 0.003,
    "favorita_metadata_util_corr": -0.06273101265822785,
    "conclusion": "typed-relation routing adds no retrieval value beyond temporal similarity on either dataset"
  }
}
```

</details>

### 13.B Held-out test tables - JSON source
Original JSON (`docs/scalerag-heldout-test-tables.json`):

<details><summary>Click to expand</summary>

```json
{
  "study": "ScaleRAG-TS \u2014 final locked held-out test (Phase 10)",
  "test_split": "M5 d_1914-d_1941 (consumed once; see M5_TEST_CONSUMED.lock)",
  "git_commit": "d42d20e3bc4d6096f82349d16284b5b6da00346f",
  "frozen_config": "ScaleRAG_gated: mean/L2/cat-filter/k=20 + scale restoration + LGBM gate",
  "gate_origins": [
    1829,
    1857
  ],
  "population": "full M5 panel, 30490 series",
  "verdict": "0/3 pre-registered criteria met on held-out test; ScaleRAG improves Chronos-2 on RMSSE (+5.49%) only, regime- and metric-dependent; LightGBM/Seasonal-Naive win official WRMSSE; Chronos-2 best on MAE/WAPE/MASE/pinball/coverage",
  "test": {
    "eval_window": "d_1914-d_1941",
    "n_series": 30490,
    "methods": {
      "recent_mean": {
        "rmsse": 0.7669006143818549,
        "wrmsse": 1.0876028485862725,
        "mase": 1.0738419948733386,
        "wape": 0.7452848690403124,
        "mae": 1.0753116612338605,
        "pinball": 0.5376558306169302,
        "cov50": 0.026348217214074873,
        "cov80": 0.026348217214074873,
        "cov90": 0.026348217214074873,
        "width80": 0.0
      },
      "seasonal_naive": {
        "rmsse": 0.9972420371212409,
        "wrmsse": 0.869700702331063,
        "mase": 1.2111840263991596,
        "wape": 0.8621813918900049,
        "mae": 1.2439722625685237,
        "pinball": 0.6219861312842618,
        "cov50": 0.4577238438832404,
        "cov80": 0.4577238438832404,
        "cov90": 0.4577238438832404,
        "width80": 0.0
      },
      "lightgbm": {
        "rmsse": 0.7664720329907873,
        "wrmsse": 0.8662986834873586,
        "mase": 1.0772949926689948,
        "wape": 0.7396488774230703,
        "mae": 1.067179941725801,
        "pinball": 0.5335899708629005,
        "cov50": 0.0,
        "cov80": 0.0,
        "cov90": 0.0,
        "width80": 0.0
      },
      "chronos2_target": {
        "rmsse": 0.8053793034204073,
        "wrmsse": 1.939512483576866,
        "mase": 0.8931894433905123,
        "wape": 0.6652695376059768,
        "mae": 0.9598639679516568,
        "pinball": 0.28859809707083134,
        "cov50": 0.35837628262193694,
        "cov80": 0.7864276343531837,
        "cov90": 0.9065033031907417,
        "width80": 2.837459087371826
      },
      "retrieval_scaleaware": {
        "rmsse": 0.7794626021660002,
        "wrmsse": 1.2292617442556775,
        "mase": 1.1107953228218945,
        "wape": 0.7432662273556818,
        "mae": 1.0723991253250997,
        "pinball": 0.3262582126615511,
        "cov50": 0.5252881506817223,
        "cov80": 0.7279775570444642,
        "cov90": 0.8045471583188868,
        "width80": 2.040890674823178
      },
      "fusion_fixed0.5": {
        "rmsse": 0.7692042933117564,
        "wrmsse": 1.380899380343342,
        "mase": 0.9911388854837756,
        "wape": 0.6909236976114185,
        "mae": 0.996878294364231,
        "pinball": 0.29571127128933483,
        "cov50": 0.3066743194489997,
        "cov80": 0.7147132549313592,
        "cov90": 0.8476467694326009,
        "width80": 2.4369727066738616
      },
      "ScaleRAG_gated": {
        "rmsse": 0.7611532841582019,
        "wrmsse": 1.223053045470008,
        "mase": 1.019515648061554,
        "wape": 0.6982989461084517,
        "mae": 1.0075194478919678,
        "pinball": 0.29812260162574966,
        "cov50": 0.3059832263505599,
        "cov80": 0.6975343203860751,
        "cov90": 0.8278182542285527,
        "width80": 2.4045504564953197
      }
    },
    "strongest_baseline": "lightgbm",
    "scalerag_vs_chronos": {
      "rel_improvement": 0.0549132800835328,
      "ci95_low": 0.0539959723861063,
      "ci95_high": 0.05587702799646904,
      "excludes_zero": true,
      "n": 30490
    },
    "scalerag_vs_strongest": {
      "rel_improvement": 0.00693926014734219,
      "ci95_low": 0.00571592726490809,
      "ci95_high": 0.008197188897119359,
      "excludes_zero": true,
      "n": 30490
    },
    "per_method_vs_chronos": {
      "recent_mean": 0.047777101888681894,
      "seasonal_naive": -0.23822655100025764,
      "lightgbm": 0.048309250392185074,
      "retrieval_scaleaware": 0.03217949746701978,
      "fusion_fixed0.5": 0.044916736691664835,
      "ScaleRAG_gated": 0.0549132800835328
    },
    "slices": {
      "intermittent(z>0.8)": {
        "n": 11783,
        "vs_chronos": 0.05967577335912072,
        "vs_chronos_ci": [
          0.05810710429505595,
          0.06129534188124747
        ],
        "vs_strongest": -0.0002926864392823806,
        "vs_strongest_ci": [
          -0.0017276978238243783,
          0.0012626276729468635
        ]
      },
      "low_volume(<med)": {
        "n": 15241,
        "vs_chronos": 0.06849335659705552,
        "vs_chronos_ci": [
          0.0671060929923205,
          0.06985955192801173
        ],
        "vs_strongest": -0.0030166396950306916,
        "vs_strongest_ci": [
          -0.004277383201738198,
          -0.0017373280561772616
        ]
      },
      "reduced_history(<100nz)": {
        "n": 1778,
        "vs_chronos": 0.031411541541359424,
        "vs_chronos_ci": [
          0.026345525178209168,
          0.036125804290178164
        ],
        "vs_strongest": 0.009322183187998236,
        "vs_strongest_ci": [
          0.004040406520728263,
          0.01510146009375584
        ]
      },
      "dense(z<0.3)": {
        "n": 2247,
        "vs_chronos": 0.0034189052385980977,
        "vs_chronos_ci": [
          0.001208127056500503,
          0.005569702422221921
        ],
        "vs_strongest": 0.050445414632569366,
        "vs_strongest_ci": [
          0.04282869553039427,
          0.059017511969839426
        ]
      }
    },
    "gate_behaviour": {
      "alpha_mean": 0.6219664455775091,
      "alpha_std": 0.2148183244693282,
      "alpha_pct_prefer_chronos(<0.5)": 0.3378812725483765,
      "corr_alpha_chronos_unc": -0.4377722692540937,
      "corr_alpha_intermittency": 0.48459063002993097
    },
    "profiling": {
      "chronos_inference_ms": 35737,
      "retrieval_ms": 42225,
      "gpu_vram_gib": 1.763,
      "host_ram_peak_gib": 26.449,
      "backbone_params_updated": 0,
      "backbone_frozen": true,
      "gate_kind": "LightGBM GBDT",
      "gate_ensemble_leaf_values_approx": 9000,
      "gate_seeds_averaged": 3
    }
  },
  "validation_full_panel": {
    "eval_window": "d_1886-d_1913",
    "n_series": 30490,
    "methods": {
      "recent_mean": {
        "rmsse": 0.7442454314369539,
        "wrmsse": 1.1014100550260513,
        "mase": 1.088942253932008,
        "wape": 0.76013465643467,
        "mae": 1.0538761454073264,
        "pinball": 0.5269380727036632,
        "cov50": 0.033181839478986085,
        "cov80": 0.033181839478986085,
        "cov90": 0.033181839478986085,
        "width80": 0.0
      },
      "seasonal_naive": {
        "rmsse": 0.975596206683179,
        "wrmsse": 0.9227813345358976,
        "mase": 1.2269697576259488,
        "wape": 0.8888669224907192,
        "mae": 1.2323548704493277,
        "pinball": 0.6161774352246638,
        "cov50": 0.47516750222555404,
        "cov80": 0.47516750222555404,
        "cov90": 0.47516750222555404,
        "width80": 0.0
      },
      "lightgbm": {
        "rmsse": 0.7439942013190757,
        "wrmsse": 0.7105798238952588,
        "mase": 1.0966171527879718,
        "wape": 0.7542986308756858,
        "mae": 1.0457848841175847,
        "pinball": 0.5228924420587923,
        "cov50": 0.0,
        "cov80": 0.0,
        "cov90": 0.0,
        "width80": 0.0
      },
      "chronos2_target": {
        "rmsse": 0.776541409212862,
        "wrmsse": 1.756786610585972,
        "mase": 0.9036047914355981,
        "wape": 0.6711934152274399,
        "mae": 0.9305650298599,
        "pinball": 0.27689154303590036,
        "cov50": 0.36422597572974746,
        "cov80": 0.790575364288057,
        "cov90": 0.9091774820784332,
        "width80": 2.8317222595214844
      },
      "retrieval_scaleaware": {
        "rmsse": 0.761730938723884,
        "wrmsse": 1.2853718973716883,
        "mase": 1.1363047862379265,
        "wape": 0.764629911416778,
        "mae": 1.0601085174654399,
        "pinball": 0.31792548770859436,
        "cov50": 0.5422843555264021,
        "cov80": 0.7392892283184183,
        "cov90": 0.813145996345406,
        "width80": 2.054276066052129
      },
      "fusion_fixed0.5": {
        "rmsse": 0.7456324189995855,
        "wrmsse": 1.2791056374848673,
        "mase": 1.0084032525118602,
        "wape": 0.7046264028049186,
        "mae": 0.9769176435439895,
        "pinball": 0.28644683394774134,
        "cov50": 0.31508925643067986,
        "cov80": 0.7218279998125849,
        "cov90": 0.8526601227568757,
        "width80": 2.4407759949617946
      },
      "ScaleRAG_gated": {
        "rmsse": 0.7371223866826532,
        "wrmsse": 1.1151712745410294,
        "mase": 1.0333662986600083,
        "wape": 0.7103241196188795,
        "mae": 0.9848171489575223,
        "pinball": 0.28768882117439176,
        "cov50": 0.31483156069905827,
        "cov80": 0.7062233519186618,
        "cov90": 0.8344351778100548,
        "width80": 2.414814914556511
      }
    },
    "scalerag_vs_chronos": {
      "rel_improvement": 0.05076229298597962,
      "ci95_low": 0.04974338784036041,
      "ci95_high": 0.05186695591859367,
      "excludes_zero": true,
      "n": 30490
    },
    "scalerag_vs_strongest": {
      "rel_improvement": 0.009236381982868972,
      "ci95_low": 0.00775738625315055,
      "ci95_high": 0.010699191470828233,
      "excludes_zero": true,
      "n": 30490
    },
    "slices": {
      "intermittent(z>0.8)": {
        "n": 11907,
        "vs_chronos": 0.05630336170319622,
        "vs_chronos_ci": [
          0.054490199250198885,
          0.05830885876370411
        ],
        "vs_strongest": 0.005043804367438135,
        "vs_strongest_ci": [
          0.002908625613056078,
          0.007125103074590082
        ]
      },
      "low_volume(<med)": {
        "n": 15233,
        "vs_chronos": 0.06404037773007273,
        "vs_chronos_ci": [
          0.062470105841241914,
          0.06564069269651664
        ],
        "vs_strongest": 0.0019388458183054143,
        "vs_strongest_ci": [
          0.0003529094358321974,
          0.0036014748369241614
        ]
      },
      "reduced_history(<100nz)": {
        "n": 1932,
        "vs_chronos": 0.03575185546576338,
        "vs_chronos_ci": [
          0.02990346199636349,
          0.04125033803241897
        ],
        "vs_strongest": 0.009848718484072719,
        "vs_strongest_ci": [
          0.004628888476640988,
          0.014757898726507776
        ]
      },
      "dense(z<0.3)": {
        "n": 2235,
        "vs_chronos": 0.0012704632828158331,
        "vs_chronos_ci": [
          -0.0006830636683984797,
          0.0031556493171828862
        ],
        "vs_strongest": 0.036190732755747176,
        "vs_strongest_ci": [
          0.029413246262766878,
          0.04330008896484834
        ]
      }
    },
    "gate_behaviour": {
      "alpha_mean": 0.6146773546938818,
      "alpha_std": 0.21537774363647316,
      "alpha_pct_prefer_chronos(<0.5)": 0.34840931452935386,
      "corr_alpha_chronos_unc": -0.4136455522130339,
      "corr_alpha_intermittency": 0.4391043870821713
    }
  },
  "favorita_reference_frozen": {
    "methods_rmsse": {
      "recent_mean": 0.7757157213669394,
      "chronos2_target": 0.7287461397547859,
      "retrieval_scaleaware": 0.78271615560888,
      "ScaleRAG_gated": 0.7226931751288974
    },
    "scalerag_vs_chronos": {
      "rel_improvement": 0.008305998887246518,
      "ci95_low": 0.006392539019263186,
      "ci95_high": 0.010307869036746171,
      "excludes_zero": true,
      "n": 5000
    },
    "strongest_baseline": "chronos2_target"
  },
  "preregistered_criteria": {
    "C1_ge3pct_over_strongest_ci_excl0": {
      "test_rmsse_margin": 0.00693926014734219,
      "test_wrmsse_scalerag": 1.223053045470008,
      "test_wrmsse_strongest": 0.8662986834873586,
      "met": false
    },
    "C2_ge5pct_over_chronos_both_datasets": {
      "m5_test": 0.0549132800835328,
      "favorita": 0.008305998887246518,
      "met": false
    },
    "C3_ge7pct_on_sparse_slice_over_strongest": {
      "best_sparse_slice_vs_strongest": 0.009322183187998236,
      "met": false
    },
    "criteria_met_count": 0
  }
}
```

</details>

### 13.C Markdown tables (generated)
### A. Frozen validation matrix (M5 1,000 series; `docs/scalerag-final-tables.json`)

#### A.1 Methods — RMSSE (val, M5 1k)

| method | RMSSE |
|---|---|
| recent_mean | 0.7221 |
| seasonal_naive | 0.9518 |
| lightgbm | 0.7175 |
| chronos2_target | 0.7540 |
| retrieval_raw | 0.7576 |
| retrieval_scaleaware_P5 | 0.7425 |
| RAFT_style | 0.8268 |
| TSRAG_style_fusion | 0.7866 |
| fusion_fixed0.5 | 0.7252 |
| ScaleRAG_gated | 0.7173 |

#### A.2 Paired-bootstrap CIs (val, M5 1k)

**ScaleRAG vs Chronos-2**

| field | value |
|---|---|
| rel. improvement | 0.0486 |
| 95% CI low | 0.0430 |
| 95% CI high | 0.0539 |
| excludes 0 | yes |
| n | 1000 |


**ScaleRAG vs strongest (lightgbm)**

| field | value |
|---|---|
| rel. improvement | 0.0003 |
| 95% CI low | -0.0055 |
| 95% CI high | 0.0063 |
| excludes 0 | no |
| n | 1000 |


#### A.3 Validation slices (M5 1k)

| slice | vs Chronos (rel) | ScaleRAG RMSSE | recent-mean RMSSE |
|---|---|---|---|
| intermittent(z>0.8) | 0.0501 | 0.7314 | 0.7296 |
| low_volume(<med) | 0.0575 | 0.7270 | 0.7225 |
| reduced_history(<100nz) | 0.0399 | 0.8683 | 0.8679 |
| dense(z<0.3) | -0.0031 | 0.6558 | 0.6931 |

#### A.4 Gate behaviour (val, M5 1k)

| field | value |
|---|---|
| alpha_mean | 0.6400 |
| alpha_std | 0.2441 |
| alpha_pct_prefer_chronos(<0.5) | 0.3040 |
| corr_alpha_chronos_unc | -0.3631 |
| corr_alpha_disagreement | -0.3505 |
| corr_alpha_intermittency | 0.3813 |

#### A.5 Calibration (val, M5 1k)

| field | value | note |
|---|---|---|
| chronos_cov80 | 0.7913 | — |
| scalerag_cov80 | 0.6885 | — |
| note | — | fusion improves point RMSSE but under-covers vs Chronos; post-hoc widening trades width for coverage |

#### A.6 Key ablations (val, M5 1k)

| ablation | RMSSE |
|---|---|
| norm_no_restore | 2.7884 |
| mean_scaling | 0.7425 |
| no_category_filter | 0.7383 |
| k=20 | 0.7425 |
| context=84 | 0.7349 |
| fixed_gate_0.5 | 0.7252 |

#### A.7 Favorita 5,000 series (val)

| method | RMSSE |
|---|---|
| recent_mean | 0.7757 |
| chronos2_target | 0.7287 |
| retrieval_scaleaware | 0.7827 |
| ScaleRAG_gated | 0.7227 |

**ScaleRAG vs Chronos-2 (Favorita 5k)**

| field | value |
|---|---|
| rel. improvement | 0.0083 |
| 95% CI low | 0.0064 |
| 95% CI high | 0.0103 |
| excludes 0 | yes |
| n | 5000 |

**Strongest baseline (Favorita):** `chronos2_target`

#### A.8 Pre-registered success criteria (frozen study, val + Favorita)

| criterion | detail | result | met? |
|---|---|---|---|
| c1_3pct_over_strongest |  —  | m5=0.0003, favorita=0.0083 | NO |
| c2_5pct_over_chronos_both |  —  | m5=0.0486, favorita=0.0083 | NO |
| c3_7pct_slice_over_strongest |  —  |  | NO |

#### A.9 Cross-dataset relational-metadata negative

| dataset | metadata utility correlation |
|---|---|
| M5 | 0.0030 |
| Favorita | -0.0627 |

**Conclusion:** typed-relation routing adds no retrieval value beyond temporal similarity on either dataset

### B. Final locked held-out test (M5 30,490 series; `docs/scalerag-heldout-test-tables.json`)

**Test split:** `M5 d_1914-d_1941 (consumed once; see M5_TEST_CONSUMED.lock)`  |  **git_commit (locked run):** `d42d20e3bc4d6096f82349d16284b5b6da00346f`
**Frozen config:** `ScaleRAG_gated: mean/L2/cat-filter/k=20 + scale restoration + LGBM gate`  |  **Population:** full M5 panel, 30490 series
**Verdict:** 0/3 pre-registered criteria met on held-out test; ScaleRAG improves Chronos-2 on RMSSE (+5.49%) only, regime- and metric-dependent; LightGBM/Seasonal-Naive win official WRMSSE; Chronos-2 best on MAE/WAPE/MASE/pinball/coverage

#### B.1 Test methods (full metrics, 30,490 series, d_1914-d_1941)

| method | rmsse | wrmsse | mase | wape | mae | pinball | cov50 | cov80 | cov90 | width80 |
|---|---|---|---|---|---|---|---|---|---|---|
| recent_mean | 0.7669 | 1.0876 | 1.0738 | 0.7453 | 1.0753 | 0.5377 | 0.0263 | 0.0263 | 0.0263 | 0.0000 |
| seasonal_naive | 0.9972 | 0.8697 | 1.2112 | 0.8622 | 1.2440 | 0.6220 | 0.4577 | 0.4577 | 0.4577 | 0.0000 |
| lightgbm | 0.7665 | 0.8663 | 1.0773 | 0.7396 | 1.0672 | 0.5336 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| chronos2_target | 0.8054 | 1.9395 | 0.8932 | 0.6653 | 0.9599 | 0.2886 | 0.3584 | 0.7864 | 0.9065 | 2.8375 |
| retrieval_scaleaware | 0.7795 | 1.2293 | 1.1108 | 0.7433 | 1.0724 | 0.3263 | 0.5253 | 0.7280 | 0.8045 | 2.0409 |
| fusion_fixed0.5 | 0.7692 | 1.3809 | 0.9911 | 0.6909 | 0.9969 | 0.2957 | 0.3067 | 0.7147 | 0.8476 | 2.4370 |
| ScaleRAG_gated | 0.7612 | 1.2231 | 1.0195 | 0.6983 | 1.0075 | 0.2981 | 0.3060 | 0.6975 | 0.8278 | 2.4046 |

**Strongest baseline (test):** `lightgbm`

#### B.2 Paired-bootstrap CIs (test)

**ScaleRAG vs Chronos-2 (test)**

| field | value |
|---|---|
| rel. improvement | 0.0549 |
| 95% CI low | 0.0540 |
| 95% CI high | 0.0559 |
| excludes 0 | yes |
| n | 30490 |


**ScaleRAG vs strongest (lightgbm) (test)**

| field | value |
|---|---|
| rel. improvement | 0.0069 |
| 95% CI low | 0.0057 |
| 95% CI high | 0.0082 |
| excludes 0 | yes |
| n | 30490 |


#### B.3 Per-method RMSSE relative improvement vs Chronos-2 (test)

| method | rel. improvement vs Chronos-2 |
|---|---|
| recent_mean | 0.0478 |
| seasonal_naive | -0.2382 |
| lightgbm | 0.0483 |
| retrieval_scaleaware | 0.0322 |
| fusion_fixed0.5 | 0.0449 |
| ScaleRAG_gated | 0.0549 |

#### B.4 Pre-registered slices (test)

| slice | n | vs Chronos (rel) | vs Chronos CI | vs strongest (rel) | vs strongest CI |
|---|---|---|---|---|---|
| intermittent(z>0.8) | 11783 | 0.0597 | [0.0581, 0.0613] | -0.0003 | [-0.0017, 0.0013] |
| low_volume(<med) | 15241 | 0.0685 | [0.0671, 0.0699] | -0.0030 | [-0.0043, -0.0017] |
| reduced_history(<100nz) | 1778 | 0.0314 | [0.0263, 0.0361] | 0.0093 | [0.0040, 0.0151] |
| dense(z<0.3) | 2247 | 0.0034 | [0.0012, 0.0056] | 0.0504 | [0.0428, 0.0590] |

#### B.5 Gate behaviour (test)

| field | value |
|---|---|
| alpha_mean | 0.6220 |
| alpha_std | 0.2148 |
| alpha_pct_prefer_chronos(<0.5) | 0.3379 |
| corr_alpha_chronos_unc | -0.4378 |
| corr_alpha_intermittency | 0.4846 |

#### B.6 Profiling (test, full panel)

| field | value |
|---|---|
| chronos_inference_ms | 35737 |
| retrieval_ms | 42225 |
| gpu_vram_gib | 1.7630 |
| host_ram_peak_gib | 26.4490 |
| backbone_params_updated | 0 |
| backbone_frozen | yes |
| gate_kind | LightGBM GBDT |
| gate_ensemble_leaf_values_approx | 9000 |
| gate_seeds_averaged | 3 |

#### B.7 Full-panel validation comparison (`d_1886-d_1913`, 30,490)

| method | RMSSE | WRMSSE | MASE | WAPE | MAE | pinball |
|---|---|---|---|---|---|---|
| recent_mean | 0.7442 | 1.1014 | 1.0889 | 0.7601 | 1.0539 | 0.5269 |
| seasonal_naive | 0.9756 | 0.9228 | 1.2270 | 0.8889 | 1.2324 | 0.6162 |
| lightgbm | 0.7440 | 0.7106 | 1.0966 | 0.7543 | 1.0458 | 0.5229 |
| chronos2_target | 0.7765 | 1.7568 | 0.9036 | 0.6712 | 0.9306 | 0.2769 |
| retrieval_scaleaware | 0.7617 | 1.2854 | 1.1363 | 0.7646 | 1.0601 | 0.3179 |
| fusion_fixed0.5 | 0.7456 | 1.2791 | 1.0084 | 0.7046 | 0.9769 | 0.2864 |
| ScaleRAG_gated | 0.7371 | 1.1152 | 1.0334 | 0.7103 | 0.9848 | 0.2877 |

**ScaleRAG vs Chronos-2 (val, 30,490)**

| field | value |
|---|---|
| rel. improvement | 0.0508 |
| 95% CI low | 0.0497 |
| 95% CI high | 0.0519 |
| excludes 0 | yes |
| n | 30490 |


**ScaleRAG vs strongest (val, 30,490)**

| field | value |
|---|---|
| rel. improvement | 0.0092 |
| 95% CI low | 0.0078 |
| 95% CI high | 0.0107 |
| excludes 0 | yes |
| n | 30490 |


| slice | n | vs Chronos (rel) | vs Chronos CI | vs strongest (rel) | vs strongest CI |
|---|---|---|---|---|---|
| intermittent(z>0.8) | 11907 | 0.0563 | [0.0545, 0.0583] | 0.0050 | [0.0029, 0.0071] |
| low_volume(<med) | 15233 | 0.0640 | [0.0625, 0.0656] | 0.0019 | [0.0004, 0.0036] |
| reduced_history(<100nz) | 1932 | 0.0358 | [0.0299, 0.0413] | 0.0098 | [0.0046, 0.0148] |
| dense(z<0.3) | 2235 | 0.0013 | [-0.0007, 0.0032] | 0.0362 | [0.0294, 0.0433] |

| field | value |
|---|---|
| alpha_mean | 0.6147 |
| alpha_std | 0.2154 |
| alpha_pct_prefer_chronos(<0.5) | 0.3484 |
| corr_alpha_chronos_unc | -0.4136 |
| corr_alpha_intermittency | 0.4391 |

#### B.8 Favorita reference (frozen)

| method | RMSSE |
|---|---|
| recent_mean | 0.7757 |
| chronos2_target | 0.7287 |
| retrieval_scaleaware | 0.7827 |
| ScaleRAG_gated | 0.7227 |

**ScaleRAG vs Chronos-2 (Favorita, frozen)**

| field | value |
|---|---|
| rel. improvement | 0.0083 |
| 95% CI low | 0.0064 |
| 95% CI high | 0.0103 |
| excludes 0 | yes |
| n | 5000 |

**Strongest baseline (Favorita):** `chronos2_target`

#### B.9 Pre-registered criteria (held-out test verdict)

| criterion | detail | result | met? |
|---|---|---|---|
| C1_ge3pct_over_strongest_ci_excl0 |  —  | test_rmsse_margin=0.0069, test_wrmsse_scalerag=1.2231, test_wrmsse_strongest=0.8663 | NO |
| C2_ge5pct_over_chronos_both_datasets |  —  | m5_test=0.0549, favorita=0.0083 | NO |
| C3_ge7pct_on_sparse_slice_over_strongest |  —  | best_sparse_slice_vs_strongest=0.0093 | NO |
| **Criteria met** | — | 0 | — |



## 14. Internal verification checklist
| check | result |
|---|---|
| All required source files were found | yes - 15/15 listed sources present |
| Source separators (`<!-- BEGIN/END SOURCE: -->`) added | yes - every embedded source |
| Numerical tables were generated from JSON | yes - `scripts/build_tables.py` parses JSON, no retyping |
| Held-out test and validation values remain distinguishable | yes - separate sub-tables A.1-A.9 (val) and B.1-B.9 (test) |
| Subset and full-panel results remain distinguishable | yes - val (M5 1k) tagged separately from val (M5 30,490) |
| Exact and inspired baselines remain labelled correctly | yes - `RAFT_style` / `TSRAG_style_fusion` labelled as inspired in A.1; M5 1k report marks them; protocol-comparability table preserved |
| Chronos-2 remains described as frozen | yes - `backbone_frozen: true`, `backbone_params_updated: 0` (B.6) and method document |
| No LoRA or full TSFM fine-tuning is claimed | yes - no LoRA experiments in any source; explicitly deferred in `paper-outline.md` |
| Graph-routing conclusions remain bounded to the tested settings | yes - bounded to M5 + Favorita, non-learned and learned routers, with controls and CIs |
| No SOTA claim was introduced | yes - packet is explicit that 0/3 pre-registered criteria met; frozen Chronos-2 wins MASE/WAPE/MAE; lightgbm wins WRMSSE |
| No private data, Kaggle data, credentials, or tokens were included | yes - see § 14.1 privacy scan |

## 14.1 Privacy & secret scan (regex sweep)
Kaggle credentials are read from the environment (see `.env.example`) and are never committed or echoed.

## 15. Items NotebookLM must independently verify
NotebookLM is asked to **independently** confirm the following, using the literature sources imported alongside this packet:

1. **Novelty.** Is mean-scaled matching + exact scale restoration + uncertainty-aware gated fusion new versus published retrieval-augmented forecasting work (RAFT, TS-RAG, AME-TS, GNBAN, etc.)?
2. **Correctness of related-work comparisons.** The packet's protocol-comparability table (Section 5.8) declares all prior-work numbers non-comparable; verify this honestly, not by picking the protocol that flatters the method.
3. **Adequacy of baselines.** Are the baselines sufficient for intermittent retail? Is the absence of an exact RAFT/TS-RAG reproduction a publication blocker?
4. **Validity of the statistical analysis.** Paired bootstrap over series, 3 gate seeds, 1 test origin. Is the inference appropriate for the unit of generalisation claimed?
5. **RMSSE vs WRMSSE interpretation.** The packet reports RMSSE as a primary gain metric and WRMSSE as a non-win. Is this framing defensible?
6. **Calibration trade-offs.** Does the 80% coverage regression (0.79 → 0.70) bound the deployment claims appropriately?
7. **Sufficiency of two retail datasets.** Is M5 + Favorita enough to support the controlled-study claim?
8. **Exact external-method reproductions.** Is an exact RAFT / TS-RAG reproduction required before publication, or is the *inspired* reimplementation an acceptable protocol?
9. **Worthiness of the negative relational-routing result.** Is the cross-dataset negative a publishable contribution on its own, or does it need additional evidence (e.g. non-retail data)?
10. **Whether further experiments are essential or merely optional.** Specifically: is the deferred LoRA/adapter efficiency study necessary for publication, or a separate efficiency paper?
