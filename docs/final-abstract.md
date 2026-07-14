# ScaleRAG-TS — Final Abstract & Contributions (locked test)

All numbers below are from the **frozen** method on the **single locked held-out
run** (M5 test `d_1914–d_1941`, full 30,490-series panel) and the frozen
validation/Favorita study. Nothing was tuned on the test results.

## Abstract

Retrieval-augmented forecasting promises to improve time-series foundation models
(TSFMs) on hard, sparse regimes, and typed-relation "graph routing" promises to make
retrieval smarter. We test both claims under a pre-registered, leakage-controlled
protocol on two intermittent-retail panels (M5, Favorita), augmenting a **frozen**
Chronos-2 backbone. Our method, **ScaleRAG-TS**, adds scale-aware temporal retrieval
— mean-normalised matching with **exact scale restoration** of retrieved
continuations — and a small **uncertainty-aware learned gate** that blends the TSFM
and retrieval per series. Scale restoration is decisive: it turns naive retrieval
(which *hurts*) into a useful signal, and on the reserved M5 test split ScaleRAG
improves the backbone by **+5.49% RMSSE** (95% CI [+5.40, +5.59]), confirming
validation (+5.08%). However, the gain is **metric- and regime-dependent**: it does
not beat the strongest simple baseline (LightGBM) by the pre-registered 3% margin
(+0.69% RMSSE), does **not** win the official dollar-weighted **WRMSSE** (LightGBM
0.866 and Seasonal-Naive 0.870 beat ScaleRAG's 1.223), and reverses on
absolute-error and probabilistic metrics, where the **frozen Chronos-2 alone is
best** (MASE, WAPE, MAE, pinball, coverage). Separately, across both datasets — with
non-learned and learned routers, shuffled-relation and random-label controls, and
paired-bootstrap CIs — **typed-relation graph routing adds no retrieval value**
beyond temporal/statistical similarity (metadata-utility correlation 0.003 on M5,
−0.063 on Favorita). All three pre-registered success criteria fail (0/3) on
held-out data. We therefore report a **controlled study** rather than a
state-of-the-art claim: scale-aware retrieval measurably helps a frozen TSFM on
squared error in sparse regimes, relational metadata does not help retrieval, and on
intermittent retail strong classical baselines remain hard to beat — a cautionary
result for TSFM benchmarking.

## Final contribution list

1. **Scale-aware retrieval augmentation of a frozen TSFM.** Mean-scaled matching +
   **exact scale restoration** converts naive retrieval (which increases RMSSE) into
   a useful augmentation, improving frozen Chronos-2 by **+5.49% RMSSE on the
   held-out M5 test** (CI [+5.40, +5.59]); restoration is the decisive component
   (ablation 0.74 → 2.79 RMSSE without it).
2. **Learned uncertainty-aware gated fusion.** A lightweight gate over retrieval
   confidence/disagreement, intermittency, demand level, and Chronos uncertainty
   routes each series between the backbone and retrieval; it beats fixed-weight
   fusion and is the best method on RMSSE, while adding **0 trainable backbone
   parameters**.
3. **Honest metric- and regime-dependence (primary negative).** The RMSSE gain does
   **not** transfer: ScaleRAG loses to strong simple baselines on **WRMSSE** and to
   the frozen backbone on **MAE/WAPE/MASE/pinball/coverage**; it helps sparse series
   vs the backbone (+6–7%) but only *ties* the strongest baseline there. **0/3**
   pre-registered criteria met on untouched test data.
4. **Cross-dataset relational-metadata negative.** Typed-relation graph routing adds
   no predictive retrieval value beyond temporal similarity on either M5 or Favorita,
   under learned/non-learned routers and shuffle/random controls with CIs.
5. **Benchmarking caution.** On intermittent-retail RMSSE, recent-mean and LightGBM
   are punishing baselines and win the official WRMSSE; a frozen TSFM + retrieval
   improves the model but not the field's strongest simple methods by a
   pre-registered margin.

## Claims we explicitly do NOT make

- **No SOTA / leaderboard claim.** On the full-panel official **WRMSSE**, ScaleRAG
  does not win (LightGBM/Seasonal-Naive are better); the headline gain is
  RMSSE-specific.
- **No general point-accuracy win.** Frozen Chronos-2 is better on MASE/WAPE/MAE and
  is the best-calibrated forecaster (ScaleRAG under-covers).
- **No superiority over the RAFT / TS-RAG originals** — only *inspired*
  reimplementations under our identical protocol.
- **No relational/graph contribution** — that hypothesis was falsified.

## Limitations (summary; full accounting in `threats-to-validity.md`)

- Two intermittent-retail datasets only; RMSSE-favourable framing; a single held-out
  test origin; gate trained on two historical origins; inspired (not exact) RAFT/
  TS-RAG reimplementations; gated fusion under-covers. The GPU retriever used for the
  full-panel run is verified bit-identical to the frozen numpy retriever.
