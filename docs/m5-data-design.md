# M5 Data Design

How GraphRoute-TS ingests and represents the M5 dataset (Phase 2). The pipeline
is offline, idempotent, and leakage-safe; it is developed and tested against a
deterministic synthetic fixture (`graphroute_ts.data.synthetic`) so the identical
code path runs on real M5 once the files are present.

## Source files (public labels only)

Three official M5 files are required in `data/raw/`:

| File | Role | Key columns |
|------|------|-------------|
| `calendar.csv` | day → date, week, calendar events, SNAP | `d`, `date`, `wm_yr_wk`, `wday`, `month`, `year`, `event_name_1/2`, `snap_CA/TX/WI` |
| `sell_prices.csv` | weekly price per store-item | `store_id`, `item_id`, `wm_yr_wk`, `sell_price` |
| `sales_train_evaluation.csv` | daily unit sales, `d_1`..`d_1941` | entity cols + `d_1`..`d_1941` |

We use **`sales_train_evaluation.csv`** (through `d_1941`) — the publicly labelled
horizon. The hidden competition labels (`d_1942`..`d_1969`) are **never** read
(CLAUDE.md rule 2); schema validation *rejects* a sales file whose last day is not
`d_1941`.

## Validation before processing (task 2)

`graphroute_ts.data.m5_schema.validate_all` fails loudly on: a missing file, a
missing required column, an empty file, an all-null `sell_price`, or a wrong last
day. Nothing is processed until validation passes.

## Entities vs dynamics (task 3)

The wide sales table is melted to long form and split into two Parquet artifacts:

- **`entities.parquet` — stable**, one row per series `id`:
  `item_id, dept_id, cat_id, store_id, state_id`. These never change over time.
- **`dynamic.parquet` — time-varying**, one row per `(id, day)`:
  `sales` (target), `sell_price`, `snap` (resolved to the series' state), calendar
  events (`event_name_1`, `event_type_1`), and calendar keys (`day_idx`, `date`,
  `wm_yr_wk`, `wday`, `month`, `year`).

Separating them keeps joins cheap, prevents accidental duplication of static
attributes across 1941 days, and makes the entity hierarchy explicit for the
12-level WRMSSE roll-up.

## Idempotency

`ingest_m5` fingerprints the three inputs (SHA-256 + size) and records it in
`_ingest_meta.json`. Re-running with unchanged inputs is a no-op (`skipped=True`)
unless `force=True`. This makes the pipeline safe to re-invoke in scripts/CI.

## Missing prices

Real M5 items have no listed price before their first sale week. Synthetic data
reproduces this (some early weeks withheld), and ingestion preserves the resulting
null `sell_price` rows (reported as `missing_price_rows`). Feature code treats
missing prices explicitly; weights treat missing price as zero dollar contribution.

## Memory note (real full data)

Real M5 is ~30,490 series × 1,941 days ≈ 59M long rows. The current ingestion is
eager (fine for the synthetic fixture and comfortable in 32 GiB). For the full
dataset, switch the melt/join to Polars streaming (`scan_csv` + `sink_parquet`)
before running unsubset — declared and reviewed per rule 12.
