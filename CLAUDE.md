# CLAUDE.md — ScaleRAG-TS (formerly GraphRoute-TS)

Project memory for Claude Code. Keep concise. Procedures live in `.claude/skills/`;
file-scoped rules in `.claude/rules/`.

## Objective (PIVOTED — read this)

Originally **GraphRoute-TS** (relation-aware graph routing for TSFM retrieval). That
central hypothesis was **rigorously rejected** across Phases 6–8 (M5 + Favorita,
non-learned and learned routers, controls, CIs — typed relations add no retrieval
value beyond temporal similarity).

The project is now **ScaleRAG-TS: Scale-Aware Retrieval Augmentation for Time-Series
Foundation Models** — augment a **frozen** Chronos-2 backbone with scale-aware
temporal retrieval + a learned uncertainty-aware **gated fusion**. The cross-dataset
graph-routing negative is a secondary empirical contribution.

## Current status (Phases 1–10 complete)

- Controlled study **finished**; method + hyperparameters **frozen**.
- **Frozen config:** `ScaleRAG_gated` = mean/L2/category-filter/k=20 + scale
  restoration + learned LightGBM gate over {nn-distance, retrieval-disagreement,
  intermittency, log-volume, Chronos-uncertainty, scale-spread}.
- **Frozen verdict (do not re-litigate):** ScaleRAG beats target-only Chronos-2
  **+4.86%** RMSSE on M5 (CI [4.30,5.39]) but only **+0.83%** on denser Favorita
  (regime-dependent); it **ties** the strongest simple baseline (LightGBM/recent-mean)
  and **fails all 3 pre-registered success criteria** → framed as a controlled study.
- **M5 test split `d_1914–d_1941` is CONSUMED** (Phase 10, commit `d42d20e`,
  `M5_TEST_CONSUMED.lock`). The single locked full-panel run **confirmed** the
  frozen verdict on untouched data: ScaleRAG **+5.49%** RMSSE over Chronos-2
  (CI [5.40,5.59]) but **+0.69%** over strongest (lightgbm, <3% bar), loses the
  official **WRMSSE** to lightgbm/seasonal-naive, and is beaten by frozen Chronos-2
  on MAE/WAPE/MASE/pinball/coverage → **0/3 criteria met**. **Do NOT re-run the test**
  (harness `scripts/scalerag_test_final.py` refuses while the lock exists); further
  test-driven tuning is blocked (rules 2, 9, 12).
- **Full-panel scale-up:** `src/graphroute_ts/retrieval_gpu.py` is a GPU batched-exact
  k-NN, verified **bit-identical** to the frozen numpy retriever
  (`scripts/verify_gpu_retrieval.py`, max diff 0.0) — arithmetic acceleration only,
  no method change.
- **Paper artifacts:** `docs/scalerag-ts-method.md`, `docs/scalerag-ts-validation-report.md`,
  `docs/final-experiment-report.md`, `docs/ablation-report.md`,
  `docs/calibration-analysis.md`, `docs/threats-to-validity.md`,
  `docs/paper-outline.md`, `docs/scalerag-final-tables.json`.
- **Phase-10 locked artifacts:** `docs/final-heldout-test-report.md`,
  `docs/scalerag-heldout-test-tables.json`, `docs/final-abstract.md`,
  `reports/scalerag-heldout-{val,test}-30490.json`.
- **HF demo (research software, NOT a scientific contribution):**
  `spaces/scalerag-demo/` (Gradio; references official `amazon/chronos-2`, no weight
  upload; synthetic example data only; no M5/Favorita/Kaggle data or creds).
- **Deferred (do NOT start unless explicitly asked as a *secondary* efficiency study):**
  adapter/LoRA (Phase 9 Part D). Never use LoRA to rescue the retrieval headline.

## Datasets (both ingested, leakage-safe, gitignored)

- **M5** → `data/processed/{entities,dynamic}.parquet` (30,490 series, d_1..d_1941).
- **Favorita** → `data/processed/favorita/{entities,dynamic}.parquet` (5,000-series
  streamed subset, 1,000 days, richer metadata: family/class/perishable/type/
  cluster/city/state). Raw in `data/raw/favorita/` (train.csv ~5 GB, gitignored).
- Kaggle downloads gated behind rules-acceptance; the browser "Download All" +
  drop-into-`data/raw/` path is the reliable workaround (token lists but 403s on
  Kaggle credentials are read from the environment (see `.env.example`) and are never committed or echoed.

## Architecture (`src/graphroute_ts/`)

```
config, reproducibility, cli, leakage         # foundations
data/{m5_schema,synthetic,m5_ingest}, splits  # M5 ingest + chronological splits
metrics, hierarchy                            # MAE/WAPE/MASE/RMSSE/WRMSSE/pinball
features, baselines/{seasonal_naive,lightgbm} # classical baselines (Phase 2-3)
retrieval, retrieval_faiss, retrieval_forecast# temporal retrieval (Phase 4-5, FAISS, scale restoration)
tsfm/chronos2                                 # frozen Chronos-2 wrapper (amazon/chronos-2, bf16)
graph, graphsage, graph_retrieval             # REJECTED graph routing (kept for the negative result)
router                                        # learned candidate-ranking router (Phase 7)
favorita_graph                                # Favorita richer relations
scalerag                                      # gated fusion + paired-bootstrap CI (Phase 9)
```
Key scripts: `scalerag_matrix.py` (M5 full matrix), `scalerag_favorita.py`,
`scalerag_eval.py`, `ingest_favorita.py`, `baseline_run.py`, plus the leakage/data
audit scripts backing the skills.

## Environment

uv-managed, Python 3.11; PyTorch `cu130` (RTX 5070 Ti, sm_120). GPU ~16 GB, but
Chronos-2 uses <2 GB. `uv sync --extra ml --extra retrieval --extra tsfm`.
HF cache is project-local `.hf_cache/` (gitignored). Commands: `make check`
(fmt+lint+type+unit+leakage), `make verify`, `uv run <cmd>`. Activate (fish):
`source .venv/bin/activate.fish`.

## Conventions & discipline

- Python 3.11, `from __future__ import annotations`, type hints, ruff + mypy clean.
- Fail loudly (no bare `except`, no silent defaults). Polars/DuckDB over pandas.
- Every experiment: seeds, versions, config, git commit, runtime, hardware; metrics
  with **dispersion / paired-bootstrap CIs**. Reports → `reports/` (gitignored,
  regenerable); curated results → `docs/`.
- Datasets/weights/secrets NEVER committed. `.env*`, `*.7z`, `*.zip` gitignored.

## NON-NEGOTIABLE RESEARCH RULES

1. **Chronological splits only** (never random/shuffled).
2. **Never use the hidden M5 labels** (`d_1942+`). The `d_1914–1941` test split was
   frozen-then-consumed once in Phase 10 (`M5_TEST_CONSUMED.lock`); **do not evaluate
   it again** or tune anything on its results (test-driven tuning is blocked).
3. **Retrieval horizon guard:** `candidate_end + H < target_forecast_origin`.
4. Distinguish known-future covariates from unavailable future info.
5. **Fit on training/historical origins only** (scalers, indices, utility labels,
   gate training).
6. **No single-run headline numbers** — report seeds + dispersion / bootstrap CIs.
7. **Never silently swap a failed model** for another; report the failure.
8. **No significance claim without a valid test / CI.**
9. **Never alter evaluation code merely to improve results.**
10. Record seeds/versions/config/commit/runtime/hardware for every experiment.
11. **Graph routing is rejected** — do not build further graph/GraphSAGE/KG/relation
    components. Do not implement LoRA except as an explicitly-secondary efficiency
    experiment (never to rescue the headline).
12. **Do not change the pre-registered success criteria, hide negative results, or
    fabricate improvements.** Preserve negatives.
