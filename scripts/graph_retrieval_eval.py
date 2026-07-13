#!/usr/bin/env python3
"""Graph-guided retrieval evaluation (Phase 6).

Compares recent-mean, the frozen Phase 5 temporal baseline (mean/l2/cat/k20 +
restore), graph-only retrieval (all relations), graph-embedding retrieval, and
hybrid graph+temporal, plus controls (shuffled edges/labels, removed relations,
random embeddings, top-k) and slice analysis (intermittent / low-volume /
reduced-history). Val split d_1886-d_1913; test untouched. RMSSE-selected.
Negative findings preserved.

    uv run python scripts/graph_retrieval_eval.py --subset 1000 --seed 42
"""

from __future__ import annotations

# ruff: noqa: N803, N806  -- H (horizon) is standard time-series notation
import argparse
import json
import resource
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import polars as pl

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from graphroute_ts import metrics  # noqa: E402
from graphroute_ts.eval import load_processed, select_subset  # noqa: E402
from graphroute_ts.graph import RELATIONS, HeteroGraph  # noqa: E402
from graphroute_ts.graph_retrieval import embedding_neighbors, graph_only_forecast  # noqa: E402
from graphroute_ts.graphsage import HeteroGraphSAGE, random_series_embeddings  # noqa: E402
from graphroute_ts.reproducibility import RunContext, set_seed  # noqa: E402
from graphroute_ts.retrieval import WindowDatabase  # noqa: E402
from graphroute_ts.retrieval_faiss import ScaleAwareIndex  # noqa: E402
from graphroute_ts.splits import make_rolling_splits, split_by_name  # noqa: E402

QL = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
L, MAXS = 56, 20  # context length, max related series


def score(name, pred, quants, sales, split, mask=None, extra=None):
    idx = np.arange(pred.shape[0]) if mask is None else np.flatnonzero(mask)
    ha = sales[:, split.h_start - 1 : split.h_end]
    tr = sales[:, : split.train_end]
    rmsse = float(np.nanmean([metrics.rmsse(ha[i], pred[i], tr[i]) for i in idx]))
    mase = float(np.nanmean([metrics.mase(ha[i], pred[i], tr[i]) for i in idx]))
    pin = float(np.nanmean([metrics.pinball_loss(ha[i], quants[i], QL) for i in idx]))
    out = {
        "config": name,
        "rmsse": rmsse,
        "mase": mase,
        "wape": metrics.wape(ha[idx].ravel(), pred[idx].ravel()),
        "mae": metrics.mae(ha[idx].ravel(), pred[idx].ravel()),
        "pinball": pin,
        "n": len(idx),
    }
    if extra:
        out.update(extra)
    return out


def graph_forecast_all(graph, index, queries, origin, H, relation, max_series, rng=None):
    t0 = time.perf_counter()
    pts, qs = [], []
    for i in range(len(queries)):
        rel = graph.related(i, relation, k=max_series, rng=rng)
        p, q = graph_only_forecast(index, queries[i], origin, H, QL, rel, max_series=max_series)
        pts.append(p)
        qs.append(q)
    return np.stack(pts), np.stack(qs), 1000 * (time.perf_counter() - t0)


def embedding_forecast_all(emb, index, queries, origin, H, m):
    t0 = time.perf_counter()
    pts, qs = [], []
    for i in range(len(queries)):
        nbr = embedding_neighbors(emb, i, m)
        p, q = graph_only_forecast(index, queries[i], origin, H, QL, nbr, max_series=m)
        pts.append(p)
        qs.append(q)
    return np.stack(pts), np.stack(qs), 1000 * (time.perf_counter() - t0)


def hybrid_forecast_all(graph, index, queries, origin, H, relation, max_series, k):
    t0 = time.perf_counter()
    pts, qs = [], []
    for i in range(len(queries)):
        rel = graph.related(i, relation, k=max_series)
        p, q = index.forecast(queries[i], origin, H, k, QL, query_series_idx=i, allowed_series=rel)
        pts.append(p)
        qs.append(q)
    return np.stack(pts), np.stack(qs), 1000 * (time.perf_counter() - t0)


def temporal_cat_all(index, queries, origin, H, k):
    t0 = time.perf_counter()
    pts, qs = [], []
    for i in range(len(queries)):
        p, q = index.forecast(
            queries[i], origin, H, k, QL, query_series_idx=i, meta_filter="cat_id"
        )
        pts.append(p)
        qs.append(q)
    return np.stack(pts), np.stack(qs), 1000 * (time.perf_counter() - t0)


def naive_recent_mean(queries, H):
    pt = np.clip(np.stack([np.full(H, q.mean()) for q in queries]), 0.0, None)
    return pt, np.repeat(pt[:, :, None], len(QL), axis=2)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--subset", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    set_seed(args.seed)

    entities, dynamic = load_processed(REPO / "data" / "processed")
    entities, dynamic = select_subset(entities, dynamic, args.subset, args.seed)
    n = entities.height
    n_days = int(dynamic["day_idx"].max())  # type: ignore[arg-type]
    sales = dynamic["sales"].to_numpy().astype(np.float64).reshape(n, n_days)
    split = split_by_name(make_rolling_splits(), "val")
    origin, H = split.h_start, split.horizon
    queries = [sales[i, split.train_end - L : split.train_end] for i in range(n)]

    db = WindowDatabase.from_training(sales, split.train_end, L, H, stride=7)
    idx = ScaleAwareIndex(db, entities, scale="mean", metric="l2")
    graph = HeteroGraph.from_entities(entities)

    results = []
    p, q = naive_recent_mean(queries, H)
    results.append(score("naive:recent_mean", p, q, sales, split))
    p, q, ms = temporal_cat_all(idx, queries, origin, H, 20)
    results.append(score("temporal:cat/k20 (Phase5)", p, q, sales, split, extra={"ms": round(ms)}))

    # graph-only per relation
    for rel in RELATIONS:
        p, q, ms = graph_forecast_all(
            graph, idx, queries, origin, H, rel, MAXS, rng=np.random.default_rng(args.seed)
        )
        results.append(score(f"graph_only:{rel}", p, q, sales, split, extra={"ms": round(ms)}))

    # graph-embedding retrieval (+ random-embedding control)
    emb = HeteroGraphSAGE(graph, dim=64, seed=args.seed).embed_series()
    p, q, ms = embedding_forecast_all(emb, idx, queries, origin, H, MAXS)
    results.append(score("graph_embedding:sage", p, q, sales, split, extra={"ms": round(ms)}))
    remb = random_series_embeddings(n, dim=64, seed=args.seed)
    p, q, _ = embedding_forecast_all(remb, idx, queries, origin, H, MAXS)
    results.append(score("CONTROL:random_embedding", p, q, sales, split))

    # hybrid graph pool + temporal ranking
    for rel in ("same_category", "relation_weighted"):
        p, q, ms = hybrid_forecast_all(graph, idx, queries, origin, H, rel, 200, 20)
        results.append(score(f"hybrid:{rel}+temporal", p, q, sales, split, extra={"ms": round(ms)}))

    # --- controls (task 8) ---
    rng = np.random.default_rng(args.seed)
    shuf = entities.with_columns(
        pl.Series("item_id", rng.permutation(entities["item_id"].to_numpy()))
    )
    g_shuf = HeteroGraph.from_entities(shuf)
    p, q, _ = graph_forecast_all(g_shuf, idx, queries, origin, H, "relation_weighted", MAXS)
    results.append(score("CONTROL:shuffled_item_edges", p, q, sales, split))
    nocat = entities.with_columns(pl.lit("C0").alias("cat_id"))
    g_nocat = HeteroGraph.from_entities(nocat)
    p, q, _ = graph_forecast_all(g_nocat, idx, queries, origin, H, "same_category", MAXS)
    results.append(score("CONTROL:removed_category", p, q, sales, split))
    nostore = entities.with_columns(pl.lit("S0").alias("store_id"))
    g_nostore = HeteroGraph.from_entities(nostore)
    p, q, _ = graph_forecast_all(g_nostore, idx, queries, origin, H, "same_store", MAXS)
    results.append(score("CONTROL:removed_store", p, q, sales, split))

    # top-k (max_series) sweep on best graph-only relation
    for ms_k in (3, 10, 50):
        p, q, _ = graph_forecast_all(graph, idx, queries, origin, H, "relation_weighted", ms_k)
        results.append(score(f"graph_only:relation_weighted/m{ms_k}", p, q, sales, split))

    # --- slice analysis (task 12) ---
    tr = sales[:, : split.train_end]
    zero_frac = (tr == 0).mean(1)
    vol = tr.mean(1)
    slices = {
        "intermittent(z>0.8)": zero_frac > 0.8,
        "low_volume(<median)": vol < np.median(vol),
        "reduced_history(<100nz)": (tr != 0).sum(1) < 100,
    }
    # best graph method so far vs temporal baseline, per slice
    best_graph = min(
        [r for r in results if r["config"].startswith(("graph", "hybrid"))],
        key=lambda r: r["rmsse"],
    )
    tp, tq, _ = temporal_cat_all(idx, queries, origin, H, 20)
    if best_graph["config"].startswith("hybrid"):
        bp, bq, _ = hybrid_forecast_all(
            graph, idx, queries, origin, H, "relation_weighted", 200, 20
        )
    else:
        best_rel = best_graph["config"].split(":")[1].split("/")[0]
        bp, bq, _ = graph_forecast_all(graph, idx, queries, origin, H, best_rel, MAXS)
    slice_report = {}
    for sname, smask in slices.items():
        if smask.sum() == 0:
            continue
        t = score("t", tp, tq, sales, split, mask=smask)
        b = score("g", bp, bq, sales, split, mask=smask)
        slice_report[sname] = {
            "n": int(smask.sum()),
            "temporal_rmsse": t["rmsse"],
            "best_graph_rmsse": b["rmsse"],
            "best_graph": best_graph["config"],
        }

    profiling = {
        "peak_rss_gib": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 / 1024, 2),
        "gpu_vram_gib": 0.0,
        "db_candidates": len(db),
    }
    best = min(
        [r for r in results if not r["config"].startswith("CONTROL")], key=lambda r: r["rmsse"]
    )
    report = {
        "phase": "6-graph-retrieval",
        "timestamp": datetime.now(UTC).isoformat(),
        "subset": n,
        "seed": args.seed,
        "split": split.as_dict(),
        "results": results,
        "best_by_rmsse": best["config"],
        "slices": slice_report,
        "profiling": profiling,
        "run_context": RunContext().to_dict(),
    }
    out = REPO / "reports" / f"graph-retrieval-subset{n}.json"
    out.write_text(json.dumps(report, indent=2, default=str))

    print(f"\n{'config':40s} {'RMSSE':>7s} {'MASE':>7s} {'WAPE':>7s} {'MAE':>7s} {'pinball':>8s}")
    for r in sorted(results, key=lambda x: x["rmsse"]):
        print(
            f"{r['config']:40s} {r['rmsse']:7.4f} {r['mase']:7.4f} {r['wape']:7.4f} "
            f"{r['mae']:7.4f} {r['pinball']:8.4f}"
        )
    print(f"\nBEST (non-control, val RMSSE): {best['config']}")
    print("\nSlice analysis (RMSSE):")
    for s, d in slice_report.items():
        print(
            f"  {s:26s} n={d['n']:4d}  temporal={d['temporal_rmsse']:.4f}  "
            f"{d['best_graph']}={d['best_graph_rmsse']:.4f}"
        )
    print(f"\nprofiling: {profiling} | report={out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
