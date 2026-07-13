"""Typed hetero-graph construction, relations, and GraphSAGE tests (Phase 6)."""

from __future__ import annotations

import numpy as np
import polars as pl
import pytest

from graphroute_ts.graph import HeteroGraph
from graphroute_ts.graphsage import HeteroGraphSAGE, random_series_embeddings


def _entities() -> pl.DataFrame:
    # i1,i2 in cat C1/dept D1; i3,i4 in cat C2/dept D2; stores S1(X), S2(Y)
    rows = [
        ("i1_S1", "i1", "D1", "C1", "S1", "X"),
        ("i1_S2", "i1", "D1", "C1", "S2", "Y"),
        ("i2_S1", "i2", "D1", "C1", "S1", "X"),
        ("i2_S2", "i2", "D1", "C1", "S2", "Y"),
        ("i3_S1", "i3", "D2", "C2", "S1", "X"),
        ("i4_S2", "i4", "D2", "C2", "S2", "Y"),
    ]
    return pl.DataFrame(
        rows, schema=["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"], orient="row"
    )


@pytest.fixture
def graph():
    return HeteroGraph.from_entities(_entities())


def _sid(graph, name):  # entities are sorted by id
    return ["i1_S1", "i1_S2", "i2_S1", "i2_S2", "i3_S1", "i4_S2"].index(name)


@pytest.mark.unit
def test_same_item_across_stores(graph):
    s = _sid(graph, "i1_S1")
    got = set(graph.related(s, "same_item").tolist())
    assert got == {_sid(graph, "i1_S2")}  # same item, other store


@pytest.mark.unit
def test_same_store(graph):
    s = _sid(graph, "i1_S1")  # store S1
    got = set(graph.related(s, "same_store").tolist())
    assert got == {_sid(graph, "i2_S1"), _sid(graph, "i3_S1")}


@pytest.mark.unit
def test_same_category(graph):
    s = _sid(graph, "i1_S1")  # cat C1
    got = set(graph.related(s, "same_category").tolist())
    assert got == {_sid(graph, "i1_S2"), _sid(graph, "i2_S1"), _sid(graph, "i2_S2")}


@pytest.mark.unit
def test_relation_weighted_prefers_same_item(graph):
    s = _sid(graph, "i1_S1")
    order = graph.related(s, "relation_weighted")
    # same item (i1_S2) shares item+cat+dept -> should rank first
    assert order[0] == _sid(graph, "i1_S2")


@pytest.mark.unit
def test_shortest_path_near_before_far(graph):
    s = _sid(graph, "i1_S1")
    order = graph.related(s, "shortest_path").tolist()
    near = {_sid(graph, "i1_S2"), _sid(graph, "i2_S1")}  # same item or same store
    # all near appear before any far (cat/dept-only) member
    near_pos = [order.index(x) for x in near if x in order]
    assert near_pos and max(near_pos) < len(order)


@pytest.mark.unit
def test_random_neighbor_deterministic(graph):
    s = _sid(graph, "i1_S1")
    a = graph.related(s, "random_neighbor", rng=np.random.default_rng(0))
    b = graph.related(s, "random_neighbor", rng=np.random.default_rng(0))
    assert list(a) == list(b)


@pytest.mark.unit
def test_graphsage_deterministic(graph):
    e1 = HeteroGraphSAGE(graph, dim=16, seed=1).embed_series()
    e2 = HeteroGraphSAGE(graph, dim=16, seed=1).embed_series()
    assert np.allclose(e1, e2)
    assert e1.shape == (6, 16)


@pytest.mark.unit
def test_graphsage_captures_structure(graph):
    # untrained SAGE: same-category series should be more similar on average than
    # cross-category pairs (structure, not noise).
    emb = HeteroGraphSAGE(graph, dim=32, seed=3).embed_series()
    c1 = [_sid(graph, x) for x in ("i1_S1", "i1_S2", "i2_S1", "i2_S2")]
    c2 = [_sid(graph, x) for x in ("i3_S1", "i4_S2")]
    within = np.mean([emb[i] @ emb[j] for i in c1 for j in c1 if i != j])
    across = np.mean([emb[i] @ emb[j] for i in c1 for j in c2])
    assert within > across


@pytest.mark.unit
def test_random_embeddings_control_normalised():
    e = random_series_embeddings(6, dim=16, seed=0)
    assert e.shape == (6, 16)
    assert np.allclose(np.linalg.norm(e, axis=1), 1.0, atol=1e-5)
