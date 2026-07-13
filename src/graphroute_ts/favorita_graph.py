"""Favorita typed metadata graph + richer relation features (Phase 8).

Favorita exposes 9 entity attributes (vs M5's 4): item, family, class, perishable,
store, store-type, cluster, city, state. This module builds per-series codes and
the **relation** feature block; the temporal/statistical features, utility labels,
scale restoration, and ranking metrics are reused verbatim from
``graphroute_ts.router`` (task 5). Sales/promotions/transactions/holidays/oil stay
temporal features, not nodes (task 3).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import polars as pl

from graphroute_ts.router import TEMPORAL_FEATURES, OriginStats, temporal_features

FAVORITA_ATTRS = (
    "item_id",
    "family_id",
    "class_id",
    "perishable_id",
    "store_id",
    "type_id",
    "cluster_id",
    "city_id",
    "state_id",
)
RELATION_FEATURES = [f"same_{a.removesuffix('_id')}" for a in FAVORITA_ATTRS] + ["graph_dist"]
FEATURE_NAMES = RELATION_FEATURES + TEMPORAL_FEATURES


@dataclass
class FavoritaGraph:
    codes: dict[str, np.ndarray]

    @classmethod
    def from_entities(cls, entities: pl.DataFrame) -> FavoritaGraph:
        ent = entities.sort("id")
        codes = {}
        for a in FAVORITA_ATTRS:
            _, inv = np.unique(ent[a].to_numpy(), return_inverse=True)
            codes[a] = inv.astype(np.int64)
        return cls(codes=codes)


def relation_features(fg: FavoritaGraph, t: int, cand: np.ndarray) -> np.ndarray:
    """(n_cand, 10): a same-<attr> indicator per attribute + a graph-distance."""
    same = {a: (fg.codes[a][cand] == fg.codes[a][t]).astype(np.float64) for a in FAVORITA_ATTRS}
    # hop metric: item/store closest, then class/cluster, family/type, city, state
    graph_dist = np.where(
        (same["item_id"] > 0) | (same["store_id"] > 0),
        2.0,
        np.where(
            (same["class_id"] > 0) | (same["cluster_id"] > 0),
            3.0,
            np.where(
                (same["family_id"] > 0) | (same["type_id"] > 0),
                4.0,
                np.where(same["city_id"] > 0, 5.0, np.where(same["state_id"] > 0, 6.0, 7.0)),
            ),
        ),
    )
    cols = [same[a] for a in FAVORITA_ATTRS] + [graph_dist]
    return np.stack(cols, axis=1)


def features(fg: FavoritaGraph, stats: OriginStats, t: int, cand: np.ndarray) -> np.ndarray:
    """Full Favorita feature matrix: relation block + shared temporal block."""
    return np.hstack([relation_features(fg, t, cand), temporal_features(stats, t, cand)])


def feature_group_mask(group: str) -> list[int]:
    if group == "all":
        return list(range(len(FEATURE_NAMES)))
    names = RELATION_FEATURES if group == "metadata" else TEMPORAL_FEATURES
    return [FEATURE_NAMES.index(n) for n in names]
