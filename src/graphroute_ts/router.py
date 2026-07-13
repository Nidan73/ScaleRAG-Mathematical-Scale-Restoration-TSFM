"""Learned candidate-ranking (retrieval routing) features & labels (Phase 7).

For a target series and a pool of candidate series at a forecast origin ``o``, we
build features and a **forecast-utility label**: how much a candidate's
scale-restored recent trajectory improves the forecast over a target-only
recent-mean base. Labels are generated only from **historical** origins
(``o <= 1885``) — never d_1914-d_1941 (task 1). The learned router ranks
candidates; the forecast reuses Phase 5 scale restoration (task 4).

Feature groups let us train temporal-only, metadata-only, and hybrid routers.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from graphroute_ts.graph import HeteroGraph

RELATION_FEATURES = ["same_item", "same_store", "same_cat", "same_dept", "same_state", "graph_dist"]
TEMPORAL_FEATURES = [
    "temporal_l2",
    "scale_ratio",
    "abs_scale_ratio",
    "t_zero",
    "c_zero",
    "t_vol",
    "c_vol",
    "seasonal_align",
]
FEATURE_NAMES = RELATION_FEATURES + TEMPORAL_FEATURES


@dataclass
class OriginStats:
    o: int
    mean: np.ndarray  # (n,) context mean
    zerofrac: np.ndarray  # (n,) context zero fraction
    znorm: np.ndarray  # (n, L) z-normalised context
    weekly: np.ndarray  # (n, 7) unit-norm weekly profile
    recent: np.ndarray  # (n, H) block ending at o  (leakage-safe forecast source)
    actual: np.ndarray  # (n, H) actuals o..o+H     (label/eval target)


def origin_stats(sales: np.ndarray, o: int, context: int = 56, horizon: int = 28) -> OriginStats:
    ctx = sales[:, o - context : o]
    mean = ctx.mean(1)
    std = ctx.std(1)
    znorm = (ctx - mean[:, None]) / np.where(std == 0, 1.0, std)[:, None]
    weekly = ctx.reshape(ctx.shape[0], context // 7, 7).mean(1)  # (n,7) by week position
    wn = weekly - weekly.mean(1, keepdims=True)
    wnorm = wn / np.where(np.linalg.norm(wn, axis=1) == 0, 1.0, np.linalg.norm(wn, axis=1))[:, None]
    return OriginStats(
        o=o,
        mean=mean,
        zerofrac=(ctx == 0).mean(1),
        znorm=znorm,
        weekly=wnorm,
        recent=sales[:, o - horizon : o],
        actual=sales[:, o : o + horizon],
    )


def features(stats: OriginStats, graph: HeteroGraph, t: int, cand: np.ndarray) -> np.ndarray:
    """Feature matrix (n_cand, n_features) for target ``t`` vs candidate series."""
    same_item = (graph.item[cand] == graph.item[t]).astype(np.float64)
    same_store = (graph.store[cand] == graph.store[t]).astype(np.float64)
    same_cat = (graph.cat[cand] == graph.cat[t]).astype(np.float64)
    same_dept = (graph.dept[cand] == graph.dept[t]).astype(np.float64)
    same_state = (graph.state[cand] == graph.state[t]).astype(np.float64)
    graph_dist = np.where(
        (same_item > 0) | (same_store > 0),
        2.0,
        np.where((same_cat > 0) | (same_dept > 0), 4.0, 6.0),
    )
    temporal_l2 = np.linalg.norm(stats.znorm[cand] - stats.znorm[t], axis=1)
    scale_ratio = np.log((stats.mean[t] + 1.0) / (stats.mean[cand] + 1.0))
    seasonal = stats.weekly[cand] @ stats.weekly[t]  # cosine of weekly profiles
    cols = [
        same_item,
        same_store,
        same_cat,
        same_dept,
        same_state,
        graph_dist,
        temporal_l2,
        scale_ratio,
        np.abs(scale_ratio),
        np.full(cand.shape, stats.zerofrac[t]),
        stats.zerofrac[cand],
        np.full(cand.shape, np.log(stats.mean[t] + 1.0)),
        np.log(stats.mean[cand] + 1.0),
        seasonal,
    ]
    return np.stack(cols, axis=1)


def utility(stats: OriginStats, t: int, cand: np.ndarray) -> np.ndarray:
    """Forecast utility of each candidate = base RMSE - candidate RMSE (>0 helps).

    Candidate forecast = its recent block, mean-scaled to the target (leakage-safe:
    the block ends at ``o``). Base = target recent-mean constant.
    """
    actual = stats.actual[t]
    base = np.full(actual.shape, stats.mean[t])
    base_rmse = np.sqrt(np.mean((actual - base) ** 2))
    scaled = stats.recent[cand] * (stats.mean[t] / (stats.mean[cand] + 1e-6))[:, None]
    cand_rmse = np.sqrt(np.mean((actual[None] - scaled) ** 2, axis=1))
    return base_rmse - cand_rmse


def router_forecast(
    stats: OriginStats, t: int, cand: np.ndarray, ranking: np.ndarray, k: int, horizon: int
) -> tuple[np.ndarray, np.ndarray]:
    """Top-k candidates by ``ranking`` (higher = better) → mean-scaled forecast."""
    if cand.size == 0:
        base = np.clip(np.full(horizon, stats.mean[t]), 0.0, None)
        return base, base[:, None]
    top = cand[np.argsort(-ranking, kind="stable")[:k]]
    scaled = stats.recent[top] * (stats.mean[t] / (stats.mean[top] + 1e-6))[:, None]
    point = np.clip(scaled.mean(0), 0.0, None)
    return point, np.clip(scaled, 0.0, None)


def feature_group_mask(group: str) -> list[int]:
    """Column indices for 'temporal', 'metadata', or 'all' feature groups."""
    if group == "all":
        return list(range(len(FEATURE_NAMES)))
    names = RELATION_FEATURES if group == "metadata" else TEMPORAL_FEATURES
    return [FEATURE_NAMES.index(n) for n in names]
