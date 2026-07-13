"""Graph-guided retrieval forecasting (Phase 6, tasks 5-7).

All methods reuse Phase 5's scale-restored continuation forecasting — only *which
candidates* are retrieved changes:

- ``graph_only_forecast``  : candidate series chosen purely by graph relation /
  embedding similarity; forecast = restored mean of each candidate series' most
  recent legal continuation (no temporal window matching).
- hybrid                    : the graph selects the series *pool*, then temporal
  k-NN ranks windows within it — use ``ScaleAwareIndex.forecast(allowed_series=...)``.
"""

from __future__ import annotations

import numpy as np

from graphroute_ts.retrieval_faiss import ScaleAwareIndex, _fit_params, restore_continuation


def embedding_neighbors(emb: np.ndarray, query_idx: int, m: int) -> np.ndarray:
    """Top-m series by embedding cosine similarity (embeddings L2-normalised)."""
    sims = emb @ emb[query_idx]
    sims[query_idx] = -np.inf
    return np.argsort(-sims, kind="stable")[:m]


def _recent_candidates(index: ScaleAwareIndex, series_ids: np.ndarray, origin: int) -> np.ndarray:
    """Most-recent legal candidate window id for each series."""
    ends = index._ser_end[series_ids] - 1
    ends = ends[ends >= index._ser_start[series_ids]]
    if ends.size == 0:
        return ends
    legal = (index.db.t_r[ends] + index.db.horizon) < origin
    return ends[legal]


def graph_only_forecast(
    index: ScaleAwareIndex,
    query_window: np.ndarray,
    origin: int,
    horizon: int,
    quantile_levels: list[float],
    related_series: np.ndarray,
    max_series: int = 20,
    restore: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """Restored mean of related series' most-recent continuations (graph picks
    the series; no temporal similarity)."""
    related = related_series[:max_series]
    cand = _recent_candidates(index, related, origin) if related.size else related
    if cand.size == 0:
        base = np.clip(np.full(horizon, float(query_window.mean())), 0.0, None)
        return base, np.repeat(base[:, None], len(quantile_levels), axis=1)
    qp = _fit_params(query_window[None], index.scale)[0]
    conts = index.db.continuations[cand]
    if restore and index.scale != "raw":
        conts = np.stack(
            [restore_continuation(conts[j], index.params[cand[j]], qp) for j in range(len(cand))]
        )
    point = np.clip(conts.mean(0), 0.0, None)
    quants = np.clip(np.quantile(conts, quantile_levels, axis=0).T, 0.0, None)
    return point, quants
