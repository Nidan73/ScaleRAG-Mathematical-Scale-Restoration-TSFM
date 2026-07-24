#!/usr/bin/env python3
"""Generate the SYNTHETIC example corpus for the demo Space (no real data).

Retail-like daily series with varied scales, weekly seasonality, mild trend, and
some intermittency — enough for the retrieval + gate demo. Deterministic (seeded).
Emits ``synthetic_retail.csv`` with columns ``series_id,t,value``. This is fully
synthetic: it contains no M5, Favorita, or any real dataset values.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent / "synthetic_retail.csv"
N_SERIES, N_DAYS = 24, 420


def main() -> None:
    rng = np.random.default_rng(20260714)
    rows = ["series_id,t,value"]
    for s in range(N_SERIES):
        scale = float(rng.uniform(3, 300))
        trend = float(rng.uniform(-0.02, 0.05))
        weekly = rng.uniform(0.6, 1.4, size=7)
        intermittent = rng.random() < 0.35
        base = scale * (1 + trend * np.arange(N_DAYS) / 30.0)
        seasonal = weekly[np.arange(N_DAYS) % 7]
        noise = rng.normal(1.0, 0.15, size=N_DAYS)
        val = base * seasonal * noise
        if intermittent:
            val *= rng.random(N_DAYS) > 0.45  # zero-inflate
        val = np.clip(np.round(val), 0, None).astype(int)
        for t, v in enumerate(val):
            rows.append(f"series_{s:02d},{t},{v}")
    OUT.write_text("\n".join(rows) + "\n")
    print(f"wrote {OUT} ({N_SERIES} series x {N_DAYS} days)")


if __name__ == "__main__":
    main()
