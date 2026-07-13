"""Graph-restricted retrieval: leakage + control tests (Phase 6, tasks 8-10)."""

from __future__ import annotations

import numpy as np
import polars as pl
import pytest

from graphroute_ts.graph import HeteroGraph
from graphroute_ts.retrieval import WindowDatabase
from graphroute_ts.retrieval_faiss import ScaleAwareIndex

L, H, TRAIN_END, ORIGIN = 14, 7, 150, 200


def _entities():
    rows = [
        ("a", "i1", "D1", "C1", "S1", "X"),
        ("b", "i1", "D1", "C1", "S2", "Y"),
        ("c", "i2", "D1", "C1", "S1", "X"),
        ("d", "i2", "D1", "C1", "S2", "Y"),
        ("e", "i3", "D2", "C2", "S1", "X"),
        ("f", "i3", "D2", "C2", "S2", "Y"),
    ]
    return pl.DataFrame(
        rows, schema=["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"], orient="row"
    )


@pytest.fixture
def setup():
    rng = np.random.default_rng(0)
    t = np.arange(260)
    sales = (np.sin(2 * np.pi * t / 7)[None, :] + 2 + rng.normal(0, 0.2, (6, 260))).astype(float)
    ent = _entities()
    db = WindowDatabase.from_training(sales, TRAIN_END, L, H)
    idx = ScaleAwareIndex(db, ent, scale="mean", metric="l2")
    graph = HeteroGraph.from_entities(ent)
    return sales, ent, db, idx, graph


@pytest.mark.leakage
def test_allowed_series_restricts_candidates(setup):
    sales, _ent, db, idx, graph = setup
    related = graph.related(0, "same_category")  # series 0 -> cat C1
    q = sales[0, TRAIN_END - L : TRAIN_END]
    ids, _d, _qp = idx.search(q, ORIGIN, k=10, query_series_idx=0, allowed_series=related)
    assert ids.size > 0
    assert set(db.series_idx[ids].tolist()).issubset(set(related.tolist()))


@pytest.mark.leakage
def test_graph_restricted_retrieval_is_legal(setup):
    sales, _ent, db, idx, graph = setup
    related = graph.related(0, "same_store")
    q = sales[0, TRAIN_END - L : TRAIN_END]
    ids, _d, _qp = idx.search(q, ORIGIN, k=10, query_series_idx=0, allowed_series=related)
    assert np.all(db.t_r[ids] + H < ORIGIN)  # rule 3 preserved under graph restriction


@pytest.mark.leakage
def test_shuffled_edges_control_changes_related_sets(setup):
    # Control (task 8): shuffling the item->series assignment must change which
    # series are "same_item" — if it didn't, the graph structure would be inert.
    _sales, ent, _db, _idx, graph = setup
    rng = np.random.default_rng(1)
    shuffled = ent.with_columns(pl.Series("item_id", rng.permutation(ent["item_id"].to_numpy())))
    g2 = HeteroGraph.from_entities(shuffled)
    base = set(graph.related(0, "same_item").tolist())
    ctrl = set(g2.related(0, "same_item").tolist())
    assert base != ctrl or len(base) != len(ctrl)


@pytest.mark.leakage
def test_removed_category_relation_empties_same_category(setup):
    # Control: if all series share one category, "same_category" collapses to the
    # whole panel (no discriminative power) — verifies the relation is what filters.
    _sales, ent, _db, _idx, _graph = setup
    one_cat = ent.with_columns(pl.lit("C0").alias("cat_id"))
    g2 = HeteroGraph.from_entities(one_cat)
    assert len(g2.related(0, "same_category")) == ent.height - 1
