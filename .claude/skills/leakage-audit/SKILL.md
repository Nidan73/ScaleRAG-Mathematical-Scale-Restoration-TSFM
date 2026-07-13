---
name: leakage-audit
description: Use to check temporal-leakage and split integrity — chronological split order, train-only fitting of transforms, the retrieval horizon guard (t_r + H < forecast origin), unavailable future covariates, duplicate/overlapping windows across splits, and target labels leaking into features. Fails loudly when any violation is found.
---

# leakage-audit

Enforce CLAUDE.md research rules 1, 3, 4, 5. **Fail loudly** — a violation must
stop the workflow, never be downgraded to a warning.

## Steps

1. Express the split/retrieval situation as a spec (JSON) or use the demo:
   ```bash
   uv run python scripts/leakage_audit.py --demo               # invalid-split demo
   uv run python scripts/leakage_audit.py --spec <spec>.json    # real check
   ```
   Spec keys: `split{train_end,val_end,test_start}`,
   `retrieval{t_r,horizon,origin}`, `windows{train[],eval[]}`,
   `features{columns,target}`.
2. The script exits non-zero on any violation and writes `reports/leakage-audit-*`.
3. Verify each invariant:
   - chronological order: `train_end < val_end < test_start`
   - retrieval horizon: `t_r + H < target_forecast_origin`
   - no train/eval window overlap (duplicate windows across splits)
   - target column not present among feature columns
   - covariates used past the origin are all known-future
4. Also confirm (by code review) that scalers/encoders/indices were fit on **train
   only**. If any check fails, report the exact violation and stop — do not proceed.

The underlying invariants live in `src/graphroute_ts/leakage.py` and are covered
by `tests/leakage/`.
