"""Typed heterogeneous M5 entity graph + non-learned graph retrieval (Phase 6).

Node types: item, department, category, store, state, series (item-store).
Typed relations (task 2):
  item  belongs_to  department
  item  belongs_to  category
  series represents item
  series sold_at    store
  store located_in  state

Sales / prices / SNAP / calendar stay as **temporal features**, never nodes
(task 3). This module provides the graph structure and *non-learned* graph
retrieval: it returns, for a query series, an ordered list of related series
(most-related first). The actual forecasting reuses Phase 5's scale-restored
temporal k-NN over those candidates (task 7).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import polars as pl

RELATIONS = (
    "same_item",  # same item, other stores
    "same_store",
    "same_category",
    "same_department",
    "shortest_path",  # ordered by hetero-graph hop distance
    "relation_weighted",
    "random_neighbor",
)

# relation-weighted heuristic weights (closer relation = higher weight)
_REL_WEIGHTS = {"item": 5.0, "store": 3.0, "dept": 2.0, "cat": 1.0, "state": 0.5}


def _encode(col: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    uniq, inv = np.unique(col, return_inverse=True)
    return inv.astype(np.int64), uniq


@dataclass
class HeteroGraph:
    n_series: int
    item: np.ndarray
    store: np.ndarray
    cat: np.ndarray
    dept: np.ndarray
    state: np.ndarray
    by_item: dict[int, np.ndarray]
    by_store: dict[int, np.ndarray]
    by_cat: dict[int, np.ndarray]
    by_dept: dict[int, np.ndarray]

    @classmethod
    def from_entities(cls, entities: pl.DataFrame) -> HeteroGraph:
        ent = entities.sort("id")
        item, _ = _encode(ent["item_id"].to_numpy())
        store, _ = _encode(ent["store_id"].to_numpy())
        cat, _ = _encode(ent["cat_id"].to_numpy())
        dept, _ = _encode(ent["dept_id"].to_numpy())
        state, _ = _encode(ent["state_id"].to_numpy())

        def rev(codes: np.ndarray) -> dict[int, np.ndarray]:
            order = np.argsort(codes, kind="stable")
            keys, starts = np.unique(codes[order], return_index=True)
            groups = np.split(order, starts[1:])
            return dict(zip(keys.tolist(), groups, strict=True))

        return cls(
            n_series=ent.height,
            item=item,
            store=store,
            cat=cat,
            dept=dept,
            state=state,
            by_item=rev(item),
            by_store=rev(store),
            by_cat=rev(cat),
            by_dept=rev(dept),
        )

    # ---- relation neighbour sets (excluding the query itself) ----
    def _members(self, mapping: dict[int, np.ndarray], code: int, exclude: int) -> np.ndarray:
        members = mapping.get(int(code), np.empty(0, np.int64))
        return members[members != exclude]

    def related(
        self, s: int, relation: str, k: int | None = None, rng: np.random.Generator | None = None
    ) -> np.ndarray:
        """Ordered related series (most related first). ``k`` truncates."""
        if relation == "same_item":
            out = self._members(self.by_item, self.item[s], s)
        elif relation == "same_store":
            out = self._members(self.by_store, self.store[s], s)
        elif relation == "same_category":
            out = self._members(self.by_cat, self.cat[s], s)
        elif relation == "same_department":
            out = self._members(self.by_dept, self.dept[s], s)
        elif relation == "shortest_path":
            out = self._shortest_path_order(s)
        elif relation == "relation_weighted":
            out = self._relation_weighted(s)
        elif relation == "random_neighbor":
            pool = self._candidate_union(s)
            r = rng or np.random.default_rng(0)
            out = r.permutation(pool)
        else:
            raise ValueError(f"unknown relation {relation!r}. Choices: {RELATIONS}")
        return out[:k] if k is not None else out

    def _candidate_union(self, s: int) -> np.ndarray:
        parts = [
            self._members(self.by_item, self.item[s], s),
            self._members(self.by_store, self.store[s], s),
            self._members(self.by_dept, self.dept[s], s),
            self._members(self.by_cat, self.cat[s], s),
        ]
        return np.unique(np.concatenate(parts)) if parts else np.empty(0, np.int64)

    def _relation_weighted(self, s: int) -> np.ndarray:
        pool = self._candidate_union(s)
        if pool.size == 0:
            return pool
        score = np.zeros(pool.size)
        score += _REL_WEIGHTS["item"] * (self.item[pool] == self.item[s])
        score += _REL_WEIGHTS["store"] * (self.store[pool] == self.store[s])
        score += _REL_WEIGHTS["dept"] * (self.dept[pool] == self.dept[s])
        score += _REL_WEIGHTS["cat"] * (self.cat[pool] == self.cat[s])
        score += _REL_WEIGHTS["state"] * (self.state[pool] == self.state[s])
        order = np.lexsort((pool, -score))  # score desc, tie-break by series id
        return pool[order]

    def _shortest_path_order(self, s: int) -> np.ndarray:
        """Order series by increasing hetero-graph hop distance. Same item/store
        are 2 hops (via item/store node); same dept/cat are 4 hops (via the type
        node). Ties broken by series id for determinism."""
        same_item = self._members(self.by_item, self.item[s], s)
        same_store = self._members(self.by_store, self.store[s], s)
        near = np.unique(np.concatenate([same_item, same_store]))
        same_dept = self._members(self.by_dept, self.dept[s], s)
        same_cat = self._members(self.by_cat, self.cat[s], s)
        far = np.setdiff1d(np.unique(np.concatenate([same_dept, same_cat])), near)
        return np.concatenate([np.sort(near), np.sort(far)])
