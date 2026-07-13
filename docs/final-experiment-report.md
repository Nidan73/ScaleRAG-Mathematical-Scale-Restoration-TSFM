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
