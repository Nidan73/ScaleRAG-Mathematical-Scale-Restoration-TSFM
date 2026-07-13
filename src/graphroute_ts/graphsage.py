"""Lightweight heterogeneous GraphSAGE encoder (Phase 6, task 5).

Untrained (random-init) 2-layer hetero SAGE that produces **series embeddings**
by mean-aggregating typed-neighbour embeddings (item / store / category /
department / state) over two hops. No end-to-end training, no LoRA, no ARM — the
encoder is frozen and used only to embed series for graph-embedding retrieval.

Because it is untrained, the embedding is a *structured random projection* of the
metadata: series sharing item/store/category/department land close together. The
`random_series_embeddings` control removes that structure entirely.
"""

from __future__ import annotations

import numpy as np

from graphroute_ts.graph import HeteroGraph


def _group_mean(values, group_idx, n_groups: int):
    import torch

    dim = values.shape[1]
    out = torch.zeros(n_groups, dim)
    out.index_add_(0, group_idx, values)
    cnt = torch.zeros(n_groups).index_add_(0, group_idx, torch.ones(len(group_idx)))
    return out / cnt.clamp(min=1).unsqueeze(1)


class HeteroGraphSAGE:
    """Frozen 2-layer hetero GraphSAGE. Deterministic given ``seed``."""

    def __init__(self, graph: HeteroGraph, dim: int = 64, seed: int = 42) -> None:
        self.graph = graph
        self.dim = dim
        self.seed = seed

    def embed_series(self) -> np.ndarray:
        """Return L2-normalised series embeddings (n_series, dim)."""
        import torch

        g = self.graph
        torch.manual_seed(self.seed)
        item = torch.from_numpy(g.item)
        store = torch.from_numpy(g.store)
        cat = torch.from_numpy(g.cat)
        dept = torch.from_numpy(g.dept)
        state = torch.from_numpy(g.state)

        def rand(n):
            return torch.randn(int(n), self.dim)

        emb = {
            "item": rand(g.item.max() + 1),
            "store": rand(g.store.max() + 1),
            "cat": rand(g.cat.max() + 1),
            "dept": rand(g.dept.max() + 1),
            "state": rand(g.state.max() + 1),
        }
        w1 = torch.randn(self.dim, self.dim) / np.sqrt(self.dim)
        w2 = torch.randn(self.dim, self.dim) / np.sqrt(self.dim)
        act = torch.tanh

        with torch.no_grad():
            # layer 1: series aggregates its typed neighbours
            x = (
                emb["item"][item]
                + emb["store"][store]
                + emb["cat"][cat]
                + emb["dept"][dept]
                + emb["state"][state]
            ) / 5.0
            h = act(x @ w1)
            # refine type nodes from series, then re-aggregate (2nd hop)
            item_h = _group_mean(h, item, int(g.item.max() + 1))
            store_h = _group_mean(h, store, int(g.store.max() + 1))
            cat_h = _group_mean(h, cat, int(g.cat.max() + 1))
            dept_h = _group_mean(h, dept, int(g.dept.max() + 1))
            state_h = _group_mean(h, state, int(g.state.max() + 1))
            x2 = (item_h[item] + store_h[store] + cat_h[cat] + dept_h[dept] + state_h[state]) / 5.0
            h2 = act(x2 @ w2)
            emb_series = torch.nn.functional.normalize(h2, dim=1).cpu().numpy()
        return emb_series.astype(np.float32)


def random_series_embeddings(n_series: int, dim: int = 64, seed: int = 42) -> np.ndarray:
    """Control: structureless random series embeddings (L2-normalised)."""
    rng = np.random.default_rng(seed)
    e = rng.standard_normal((n_series, dim)).astype(np.float32)
    return e / np.linalg.norm(e, axis=1, keepdims=True)
