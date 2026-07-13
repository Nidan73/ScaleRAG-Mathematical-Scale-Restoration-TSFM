---
name: research-code-review
description: Use to review research code specifically for numerical correctness, temporal leakage, reproducibility, memory usage, unnecessary complexity, silent exception handling, and misleading metric aggregation. A focused scientific-correctness review, not a general style pass.
---

# research-code-review

Review code for the failure modes that silently corrupt research results.

## Focus areas

1. **Numerical correctness** — off-by-one in windows/horizons, wrong axis in
   reductions, unsafe float compares, NaN/inf handling, integer overflow, unit mismatches.
2. **Temporal leakage** — future data reaching the model/features; transforms fit
   on val/test; retrieval violating `t_r + H < origin`; shuffling time. Cross-check
   `.claude/rules/forecasting-evaluation.md` and `/leakage-audit`.
3. **Reproducibility** — unseeded randomness, nondeterministic ordering, uncaptured
   config/versions, hidden global state, time/host-dependent behavior.
4. **Memory usage** — full-dataset loads where streaming/lazy would do, needless
   copies, unbounded caches, retained graphs/tensors, GPU OOM risks (16 GiB VRAM).
5. **Unnecessary complexity** — over-abstraction, dead code, premature generality
   that obscures correctness.
6. **Silent exception handling** — bare `except`, `except: pass`, swallowed errors,
   silent fallbacks/defaults that mask failures (rule 7).
7. **Misleading metric aggregation** — wrong pooling level, unweighted means passed
   off as weighted, mixing per-series and global stats, cherry-picked subsets.

Report concrete file:line findings with severity. Prefer failing loudly over
clever recovery. Do not silently rewrite; propose changes for review.
