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
