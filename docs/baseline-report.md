# Baseline Report (Phase 2)

Classical baselines on the M5 `val` split (forecast **d_1886–d_1913**, H=28).
Reported with dispersion across seeds (CLAUDE.md rule 6). The `test` split
(d_1914–d_1941) is held out and untouched.

> **Data:** these numbers are on the **synthetic M5-shaped fixture** (24 series),
> not real M5 — the real dataset has not been downloaded (see the download
> declaration in `docs/m5-data-design.md` / the session log). The synthetic data
> is deterministic but random-ish, so absolute values are only meaningful for
> pipeline validation and relative comparison, not as M5 leaderboard numbers.

## Results (val split, 24 series)

| Model | Seeds | MAE | WAPE | MASE | RMSSE | **WRMSSE** |
|-------|-------|-----|------|------|-------|------------|
| Seasonal Naive (s=7) | 1 (deterministic) | 1.461 | 1.164 | 0.990 | 0.971 | **0.980** |
| LightGBM (tweedie) | 3 (42,43,44) | 1.166 ±0.003 | 0.928 ±0.002 | 0.816 ±0.001 | 0.712 ±0.001 | **0.670 ±0.003** |

**Reading it:** LightGBM improves WRMSSE from 0.980 → 0.670 over Seasonal Naive,
with tight seed dispersion (±0.003). MASE/RMSSE near 1.0 for Seasonal Naive is
expected (it *is* essentially the naive scale). Machine-readable per-run reports:
`reports/baseline-seasonal_naive_smoke.json`, `reports/baseline-lightgbm_smoke.json`
(each includes the 12-level WRMSSE breakdown and a reproducibility fingerprint).

## Reproduce

```bash
# 0) environment
make verify

# 1) build the offline fixture and ingest it (idempotent)
uv run python scripts/make_synthetic.py --days 1941 --raw data/raw_synth --processed data/processed

# 2) verify split integrity (leakage-audit skill)
uv run python scripts/leakage_audit.py --spec configs/split_check_val.json

# 3) declare, then run the baselines (baseline-run skill)
uv run python scripts/baseline_run.py --config configs/baseline_seasonal_naive.yaml --dry-run
uv run python scripts/baseline_run.py --config configs/baseline_seasonal_naive.yaml --confirm
uv run python scripts/baseline_run.py --config configs/baseline_lightgbm.yaml --confirm
```

## Method notes

- **Seasonal Naive** repeats the last observed weekly cycle across the horizon —
  leakage-safe by construction (training data only).
- **LightGBM** uses leakage-safe features with lags **≥ horizon** (28), so one
  model predicts all 28 days directly with no recursion and no future leakage;
  price/series statistics are fit on training days only. Objective: Tweedie
  (intermittent demand). Predictions clipped at 0.
- **WRMSSE** is official-style: 12 aggregation levels, per-level dollar-sales
  weights from the last 28 training days, each level contributing 1/12.
