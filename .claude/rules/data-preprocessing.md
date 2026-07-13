# Rule: Data preprocessing (`scripts/**`, data pipelines)

- Flow is one-directional: `data/raw` → `data/interim` → `data/processed`.
  Raw is read-only; processed is regenerated, never edited in place.
- **Never commit datasets** (raw, interim, or processed) — enforced by `.gitignore`.
- Prefer Polars lazy frames and DuckDB over pandas for scale and memory safety.
  Stream / chunk large files; do not load full M5 into RAM without need.
- Write columnar outputs as Parquet with explicit schema and dtypes.
- **All fitted transforms (scalers, encoders, category maps) are fit on TRAIN only**
  and persisted, then applied to val/test. Never fit on the full dataset.
- Preserve and validate timestamp ordering and frequency; assert monotonic time
  per series. Record row counts and null counts at each stage.
- Never read, print, or log credentials. Dataset access uses env-var-provided
  tokens that are never echoed.
