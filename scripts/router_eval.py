#!/usr/bin/env python3
"""Learned relation-aware retrieval routing (Phase 7).

Trains candidate-ranking routers on forecast-utility labels from HISTORICAL
origins (d_1830-1857, d_1858-1885) and evaluates on val (d_1886-1913); test
(d_1914-1941) untouched. Compares temporal-only / metadata-only / relation-aware
routers vs the frozen Phase 5 baseline, with shuffled-relation and random-label
controls, ranking metrics (task 7), and slice analysis. Negatives preserved.

    uv run python scripts/router_eval.py --subset 1000 --seed 42
"""

from __future__ import annotations

# ruff: noqa: N806
import argparse
import json
import resource
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from graphroute_ts import metrics, router  # noqa: E402
from graphroute_ts.eval import load_processed, select_subset  # noqa: E402
from graphroute_ts.graph import HeteroGraph  # noqa: E402
from graphroute_ts.reproducibility import RunContext, set_seed  # noqa: E402
from graphroute_ts.splits import make_rolling_splits, split_by_name  # noqa: E402

QL = [0.1, 0.3, 0.5, 0.7, 0.9]
K, POOL, H = 20, 80, 28
LABEL_ORIGINS = [1829, 1857]  # val_m2, val_m1 train_ends; eval origin = 1885 (val)


def build_pools(n, seed, size):
    rng = np.random.default_rng(seed)
    pools = []
    for t in range(n):
        c = rng.choice(n - 1, size=min(size, n - 1), replace=False)
        c[c >= t] += 1  # exclude self
        pools.append(c)
    return pools


def score(name, pred, quants, sales, split, mask=None, extra=None):
    idx = np.arange(pred.shape[0]) if mask is None else np.flatnonzero(mask)
    ha = sales[:, split.h_start - 1 : split.h_end]
    tr = sales[:, : split.train_end]
    out = {
        "config": name,
        "rmsse": float(np.nanmean([metrics.rmsse(ha[i], pred[i], tr[i]) for i in idx])),
        "mase": float(np.nanmean([metrics.mase(ha[i], pred[i], tr[i]) for i in idx])),
        "wape": metrics.wape(ha[idx].ravel(), pred[idx].ravel()),
        "mae": metrics.mae(ha[idx].ravel(), pred[idx].ravel()),
        "pinball": float(np.nanmean([metrics.pinball_loss(ha[i], quants[i], QL) for i in idx])),
        "n": len(idx),
    }
    if extra:
        out.update(extra)
    return out


def ndcg_at_k(true_u, order, k):
    rel = np.maximum(true_u, 0.0)
    disc = 1.0 / np.log2(np.arange(2, k + 2))
    dcg = (rel[order[:k]] * disc).sum()
    idcg = (np.sort(rel)[::-1][:k] * disc).sum()
    return dcg / idcg if idcg > 0 else np.nan


def ranking_metrics(pred_u, true_u, k):
    order = np.argsort(-pred_u, kind="stable")
    ben = true_u > 0
    nben = ben.sum()
    recall = ben[order[:k]].sum() / min(k, nben) if nben > 0 else np.nan
    pct = (true_u[order[:k]] > 0).mean()
    # Spearman via rank correlation
    pr = np.argsort(np.argsort(pred_u))
    trk = np.argsort(np.argsort(true_u))
    corr = np.corrcoef(pr, trk)[0, 1] if len(pred_u) > 2 else np.nan
    return recall, ndcg_at_k(true_u, order, k), pct, corr


def router_forecast_all(model, mask, stats_e, graph, pools, n, perturb_relation=False, rng=None):
    pts, qs = [], []
    for t in range(n):
        c = pools[t]
        feats = router.features(stats_e, graph, t, c)
        if perturb_relation:
            perm = rng.permutation(len(c))
            feats[:, :6] = feats[perm, :6]  # shuffle relation columns
        pu = model.predict(feats[:, mask])
        p, s = router.router_forecast(stats_e, t, c, pu, K, H)
        pts.append(p)
        if s.ndim == 2 and s.shape[0] > 1:
            qs.append(np.clip(np.quantile(s, QL, axis=0).T, 0.0, None))  # (H, len(QL))
        else:
            qs.append(np.repeat(p[:, None], len(QL), axis=1))
    return np.stack(pts), np.stack(qs)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--subset", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    set_seed(args.seed)
    import lightgbm as lgb

    entities, dynamic = load_processed(REPO / "data" / "processed")
    entities, dynamic = select_subset(entities, dynamic, args.subset, args.seed)
    n = entities.height
    n_days = int(dynamic["day_idx"].max())
    sales = dynamic["sales"].to_numpy().astype(np.float64).reshape(n, n_days)
    split = split_by_name(make_rolling_splits(), "val")
    graph = HeteroGraph.from_entities(entities)
    pools = build_pools(n, args.seed, POOL)

    # --- labels from historical origins only (task 1) ---
    t0 = time.perf_counter()
    Xtr, ytr = [], []
    for o in LABEL_ORIGINS:
        st = router.origin_stats(sales, o)
        for t in range(n):
            c = pools[t]
            Xtr.append(router.features(st, graph, t, c))
            ytr.append(router.utility(st, t, c))
    X = np.vstack(Xtr)
    y = np.concatenate(ytr)
    label_ms = 1000 * (time.perf_counter() - t0)

    def train(mask, labels):
        m = lgb.LGBMRegressor(
            n_estimators=300,
            num_leaves=31,
            learning_rate=0.05,
            min_child_samples=50,
            verbose=-1,
            random_state=args.seed,
        )
        m.fit(X[:, mask], labels)
        return m

    masks = {g: router.feature_group_mask(g) for g in ("temporal", "metadata", "all")}
    models = {g: train(masks[g], y) for g in masks}
    rng = np.random.default_rng(args.seed)
    model_randlabel = train(masks["all"], rng.permutation(y))

    stats_e = router.origin_stats(sales, split.train_end)
    results = []

    # baseline: recent-mean
    rm = np.clip(np.stack([np.full(H, stats_e.mean[t]) for t in range(n)]), 0.0, None)
    rmq = np.repeat(rm[:, :, None], len(QL), axis=2)
    results.append(score("baseline:recent_mean", rm, rmq, sales, split))

    # learned routers + ranking metrics
    true_u = [router.utility(stats_e, t, pools[t]) for t in range(n)]
    router_preds = {}
    for g in ("temporal", "metadata", "all"):
        pts, qs = router_forecast_all(models[g], masks[g], stats_e, graph, pools, n)
        rk = np.array(
            [
                ranking_metrics(
                    models[g].predict(router.features(stats_e, graph, t, pools[t])[:, masks[g]]),
                    true_u[t],
                    K,
                )
                for t in range(n)
            ]
        )
        extra = {
            "recall@20": float(np.nanmean(rk[:, 0])),
            "ndcg@20": float(np.nanmean(rk[:, 1])),
            "pct_improve": float(np.nanmean(rk[:, 2])),
            "util_corr": float(np.nanmean(rk[:, 3])),
        }
        name = {
            "temporal": "router:temporal_only",
            "metadata": "router:metadata_only",
            "all": "router:relation_aware",
        }[g]
        results.append(score(name, pts, qs, sales, split, extra=extra))
        router_preds[g] = (pts, qs)

    # controls
    pts, qs = router_forecast_all(
        models["all"],
        masks["all"],
        stats_e,
        graph,
        pools,
        n,
        perturb_relation=True,
        rng=np.random.default_rng(0),
    )
    results.append(score("CONTROL:shuffled_relation", pts, qs, sales, split))
    pts, qs = router_forecast_all(model_randlabel, masks["all"], stats_e, graph, pools, n)
    results.append(score("CONTROL:random_label", pts, qs, sales, split))

    # slices (task 6)
    tr = sales[:, : split.train_end]
    slices = {
        "intermittent(z>0.8)": (tr == 0).mean(1) > 0.8,
        "low_volume(<median)": tr.mean(1) < np.median(tr.mean(1)),
        "reduced_history(<100nz)": (tr != 0).sum(1) < 100,
    }
    ra_pts, ra_qs = router_preds["all"]
    to_pts, to_qs = router_preds["temporal"]
    slice_report = {}
    for sn, sm in slices.items():
        if sm.sum() == 0:
            continue
        slice_report[sn] = {
            "n": int(sm.sum()),
            "temporal_only": score("x", to_pts, to_qs, sales, split, mask=sm)["rmsse"],
            "relation_aware": score("x", ra_pts, ra_qs, sales, split, mask=sm)["rmsse"],
        }

    prof = {
        "peak_rss_gib": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 / 1024, 2),
        "label_gen_ms": round(label_ms),
        "train_rows": len(y),
        "gpu_vram_gib": 0.0,
    }
    best = min(
        [r for r in results if not r["config"].startswith("CONTROL")], key=lambda r: r["rmsse"]
    )
    report = {
        "phase": "7-learned-router",
        "timestamp": datetime.now(UTC).isoformat(),
        "subset": n,
        "seed": args.seed,
        "split": split.as_dict(),
        "results": results,
        "best_by_rmsse": best["config"],
        "slices": slice_report,
        "profiling": prof,
        "run_context": RunContext().to_dict(),
    }
    out = REPO / "reports" / f"router-subset{n}.json"
    out.write_text(json.dumps(report, indent=2, default=str))

    print(
        f"\n{'config':30s} {'RMSSE':>7s} {'MASE':>7s} {'WAPE':>7s} {'recall@20':>10s} "
        f"{'ndcg@20':>8s} {'util_corr':>10s}"
    )
    for r in sorted(results, key=lambda x: x["rmsse"]):
        print(
            f"{r['config']:30s} {r['rmsse']:7.4f} {r['mase']:7.4f} {r['wape']:7.4f} "
            f"{r.get('recall@20', float('nan')):10.3f} {r.get('ndcg@20', float('nan')):8.3f} "
            f"{r.get('util_corr', float('nan')):10.3f}"
        )
    print(f"\nBEST (non-control): {best['config']}")
    print("Slices (RMSSE  temporal_only -> relation_aware):")
    for sn, d in slice_report.items():
        print(f"  {sn:26s} n={d['n']:4d}  {d['temporal_only']:.4f} -> {d['relation_aware']:.4f}")
    print(f"profiling: {prof} | report={out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
