# Phase 11B Preregistration — Native TS-RAG Final Evaluation (FROZEN · NOT EXECUTED)

**Status:** ⛔ **BLOCKED — not executed.** Phase 11A's development decision gate was **not
passed** (4/5; condition 3 — restored fixed fusion improving target-only Chronos-Bolt on MSE
— failed on ETTm2: −0.85%, CI [−1.39, −0.28]). Per the pre-registered protocol and rules 9
and 12, the four Phase-11B test datasets are **not opened** and this plan is **not run**. This
document is retained as the frozen record of what *would* have been executed had the gate
passed, so the negative decision is auditable.

> This file must not be executed while the Phase-11A gate is unmet. Opening ETTh1 / ETTm1 /
> Weather / Electricity now would be test-driven tuning against a failed development result.

## 1. Frozen method (locked in Phase 11A, before any test dataset)

- Method: `scalerag_restored_fixed_fusion` = `(1−w)·Chronos-Bolt + w·restored_retrieval`.
- Backbone: frozen `amazon/chronos-bolt-base` (0 trainable params).
- Config: **scale = mean, top-k = 20, weight = 0.25** (`docs/scalerag-native-frozen-config.json`).
- Retriever: non-neural exact scale-aware k-NN; strictly train-only candidate pool
  (`t_r + H ≤ train_end`); no learned gate; no per-dataset re-tuning.
- Context 512, horizon 64, train-only `StandardScaler` normalised space, MSE/MAE.

## 2. Final test datasets (to open exactly once, never before)

ETTh1, ETTm1, Weather, Electricity — official TS-RAG splits, contexts/horizon/metrics
**unchanged**. Each evaluated **once** with the frozen config; no config touches test twice.

## 3. Pre-registered success criteria (all must hold)

1. **Aggregate improvement:** ≥ **2%** aggregate MSE improvement over official TS-RAG, with a
   paired 95% CI **excluding zero**.
2. **Breadth:** ScaleRAG wins on ≥ **3 of 4** datasets.
3. **No regression:** no dataset degrades > **3%** MSE vs official TS-RAG.
4. **MAE non-inferiority:** MAE improves, or is within **1%** (non-inferior).
5. **Mechanism:** restored retrieval **significantly** beats non-restored on every dataset.
6. **Discipline:** every test config evaluated exactly once; frozen config unchanged.

## 4. Method (had the gate passed)

For each dataset: build the train-only scale-aware index; produce the five protocol methods
(`chronos_bolt_target`, `tsrag_official`, `scalerag_raw_retrieval`,
`scalerag_restored_retrieval`, `scalerag_restored_fixed_fusion`); compute MSE/MAE, per-series
errors, paired-bootstrap 95% CIs (window-level, autocorrelation caveat), wins/losses by
series, and the same measured compute/storage/param table as Phase 11A. Report all five
criteria with an explicit pass/fail per dataset and in aggregate. Preserve negatives.

## 5. Why this is blocked (Phase 11A evidence)

On ETTm2 the restored fixed fusion is **worse** than the frozen backbone (−0.85% MSE) and
**loses to official TS-RAG** (−2.30% MSE), despite the scale-restoration mechanism working
strongly (+85.4% over raw retrieval). A method that cannot beat its own backbone on the
development dataset has no pre-registered basis for consuming the final test datasets. Any
future attempt to open Phase 11B must first pass the Phase-11A gate on the development data —
not by re-tuning against test.
