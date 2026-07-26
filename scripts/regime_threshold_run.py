#!/usr/bin/env python3
"""Where does retrieval stop helping? A crossing threshold on M5 validation.

TS-RAG reports correlations between retrieval effectiveness and series properties
but names no value at which retrieval ceases to pay, leaving "retrieval sometimes
helps" as the state of the art. This estimates the crossing point.

Per series at the M5 **validation** origin (d_1886-1913) it computes retrieval
utility ``U = RMSSE(Chronos-2) - RMSSE(scale-restored retrieval)`` alongside the
six frozen gate diagnostics, then fits where ``P(U > 0)`` crosses one half.

Validation only. The test split d_1914-d_1941 is consumed and is never touched
(rule 2); nothing here selects or tunes a configuration (rules 9, 12) — the frozen
scale=mean / k=20 / cat_id retrieval is imported from `scripts/scalerag_eval.py`
rather than re-derived.

    uv run python scripts/regime_threshold_run.py --subset 1000
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts"))

import scalerag_eval as SE  # noqa: E402,N812 — frozen M5 retrieval + gate-feature defs
from graphroute_ts.eval import load_processed, select_subset  # noqa: E402
from graphroute_ts.regime import (  # noqa: E402
    estimate_band,
    estimate_threshold,
    utility_correlates,
)
from graphroute_ts.reproducibility import RunContext, set_seed  # noqa: E402
from graphroute_ts.splits import make_rolling_splits, split_by_name  # noqa: E402

OUT = REPO / "reports" / "regime-threshold"
LOCK = REPO / "M5_TEST_CONSUMED.lock"
FEATURES = [
    "retr_nn_dist",
    "retr_disagreement",
    "intermittency",
    "log_volume",
    "chronos_uncertainty",
    "scale_spread",
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--subset", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n-boot", type=int, default=1000)
    args = ap.parse_args()

    set_seed(args.seed)
    started = time.time()

    from graphroute_ts.tsfm.chronos2 import Chronos2Forecaster

    entities, dynamic = load_processed(REPO / "data" / "processed")
    entities, dynamic = select_subset(entities, dynamic, args.subset, args.seed)
    n = entities.height
    n_days = int(dynamic["day_idx"].max())
    sales = dynamic["sales"].to_numpy().astype(np.float64).reshape(n, n_days)

    splits = make_rolling_splits(last_labeled_day=n_days)
    o_eval = split_by_name(splits, "val").train_end
    test_start = split_by_name(splits, "test").train_end
    if o_eval >= test_start:
        raise SystemExit(
            f"refusing to run: eval origin {o_eval} reaches the consumed test split "
            f"(starts {test_start}). See {LOCK.name}."
        )

    fc = Chronos2Forecaster()
    queries = [sales[i, o_eval - SE.L : o_eval] for i in range(n)]
    c_pt, c_q = fc.forecast([sales[i, :o_eval] for i in range(n)], SE.H, SE.QL)
    c_pt = np.clip(c_pt, 0.0, None)
    r_pt, _r_q, nnd, dis = SE.retrieval_all(sales, entities, o_eval, queries, scale="mean")

    # Utility is positive where retrieval beat the frozen backbone on that series.
    rmsse_c = SE.rmsse_series(c_pt, sales, o_eval)
    rmsse_r = SE.rmsse_series(r_pt, sales, o_eval)
    finite = np.isfinite(rmsse_c) & np.isfinite(rmsse_r)
    if not finite.all():
        print(f"dropping {int((~finite).sum())} series with a non-finite RMSSE (flat history)")
    utility = (rmsse_c - rmsse_r)[finite]
    feats = SE.gate_features(sales, o_eval, nnd, dis, c_q)[finite]

    corr = utility_correlates(utility, feats, FEATURES)
    thresholds = {
        name: estimate_threshold(
            utility, feats[:, j], name, n_boot=args.n_boot, seed=args.seed
        ).to_dict()
        for j, name in enumerate(FEATURES)
    }

    # The diagnostics are not independent, so a marginal correlation with utility can
    # be inherited from a neighbour. Record the inter-diagnostic ranks so any
    # single-feature reading can be checked for confounding rather than trusted.
    from scipy.stats import spearmanr as _spearmanr

    feat_corr = {
        FEATURES[i]: {
            FEATURES[j]: float(_spearmanr(feats[:, i], feats[:, j]).statistic)
            for j in range(len(FEATURES))
            if j != i
        }
        for i in range(len(FEATURES))
    }

    # A single increasing threshold assumes retrieval keeps getting more useful.
    # Fit both edges so a non-monotone relationship is visible rather than hidden.
    bands = {
        name: estimate_band(
            utility, feats[:, j], name, n_boot=args.n_boot, seed=args.seed
        ).to_dict()
        for j, name in enumerate(FEATURES)
    }

    # Decile profile along intermittency: the headline regime axis.
    inter = feats[:, FEATURES.index("intermittency")]
    edges = np.quantile(inter, np.linspace(0, 1, 11))
    deciles = []
    for lo, hi in pairwise(edges):
        m = (inter >= lo) & (inter <= hi if hi == edges[-1] else inter < hi)
        if not m.any():
            continue
        deciles.append(
            {
                "intermittency_lo": float(lo),
                "intermittency_hi": float(hi),
                "n": int(m.sum()),
                "win_rate": float((utility[m] > 0).mean()),
                "mean_utility": float(utility[m].mean()),
            }
        )

    payload = {
        "experiment": "retrieval-utility-regime-threshold",
        "dataset": "M5",
        "split": "validation (d_1886-d_1913)",
        "guard": "test split d_1914-d_1941 is consumed and untouched (rule 2)",
        "note": "no configuration is selected or tuned; frozen retrieval imported from scalerag_eval",
        "n_series": int(utility.size),
        "subset": args.subset,
        "seed": args.seed,
        "eval_origin": int(o_eval),
        "frozen_retrieval": {
            "scale": "mean",
            "k": SE.K,
            "meta_filter": "cat_id",
            "L": SE.L,
            "H": SE.H,
        },
        "overall_win_rate": float((utility > 0).mean()),
        "mean_utility_rmsse": float(utility.mean()),
        "correlates": corr.to_dict(),
        "bands": bands,
        "diagnostic_intercorrelation_spearman": feat_corr,
        "thresholds": thresholds,
        "intermittency_deciles": deciles,
        "timestamp": datetime.now(UTC).isoformat(),
        "runtime_sec": round(time.time() - started, 2),
        "run_context": RunContext().to_dict(),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"m5-val-regime-threshold-{args.subset}.json"
    path.write_text(json.dumps(payload, indent=2))

    print(
        f"\nM5 val, {utility.size} series. Retrieval beats Chronos-2 on "
        f"{100 * (utility > 0).mean():.1f}% of them (mean dU = {utility.mean():+.4f} RMSSE)\n"
    )
    print(f"{'diagnostic':22s} {'spearman':>9s} {'threshold':>12s} {'win<':>7s} {'win>':>7s}")
    for j, name in enumerate(FEATURES):
        t = thresholds[name]
        thr = f"{t['threshold']:.4f}" if t["crosses_half"] else "no crossing"
        print(
            f"{name:22s} {corr.rho[j]:+9.3f} {thr:>12s} "
            f"{t['win_rate_below']:7.2f} {t['win_rate_above']:7.2f}"
        )
    print(f"\n{'diagnostic':22s} {'band lower':>12s} {'band upper':>12s} {'in':>6s} {'out':>6s}")
    for name in FEATURES:
        b = bands[name]
        lo = f"{b['lower']:.4f}" if b["lower"] is not None else "-inf"
        hi = f"{b['upper']:.4f}" if b["bounded_above"] else "none"
        print(
            f"{name:22s} {lo:>12s} {hi:>12s} {b['win_rate_inside']:6.2f} {b['win_rate_outside']:6.2f}"
        )
    print(f"\n{'intermittency band':>24s}  {'n':>5s}  {'win rate':>9s}  {'mean dU':>9s}")
    for d in deciles:
        band = f"{d['intermittency_lo']:.2f}-{d['intermittency_hi']:.2f}"
        print(f"{band:>24s}  {d['n']:5d}  {d['win_rate']:9.2f}  {d['mean_utility']:+9.4f}")
    print(f"\nwrote {path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
