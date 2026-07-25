# ScaleRAG-TS  (formerly GraphRoute-TS)

**Scale-Aware Retrieval Augmentation for Time-Series Foundation Models.**

Research codebase studying whether scale-aware temporal retrieval + a learned
gated fusion improves a **frozen** Chronos-2 backbone on intermittent-retail
forecasting (M5 + Favorita). The original relation-aware **graph-routing**
hypothesis was rigorously **rejected** cross-dataset (Phases 6–8) and is kept as a
controlled negative result.

> **Status:** Phases 1–11A complete. M5/Favorita controlled study finished and method
> frozen (Phase 9); the M5 test split `d_1914–d_1941` was consumed once and confirmed
> the frozen verdict (Phase 10). A native-TS-RAG feasibility check on ETTm2 (Phase 11A)
> found the same scale-restoration mechanism validated (+85.4% MSE vs. raw retrieval)
> but the fused forecaster did not beat its own frozen backbone — the Phase-11B decision
> gate was **not** passed, so the four final TS-RAG datasets remain unopened. See
> `docs/project-status.md`, `docs/scalerag-native-dev-report.md`,
> `ScaleRAG_Final_Audit_Report.md`, and the research rules in `CLAUDE.md`.
>
> **Note:** this project's folder and GitHub remote were renamed to `ScaleRAG-TS`
> (2026-07-24); the GitHub repository itself may still need renaming to match — see
> `CLAUDE.md` → "Repo identity" before pushing.

## Requirements

- Linux (developed on CachyOS/Arch), NVIDIA GPU with recent driver (RTX 5070 Ti,
  Blackwell/sm_120, CUDA 13.x here).
- [`uv`](https://docs.astral.sh/uv/) for environment management.
- Python 3.11 (provisioned automatically by `uv` — pinned in `.python-version`).

## Install dependencies

```bash
# uv provisions Python 3.11 and creates a project-local .venv from the lockfile.
uv sync --extra ml --extra retrieval --extra tsfm
```

`torch` is pulled from the CUDA 13.0 (`cu130`) index configured in `pyproject.toml`
to match the Blackwell GPU. Heavy optional groups (`graph`, `gpu-retrieval`) are
defined but intentionally **not** installed yet.

## Activate the environment (Fish)

```fish
source .venv/bin/activate.fish
```

<details><summary>bash / zsh</summary>

```bash
source .venv/bin/activate
```
</details>

Or prefix any command with `uv run` (no activation needed), e.g. `uv run pytest`.

## Verify GPU support

```bash
uv run python scripts/environment_check.py      # full pass/fail report
uv run python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

## Fast checks

```bash
make check      # format + lint + type + unit + leakage
make verify     # environment health check
make test       # unit tests
make leakage    # leakage / split-integrity tests
make smoke      # environment smoke tests
```

## Start Jupyter

```bash
make jupyter    # or: uv run jupyter lab
```

## Project skills (Claude Code)

Invoke inside Claude Code:

| Skill | Purpose |
|-------|---------|
| `/environment-check` | Verify the dev environment (read-only). |
| `/data-audit` | Audit a dataset (schema, missing, ordering, leakage hints). |
| `/leakage-audit` | Enforce chronological-split & retrieval-horizon integrity. |
| `/baseline-run` | Run one small **declared** baseline (refuses full-scale runs). |
| `/experiment-review` | Audit an experiment for soundness & reproducibility. |
| `/research-code-review` | Review code for correctness, leakage, reproducibility. |

## M5 pipeline & baselines (Phase 2)

Developed against a deterministic **synthetic** M5 fixture (offline); the same
code path runs on real M5 once the files are in `data/raw/`. See
`docs/m5-data-design.md`, `docs/m5-split-policy.md`, `docs/processed-schema.md`,
and `docs/baseline-report.md`.

```bash
# 1) build + ingest the offline synthetic fixture (idempotent)
uv run python scripts/make_synthetic.py --days 1941 --raw data/raw_synth --processed data/processed

# 2) verify chronological-split integrity
uv run python scripts/leakage_audit.py --spec configs/split_check_val.json

# 3) declare, then run the classical baselines (val split; test held out)
uv run python scripts/baseline_run.py --config configs/baseline_seasonal_naive.yaml --dry-run
uv run python scripts/baseline_run.py --config configs/baseline_seasonal_naive.yaml --confirm
uv run python scripts/baseline_run.py --config configs/baseline_lightgbm.yaml --confirm
```

Real M5 ingestion (once files are present in `data/raw/`) uses the identical
`ingest_m5` path — validate first, then point a config's `processed_dir` at it.

## Layout

See `CLAUDE.md` for the full architecture, environment commands, and the
non-negotiable research rules. Data, checkpoints, artifacts, logs, and secrets are
never committed (`.gitignore`).
