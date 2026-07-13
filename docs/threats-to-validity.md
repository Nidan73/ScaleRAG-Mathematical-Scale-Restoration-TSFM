# ScaleRAG-TS — Threats to Validity

Honest accounting of what could undermine the study's conclusions and how we
mitigated each. Conclusions are stated within these bounds.

## Construct / metric validity
- **RMSSE against recent-mean is a punishing bar on intermittent retail.** A large
  share of M5 series are ~68% zeros, where a recent-mean constant is near-optimal
  for squared-error. Our headline ("retrieval helps the TSFM but not the strongest
  simple baseline") is specific to this metric/regime; a different loss (e.g.
  service-level, quantile at high τ, or dollar-weighted WRMSSE) could reorder
  methods. We report MASE/WAPE/MAE/pinball/coverage alongside RMSSE to bound this.
- **Subset WRMSSE is not the official M5 WRMSSE.** The 12-level hierarchy on a
  1k/5k subset is not comparable to the full-panel competition metric; we report
  per-series RMSSE as primary and do not claim leaderboard positions.

## Internal validity (leakage / protocol)
- **Leakage guards** enforce `candidate_end + H < origin`; retriever fitting,
  utility labels, normalisation stats, and gate training use **historical origins
  only**; the M5 test split `d_1914–d_1941` is untouched (verified by tests). This
  is our strongest guarantee.
- **Single eval origin per bootstrap.** Paired bootstrap is over *series* at the
  val origin; multi-origin rolling evaluation (≥3) strengthens generalisation but
  the gate is trained on 2 historical origins, so held-out-origin count is limited.
  Mitigation: baselines are origin-agnostic; the gate's marginal effect is small.
- **Gate label definition** (retrieval-beats-Chronos in RMSE at historical origins)
  is one of several reasonable choices; a different utility target could shift the
  gate slightly (ablations show the gate's effect is ~1% regardless).

## External validity (generalisation)
- **Two datasets, retail only.** M5 (Walmart) and Favorita (Ecuador grocery) are
  both intermittent retail. Conclusions may not transfer to dense, high-frequency,
  or non-retail series. The cross-dataset *negative* (graph routing) is robust
  within retail; we bound it accordingly.
- **Subset sampling.** 1k/5k series are seeded samples of larger panels; results
  are stable across the scales we ran, but full-panel behaviour is confirmed only
  for the frozen temporal retriever (Phase 5), not every ablation.

## Statistical validity
- **Paired bootstrap over series** (2,000 resamples) with per-series relative
  improvements — not seed variance alone. Gate uses 3 seeds. CIs are reported for
  every headline comparison. Multiple-comparison inflation across many ablations is
  possible; we treat ablation CIs as descriptive, not confirmatory.

## Reproduction fidelity
- **RAFT-style and TS-RAG-style are inspired reimplementations**, not exact
  reproductions of released code — labelled as such. Comparisons are only under our
  identical splits/metrics/leakage protocol; we make **no** claim of superiority
  over the original papers (see the protocol-comparability table).

## Calibration
- The gated fusion under-covers (80% coverage 0.69 vs Chronos 0.79). We report this
  and offer point-preserving post-hoc widening; we do not hide the regression.

## Bottom line
The controlled-study conclusions — (1) scale-aware retrieval augments a frozen TSFM
by ~5% but does not beat the strongest simple baseline by the pre-registered
margin; (2) typed-relation graph routing adds nothing across two datasets — hold
**within intermittent retail, under RMSSE, with our leakage-safe protocol**. They
are not asserted beyond those bounds.
