# Project Status

**Project:** ScaleRAG-TS (pivoted from GraphRoute-TS — the graph-routing hypothesis
was rejected). **Phases 1–9 complete.** Method + hyperparameters frozen. The M5 test
split `d_1914–d_1941` remains **untouched**.

## Phase summary

| Phase | Scope | Outcome |
|-------|-------|---------|
| 1 | Environment + reproducible workspace | ✅ uv/Python 3.11, Chronos-2 cu130, hooks, skills, agents, 12 smoke tests |
| 2 | Leakage-safe M5 pipeline + classical baselines (synthetic) | ✅ ingest, chronological splits, metrics/WRMSSE, Seasonal Naive + LightGBM |
| 3 | Validate pipeline on **official M5** | ✅ full-panel ingest (59M rows), leakage-audit, LightGBM WRMSSE 0.71 |
| 4 | Frozen Chronos-2 + naive retrieval | ✅/⚠️ Chronos-2 integrated; naive Euclidean retrieval *hurts* (scale mismatch) |
| 5 | Scalable scale-aware retrieval (FAISS) | ✅ scale restoration fixes it; `mean/L2/cat/k20` frozen baseline; full-panel feasible |
| 6 | Typed graph + graph-guided retrieval | ❌ frozen graph/GraphSAGE ≈ random controls |
| 7 | Learned relation-aware router (M5) | ❌ relation ≡ temporal; metadata util-corr 0.003 |
| 8 | Favorita transfer + graph kill test | ❌ rejected cross-dataset (metadata util-corr −0.063); hypothesis falsified |
| 9 | **ScaleRAG-TS** (pivot): scale-aware retrieval + gated fusion | ⚖️ best method; +4.86% over Chronos (M5), +0.83% (Favorita); ties strongest baseline; controlled-study framing |

## Frozen result (do not re-litigate)

- **ScaleRAG_gated** = mean/L2/category/k=20 + scale restoration + learned gate.
- Beats target-only Chronos-2 **+4.86%** RMSSE on M5 (CI [4.30, 5.39]); **+0.83%** on
  Favorita — **regime-dependent** (helps intermittent, marginal on dense).
- **Ties** the strongest simple baseline (M5 LightGBM 0.7175 vs ScaleRAG 0.7173).
- **All 3 pre-registered criteria fail** → controlled study, not a SOTA claim.
- Scale restoration is decisive (ablation: 0.74 → 2.79 without); learned gate > fixed.
- Calibration regresses (cov80 0.69 vs Chronos 0.79) — reported, mitigable post-hoc.
- Cross-dataset graph-routing **negative** is the secondary contribution.

## Deliverables

- Code: full pipeline through Phase 9 (see `CLAUDE.md` architecture); 110 tests,
  ruff + mypy clean; every phase committed + tagged (`phase1..phase9-*`).
- Docs (paper artifacts): `scalerag-ts-method`, `scalerag-ts-validation-report`,
  `final-experiment-report`, `ablation-report`, `calibration-analysis`,
  `threats-to-validity`, `paper-outline`, `scalerag-final-tables.json`, plus the
  per-phase reports (`m5-*`, `*-retrieval-report`, `learned-router-report`,
  `favorita-router-report`, `graph-retrieval-report`).

## Open / next (only if authorized)

- Single **final M5 test-split** confirmation run (method now frozen).
- Optional: full M5-5k/full-panel matrix + ≥3 held-out eval origins (tightens CIs,
  won't change the verdict — see `threats-to-validity.md`).
- Secondary, only if requested: adapter/LoRA efficiency experiment (never to rescue
  the headline).
Kaggle credentials are read from the environment (see `.env.example`) and are never committed or echoed.
