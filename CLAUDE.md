# CLAUDE.md — GraphRoute-TS

Project memory for Claude Code. Keep this concise. Detailed procedures live in
`.claude/skills/`; file-scoped rules live in `.claude/rules/`.

## Objective

**GraphRoute-TS: Relation-Aware Context Retrieval for Parameter-Efficient
Time-Series Foundation Models.** Investigate whether relation-aware retrieval of
supporting context (via a learned graph router) improves parameter-efficient
adaptation of time-series foundation models (TSFMs) on forecasting benchmarks
(primarily M5), versus strong classical and TSFM baselines.

## Approved research scope (current phase)

Environment, reproducibility, and evaluation scaffolding **only**. The following
are explicitly **out of scope until the baseline pipeline is verified**:
GraphSAGE, LoRA/PEFT adapters, the ARM component, and the hybrid router. Do not
download full datasets, train models, or launch long experiments yet.

## Repository architecture

```
src/graphroute_ts/   Python package (config, reproducibility, cli; models later)
configs/             YAML experiment configs (validated by config.py)
data/{raw,interim,processed}/   Datasets — NEVER committed
tests/{unit,integration,leakage}/   Leakage tests are first-class
scripts/             CLI utilities; scripts/hooks/ holds Claude Code hooks
docs/                Audit, setup, reproducibility, MCP, status docs
artifacts/ logs/ reports/   Run outputs — NEVER committed
.claude/             rules/, skills/, agents/, settings.json
```

## Environment commands

Package/env manager is **uv**. Python is pinned to 3.11 (`.python-version`).
PyTorch comes from the `cu130` index (Blackwell / RTX 5070 Ti, sm_120).

| Task | Command |
|------|---------|
| Install / sync env | `uv sync --extra ml --extra retrieval --extra tsfm` |
| Verify environment | `make verify` (or `/environment-check`) |
| Format | `make fmt` |
| Lint | `make lint` |
| Type check | `make type` |
| Unit tests | `make test` |
| Leakage tests | `make leakage` |
| All fast checks | `make check` |
| Run any tool | `uv run <cmd>` |

Activate in Fish: `source .venv/bin/activate.fish`.

## Coding conventions

- Python 3.11, `from __future__ import annotations`, full type hints on public APIs.
- Ruff for format + lint; mypy for types. No committed code that fails `make check`.
- Prefer Polars / DuckDB / PyArrow for data; pandas only when an API requires it.
- Fail loudly. No bare `except:`; no silently swallowed exceptions; no silent defaults.
- Small, composable functions; keep modules dependency-light (config/repro import without torch).

## Testing expectations

- Every data/eval component ships unit tests. Temporal-leakage tests are mandatory
  and live in `tests/leakage/`.
- `make check` (format, lint, types, unit + leakage) must pass before any commit.
- No network or dataset downloads inside the fast test suite.

## Data-handling rules

- Datasets are never committed (enforced by `.gitignore`). Only code + configs are.
- Raw → interim → processed is one-directional; processed never edited in place.
- Secrets (`.env`, Kaggle/HF tokens, keys) are never read, printed, or committed.

## Reproducibility rules

- Record for every run: seeds, package versions, config file, git commit, runtime,
  hardware. Use `graphroute_ts.reproducibility.RunContext` + `set_seed`.
- `uv.lock` is committed and authoritative. Do not hand-edit it.

## Experiment-recording requirements

Every experiment writes a config + a run record (seed, versions, git commit,
hardware, metrics with dispersion). No result is reported from a single
unexplained run (see rule 6 below).

## Prohibited shortcuts

Never bypass leakage checks, never edit evaluation code to improve a number,
never swap a failing model for a different one silently, never fabricate
significance, never commit data/weights/secrets.

---

## NON-NEGOTIABLE RESEARCH RULES

1. **Chronological splits only.** Never random or shuffled splits for forecasting.
2. **Never use the hidden M5 competition evaluation labels.**
3. **Retrieval horizon guard.** For a retrieved context ending at `t_r` with
   horizon `H`: require `t_r + H < target_forecast_origin`.
4. **Distinguish known-future covariates from unavailable future information.**
   Only genuinely known-ahead covariates may enter the forecast for time > origin.
5. **Fit on training data only.** Scalers, encoders, retrieval indices, and feature
   transforms are fit on train, then applied to val/test.
6. **Never report metrics from a single unexplained run.** Report seeds + dispersion.
7. **Never silently replace a failed model with another implementation.** Report the failure.
8. **Never claim statistical significance without a valid test or confidence interval.**
9. **Never alter evaluation code merely to improve results.**
10. **Record seeds, package versions, config files, git commit, runtime, and hardware
    for every experiment.**
11. **Do not begin GraphSAGE, LoRA, ARM, or hybrid-router work until the baseline
    pipeline is verified.**
12. **Do not launch long training jobs** without first showing the command,
    configuration, expected outputs, and approximate resource demand.
