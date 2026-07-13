---
name: experiment-review
description: Use to audit a completed forecasting experiment for scientific soundness — configuration completeness, reproducibility metadata, leakage, correct metric use, comparable baselines, seed coverage, confidence intervals, and suspiciously strong results. Challenges results rather than rubber-stamping them.
---

# experiment-review

Independently audit an experiment before its numbers are trusted or reported.
Adopt an adversarial stance: assume a result is wrong until the evidence holds.

## Checklist

1. **Configuration completeness** — config file present and validating; all
   hyperparameters captured, nothing hardcoded outside the config.
2. **Reproducibility** — seed, package versions, `uv.lock`, git commit, runtime,
   and hardware recorded (rule 10). Could someone re-run this exactly?
3. **Leakage** — chronological split; `t_r + H < origin`; transforms fit on train
   only; no future covariates; no target in features. Cross-check `/leakage-audit`.
4. **Metric correctness** — right metric for the benchmark, scaling stats from the
   training window, honest aggregation level and weighting.
5. **Comparable baselines** — baselines run on the identical split, data subset,
   and metric. No apples-to-oranges comparison.
6. **Seed coverage & dispersion** — multiple seeds; central tendency + spread.
   No single-run headline number (rule 6).
7. **Statistical claims** — any "significant"/"better" backed by a named test or CI (rule 8).
8. **Suspiciously strong results** — improbably large gains, near-perfect scores,
   or variance collapse → suspect leakage or an evaluation bug; investigate before believing.

Report findings as pass/concern/fail with specifics. Do not edit results.
