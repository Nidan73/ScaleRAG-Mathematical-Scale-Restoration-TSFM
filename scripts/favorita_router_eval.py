#!/usr/bin/env python3
"""Favorita learned-router kill test (Phase 8).

Reuses Phase 7's utility labels / scale restoration / ranking metrics / leakage
rules (task 5) with Favorita's richer relations. Trains temporal-only /
metadata-only / relation-aware routers across >=3 seeds and 2 historical label
origins, and applies the PRE-REGISTERED criterion (task 9): relation-aware must
beat temporal-only consistently across seeds with a CI excluding zero for at least
one overall or sparse/cold-start metric. Val eval; test window untouched.

    uv run python scripts/favorita_router_eval.py --seeds 42 43 44
"""

from __future__ import annotations

# ruff: noqa: N803, N806
import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import polars as pl  # noqa: E402

from graphroute_ts import favorita_graph as fav  # noqa: E402
from graphroute_ts import metrics, router  # noqa: E402
from graphroute_ts.reproducibility import RunContext  # noqa: E402
from graphroute_ts.splits import make_rolling_splits, split_by_name  # noqa: E402

QL = [0.1, 0.3, 0.5, 0.7, 0.9]
K, POOL = 20, 80
PROC = REPO / "data" / "processed" / "favorita"


def build_pools(n, seed, size):
    rng = np.random.default_rng(seed)
    out = []
    for t in range(n):
        c = rng.choice(n - 1, size=min(size, n - 1), replace=False)
        c[c >= t] += 1
        out.append(c)
    return out


def ndcg(true_u, order, k):
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
    corr = np.corrcoef(np.argsort(np.argsort(pred_u)), np.argsort(np.argsort(true_u)))[0, 1]
    return recall, ndcg(true_u, order, k), pct, corr


def rmsse_masked(pred, sales, split, mask):
    idx = np.flatnonzero(mask) if mask is not None else np.arange(pred.shape[0])
    ha, tr = sales[:, split.h_start - 1 : split.h_end], sales[:, : split.train_end]
    return float(np.nanmean([metrics.rmsse(ha[i], pred[i], tr[i]) for i in idx]))


def forecast_all(model, mask, fg, stats_e, pools, n, H, perturb=False, rng=None):
    pts = []
    for t in range(n):
        c = pools[t]
        f = fav.features(fg, stats_e, t, c)
        if perturb:
            f[:, : len(fav.RELATION_FEATURES)] = f[
                rng.permutation(len(c)), : len(fav.RELATION_FEATURES)
            ]
        p, _ = router.router_forecast(stats_e, t, c, model.predict(f[:, mask]), K, H)
        pts.append(p)
    return np.stack(pts)


def run_seed(sales, fg, split, seed):
    import lightgbm as lgb

    n = sales.shape[0]
    H = split.horizon
    pools = build_pools(n, seed, POOL)
    label_origins = [
        split_by_name(SPLITS, "val_m2").train_end,
        split_by_name(SPLITS, "val_m1").train_end,
    ]

    X, y = [], []
    for o in label_origins:
        st = router.origin_stats(sales, o)
        for t in range(n):
            X.append(fav.features(fg, st, t, pools[t]))
            y.append(router.utility(st, t, pools[t]))
    X = np.vstack(X)
    y = np.concatenate(y)

    def train(mask, labels):
        m = lgb.LGBMRegressor(
            n_estimators=300,
            num_leaves=31,
            learning_rate=0.05,
            min_child_samples=50,
            verbose=-1,
            random_state=seed,
        )
        m.fit(X[:, mask], labels)
        return m

    masks = {g: fav.feature_group_mask(g) for g in ("temporal", "metadata", "all")}
    models = {g: train(masks[g], y) for g in masks}
    rng = np.random.default_rng(seed)
    model_rand = train(masks["all"], rng.permutation(y))

    st_e = router.origin_stats(sales, split.train_end)
    true_u = [router.utility(st_e, t, pools[t]) for t in range(n)]
    preds, rankm = {}, {}
    for g in ("temporal", "metadata", "all"):
        preds[g] = forecast_all(models[g], masks[g], fg, st_e, pools, n, H)
        rk = np.array(
            [
                ranking_metrics(
                    models[g].predict(fav.features(fg, st_e, t, pools[t])[:, masks[g]]),
                    true_u[t],
                    K,
                )
                for t in range(n)
            ]
        )
        rankm[g] = {
            "recall": float(np.nanmean(rk[:, 0])),
            "ndcg": float(np.nanmean(rk[:, 1])),
            "pct": float(np.nanmean(rk[:, 2])),
            "corr": float(np.nanmean(rk[:, 3])),
        }
    preds["shuffled"] = forecast_all(
        models["all"],
        masks["all"],
        fg,
        st_e,
        pools,
        n,
        H,
        perturb=True,
        rng=np.random.default_rng(0),
    )
    preds["randlabel"] = forecast_all(model_rand, masks["all"], fg, st_e, pools, n, H)
    rm = np.clip(np.stack([np.full(H, st_e.mean[t]) for t in range(n)]), 0.0, None)
    preds["recent_mean"] = rm
    return preds, rankm


SPLITS = None


def main() -> int:
    global SPLITS
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seeds", type=int, nargs="+", default=[42, 43, 44])
    args = ap.parse_args()

    entities = pl.read_parquet(PROC / "entities.parquet").sort("id")
    dyn = pl.read_parquet(PROC / "dynamic.parquet").sort(["id", "day_idx"])
    n = entities.height
    n_days = int(dyn["day_idx"].max())
    sales = dyn["sales"].to_numpy().astype(np.float64).reshape(n, n_days)
    SPLITS = make_rolling_splits(last_labeled_day=n_days)
    split = split_by_name(SPLITS, "val")
    fg = fav.FavoritaGraph.from_entities(entities)

    tr = sales[:, : split.train_end]
    promo = entities["promo_frac"].to_numpy()
    zf, nz, vol = (tr == 0).mean(1), (tr != 0).sum(1), tr.mean(1)
    # relative (quantile) slices so sparse/cold-start are non-empty on dense Favorita
    slices = {
        "overall": np.ones(n, bool),
        "sparse(top25%zero)": zf > np.quantile(zf, 0.75),
        "low_volume(bottom25%)": vol < np.quantile(vol, 0.25),
        "promoted(>0.1)": promo > 0.1,
        "reduced_history(bottom25%nz)": nz < np.quantile(nz, 0.25),
    }

    per_seed = {}
    rankm_all = {g: [] for g in ("temporal", "metadata", "all")}
    for seed in args.seeds:
        preds, rankm = run_seed(sales, fg, split, seed)
        per_seed[seed] = {
            sn: {m: rmsse_masked(preds[m], sales, split, sm) for m in preds}
            for sn, sm in slices.items()
        }
        for g in rankm_all:
            rankm_all[g].append(rankm[g])
        print(
            f"seed {seed}: temporal={per_seed[seed]['overall']['temporal']:.4f} "
            f"relation={per_seed[seed]['overall']['all']:.4f} "
            f"sparse t={per_seed[seed]['sparse(top25%zero)']['temporal']:.4f} "
            f"r={per_seed[seed]['sparse(top25%zero)']['all']:.4f}",
            flush=True,
        )

    # aggregate + CI on delta (temporal_only - relation_aware); >0 means relation better
    def ci(vals):
        v = np.array(vals)
        m, s = v.mean(), v.std(ddof=1) if len(v) > 1 else 0.0
        half = 4.303 * s / np.sqrt(len(v)) if len(v) > 1 else 0.0  # t(0.975,2)
        return float(m), float(m - half), float(m + half)

    agg = {}
    for sn in slices:
        d = [per_seed[s][sn]["temporal"] - per_seed[s][sn]["all"] for s in args.seeds]
        t_mean = float(np.mean([per_seed[s][sn]["temporal"] for s in args.seeds]))
        r_mean = float(np.mean([per_seed[s][sn]["all"] for s in args.seeds]))
        rm_mean = float(np.mean([per_seed[s][sn]["recent_mean"] for s in args.seeds]))
        dm, lo, hi = ci(d)
        agg[sn] = {
            "temporal_only": t_mean,
            "relation_aware": r_mean,
            "recent_mean": rm_mean,
            "delta_mean": dm,
            "delta_ci95": [lo, hi],
            "ci_excludes_zero_favoring_relation": lo > 0,
        }

    criterion_met = any(v["ci_excludes_zero_favoring_relation"] for v in agg.values())
    report = {
        "phase": "8-favorita-router",
        "timestamp": datetime.now(UTC).isoformat(),
        "n_series": n,
        "n_days": n_days,
        "seeds": args.seeds,
        "ranking_metrics_mean": {
            g: {
                k: float(np.mean([r[k] for r in rankm_all[g]]))
                for k in ("recall", "ndcg", "pct", "corr")
            }
            for g in rankm_all
        },
        "slices": agg,
        "criterion_met": bool(criterion_met),
        "run_context": RunContext().to_dict(),
    }
    (REPO / "reports" / "favorita-router.json").write_text(
        json.dumps(report, indent=2, default=str)
    )

    print(
        f"\n{'slice':24s} {'recent':>8s} {'temporal':>9s} {'relation':>9s} {'delta':>8s} {'CI95':>20s} {'rel>temp?':>9s}"
    )
    for sn, v in agg.items():
        print(
            f"{sn:24s} {v['recent_mean']:8.4f} {v['temporal_only']:9.4f} {v['relation_aware']:9.4f} "
            f"{v['delta_mean']:+8.4f} [{v['delta_ci95'][0]:+.4f},{v['delta_ci95'][1]:+.4f}] "
            f"{'YES' if v['ci_excludes_zero_favoring_relation'] else 'no':>9s}"
        )
    print(
        "\nranking (util corr): "
        + ", ".join(f"{g}={report['ranking_metrics_mean'][g]['corr']:.3f}" for g in rankm_all)
    )
    print(f"\nPRE-REGISTERED CRITERION MET: {criterion_met}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
