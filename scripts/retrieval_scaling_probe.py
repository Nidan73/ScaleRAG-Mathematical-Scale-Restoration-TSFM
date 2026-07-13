#!/usr/bin/env python3
"""Scaling profile for the strongest SCALABLE retrieval config (Phase 5, task 3).

The strongest config overall (mean/l2/cat_id/k20) uses per-query filtered search;
the near-equal **global** variant (mean/l2/global/k20) batches with FAISS and
scales. This probes index-build + retrieval latency + RMSSE + RAM at increasing
panel sizes on the val split (test untouched). Larger sizes use a coarser stride
so the candidate pool stays tractable.

    uv run python scripts/retrieval_scaling_probe.py
"""

from __future__ import annotations

import resource
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from graphroute_ts import metrics  # noqa: E402
from graphroute_ts.eval import load_processed, select_subset  # noqa: E402
from graphroute_ts.reproducibility import set_seed  # noqa: E402
from graphroute_ts.retrieval import WindowDatabase  # noqa: E402
from graphroute_ts.retrieval_faiss import ScaleAwareIndex, _fit_params, _transform  # noqa: E402
from graphroute_ts.splits import make_rolling_splits, split_by_name  # noqa: E402

QL = [0.5]
L, K = 56, 20


def rss_gib():
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 / 1024, 2)


def main() -> int:
    set_seed(42)
    entities_all, dynamic_all = load_processed(REPO / "data" / "processed")
    split = split_by_name(make_rolling_splits(), "val")
    # global exact search is O(queries x candidates); coarser stride keeps the pool
    # tractable. Full 30,490 is infeasible for exact global search on CPU (~2h) and
    # is profiled analytically in the report.
    plan = [(30490, 7)]  # full panel (1000/5000 already profiled)
    print(
        f"{'n':>6s} {'stride':>6s} {'cands':>10s} {'idx_ms':>8s} {'retr_ms':>9s} "
        f"{'RMSSE':>7s} {'RAM_GiB':>8s}",
        flush=True,
    )
    for size, stride in plan:
        ent, dyn = select_subset(entities_all, dynamic_all, size, 42)
        n = ent.height
        n_days = int(dyn["day_idx"].max())
        sales = dyn["sales"].to_numpy().astype(np.float64).reshape(n, n_days)
        q_arr = np.stack([sales[i, split.train_end - L : split.train_end] for i in range(n)])
        db = WindowDatabase.from_training(
            sales, split.train_end, L, horizon=split.horizon, stride=stride
        )

        t0 = time.perf_counter()
        idx = ScaleAwareIndex(db, ent, scale="mean", metric="l2")
        idx_ms = 1000 * (time.perf_counter() - t0)

        t0 = time.perf_counter()
        qp = _fit_params(q_arr, "mean")
        qv = _transform(q_arr, qp).astype(np.float32)
        _d, sel = idx.index.search(qv, K)
        conts = db.continuations[sel]
        cp = idx.params[sel]
        conts = (conts - cp[..., 0:1]) / cp[..., 1:2] * qp[:, None, 1:2] + qp[:, None, 0:1]
        pred = np.clip(conts.mean(1), 0.0, None)
        retr_ms = 1000 * (time.perf_counter() - t0)

        ha = sales[:, split.h_start - 1 : split.h_end]
        tr = sales[:, : split.train_end]
        rmsse = float(np.nanmean([metrics.rmsse(ha[i], pred[i], tr[i]) for i in range(n)]))
        print(
            f"{n:6d} {stride:6d} {len(db):10d} {idx_ms:8.0f} {retr_ms:9.0f} "
            f"{rmsse:7.4f} {rss_gib():8.2f}",
            flush=True,
        )
        del idx, db, conts, sel
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
