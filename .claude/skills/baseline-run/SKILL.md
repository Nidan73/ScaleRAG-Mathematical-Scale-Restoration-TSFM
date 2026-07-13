---
name: baseline-run
description: Use to run exactly one small, explicitly-declared baseline forecasting configuration. Before executing it prints model, dataset subset, split, metrics, seed, expected output files, and approximate compute demand, and it refuses to launch an undeclared or full-scale training run.
---

# baseline-run

Run a single, small, **declared** baseline. Enforces CLAUDE.md research rule 12.

## Steps

1. Always start with a dry run to print the declaration:
   ```bash
   uv run python scripts/baseline_run.py --config configs/<baseline>.yaml --dry-run
   ```
   The declaration must show: model, dataset + subset size, chronological split,
   metrics, seed, expected output paths, and approximate compute (time/RAM/VRAM).
2. Only after the declaration is reviewed, execute the *same* declared config:
   ```bash
   uv run python scripts/baseline_run.py --config configs/<baseline>.yaml --confirm
   ```
3. The runner refuses subsets larger than the small-run cap and any undeclared
   full-scale run. It will not silently escalate scope.
4. Never launch a long or full-dataset job here. That requires a separate, explicit
   approval showing command, config, expected outputs, and resource demand.

During the setup phase no baseline model exists yet — the runner declares and exits.
