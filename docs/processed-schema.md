# Processed Data Schema

Output of `graphroute_ts.data.m5_ingest.ingest_m5` under `data/processed/`
(gitignored). Two Parquet tables plus an ingestion metadata sidecar.

## `entities.parquet` — stable hierarchy (one row per series)

| Column | Type | Notes |
|--------|------|-------|
| `id` | str | Series id, e.g. `FOODS_1_001_CA_1_evaluation` (primary key) |
| `item_id` | str | Item, e.g. `FOODS_1_001` |
| `dept_id` | str | Department, e.g. `FOODS_1` |
| `cat_id` | str | Category, e.g. `FOODS` |
| `store_id` | str | Store, e.g. `CA_1` |
| `state_id` | str | State, e.g. `CA` |

Rows: one per series (M5 = 30,490; synthetic fixture = 24). Used for the 12-level
WRMSSE hierarchy roll-up.

## `dynamic.parquet` — time-varying panel (one row per series-day)

| Column | Type | Notes |
|--------|------|-------|
| `id` | str | Series id (FK → entities) |
| `d` | str | Day label, `d_1`..`d_1941` |
| `day_idx` | i32 | Integer day index (1..1941) — canonical time unit |
| `date` | str | ISO calendar date |
| `wm_yr_wk` | i64 | M5 week key (joins prices) |
| `sales` | i32 | **Target** — daily units sold |
| `sell_price` | f64 | Weekly price (null before first sale week) |
| `snap` | i8 | SNAP flag for the series' state (0/1) |
| `event_name_1` | str | Calendar event name (nullable) |
| `event_type_1` | str | Calendar event type (nullable) |
| `wday` | i64 | Day of week (1..7) |
| `month` | i64 | Month (1..12) |
| `year` | i64 | Calendar year |

Rows: `n_series × n_days`, sorted by `(id, day_idx)` — a dense panel (enables the
fast matrix reshape in `eval`).

Known-future covariates (usable at/after the forecast origin): `sell_price`,
`snap`, calendar fields. The target `sales` is never a feature.

## `_ingest_meta.json` — provenance / idempotency

`n_days`, `n_series`, `n_rows`, `missing_price_rows`, per-file SHA-256 fingerprint,
and output paths. Re-ingestion is skipped when the fingerprint matches.
