# Literature Verification of Published Claims

Claims that appear in `paper/main.tex` and in the unpublished manuscript were checked
against a 98-source NotebookLM corpus of TSFM and retrieval-augmented forecasting
papers. The ScaleRAG project's own documents were **excluded from every query**, so
none of these verdicts is self-referential; all queries returned zero self-citations.

Checked 2026-07-26. Corpus: 98 sources (81 web, 13 PDF, 4 markdown).

## Verdicts

| # | Claim | Verdict | Grounding |
|---|---|---|---|
| 1 | RAID normalizes a retrieved trajectory by its own mean and standard deviation before mapping the aggregate onto a target scale | **SUPPORTED** | RAID ×9 |
| 2 | RAID reports results on M5 and Favorita | **SUPPORTED** | RAID |
| 3 | RAID targets true cold start; target statistics are regressed by a trained network from text metadata | **SUPPORTED** | RAID |
| 4 | RAID retrieves over frozen multilingual text embeddings by cosine similarity, not numeric windows | **SUPPORTED** | RAID |
| 5 | TS-RAG trains its ARM on a multi-domain corpus and applies it zero-shot without task-specific fine-tuning | **SUPPORTED**, and empirically demonstrated (a "Cross-Domain" ablation row) | TS-RAG ×3 |
| 6 | TS-RAG correlates properties at the dataset level, not per series | **SUPPORTED** — Table 13 is a Pearson coefficient over **4 points** (ETTh1/h2/m1/m2) | TS-RAG |
| 7 | No paper here reports the accuracy of the retrieved continuation separately from the fused forecast | **SUPPORTED** (negative, see caveat) | none possible |
| 8 | Only RAID evaluates on intermittent retail demand among retrieval papers | **CONTRADICTED** | GNBAN ×3 |

## What changed as a result

**Claim 8 was wrong and was never published.** GNBAN also evaluates on M5 and
Favorita and speaks of a "retrieved context vector". The manuscripts say only that
RAID *also* reports on M5 and Favorita, which is accurate and claims no
exclusivity. Any future wording must not claim RAID is the sole retrieval paper on
intermittent retail data.

**Claim 6 sharpened the regime result.** TS-RAG's correlation table rests on four
dataset-level averages, so it structurally cannot show a non-monotone relationship.
That is now stated in `docs/regime-threshold-report.md` as the reason the per-series
inverted U is visible here and not there.

**Claim 5 removed a hedge.** An earlier draft described TS-RAG's cross-dataset
mixer transfer as "plausible from its design, thin as evidence". It is in fact
demonstrated with a dedicated ablation row, so `docs/gate-transfer-report.md` is
correct to treat cross-dataset transfer as table stakes rather than a
differentiator.

## Prior-art sweep, and why it is weak evidence

A systematic sweep asked for **any** source beyond TS-RAG, TimeRAF, SARAF, SERAF,
TRACE and RAID performing normalize-then-restore on a retrieved segment, phrased to
match a dozen synonyms (denormalization, shape-scale decomposition, scale transfer,
analog rescaling, and so on). It returned none, and reported that no source combines
a frozen backbone with a non-neural numeric retriever and a closed-form rescaling of
the retrieved future.

**Treat that as suggestive, not settled.** Three reasons:

1. **The answer carried zero citations.** A negative finding has nothing to cite, so
   it cannot be audited the way the supported claims above can.
2. **The corpus has known holes.** RAFT, ReTime, TimeRAG and RATD are named inside
   other papers' related-work sections but their own papers are **not** sources
   here. Any of them could contain the mechanism. Analog forecasting, nearest
   neighbour forecasting, and the intermittent-demand literature (Croston, SBA, TSB)
   are absent entirely, and the RevIN paper is cited by others rather than present.
3. **Absence from 98 sources is not absence from the field.**

Before any novelty claim goes to a reviewer, add at minimum: the RAFT, ReTime,
TimeRAG and RATD papers, the RevIN paper itself, and a sample of the analog and
intermittent-demand literature. The claim as currently stated is "no prior art in
the surveyed corpus", and it should not be strengthened beyond that without them.

## Method note

Queries used `notebooklm ask --json` so citations could be mapped back to source
titles. An earlier round, before the ScaleRAG documents were excluded, produced a
novelty verdict in which 7 of 22 citations were the project's own audit report; that
result was discarded as circular. Every verdict above comes from a query that
excluded those documents and returned zero self-citations.
