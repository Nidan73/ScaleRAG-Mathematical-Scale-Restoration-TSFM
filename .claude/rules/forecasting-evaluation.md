# Rule: Forecasting evaluation (`src/graphroute_ts/eval/**`, eval scripts)

- **Chronological splits only.** Train/val/test are separated by time boundaries,
  never randomly. `t_r + H < target_forecast_origin` for any retrieved context.
- **Never touch the hidden M5 evaluation labels.** Use the public split conventions.
- Metrics must match the benchmark (e.g. M5: WRMSSE and its scaling weights). Compute
  scaling statistics from the training window only.
- Distinguish known-future covariates (calendar, prices announced ahead) from
  information unavailable at the forecast origin. Never leak future targets.
- Report central tendency **and dispersion** across ≥ multiple seeds. A single-run
  number is not a result.
- Statistical claims require a named test or confidence interval. No informal "better".
- **Evaluation code is not tuned to improve scores.** Changing eval logic requires an
  explicit, reviewed reason recorded in the experiment log.
- Aggregation must be honest: state the level (per-series vs pooled) and the weighting.
