# Graph Construction & Graph-Guided Retrieval (Phase 6)

Typed heterogeneous M5 entity graph + non-learned graph retrieval and a
lightweight (frozen, untrained) heterogeneous GraphSAGE. **No LoRA, ARM,
cross-attention, or joint training** (task 14). Val split `d_1886–d_1913`; test
untouched. Selection by RMSSE on validation only. **Negative findings preserved.**

## Graph (tasks 1–3)

- **Nodes:** item (3,049), department (7), category (3), store (10), state (3),
  series/item-store (30,490) — 33,562 total (tiny → pure-torch, no PyG).
- **Typed relations:** item→department, item→category, series→item, series→store,
  store→state.
- Sales / prices / SNAP / calendar remain **temporal features, not nodes** (task 3).

All forecasting reuses **Phase 5's scale-restored continuation k-NN** — only the
*retrieval* (which candidates) changes (task 7).

## Results — 1,000-series subset, val split, seed 42

Ranked by RMSSE. `CONTROL:*` are task-8 controls. Graph forecasting selects
candidate series by relation/embedding; hybrid = graph pool + temporal ranking.

| Method | RMSSE | MASE | WAPE | MAE | Pinball |
|--------|-------|------|------|-----|---------|
| naive:recent_mean | **0.7221** | 1.0146 | 0.7416 | 1.0530 | 0.5265 |
| hybrid:relation_weighted+temporal | 0.7403 | 1.0667 | 0.7587 | 1.0773 | 0.4179 |
| hybrid:same_category+temporal | 0.7415 | 1.0558 | 0.7577 | 1.0760 | 0.4138 |
| **temporal:cat/k20 (frozen Phase 5)** | 0.7425 | 1.0571 | 0.7615 | 1.0813 | 0.4166 |
| CONTROL:removed_category | 0.8118 | 1.2094 | 0.8349 | 1.1856 | 0.4600 |
| graph_only:same_category | 0.8195 | 1.2231 | 0.8442 | 1.1988 | 0.4622 |
| graph_only:same_department | 0.8648 | 1.3024 | 0.8750 | 1.2425 | 0.4600 |
| graph_only:same_item | 0.8873 | 1.1400 | 0.9013 | 1.2799 | 0.6378 |
| graph_only:shortest_path | 0.9013 | 1.3347 | 0.9674 | 1.3738 | 0.4792 |
| graph_only:same_store | 0.9014 | 1.3347 | 0.9677 | 1.3741 | 0.4794 |
| **graph_embedding:sage** | 0.9108 | 1.3522 | 0.9437 | 1.3401 | 0.4636 |
| graph_only:random_neighbor | 0.9149 | 1.3335 | 0.9672 | 1.3734 | 0.4875 |
| graph_only:relation_weighted | 0.9265 | 1.3756 | 0.9677 | 1.3741 | 0.4661 |
| CONTROL:shuffled_item_edges | 0.9282 | 1.3784 | 0.9671 | 1.3733 | 0.4672 |
| CONTROL:random_embedding | 0.9295 | 1.3592 | 1.0304 | 1.4632 | 0.5035 |

(top-k sweep: relation_weighted m50=0.854, m20=0.927, m10=0.989, m3=1.147 — more
related series → better, as averaging suppresses noise.)

## Findings (honest, negatives preserved)

1. **Graph does NOT beat the frozen Phase 5 temporal baseline.** The best graph
   method (`hybrid:relation_weighted+temporal`, 0.7403) merely **ties**
   `temporal:cat/k20` (0.7425, a 0.3% difference) — and only because it reuses
   temporal ranking within a graph pool that is ≈ the category filter Phase 5
   already used. The graph **complements marginally at best; it does not win.**
2. **Untrained graph embeddings add nothing.** `graph_embedding:sage` (0.9108) is
   statistically indistinguishable from the **random-embedding control** (0.9295),
   **shuffled-edges** (0.9282), and **random-neighbor** (0.9149). The graph
   structure, as encoded by a frozen SAGE, carries no useful forecasting signal
   here beyond what category-filtering already provides.
3. **Pure graph-only retrieval is weak** (0.82–0.93) — worse than temporal (0.74).
   Selecting candidates by graph structure *without* temporal window matching
   loses the pattern-similarity that drives good retrieval.
4. **Controls confirm category is the only informative relation.** Removing
   category hurts (0.81); shuffling item edges leaves graph-only essentially
   unchanged (0.93 ≈ 0.93). Removing store barely matters. The single useful
   "relation" is category — which the Phase 5 baseline already exploits.
5. **`naive:recent_mean` (0.7221) still leads on RMSSE** across Phases 4–6 (though
   retrieval/hybrid win decisively on pinball: 0.414 vs 0.527).

## Slice analysis (task 12)

| Slice | n | Temporal RMSSE | Best-graph RMSSE (hybrid:rel_wt) |
|-------|--:|---------------:|---------------------------------:|
| intermittent (zero-frac > 0.8) | 384 | 0.7579 | **0.7551** |
| low-volume (< median) | 500 | 0.7484 | **0.7445** |
| reduced-history (< 100 nonzero) | 66 | **0.8994** | 0.9265 |

At 1,000 the hybrid gives a **tiny** edge for intermittent and low-volume series
and is worse for reduced-history — **but this edge did not replicate at 5,000**
(hybrid worse on all three slices), so it is treated as noise, not a graph
benefit. Unseen item-store combinations are **not evaluable on M5** (every series
is a known item-store) — noted, not fabricated.

## Scaling (task 9)

- 1,000 series: complete (above). DB stride 7, 258k candidates, peak RAM 21.6 GiB,
  VRAM 0 (retrieval CPU; SAGE embed is a one-off CPU pass).
- 5,000 series: **confirms the finding.** `naive:recent_mean` 0.7431 <
  `hybrid:same_category+temporal` 0.7542 ≈ `temporal:cat/k20` 0.7574; embedding
  0.9843 ≈ random-embedding control 0.9891. Moreover the small slice edges seen at
  1,000 **did not hold** — at 5,000 the hybrid is *worse* than temporal on all
  three slices (intermittent 0.7939 vs 0.7886; low-volume 0.7748 vs 0.7698;
  reduced-history 0.9459 vs 0.9221), i.e. the 1,000-subset edge was noise. The
  negative result is **stable across scales**.
- Full panel: **not pursued** — the method does not beat the Phase 5 baseline at
  1k or 5k, so a full-scale graph run is not warranted (it would only confirm a
  negative more expensively). Full-scale *temporal* retrieval feasibility was
  already established in Phase 5.

## Frozen strongest configurations (task 14)

- **Strongest graph-only:** `graph_only:same_category` (RMSSE 0.8195) — but it is
  *worse* than the Phase 5 temporal baseline; recorded for completeness.
- **Strongest graph-temporal:** `hybrid:relation_weighted+temporal` (RMSSE 0.7403)
  — ties the frozen Phase 5 baseline (0.7425); best pinball among all methods.

## Conclusion & recommendation

**The typed graph, as a non-learned retrieval prior and as frozen SAGE embeddings,
does not improve over the Phase 5 temporal baseline on M5 validation.** Its only
informative relation (category) is already used by Phase 5. This is a genuine
negative result and sets an honest, high bar: **a graph phase is only worthwhile
if a *trained* relation-aware component (e.g. learned edge/relation weighting or
trained embeddings) extracts signal the frozen structure cannot** — which is where
LoRA / ARM / trained routing (explicitly out of scope here) would come in. Until
then, the frozen Phase 5 `mean/l2/cat/k20` (and its hybrid tie) remains the
baseline to beat.

## Reproduce & tests

```bash
uv run python scripts/graph_retrieval_eval.py --subset 1000 --seed 42
```
Tests: `tests/unit/test_graph.py` (relations, GraphSAGE structure/determinism,
controls) and `tests/leakage/test_graph_retrieval.py` (allowed-series restriction
stays leakage-safe, shuffled-edge & removed-relation controls). Full suite green.
Report: `reports/graph-retrieval-subset1000.json`.
