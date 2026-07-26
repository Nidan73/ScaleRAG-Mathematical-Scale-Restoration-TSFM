# ScaleRAG-TS — Final Audit Report (through Phase 11A)

**Purpose.** An objective, evidence-based summary of the ScaleRAG-TS research programme,
prepared for external evaluation of its readiness for an Applied-AI journal. All numeric
claims are traceable to committed artifacts (`docs/`, `reports/`, git history); the two
items that could **not** be located in committed artifacts during this audit are marked
explicitly as *unverified*.

**Audit provenance note.** Independently verified from the repository: the graph-routing
negative result, the scale-restoration mechanism and its ablation, the full-panel M5
controlled study, and all Phase-11A results. **Not located in any retained artifact** — a
LightGBM data-leakage discovery and a nested-rolling correction (Section 2, "Attempt 11/12"):

- *Committed artifacts* (docs, reports, 12-commit git log): no record; the log describes
  LightGBM as leakage-safe by construction.
- *Session transcripts*: all four retained session logs
  (the local session transcripts) were parsed and searched for
  `leakage`, `leaking/leaked`, `look-ahead`, `backward rolling`, `nested`, `walk-forward`,
  `refit-per-origin`, and LightGBM-adjacent leakage language. **No matching event was found.**
  Every hit was unrelated: the method-doc baseline listing, the retriever's own leakage
  *unit test* (`test_retrieve_raises_on_leaking_origin`), a `RollingSplit` import, and a
  shell-`nohup` nesting note. The only occurrences of the phrases "LightGBM leakage" and
  "nested rolling" are in the current session's discussion of *this* report.
- *Coverage gap*: the retained transcripts begin **2026-07-14 06:23 UTC**, whereas the
  LightGBM baselines were built in Phase 2–3, committed **2026-07-13** (`a291626`). The
  session(s) in which such a discovery would most plausibly have occurred **predate all
  retained transcripts** and are not available for citation.

Because no citable turn exists, these two items remain **unverified** and are retained only
at the project lead's direction; they must be sourced (a retained log or commit) before
appearing in a submission. No metrics are attributed to them.

---

## 1. Project Objective

**Original goal.** Build a *zero-shot, retrieval-augmented* forecaster: augment a **frozen**
time-series foundation model (TSFM) with retrieved historical analogues, without fine-tuning
the backbone and without leaking future information into its context. The founding hypothesis
(the project was named **GraphRoute-TS**) was that **typed relational structure** — a
knowledge-graph / GraphSAGE router over series relations — would select more useful retrieval
candidates than temporal similarity alone.

**Backbones.**
- **Chronos-2** (`amazon/chronos-2`, bf16, frozen) — backbone for the retail panels (M5,
  Favorita). Used strictly frozen; retrieved *future* values never enter its input.
- **Chronos-Bolt-base** (T5-based quantile forecaster; 205.29 M parameters, **0 trainable**
  when frozen) — the backbone of the official **TS-RAG** benchmark, used for the Phase-11A
  native-protocol study on ETTm2. Verified frozen: the 269 shared backbone tensors in the
  TS-RAG checkpoint are **bit-identical** to the public base weights (max abs diff 0.0); only
  the Adaptive Retrieval Mixer (ARM, 4.78 M params) is trained.

**Evaluation discipline (enforced throughout).** Chronological splits only; retrieval horizon
guard `candidate_end + H < target_forecast_origin`; all fitted transforms (scalers, indices,
utility labels, gates) fit on historical origins only; paired-bootstrap 95% CIs; no
single-run headline numbers; the M5 test split `d_1914–d_1941` reserved and consumed exactly
once.

---

## 2. Chronological Research History

The committed history comprises 12 milestones (git `5b9b0c6` → `623a036`) plus the Phase-11A
work of the current session. The table follows the **evidenced commit order**; where the
project lead's "Attempt N" framing diverges from the committed order, the divergence is noted.

| Phase (commit) | Content | Outcome |
|---|---|---|
| 1 (`5b9b0c6`) | Reproducible workspace, config/leakage foundations | scaffolding |
| 2–3 (`a291626`, `9c00ee9`) | Leakage-safe M5 ingest; classical baselines (seasonal-naive, **LightGBM** with lags ≥ horizon, recent-mean); validated on official M5 | baselines pass leakage audits |
| 4–5 (`095be86`, `f58f60e`) | Frozen Chronos-2 wrapper; **temporal retrieval**; **scale-aware FAISS** retrieval | **core mechanism discovered** (Section 3) |
| 6 (`7888e44`) | Heterogeneous graph retrieval + shuffled-edge / removed-relation controls | graph adds no value over temporal similarity |
| 7 (`b7e7a2e`) | Learned relation-aware router; negative M5 results | router does not beat similarity |
| 8 (`c7525a0`) | Favorita transfer; graph-routing "kill test" | **graph-routing hypothesis rejected** on M5 **and** Favorita |
| 9 (`3dbac53`) | Uncertainty-aware **learned gated fusion**; controlled study | gate beats fixed fusion (~1.1%) |
| 10 (`d42d20e`, `fc8334e`, `fd40e3c`) | Full-panel controlled study; held-out val/test (test consumed once) | frozen verdict (Section 4) |
| 11 (`623a036`) | Hugging Face demo (research software, not a scientific claim) | packaging |
| 11A (this session) | Native **TS-RAG** feasibility on ETTm2 (dev only) | decision gate not passed (Section 4) |

**Graph-routing failure (verified).** The founding relational hypothesis was tested with both
non-learned graph retrieval and a learned relation-aware router, under shuffled-edge and
removed-relation controls, on two datasets (M5, Favorita), with paired-bootstrap CIs. Across
all of these, **typed relations added no retrieval value beyond temporal similarity**. This
cross-dataset negative is retained as a secondary empirical contribution and directly caused
the project's pivot from GraphRoute-TS to ScaleRAG-TS.

**LightGBM data-leakage discovery — "Attempt 11" (UNVERIFIED).** The project lead reports
that a data-leakage issue was identified in a LightGBM baseline configuration. *This audit
located no record of such a discovery in any committed artifact or in the four retained session
transcripts* (which begin 2026-07-14, after the Phase 2–3 baseline work of 2026-07-13; see the
provenance note). The committed record describes
LightGBM as leakage-safe **by construction** (direct multi-horizon prediction with lags ≥ the
28-day horizon, no recursion; `docs/baseline-report.md`), and its splits passing the
leakage-audit on all chronological folds. The claim is included at the project lead's
direction and should be independently sourced (commit / session log) before publication.

**Nested-rolling correction — "Attempt 12" (UNVERIFIED).** The project lead reports a
subsequent correction to a nested / rolling-origin evaluation protocol. *This audit located no
record of such a correction in any committed artifact or in the four retained session
transcripts.* The committed protocol uses
chronological expanding-window rolling origins with ≥3 origins for trainable components
(`docs/scalerag-ts-method.md`, `docs/m5-split-policy.md`); no artifact records a change made
to fix a prior nested-rolling defect. Included at the project lead's direction; source before
publication.

---

## 3. The Core Mechanism (Phase 4–5)

Naive retrieval *hurt* in Phase 4: matching raw context windows and copying their
continuations degraded accuracy, because two series (or two windows of one series) that share
a temporal *shape* can live at completely different *scales*. The mechanism that resolves this
has two components, applied around an exact FAISS search.

**(a) Scale normalization — pre-FAISS.** Each context window `x` is reduced to per-window
location/scale parameters and transformed into a scale-invariant vector before indexing/search:

```
x_transformed = (x − loc) / scale
```

with strategy-dependent `(loc, scale)`:

```
raw    → (0, 1)
mean   → (0,   mean(x))
rms    → (0,   rms(x))
znorm  → (mean(x), std(x))
```

Retrieval (FAISS `IndexFlatL2`, exact) is then performed in this normalized space, so
neighbours are selected by **shape**, not absolute magnitude.

**(b) Explicit scale restoration — post-retrieval.** A retrieved candidate continuation `cont`
is mapped from the *candidate's* scale to the *query's* scale before it is used as a forecast:

```
restored = (cont − c_loc) / c_scale · q_scale + q_loc
```

where `(c_loc, c_scale)` are the candidate-window parameters and `(q_loc, q_scale)` the query
parameters under the same strategy. For `mean` scaling this reduces to
`restored = cont · (q_mean / c_mean)`; for `rms`, `restored = cont · (q_rms / c_rms)`. Near-zero
scale denominators (e.g. `mean` on zero-centred data) are detected, counted, and served a
constant fallback rather than dividing by ~0.

**Ablation — restoration is decisive.** On M5 (1,000-series validation,
`docs/ablation-report.md`), removing scale restoration while keeping normalization degrades
RMSSE from **0.7425 → 2.7884** — a **3.8× degradation** — collapsing retrieval from
competitive to catastrophic. Normalization alone is *worse than doing nothing* (raw retrieval
RMSSE 0.7576); it is the **restoration** step that makes non-neural retrieval usable. Secondary
levers (top-k monotone to k=20; mean ≻ rms ≻ z-norm; category filter marginal) are second-order
relative to restoration.

---

## 4. Phase 11A Empirical Results (ETTm2 development gate)

Phase 11A tested whether the ScaleRAG scale-restoration mechanism transfers to the **official
TS-RAG regime** (context 512, horizon 64, frozen Chronos-Bolt, MSE/MAE), using **ETTm2 as the
sole development dataset**. The four final datasets (ETTh1, ETTm1, Weather, Electricity) were
**not opened**.

**Reproduction (gate condition 1 — met).** Official target-only Chronos-Bolt and official
TS-RAG were reproduced on ETTm2 to **≤0.10% relative** on MSE and MAE (target-only MSE
0.14856 vs paper 0.1487; TS-RAG MSE 0.14646 vs paper 0.1466), and the TS-RAG−backbone delta
reproduced essentially exactly (−1.41% MSE). The retriever was re-implemented non-neurally,
reusing the frozen ScaleRAG scale math; its exact top-k search is verified **bit-equivalent to
a FAISS reference** and passes five temporal-leakage tests (train-only candidate pool,
`t_r + H ≤ 34560`).

**Mechanism transfers (gate condition 2 — met).** Scale-restored retrieval beats
non-restored (raw) retrieval on the ETTm2 test split by **+85.4% MSE** (paired-bootstrap 95%
CI **[+85.18%, +85.64%]**, window-level; **7 of 7 channels** improved). This independently
confirms, in a second regime, the M5 ablation finding: restoration is what makes statistical
retrieval work.

**End-to-end forecasting fails (gate condition 3 — NOT met).** When the restored retrieval is
fused with the frozen backbone via the frozen non-learned config (mean scaling, k=20, fixed
weight 0.25), the fused forecaster is **worse than the target-only backbone**: **−0.85% MSE**
(95% CI **[−1.39%, −0.28%]**, i.e. significantly worse), and MAE also regresses. It further
**loses to official TS-RAG** by **−2.30% MSE** (95% CI [−2.86%, −1.70%]). Per-channel, fusion
beats the backbone on 5 of 7 channels but **loses in the pooled mean**, because one
high-variance channel (MULL) dominates the element-weighted average — an honest-aggregation
caveat.

**Compute disadvantage.** Measured on one machine (RTX 5070 Ti, batch 256, warm-up excluded):
the frozen backbone runs at **0.431 ms/window (GPU), 0 trainable params**; TS-RAG adds
**4.78 M** ARM parameters at ~+3.8% wall time; ScaleRAG adds **0.607 ms/window (CPU exact
k-NN)** and a **~1.1 GB in-RAM index**, ≈ **2.4× slower** end-to-end — for a *worse* result.
ScaleRAG is Pareto-dominated on the latency–accuracy plane.

**Decision gate: 4/5 conditions met; condition 3 fails → Phase 11B not initiated.** The four
final datasets remain untouched, per the pre-registration and the project's non-negotiable
rules against test-driven tuning.

**Consistency with the M5/Favorita record.** The Phase-10 controlled study found the learned
gated system beats target-only Chronos-2 by **+5.08% RMSSE** on the M5 full-panel validation
(CI [+4.97%, +5.19%]) and **+5.49%** on the consumed test split (CI [+5.40%, +5.59%]), but only
**+0.69%** over the strongest simple baseline (LightGBM; below the pre-registered 3% bar),
loses the official WRMSSE to LightGBM/seasonal-naive, and meets **0 of 3** pre-registered
success criteria. On the denser Favorita panel the improvement over Chronos-2 shrinks to
**+0.83%**. ETTm2 (dense, continuous) now extends the trend to **−0.85%**. The relationship
between dataset sparsity and retrieval utility is monotone across all measured regimes.

---

## 5. The Proposed Publication Pivot

The evidence does not support a **state-of-the-art accuracy** claim: the method ties or trails
strong simple baselines on M5, gives negligible gains on Favorita, and is net-negative and
Pareto-dominated on ETTm2. Publishing an accuracy headline would be unsupported.

The evidence **does** support a **mechanism-and-regime** contribution, which is the proposed
framing:

1. **Scale restoration is the necessary-and-sufficient fix for non-neural retrieval.** The
   same lightweight, non-learned operation converts catastrophic raw retrieval into a
   competitive retriever in two independent regimes and metrics: **3.8× RMSSE** recovery on M5
   and **+85.4% MSE** on ETTm2 (both with CIs; 7/7 ETTm2 channels). This is a clean, reusable,
   architecture-agnostic result about *why* retrieval-augmented TSFMs work when they work.

2. **A regime taxonomy for retrieval-augmented forecasting.** Utility of statistical
   (non-neural) retrieval augmentation is **regime-dependent and predictable from data
   sparsity / scale heterogeneity**: it helps on sparse, intermittent, scale-heterogeneous
   panels (M5 intermittent slices up to +5.6%), fades as density rises (Favorita +0.83%), and
   turns negative on dense continuous channels where a frozen TSFM is already near-optimal and
   a *learned* mixer (TS-RAG) or the target-only backbone wins (ETTm2). This reframes
   apparently contradictory RAG-for-time-series results as points on a single axis.

3. **A cross-dataset negative for typed relational routing.** Graph/relational structure adds
   no retrieval value beyond temporal similarity on M5 or Favorita, under controls and CIs — a
   result worth reporting to redirect effort in the sub-field.

**Scientific strengths for review.** Pre-registered success criteria and a consumed-once test
split; paired-bootstrap CIs throughout; leakage guards with adversarial tests; exact,
FAISS-verified retrieval; frozen-backbone verification (bit-identical weights); faithful
reproduction of the external TS-RAG baseline (≤0.10%); measured compute/parameter accounting;
and **preserved negative results** rather than a tuned headline.

**Threats to validity (declared).** (i) The ScaleRAG native adapter uses a *stricter*
train-only candidate pool than TS-RAG's full-series KB — a conservative choice that can only
disadvantage ScaleRAG. (ii) Bootstrap CIs are window-level over stride-1 (autocorrelated)
windows, so intervals are approximate (too narrow); point estimates and signs are unaffected.
(iii) ETTm2 is a single development dataset; the regime taxonomy is supported across M5 /
Favorita / ETTm2 but a broader dense-dataset sweep (the frozen, unexecuted Phase-11B
pre-registration) would strengthen it. (iv) The Section-2 "Attempt 11/12" leakage and
nested-rolling events are unverified in committed artifacts and must be sourced before they
appear in a submission.

---

### Artifact index (for verification)

`docs/ablation-report.md` (3.8× restoration ablation, top-k), `docs/final-experiment-report.md`
& `docs/final-heldout-test-report.md` (M5 controlled study, 0/3 criteria),
`docs/scalerag-ts-method.md` (mechanism, protocol), `docs/tsrag-official-audit.md` &
`docs/tsrag-ettm2-reproduction.md` (TS-RAG reproduction ≤0.10%),
`docs/scalerag-native-dev-report.md` & `docs/scalerag-native-dev-results.json` (Phase-11A
mechanisms, CIs, per-series), `docs/phase11b-preregistration.md` (frozen, not executed),
`paper/figures/fig1…fig6` + `architecture.pdf` (publication figures), `reports/phase11a/*` (per-window preds,
compute JSONs), `reports/scalerag-heldout-{val,test}-30490.json` (M5 full-panel),
`reports/scalerag-favorita.json` (Favorita +0.83%).
