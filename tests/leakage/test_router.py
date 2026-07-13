"""Learned-router feature/label tests + leakage guard (Phase 7, task 1)."""

from __future__ import annotations

import numpy as np
import polars as pl
import pytest

from graphroute_ts import router
from graphroute_ts.graph import HeteroGraph


def _entities(n):
    rows = [
        (f"s{i}", f"i{i % 5}", f"D{i % 3}", f"C{i % 2}", f"S{i % 4}", f"X{i % 2}") for i in range(n)
    ]
    return pl.DataFrame(
        rows, schema=["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"], orient="row"
    )


@pytest.fixture
def data():
    rng = np.random.default_rng(0)
    sales = rng.poisson(2.0, size=(20, 1941)).astype(float)
    graph = HeteroGraph.from_entities(_entities(20))
    return sales, graph


@pytest.mark.leakage
def test_label_and_eval_stats_never_read_test_period(data):
    # Corrupt every day in d_1914..d_1941 (indices 1913..1940). Stats at the label
    # origins (o<=1857) and the eval origin (o=1885) must be unchanged.
    sales, _graph = data
    corrupt = sales.copy()
    corrupt[:, 1913:] = 1e9
    for o in (1829, 1857, 1885):
        a = router.origin_stats(sales, o)
        b = router.origin_stats(corrupt, o)
        assert np.array_equal(a.actual, b.actual), f"origin {o} read the test period"
        assert np.array_equal(a.recent, b.recent)
        assert np.array_equal(a.mean, b.mean)


@pytest.mark.leakage
def test_utility_perfect_candidate_is_positive(data):
    sales, _graph = data
    # make candidate 1's recent block equal target 0's future, same mean scale
    o = 1857
    sales = sales.copy()
    sales[1, o - 28 : o] = sales[0, o : o + 28]
    sales[1, o - 56 : o] = sales[1, o - 56 : o].mean() * 0 + sales[0, o - 56 : o].mean()
    stats = router.origin_stats(sales, o)
    u = router.utility(stats, 0, np.array([1]))
    assert u[0] > 0  # a candidate matching the future beats the recent-mean base


@pytest.mark.unit
def test_features_deterministic_and_shaped(data):
    sales, graph = data
    stats = router.origin_stats(sales, 1857)
    cand = np.array([1, 2, 3, 4])
    f1 = router.features(stats, graph, 0, cand)
    f2 = router.features(stats, graph, 0, cand)
    assert f1.shape == (4, len(router.FEATURE_NAMES))
    assert np.array_equal(f1, f2)


@pytest.mark.unit
def test_feature_group_masks_partition():
    m_all = router.feature_group_mask("all")
    m_t = router.feature_group_mask("temporal")
    m_m = router.feature_group_mask("metadata")
    assert sorted(m_t + m_m) == m_all
    assert set(m_t).isdisjoint(m_m)
