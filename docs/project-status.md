# Project Status

**Phase:** 1 — environment & reproducible workspace setup.
**Scope reminder:** no datasets, no model implementation, no training this phase.

## Done

- [x] Phase 1 — machine & repo audit (`docs/environment-audit.md`).
- [x] Phase 2 — repository structure created; git initialized (branch `main`);
      `.gitignore` excludes secrets, data, checkpoints, artifacts, caches, `.venv`,
      local Claude/MCP settings.
- [x] Phase 3 — `pyproject.toml` with grouped deps; Python pinned to 3.11; PyTorch
      pinned to the verified `cu130` index (Blackwell/sm_120). **Env not yet built
      (blocked on `uv`).**
- [x] Phase 4 — `CLAUDE.md` with the 12 non-negotiable research rules; 5 file-scoped
      rules under `.claude/rules/`.
- [x] Phase 5 — 6 skills under `.claude/skills/` with backing scripts.
- [x] Phase 6 — 4 subagents under `.claude/agents/`.
- [x] Phase 7 — `.mcp.json` (GitHub hosted server, env-var auth); `docs/mcp-setup.md`.
- [x] Phase 8 — hook scripts + `.claude/settings.json` (pre-bash guard, post-edit
      format, post-task checks, session-start, notification).
- [x] Phase 9 — permissions in `.claude/settings.json`; secrets denied; machine-local
      `.claude/settings.local.json` (untracked).

- [x] Phase 3 — `uv sync` built `.venv` (Python 3.11.15); `uv.lock` committed-ready.
- [x] Phase 10 — all 12 smoke tests pass (see below).

## Blocked / pending (user actions)

- [ ] Set `GITHUB_MCP_PAT` and approve the GitHub MCP server (`claude mcp list`
      shows it *pending approval / missing env var* — by design).
- [ ] Fix the malformed global git email (see environment audit).
- [ ] (Optional) Make the first git commit — not done automatically.

## Smoke-test results — 12/12 PASS

Verified via `uv run pytest -q` (33 passed) plus the two script-level checks:

| # | Check | Result |
|---|-------|--------|
| 1 | package imports | ✅ |
| 2 | PyTorch imports (`2.13.0+cu130`) | ✅ |
| 3 | CUDA visible (runtime 13.0, RTX 5070 Ti sm_120) | ✅ |
| 4 | tensor → GPU → back + matmul | ✅ |
| 5 | mixed-precision reported (bf16 supported) | ✅ |
| 6 | Polars Parquet write/read | ✅ |
| 7 | DuckDB query over Parquet | ✅ |
| 8 | LightGBM tiny fit | ✅ |
| 9 | config loader | ✅ |
| 10 | pytest / ruff / mypy execute | ✅ |
| 11 | leakage audit catches invalid split (`--demo` → exit 2) | ✅ |
| 12 | pre-bash guard blocks `rm -rf /` (nothing executed → exit 2) | ✅ |

Checks: `ruff format` clean · `ruff check` clean · `mypy` clean · 33 tests pass.

## Phase 2 — M5 pipeline & classical baselines (DONE, synthetic data)

Implemented the leakage-safe M5 pipeline and the two classical baselines. Built
and validated against a deterministic synthetic M5-shaped fixture (24 series);
the real M5 has **not** been downloaded (declaration pending user approval).

- [x] Idempotent M5 ingestion (Polars/PyArrow → Parquet); schema validation.
- [x] Entities vs dynamics separation.
- [x] Chronological rolling splits through d_1941 (val d_1886–1913, test d_1914–1941,
      + val_m1/val_m2 earlier origins).
- [x] Train-only fitted transforms; leakage guard test on horizon corruption.
- [x] Metrics: MAE, WAPE, MASE, RMSSE, official-style WRMSSE (12 levels).
- [x] Baselines: Seasonal Naive + LightGBM (Tweedie), reproducible over seeds.
- [x] Docs: `m5-data-design.md`, `m5-split-policy.md`, `processed-schema.md`,
      `baseline-report.md`; baseline configs; reproducible CLI commands.
- [x] 61 tests pass (unit + leakage + integration); ruff + mypy clean.
- [x] End-to-end declared smoke run passes (WRMSSE: naive 0.980 vs LightGBM 0.670±0.003).

**Out of scope / not started (rule 11):** Chronos-2/TSFM, retrieval, graphs, LoRA,
ARM, neural training. Real M5 download awaits approval (see `docs/m5-data-design.md`).

## Next coding task (after real-data approval)

Run the identical pipeline on **real M5** (download declared, then ingest with
streaming for the full 30,490-series panel), reproduce the baselines on the real
`val` split, and record them as the reference numbers before any TSFM work begins.
