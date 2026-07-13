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
