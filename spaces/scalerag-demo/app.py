"""ScaleRAG-TS — research demo (Gradio Space).

Illustrates scale-aware retrieval augmentation of a **frozen** Chronos-2 backbone
with a learned gated fusion. This is RESEARCH SOFTWARE for illustration; it is not
a product and does not reproduce the paper's exact reported numbers. The official
`amazon/chronos-2` checkpoint (Apache-2.0) is loaded from the Hugging Face Hub — no
Chronos-2 weights are redistributed by this Space. Example data is synthetic; no
M5, Favorita, or Kaggle data or credentials are used or distributed.
"""

# ruff: noqa: N806  # L (time-series context length) is standard notation
from __future__ import annotations

from pathlib import Path

import gradio as gr
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scalerag_lite import LogisticGate, build_windows, fuse, gate_feature_row, retrieve

matplotlib.use("Agg")  # headless rendering (set before any figure is drawn)

HERE = Path(__file__).resolve().parent
EXAMPLE_CSV = HERE / "examples" / "synthetic_retail.csv"

REPO_URL = "https://github.com/Nidan73/ScaleRAG-Mathematical-Scale-Restoration-TSFM"
PAPER_URL = (
    "https://github.com/Nidan73/ScaleRAG-Mathematical-Scale-Restoration-TSFM"
    "/blob/main/docs/paper-outline.md"
)

MODEL_NAME = "amazon/chronos-2"
MAX_SERIES = 200  # keep the demo lightweight
_PIPE = None


def _load_pipe():
    """Lazily load the frozen Chronos-2 pipeline from the Hub (Apache-2.0)."""
    global _PIPE
    if _PIPE is None:
        import torch
        from chronos import BaseChronosPipeline

        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.bfloat16 if device == "cuda" else torch.float32
        _PIPE = BaseChronosPipeline.from_pretrained(
            MODEL_NAME, device_map=device, torch_dtype=dtype
        )
    return _PIPE


def _chronos(contexts: list[np.ndarray], h: int):
    pipe = _load_pipe()
    q, mean = pipe.predict_quantiles(
        [c.astype("float32") for c in contexts],
        prediction_length=h,
        quantile_levels=[0.1, 0.5, 0.9],
    )
    pt = np.stack([t[0].float().cpu().numpy() for t in mean])
    qq = np.stack([t[0].float().cpu().numpy() for t in q])  # (n, h, 3)
    return np.clip(pt, 0.0, None), qq


def _parse_csv(path: str) -> dict[str, np.ndarray]:
    df = pd.read_csv(path)
    cols = {c.lower(): c for c in df.columns}
    sid = cols.get("series_id") or cols.get("id") or cols.get("series")
    val = cols.get("value") or cols.get("sales") or cols.get("y")
    if sid is None or val is None:
        raise gr.Error("CSV needs a 'series_id' column and a 'value' column.")
    order = cols.get("t") or cols.get("date") or cols.get("step")
    corpus: dict[str, np.ndarray] = {}
    for name, g in df.groupby(sid):
        gg = g.sort_values(order) if order else g
        corpus[str(name)] = gg[val].to_numpy(dtype=float)
    return dict(list(corpus.items())[:MAX_SERIES])


def run_demo(csv_file, target_series, horizon, context_len, k):
    h, L, k = int(horizon), int(context_len), int(k)
    path = csv_file.name if csv_file is not None else str(EXAMPLE_CSV)
    corpus = _parse_csv(path)
    if target_series not in corpus:
        target_series = next(iter(corpus))
    target = corpus[target_series]
    if len(target) < L + h:
        raise gr.Error(
            f"Series '{target_series}' too short: need >= {L + h} points, got {len(target)}."
        )

    origin = len(target) - h  # forecast the last h points so actuals can be shown
    hist_origin = origin - h  # a historical origin for gate fitting
    query = target[origin - L : origin]
    actuals = target[origin : origin + h]

    # --- forecasts at the origin ---
    c_pt, c_q = _chronos([target[:origin]], h)
    chronos_pt, c_lo, c_hi = c_pt[0], c_q[0, :, 0], c_q[0, :, 2]
    windows = build_windows(corpus, origin, L, h)
    r = retrieve(query, windows, k)

    # --- gate: fit on the uploaded corpus at a historical origin (paper procedure) ---
    gate = LogisticGate()
    if hist_origin >= L + h:
        long_series = [s for s in corpus.values() if len(s) >= hist_origin]
        if len(long_series) >= 20:
            hc_pt, hc_q = _chronos([s[:hist_origin] for s in long_series], h)
            hwins = build_windows(corpus, hist_origin, L, h)
            X, y = [], []
            for i, s in enumerate(long_series):
                hr = retrieve(s[hist_origin - L : hist_origin], hwins, k)
                act = s[hist_origin : hist_origin + h]
                X.append(
                    gate_feature_row(
                        s[hist_origin - L : hist_origin],
                        hr.nn_dist,
                        hr.disagreement,
                        hc_q[i, :, 0],
                        hc_q[i, :, 2],
                    )
                )
                y.append(int(np.mean((act - hr.point) ** 2) < np.mean((act - hc_pt[i]) ** 2)))
            gate.fit(np.array(X), np.array(y, dtype=float))
    alpha = gate.alpha(gate_feature_row(query, r.nn_dist, r.disagreement, c_lo, c_hi))
    scalerag_pt = fuse(chronos_pt, r.point, alpha)

    def _rmse(p):
        return float(np.sqrt(np.mean((actuals - p) ** 2)))

    # --- plot A: forecast comparison ---
    show = min(origin, 3 * L)
    hx = np.arange(origin - show, origin)
    fx = np.arange(origin, origin + h)
    figA, axA = plt.subplots(figsize=(9, 4))
    axA.plot(hx, target[origin - show : origin], color="#555", lw=1, label="history")
    axA.axvline(origin - 0.5, color="#bbb", ls=":", lw=1)
    axA.plot(fx, actuals, color="#111", lw=2, marker="o", ms=3, label="actual")
    axA.fill_between(fx, c_lo, c_hi, color="#4c78a8", alpha=0.18, label="Chronos-2 80% band")
    axA.plot(
        fx,
        chronos_pt,
        color="#4c78a8",
        lw=2,
        ls="--",
        label=f"Chronos-2 (RMSE {_rmse(chronos_pt):.2f})",
    )
    axA.plot(
        fx, scalerag_pt, color="#e45756", lw=2.2, label=f"ScaleRAG (RMSE {_rmse(scalerag_pt):.2f})"
    )
    axA.set_title(f"'{target_series}' — forecast horizon = {h}")
    axA.legend(fontsize=8, loc="upper left")
    figA.tight_layout()

    # --- plot B: retrieved historical contexts (scale-restored continuations) ---
    figB, axB = plt.subplots(figsize=(9, 4))
    for cont in r.restored:
        axB.plot(fx, cont, color="#54a24b", lw=0.8, alpha=0.5)
    axB.plot(fx, r.point, color="#2a6f2a", lw=2.4, label="retrieval mean")
    axB.plot(np.arange(origin - L, origin), query, color="#333", lw=1.5, label="target context")
    axB.axvline(origin - 0.5, color="#bbb", ls=":", lw=1)
    axB.set_title(f"{k} retrieved analog windows (scale-restored) from {len(windows)} candidates")
    axB.legend(fontsize=8, loc="upper left")
    figB.tight_layout()

    src = "learned on your corpus" if gate.fitted else "fallback fixed 0.5 (too little data to fit)"
    gate_md = (
        f"### Learned gate weight alpha = **{alpha:.3f}**\n"
        f"- alpha weights **retrieval**; **(1 - alpha) = {1 - alpha:.3f}** weights **Chronos-2**.\n"
        f"- Gate source: {src}.\n"
        f"- Retrieval nn-distance = {r.nn_dist:.3f}, disagreement = {r.disagreement:.3f}, "
        f"intermittency = {np.mean(query == 0):.2f}.\n\n"
        f"**Horizon RMSE** -- Chronos-2 {_rmse(chronos_pt):.3f} / ScaleRAG {_rmse(scalerag_pt):.3f} "
        f"({'ScaleRAG better' if _rmse(scalerag_pt) < _rmse(chronos_pt) else 'Chronos better'} on this series)."
    )
    return figA, figB, gate_md


DISCLAIMER = f"""
# ScaleRAG-TS — research demo 🔬
**Scale-Aware Retrieval Augmentation for Time-Series Foundation Models.**
Augments a **frozen** [`{MODEL_NAME}`](https://huggingface.co/{MODEL_NAME}) backbone with
scale-aware temporal retrieval + a learned uncertainty-aware gated fusion.

> ⚠️ **Research software — not a product.** Illustrative only; it does **not** reproduce
> the paper's exact reported metrics. The frozen Chronos-2 checkpoint is loaded from the
> Hub (Apache-2.0) and **not redistributed** here. The bundled example data is **synthetic**
> — no M5, Favorita, or Kaggle data or credentials are included.

**Upload a CSV** with columns `series_id`, `value` (optional `t`/`date` for ordering), or use
the bundled synthetic example. The last *horizon* points of the chosen series are held out so
you can compare forecasts against the actuals.

[📄 Paper]({PAPER_URL}) · [💻 Code repository]({REPO_URL})
"""


def _build_ui() -> gr.Blocks:
    example_series = list(_parse_csv(str(EXAMPLE_CSV))) if EXAMPLE_CSV.exists() else []
    with gr.Blocks(title="ScaleRAG-TS demo") as demo:
        gr.Markdown(DISCLAIMER)
        with gr.Row():
            with gr.Column(scale=1):
                csv_in = gr.File(label="Time-series CSV (optional)", file_types=[".csv"])
                series_in = gr.Dropdown(
                    choices=example_series,
                    value=example_series[0] if example_series else None,
                    label="Target series",
                    allow_custom_value=True,
                )
                horizon_in = gr.Slider(7, 56, value=28, step=1, label="Forecast horizon (H)")
                ctx_in = gr.Slider(28, 112, value=56, step=7, label="Context length (L)")
                k_in = gr.Slider(3, 40, value=20, step=1, label="Retrieval neighbours (k)")
                run_btn = gr.Button("Forecast", variant="primary")
            with gr.Column(scale=2):
                gate_out = gr.Markdown()
                plotA = gr.Plot(label="Forecast: Chronos-2 vs ScaleRAG")
                plotB = gr.Plot(label="Retrieved historical analog windows")
        run_btn.click(
            run_demo,
            inputs=[csv_in, series_in, horizon_in, ctx_in, k_in],
            outputs=[plotA, plotB, gate_out],
        )
        if EXAMPLE_CSV.exists():
            gr.Examples(
                examples=[[str(EXAMPLE_CSV), s, 28, 56, 20] for s in example_series[:3]],
                inputs=[csv_in, series_in, horizon_in, ctx_in, k_in],
            )
    return demo


if __name__ == "__main__":
    _build_ui().launch()
