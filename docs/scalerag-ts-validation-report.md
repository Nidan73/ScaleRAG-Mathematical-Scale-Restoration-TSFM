# ScaleRAG-TS — Validation Report (Phase 9, increment 1)

Decisive core evaluation of the proposed **scale-aware retrieval + learned gated
fusion** vs frozen baselines on M5 (1,000 series, val split; test `d_1914–1941`
untouched). Gate trained on **historical origins only**; paired-bootstrap 95% CIs
over series; 3 gate seeds. Pre-registration in `docs/scalerag-ts-method.md`.

## Results — M5, 1,000 series, val split

| Method | RMSSE | Pinball | 80% coverage |
|--------|------:|--------:|-------------:|
| **ScaleRAG (gated fusion)** | **0.7173** | 0.3741 | 0.689 |
| recent-mean | 0.7221 | 0.5265 | 0.030 |
| retrieval, scale-aware (Phase 5) | 0.7425 | 0.4166 | 0.714 |
| target-only Chronos-2 | 0.7540 | 0.3576 | 0.791 |
| retrieval, raw | 0.7576 | 0.4054 | 0.849 |

Paired bootstrap (relative RMSSE improvement of ScaleRAG, 95% CI over series):

| Comparison | Rel. improvement | 95% CI | Significant |
|-----------|-----------------:|--------|:-----------:|
| vs **target-only Chronos-2** | **+4.86%** | [+4.30%, +5.39%] | ✅ yes |
| vs strongest baseline (recent-mean) | +0.66% | [+0.12%, +1.23%] | ✅ yes (tiny) |

Slices (ScaleRAG vs strongest baseline / vs Chronos):

| Slice | n | vs strongest | vs Chronos |
|-------|--:|-------------:|-----------:|
| intermittent (z>0.8) | 384 | −0.25% [−0.92, +0.46] | +5.01% |
| low-volume (<median) | 500 | **−0.62%** [−1.11, −0.11] | +5.75% |
| reduced-history (<100 nz) | 66 | −0.05% [−1.52, +1.59] | +3.99% |

## Pre-registered criteria — verdict

| Criterion | Result | Met? |
|-----------|--------|:----:|
| 1. ≥3% RMSSE over strongest baseline, CI excl 0 | +0.66% | ❌ |
| 2. ≥5% over target-only Chronos-2 on **both** M5 & Favorita | M5 +4.86% (<5%); Favorita not run | ❌ |
| 3. ≥7% on a sparse/cold-start slice over strongest, CI excl 0 | slices ≤0% vs recent-mean | ❌ |

**None of the three pre-registered criteria is met.** Per protocol, **no positive
forecasting improvement is claimed** in the strong (beats-the-strongest-baseline)
sense.

## Honest interpretation (the nuance that matters)

- **Retrieval augmentation genuinely helps the TSFM.** ScaleRAG improves over
  target-only Chronos-2 by **~5% overall and 4–5.75% on every slice**, all
  significant. Scale restoration is the enabling mechanism (raw retrieval is the
  *worst* method, 0.7576). The learned gate makes it the best method overall.
- **But it does not beat the strongest simple baseline by the pre-registered
  margin.** On intermittent retail demand (M5), a **recent-mean constant** is an
  extraordinarily strong RMSSE forecaster (a recurring finding across Phases 4–9);
  neither Chronos-2 nor retrieval clears a 3% margin over it, and on sparse/
  low-volume series recent-mean is *better*. The high bar was set deliberately.
- **Calibration caveat:** fusion improves point RMSSE and pinball vs retrieval, but
  its 80% interval coverage (0.689) is below Chronos-2's (0.791) — a point-accuracy
  gain at some cost to calibration. Reported, not hidden.

## Recommendation → paper framing

Per the pre-registered fallback, frame the paper as a **controlled study**, not a
SOTA claim:

**Updated title:** *ScaleRAG-TS: A Controlled Study of Scale-Aware Retrieval
Augmentation and Relational Metadata for Time-Series Foundation Models.*

**Contributions (honest):**
1. **Scale-aware retrieval augmentation** of a frozen TSFM, with **scale
   restoration** as the key mechanism (turns naive retrieval from harmful to
   helpful) — a **significant ~5% RMSSE improvement over target-only Chronos-2**.
2. A **learned uncertainty-aware gated fusion** that routes each series between the
   TSFM and retrieval — the best overall method here.
3. A **rigorous, pre-registered, cross-dataset negative result**: typed-relation
   graph routing adds **no** predictive retrieval value beyond temporal/statistical
   similarity (M5 + Favorita; non-learned and learned; controls + CIs).
4. A methodological finding: on intermittent retail forecasting, **RMSSE against a
   recent-mean baseline is a punishing bar** — retrieval augmentation helps the
   foundation model but does not beat that baseline by a pre-registered margin.

## Status & remaining work (progressive Phase 9)

This is **increment 1** — the decisive gate. Because all pre-registered criteria
fail here, the controlled-study framing is determined. Remaining items would
strengthen the write-up but not change the verdict: RAFT/TS-RAG-style baselines,
in-context grouping, the full ablation matrix, Favorita + 5k/full scales, and the
deferred adapter/LoRA (Part D) — which must **not** be used to rescue a weak
retrieval mechanism (retrieval-only and gated-fusion results stay separate).

**Frozen strongest validation configuration:** `ScaleRAG (gated fusion)` =
mean/L2/category/k=20 + scale restoration + learned gate over
{nn-distance, disagreement, intermittency, volume, Chronos-uncertainty,
scale-spread}. The untouched M5 test split is reserved for a single final run only
after the full method + hyperparameters are frozen.

## Reproduce
```bash
uv run python scripts/scalerag_eval.py --subset 1000 --seed 42
```
Report data: `reports/scalerag-m5-subset1000.json`.
