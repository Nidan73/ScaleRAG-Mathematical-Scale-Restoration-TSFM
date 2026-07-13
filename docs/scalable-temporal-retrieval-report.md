# Scalable & Scale-Aware Temporal Retrieval (Phase 5)

The strongest **fair, non-graph** retrieval baseline before graph development.
No heterogeneous graphs, GraphSAGE, graph routing, LoRA, or ARM. Evaluated on the
**validation split `d_1886–d_1913`**; `d_1914–d_1941` untouched. Selection is by
**RMSSE on validation only**. Negative results are preserved.

## What changed vs Phase 4

Phase 4 found naive cross-series Euclidean retrieval *hurt* (scale mismatch on
68%-intermittent M5). Phase 5 addresses that directly:
- **FAISS-CPU** exact search (`IndexFlatL2` / `IndexFlatIP`) — verified identical
  top-k to brute force (task 2), but fast/scalable.
- **Scale strategies** (raw / z-norm / mean / RMS) on context windows + **scale
  restoration** of retrieved continuations back to the query's level.
- **Metadata filters** (same store / category / department, seasonal position).

## Two bugs caught and fixed (integrity)

1. **Silent seasonal fallback.** With `stride=7`, every candidate sits on weekly
   phase 0, so the seasonal-position filter matched nothing and silently fell back
   to a constant forecast — which then looked like the "best" method. Fixed with
   `stride=2` (coprime to 7 → all phases), **explicit labelled naive baselines**,
   and **fallback counting** (0 fallbacks in the final run). The earlier "seasonal
   wins" was an artifact and is **not** reported as a result.
2. FAISS `IDSelector`/`SearchParametersFlat` is not exposed in faiss-cpu 1.14.3 →
   filtered search uses exact numpy over the (small) restricted pool; global search
   uses batched FAISS.

## Results — 1,000-series subset, val split, seed 42

Context L=56, stride=2 (901,000 candidates), scale restoration on unless noted.
Ranked by RMSSE (lower better); `fb` = empty-retrieval fallbacks.

| Config | RMSSE | MASE | WAPE | MAE | Pinball | fb |
|--------|-------|------|------|-----|---------|----|
| naive:recent_mean | **0.7221** | 1.0146 | 0.7416 | 1.0530 | 0.5265 | 0 |
| **knn:mean/l2/cat_id/k20** | 0.7264 | 1.0216 | **0.7145** | **1.0145** | **0.3894** | 0 |
| knn:mean/l2/cat_id/k10 | 0.7339 | 1.0151 | 0.7202 | 1.0227 | 0.3995 | 0 |
| knn:mean/l2/dept_id/k5 | 0.7546 | 1.0270 | 0.7309 | 1.0378 | 0.4188 | 0 |
| knn:mean/l2/store_id/k5 | 0.7547 | 1.0382 | 0.7298 | 1.0363 | 0.4193 | 0 |
| knn:mean/l2/seasonal/k5 | 0.7550 | 1.0341 | 0.7292 | 1.0355 | 0.4207 | 0 |
| knn:mean/l2/global/k5 | 0.7599 | 1.0466 | 0.7337 | 1.0418 | 0.4209 | 0 |
| knn:raw/l2/global/k5 | 0.7952 | 1.0323 | 0.7378 | 1.0476 | 0.4141 | 0 |
| knn:znorm/l2/global/k5 | 0.8582 | 1.1817 | 0.8187 | 1.1626 | 0.4428 | 0 |
| naive:seasonal7 | 0.9518 | 1.1299 | 0.8451 | 1.2000 | 0.6000 | 0 |
| knn:raw/cosine/global/k5 | 2.3560 | 3.3794 | 2.7290 | 3.8752 | 1.2260 | 0 |
| **knn:mean/l2/cat_id/k5 / NO-restore** | **2.6873** | 4.0799 | 2.9115 | 4.1343 | 1.3168 | 0 |

### Findings

1. **Scale restoration is decisive.** Same config with vs without restoration:
   **0.7546 → 2.6873** RMSSE (3.6× worse). This is the core Phase 5 result — it
   converts Phase 4's failing retrieval into a competitive one.
2. **Mean-scaling** is the best scale strategy; z-norm and RMS are worse; cosine on
   **raw** windows is catastrophic (2.36). Metric `l2` beats cosine here.
3. **Metadata filtering helps** modestly and consistently (cat/dept/store/seasonal
   all beat global). **Category (`cat_id`)** is best.
4. **Larger k helps**: k20 > k10 > k5 > k3 > k1 (averaging suppresses intermittent noise).
5. **Honest headline (preserved).** The **recent-mean constant (0.7221)** ties the
   best retrieval on RMSSE. But `mean/l2/cat_id/k20` **beats it on pinball
   (0.389 vs 0.527), WAPE, and MAE** — i.e. retrieval gives materially better
   point and probabilistic forecasts, at a near-identical RMSSE. Retrieval is
   competitive-to-better, but does **not** dominate a trivial baseline on RMSSE —
   a nuanced result that motivates the relation-aware graph work.

## Scaling (task 3) — scalable global config `mean/l2/global/k20`

The strongest config (`cat_id`) uses per-query filtered search; the near-equal
**global** variant (`mean/l2/global/k20` + restoration) batches via FAISS and
scales. Larger panels use a coarser stride (7) to keep the candidate pool
tractable. Exact global search is O(queries × candidates) but well within reach on
CPU (16 threads, BLAS): measured throughput ≈ **2.4×10⁹ candidate-pairs/s**.

| Panel (series) | Stride | Candidates | Index build | Retrieval (all series) | RMSSE | Peak RAM |
|---------------:|-------:|-----------:|------------:|-----------------------:|------:|---------:|
| 1,000  | 7 | 258,000   | 0.49 s | 0.35 s | 0.7378 | 22.9 GiB |
| 5,000  | 7 | 1,290,000 | 2.23 s | 2.67 s | 0.7580 | 22.9 GiB |
| **30,490 (full)** | 7 | 7,866,420 | **22 s** | **99 s** | **0.7741** | 24.3 GiB |

**Full-scale exact global retrieval is feasible** — ~2 minutes total, 24.3 GiB RAM.
(An earlier off-the-cuff "~2 hours" estimate was an arithmetic error, corrected by
direct measurement.) RAM is dominated by loading the full 59M-row panel (~20 GiB),
independent of the retrieval subset; VRAM = 0 (retrieval is CPU-only). Retrieval
RMSSE drifts up slightly with scale (0.738 → 0.758 → 0.774) as the global pool
grows more diverse — where metadata filtering (`cat_id`) would help but needs an
ANN index or per-group sub-indices to stay cheap at full scale (future work).

## Strongest frozen baseline (task 12, 15)

- **Accuracy-optimal (small/medium panels):** `mean/l2/cat_id/k20` + scale
  restoration — RMSSE 0.7264, best WAPE/MAE/pinball.
- **Scalable (full panel):** `mean/l2/global/k20` + scale restoration.

Both are **frozen** as the non-graph retrieval baseline to beat. The graph phase
must improve on these on validation before it is worthwhile.

## Reproduce & tests

```bash
uv run python scripts/scalable_retrieval_eval.py --subset 1000 --seed 42
uv run python scripts/retrieval_scaling_probe.py
```
Tests (task 13, `tests/unit/test_faiss_retrieval.py`): FAISS==brute-force,
scale restoration, metadata-filtered candidate sets, deterministic retrieval,
cosine, seasonal-phase filtering. Unavailable-future-covariate guard:
`tests/leakage/test_retrieval.py`. Full suite green.

Reports: `reports/scalable-retrieval-subset1000.json`.
