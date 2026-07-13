# Chronos-2 & Temporal-Retrieval Baselines (Phase 4)

Frozen (inference-only) Chronos-2 as the TSFM backbone, plus simple, model-agnostic
temporal-retrieval baselines. **No GraphSAGE, heterogeneous graphs, hybrid routing,
LoRA, or ARM** (CLAUDE.md rule 11; task 9 — this is deliberately *not* TS-RAG's ARM).

Evaluated on the **validation split `d_1886–d_1913`**; `d_1914–d_1941` untouched.

## Model & checkpoint

- **Backbone:** official `amazon/chronos-2` (HF, Apache-2.0, T5-based, d_model 768),
  via `chronos-forecasting 2.3.1` `Chronos2Pipeline`. Used **frozen**.
- **Checkpoint:** `model.safetensors` **477.9 MB**, cached in project-local
  `.hf_cache/` (gitignored). Loaded **bfloat16** on the RTX 5070 Ti (sm_120).
- **GPU smoke test (task 2):** PASS on tiny synthetic + real-M5 subset —
  peak VRAM **0.26–0.28 GiB**, warm latency ~130 ms/8-series. Blackwell-compatible.

## Methods (task 8)

| Method | What it does |
|--------|--------------|
| `random_knn` | mean of top-k **random** legal retrieved continuations |
| `seasonal_knn` | mean of top-k **same-series seasonal** continuations (heuristic) |
| `euclidean_knn` | mean of top-k **z-normed Euclidean-nearest** continuations |
| `chronos2_target` | frozen Chronos-2, target history only (task 3) |
| `chronos2_{random,seasonal,euclidean}` | Chronos-2 **late-fused** (α=0.5) with retrieved context (task 8/13) |

Retrieval is leakage-safe: candidates are built from **training days only**, and
every returned candidate satisfies `t_r + H < origin` (rule 3). Known-future
covariate support (price, SNAP) is **implemented and guarded**
(`Chronos2Forecaster.forecast_with_covariates` + `assert_no_future_covariates`,
task 4) though not included as a comparison line below.

## Results — declared 100-series subset, val split, seed 42

Context window L=56, top-k=5, fusion α=0.5, DB=25,800 candidates (stride 7).

| Method | WRMSSE† | RMSSE | MASE | WAPE | MAE | Pinball | Retr. ms |
|--------|--------|-------|------|------|-----|---------|----------|
| chronos2_seasonal | 1.3125 | 0.7695 | 0.9729 | 0.7321 | 1.0493 | 0.4169 | — |
| seasonal_knn | 1.3443 | 0.8437 | 1.1319 | 0.8079 | 1.1579 | 0.4628 | 16.7 |
| **chronos2_target** | 1.4713 | **0.7739** | **0.8659** | **0.7013** | **1.0052** | **0.4021** | — |
| chronos2_random | 1.5744 | 0.9886 | 1.4527 | 0.9271 | 1.3288 | 0.5025 | — |
| chronos2_euclidean | 1.7596 | 0.8842 | 1.1896 | 0.8254 | 1.1830 | 0.4799 | — |
| random_knn | 1.9136 | 1.4564 | 2.2546 | 1.2772 | 1.8306 | 0.6975 | 18.0 |
| euclidean_knn | 2.1523 | 1.1427 | 1.6436 | 1.0480 | 1.5021 | 0.6603 | 2231.1 |

† **WRMSSE on a 100-series subset is NOT comparable** to the full-data WRMSSE in
`docs/real-m5-validation-report.md` (aggregate hierarchy levels are computed over
tiny groups and are dominated by a few high-dollar series). Use RMSSE / MASE /
pinball as the stable subset metrics; WRMSSE is shown for ranking within this run.

### Profiling (task 5, 11)

| | |
|---|---|
| GPU VRAM (peak) | **0.68 GiB** (of 16) |
| Peak RAM | 21.6 GiB (dominated by loading the full 59M-row panel, then subsetting) |
| Checkpoint size | 477.9 MB |
| Chronos-2 inference | ~1.08 s (100 series, one batch, bf16) |
| Retrieval latency | seasonal 17 ms · random 18 ms · **euclidean 2.2 s** (brute force) |

## Findings

1. **Zero-shot Chronos-2 is strong per-series.** `chronos2_target` (no training)
   reaches RMSSE **0.774** / MASE 0.866 / best pinball — competitive with the tuned
   LightGBM from Phase 3 (RMSSE 0.744 on full data), which is notable for a frozen
   foundation model. Its weaker *WRMSSE* suggests poorer absolute-**level**
   calibration at aggregate hierarchy levels than a trained model.

2. **Retrieved context ≠ automatic win (task 13).** Only the **seasonal** heuristic
   context marginally helps (WRMSSE 1.31 vs target 1.47; RMSSE ≈ equal). **Random**
   and **Euclidean** contexts *hurt* fusion. `euclidean_knn` is the worst method.

3. **Why naive Euclidean retrieval underperforms (hypothesis):** M5 is ~68%
   intermittent. Matching z-normalised context *shape* across series retrieves
   continuations whose **absolute scale** is mismatched to the query series, so the
   averaged continuation is a poor numerical prior. Same-series seasonal retrieval
   avoids this. This is a genuine negative result that motivates scale-aware,
   relation-aware retrieval — i.e. the graph work in later phases (not started).

4. **Scaling (task 5): profiling did NOT clear full-scale Euclidean.** Brute-force
   Euclidean is O(candidates × queries) — 2.2 s for 100 series would be ~11 min and a
   far larger DB at 30,490 series. Seasonal/random scale fine; Euclidean needs an ANN
   index (FAISS, deferred in Phase 1) before a full-data run. VRAM is a non-issue.

## Reproduce

```bash
uv run python scripts/chronos2_smoke.py                       # GPU compat smoke test
uv run python scripts/retrieval_eval.py --subset 100 --seed 42  # full comparison
```
Machine-readable results + repro fingerprint: `reports/retrieval-eval-subset100.json`.

## Tests (task 12) — all pass

`tests/leakage/test_retrieval.py` (14) covers: illegal retrieval horizons, duplicate/
overlapping windows across splits, candidate-index fitting on training data only,
deterministic top-k, empty/insufficient history, and unavailable future covariates.
Plus `tests/unit/test_retrieval_forecast.py` (pinball, k-NN, fusion). Suite: 82 pass.

## Status (task 15)

Frozen Chronos-2 and temporal-retrieval baselines are reproducible on the declared
subset. **Stopping here — no graph / GraphSAGE / LoRA / ARM work started.**

Open items (recommend before/with the next phase): (a) full-scale Euclidean via
FAISS; (b) scale-aware retrieved-context normalisation; (c) leading-zero / point-
estimator (mean vs median) sensitivity for Chronos-2; (d) a covariate-augmented
Chronos-2 comparison line.
