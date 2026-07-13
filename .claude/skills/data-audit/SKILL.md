---
name: data-audit
description: Use to audit a time-series dataset (Parquet/CSV) before using it — schema, missing values, duplicate rows, timestamp ordering and frequency, zero-value proportion, group cardinalities, split boundaries, and heuristic scans for leakage and unexpected future columns. Produces Markdown + JSON reports and is read-only on the data.
---

# data-audit

Audit a dataset before it enters any pipeline. **Read-only** on the dataset.

## Steps

1. Run the auditor against the target table:
   ```bash
   uv run python scripts/data_audit.py \
     --path data/processed/<file>.parquet \
     --time-col <ts_col> --group-cols <id cols...> --target <target_col>
   ```
2. Reports are written to `reports/data-audit-*.md` and `.json`.
3. Review and report:
   - schema and dtypes; unexpected types
   - missing-value counts per column
   - duplicate rows
   - timestamp min/max, monotonicity, distinct count, inferred frequency
   - zero-value proportion of the target (intermittency)
   - cardinalities of grouping keys
   - any `future_like_columns` — treat as suspected leakage until proven otherwise
4. Flag anything that could indicate leakage or a broken split. Do **not** modify
   the dataset or "fix" it silently; report and propose.

Cross-check split boundaries with `/leakage-audit` when splits are involved.
