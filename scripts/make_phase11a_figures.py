#!/usr/bin/env python3
"""Publication figures for the ScaleRAG-TS native TS-RAG study (Phase 11A).

Every value is sourced from a real artifact — no fabricated numbers:

* ETTm2 dev/test grid + per-window preds  -> ``reports/phase11a/*``
* ETTm2 mechanism CIs + per-series wins    -> ``docs/scalerag-native-dev-results.json``
* compute / latency                        -> ``reports/phase11a/compute_*.json``
* M5 ablation (restoration, top-k)         -> ``docs/ablation-report.md`` (cited constants)
* M5 regime slices + cross-dataset utility -> ``reports/scalerag-heldout-val-30490.json``,
                                              ``reports/scalerag-favorita.json``
* fig1 / fig3 exemplar windows             -> reconstructed with the frozen retriever
                                              (:mod:`graphroute_ts.scalerag_native`)

Outputs vector PDFs to ``paper/figures/`` in IEEE/AII-style serif styling.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ettm2_data as E  # noqa: N812  (canonical helper; `E` matches sibling scripts)
from graphroute_ts.scalerag_native import NativeScaleRetriever

ROOT = Path(__file__).resolve().parents[1]
P11 = ROOT / "reports/phase11a"
FIG = ROOT / "paper/figures"

# ---- colour + style (high contrast, colour-blind aware) -----------------------------
C_QUERY = "#111111"
C_TRUE = "#111111"
C_BACKBONE = "#1f77b4"  # steel blue
C_SCALERAG = "#d62728"  # crimson
C_TSRAG = "#2ca02c"  # green
C_RAW = "#8c8c8c"  # grey
C_RESTORE = "#d62728"
PALETTE = ["#d62728", "#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd"]


def _style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Liberation Serif", "Times New Roman", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "axes.grid": True,
            "grid.alpha": 0.30,
            "grid.linestyle": "--",
            "grid.linewidth": 0.6,
            "font.size": 11,
            "axes.labelsize": 12,
            "axes.titlesize": 12,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 9.5,
            "figure.dpi": 150,
            "savefig.bbox": "tight",
            "pdf.fonttype": 42,  # embed editable TrueType (journal-safe)
            "ps.fonttype": 42,
            "axes.linewidth": 0.8,
        }
    )


# ---- shared data --------------------------------------------------------------------
def load_ettm2_test() -> dict:
    d = np.load(P11 / "scalerag_native_ettm2_test_preds.npz")
    tsrag = np.load(P11 / "repro_tsrag_official_ettm2.npz")["preds"].astype(np.float64)
    grid = json.loads((P11 / "scalerag_native_ettm2_test.json").read_text())
    dev = json.loads((ROOT / "docs/scalerag-native-dev-results.json").read_text())
    return {
        "trues": d["trues"].astype(np.float64),
        "var_of": d["var_of"],
        "chronos": d["chronos"].astype(np.float64),
        "res_mean_20": d["res_mean_20"].astype(np.float64),
        "tsrag": tsrag,
        "grid": grid,
        "dev": dev,
        "names": grid["variables"],
    }


def _pf(x: object) -> float:
    """Float a polars scalar (its stub return type is a broad union)."""
    return float(x)  # type: ignore[arg-type]


def build_retriever(scale: str, var: int) -> NativeScaleRetriever:
    z, _ = E.load_normalized()
    return NativeScaleRetriever(z[:, var], E.TRAIN_END, scale, E.L, E.H)


# ---- fig1: motivation ---------------------------------------------------------------
def fig1_motivation() -> None:
    """Query vs a raw-Euclidean candidate (scale mismatch) vs the restored candidate.

    Across the smoother ETTm2 channels, pick the real (query, top-1 candidate) pair whose
    candidate continuation best matches the query's future *shape* while differing most in
    *scale* — the exact case scale restoration is designed for.
    """
    z, names = E.load_normalized()
    scale = "rms"
    w = E.build_windows(z, "test")
    best: tuple[float, int, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray] | None = (
        None
    )
    for var in (6, 2, 0, 1):  # OT, MUFL, HUFL, HULL (smoother channels)
        retr = build_retriever(scale, var)
        m = w["var_of"] == var
        ctx, tru, org = w["contexts"][m], w["trues"][m], w["origins"][m]
        idx = np.arange(0, ctx.shape[0], 37)
        tk = retr.retrieve(ctx[idx], org[idx], 1)
        cid = tk.ids[:, 0]
        cont = retr.db.continuations[cid]  # (S, H) raw candidate continuations
        cp, qp = retr.params[cid], tk.qparams  # (S, 2)
        ratio = qp[:, 1] / cp[:, 1]
        a = cont - cont.mean(1, keepdims=True)
        b = tru[idx] - tru[idx].mean(1, keepdims=True)
        corr = (a * b).sum(1) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1) + 1e-9)
        logr = np.abs(np.log2(np.clip(ratio, 1e-3, None)))
        fvar = tru[idx].var(1)
        elig = (logr > 0.7) & (fvar > np.median(fvar)) & np.isfinite(corr)
        score = np.where(elig, corr, -np.inf)
        j = int(np.argmax(score))
        if np.isfinite(score[j]) and (best is None or score[j] > best[0]):
            best = (float(score[j]), var, ctx[idx[j]], tru[idx[j]], cont[j], cp[j], qp[j])
    assert best is not None, "no eligible shape-match/scale-gap window found"
    _, var, q_ctx, q_true, cand_cont, cp1, qp1 = best
    restored = (cand_cont - cp1[0]) / cp1[1] * qp1[1] + qp1[0]
    qp = qp1
    cp = cp1

    tail = 96
    hx = np.arange(-tail, 0)
    fx = np.arange(0, E.H)
    fig, ax = plt.subplots(1, 3, figsize=(11.5, 3.1), sharey=True)

    ax[0].plot(hx, q_ctx[-tail:], color=C_QUERY, lw=1.4, label="query context")
    ax[0].plot(fx, q_true, color=C_TRUE, lw=1.8, label="query future (truth)")
    ax[0].axvline(0, color="k", lw=0.6, ls=":")
    ax[0].set_title("(a) Query window", loc="left")
    ax[0].set_xlabel("step relative to forecast origin")
    ax[0].set_ylabel("normalized value")
    ax[0].legend(frameon=False, loc="upper left")

    ax[1].plot(fx, q_true, color=C_TRUE, lw=1.8, label="query future (truth)")
    ax[1].plot(fx, cand_cont, color=C_RAW, lw=1.8, ls="-", label="raw NN candidate")
    ax[1].set_title(
        f"(b) Raw Euclidean match  (rms $\\times${1 / (qp[1] / cp[1]):.2f})", loc="left"
    )
    ax[1].set_xlabel("horizon step")
    ax[1].legend(frameon=False, loc="upper left")

    ax[2].plot(fx, q_true, color=C_TRUE, lw=1.8, label="query future (truth)")
    ax[2].plot(fx, restored, color=C_RESTORE, lw=1.8, label="restored candidate")
    ax[2].set_title("(c) After scale restoration", loc="left")
    ax[2].set_xlabel("horizon step")
    ax[2].legend(frameon=False, loc="upper left")

    fig.suptitle(
        f"Scale restoration aligns a mis-scaled retrieved candidate (ETTm2 · channel {names[var]})",
        y=1.02,
        fontsize=12,
    )
    fig.savefig(FIG / "fig1_motivation.pdf")
    plt.close(fig)


# ---- fig2: ablation -----------------------------------------------------------------
# M5 ablation constants — source: docs/ablation-report.md (1,000-series val)
M5_NO_RESTORE = 2.7884
M5_RESTORE = 0.7425


def fig2_ablation() -> None:
    d = load_ettm2_test()
    per = d["dev"]["test_per_series"]["A_restoration"]["per_series"]
    labels = [r["var"] for r in per]
    raw = np.array([r["baseline_mse"] for r in per])
    res = np.array([r["method_mse"] for r in per])

    fig, (ax_l, ax_r) = plt.subplots(
        1, 2, figsize=(11.0, 3.6), gridspec_kw={"width_ratios": [2.4, 1]}
    )
    x = np.arange(len(labels))
    bw = 0.4
    ax_l.bar(x - bw / 2, raw, bw, color=C_RAW, label="raw retrieval (no restoration)")
    ax_l.bar(x + bw / 2, res, bw, color=C_RESTORE, label="scale-restored retrieval")
    ax_l.set_yscale("log")
    ax_l.set_xticks(x)
    ax_l.set_xticklabels(labels)
    ax_l.set_ylabel("retrieval MSE (log scale)")
    ax_l.set_xlabel("ETTm2 channel")
    ax_l.set_title(
        "(a) ETTm2 test: restoration cuts retrieval MSE  (+85.4% aggregate, 7/7)", loc="left"
    )
    ax_l.legend(frameon=False)
    ax_l.grid(axis="x", visible=False)

    xb = np.array([0, 1])
    bars = ax_r.bar(
        xb,
        [M5_NO_RESTORE, M5_RESTORE],
        0.6,
        color=[C_RAW, C_RESTORE],
    )
    ax_r.set_xticks(xb)
    ax_r.set_xticklabels(["no\nrestoration", "scale\nrestored"])
    ax_r.set_ylabel("M5 RMSSE")
    ax_r.set_title("(b) M5 (1k): 3.8$\\times$ worse\nwithout restoration", loc="left")
    for b, v in zip(bars, [M5_NO_RESTORE, M5_RESTORE], strict=True):
        ax_r.text(b.get_x() + b.get_width() / 2, v + 0.05, f"{v:.3f}", ha="center", fontsize=9.5)
    ax_r.grid(axis="x", visible=False)
    ax_r.set_ylim(0, M5_NO_RESTORE * 1.15)

    fig.suptitle("Scale restoration is decisive in both regimes", y=1.03, fontsize=12.5)
    fig.savefig(FIG / "fig2_ablation.pdf")
    plt.close(fig)


# ---- fig3: qualitative --------------------------------------------------------------
def fig3_qualitative() -> None:
    d = load_ettm2_test()
    z, names = E.load_normalized()
    scale, var, k = "mean", 6, 20  # OT: mid-scale, well-behaved channel
    retr = build_retriever(scale, var)
    w = E.build_windows(z, "test")
    m = w["var_of"] == var
    ctx, tru, org = w["contexts"][m], w["trues"][m], w["origins"][m]
    tot = int(w["tot"])
    # row offset of this channel in the canonical bundle (var outer, window inner)
    base_row = var * tot
    # pick a window with a clear, non-trivial future (above-median future variance)
    fut_var = tru.var(axis=1)
    order = np.argsort(-fut_var)
    s = int(order[order.size // 20])  # a high-variance but not extreme window
    q_ctx, q_true, q_org = ctx[s], tru[s], int(org[s])
    row = base_row + s

    tk = retr.retrieve(q_ctx[None, :], np.array([q_org]), k)
    ids3 = tk.ids[0, :3]
    conts = retr.db.continuations[ids3]
    cp, qp = retr.params[ids3], tk.qparams[0]
    restored3 = (conts - cp[:, 0:1]) / cp[:, 1:2] * qp[1] + qp[0]
    res_mean = d["res_mean_20"][row]
    chronos = d["chronos"][row]
    fused = 0.75 * chronos + 0.25 * res_mean  # frozen weight 0.25
    tsrag = d["tsrag"][row]

    fx = np.arange(0, E.H)
    tail = 96
    hx = np.arange(-tail, 0)
    fig, (ax_t, ax_b) = plt.subplots(2, 1, figsize=(7.6, 5.6), sharex=True)

    ax_t.plot(hx, q_ctx[-tail:], color=C_QUERY, lw=1.3)
    ax_t.plot(fx, q_true, color=C_TRUE, lw=2.0, label="ground truth")
    for i in range(3):
        ax_t.plot(
            fx, restored3[i], lw=1.2, color=PALETTE[i + 1], alpha=0.9, label=f"restored NN #{i + 1}"
        )
    ax_t.axvline(0, color="k", lw=0.6, ls=":")
    ax_t.set_title(
        f"(a) Query + top-3 scale-restored candidates  (ETTm2 · {names[var]})", loc="left"
    )
    ax_t.set_ylabel("normalized value")
    ax_t.legend(frameon=False, ncol=2, loc="upper left")

    ax_b.plot(hx, q_ctx[-tail:], color=C_QUERY, lw=1.3)
    ax_b.plot(fx, q_true, color=C_TRUE, lw=2.2, label="ground truth")
    ax_b.plot(fx, chronos, color=C_BACKBONE, lw=1.7, ls="--", label="Chronos-Bolt (target-only)")
    ax_b.plot(fx, tsrag, color=C_TSRAG, lw=1.4, ls=":", label="TS-RAG (official)")
    ax_b.plot(fx, fused, color=C_SCALERAG, lw=1.7, label="ScaleRAG (restored fusion)")
    ax_b.axvline(0, color="k", lw=0.6, ls=":")
    ax_b.set_title("(b) Forecasts vs ground truth", loc="left")
    ax_b.set_xlabel("step relative to forecast origin")
    ax_b.set_ylabel("normalized value")
    ax_b.legend(frameon=False, ncol=2, loc="upper left")

    fig.savefig(FIG / "fig3_qualitative.pdf")
    plt.close(fig)


# ---- fig4: regimes ------------------------------------------------------------------
def _zero_fraction(parquet: Path) -> pl.DataFrame:
    return (
        pl.scan_parquet(parquet)
        .select("id", "sales")
        .group_by("id")
        .agg((pl.col("sales") <= 0).mean().alias("zf"))
        .collect()
    )


def fig4_regimes() -> None:
    m5 = _zero_fraction(ROOT / "data/processed/dynamic.parquet")
    fav = _zero_fraction(ROOT / "data/processed/favorita/dynamic.parquet")
    m5_zf = m5["zf"]
    ettm2_zf = 0.0  # continuous channels, no zeros
    dev = json.loads((ROOT / "docs/scalerag-native-dev-results.json").read_text())
    ettm2_util = dev["test_mechanisms"]["C_vs_target"]["rel_mse_improvement"]

    # (x=mean zero-fraction, y=utility over target-only TSFM, label, colour, marker)
    # utility sources: reports/scalerag-heldout-val-30490.json (M5 overall+slices),
    #                  reports/scalerag-favorita.json (Favorita), Phase-11A dev (ETTm2)
    pts = [
        (
            _pf(m5_zf.filter(m5_zf > 0.8).mean()),
            0.05630,
            "M5 intermittent (z>0.8)",
            PALETTE[0],
            "o",
        ),
        (_pf(m5_zf.mean()), 0.05076, "M5 overall", PALETTE[1], "s"),
        (_pf(m5_zf.filter(m5_zf < 0.3).mean()), 0.00130, "M5 dense (z<0.3)", PALETTE[3], "^"),
        (_pf(fav["zf"].mean()), 0.008306, "Favorita", PALETTE[2], "D"),
        (ettm2_zf, ettm2_util, "ETTm2", PALETTE[4], "P"),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    xs = np.array([p[0] for p in pts])
    ys = np.array([p[1] * 100 for p in pts])
    # qualitative trend guide
    o = np.argsort(xs)
    ax.plot(xs[o], ys[o], color="#bbbbbb", lw=1.0, ls="--", zorder=1)
    for x, y, lab, col, mk in pts:
        ax.scatter(
            x, y * 100, s=120, color=col, marker=mk, edgecolor="k", lw=0.6, zorder=3, label=lab
        )
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("intermittency  (mean fraction of zero observations)")
    ax.set_ylabel("retrieval utility: % improvement over target-only TSFM")
    ax.set_title(
        "Retrieval augmentation helps only in sparse / scale-heterogeneous regimes", loc="left"
    )
    ax.annotate(
        "RMSSE: M5 / Favorita (counts)\nMSE: ETTm2 (continuous)",
        xy=(0.98, 0.04),
        xycoords="axes fraction",
        ha="right",
        va="bottom",
        fontsize=8.5,
        color="#555555",
    )
    ax.legend(frameon=False, loc="upper left")
    fig.savefig(FIG / "fig4_regimes.pdf")
    plt.close(fig)


# ---- fig5: pareto -------------------------------------------------------------------
def fig5_pareto() -> None:
    cb = json.loads((P11 / "compute_backbone.json").read_text())
    sc = json.loads((P11 / "compute_scalerag.json").read_text())
    grid = json.loads((P11 / "scalerag_native_ettm2_test.json").read_text())
    back_ms = cb["backbone_latency_ms_per_window"]
    retr_ms = sc["retrieval_latency_ms_per_window"]
    # wall-clock ratios from the reproduction (backbone 34.06s, TS-RAG 35.53s)
    tsrag_ms = back_ms * (35.53 / 34.06)
    chronos_mse = grid["chronos_bolt_target"]["mse"]
    tsrag_mse = json.loads((P11 / "repro_tsrag_official_ettm2.json").read_text())["mse"]
    fused_mse = next(
        r["mse"]
        for r in grid["scalerag_restored_fixed_fusion"]
        if r["scale"] == "mean" and r["k"] == 20 and r["weight"] == 0.25
    )
    pts = [
        (back_ms, chronos_mse, "Chronos-Bolt (target-only)", C_BACKBONE, "s"),
        (tsrag_ms, tsrag_mse, "TS-RAG (official ARM)", C_TSRAG, "D"),
        (back_ms + retr_ms, fused_mse, "ScaleRAG (restored fusion)", C_SCALERAG, "P"),
    ]
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    for x, y, lab, col, mk in pts:
        ax.scatter(x, y, s=150, color=col, marker=mk, edgecolor="k", lw=0.7, zorder=3, label=lab)
    # annotate away from the top-right edge so the ScaleRAG label is not clipped
    ax.annotate(
        pts[0][2], (pts[0][0], pts[0][1]), textcoords="offset points", xytext=(9, 5), fontsize=9
    )
    ax.annotate(
        pts[1][2], (pts[1][0], pts[1][1]), textcoords="offset points", xytext=(9, 5), fontsize=9
    )
    ax.annotate(
        pts[2][2],
        (pts[2][0], pts[2][1]),
        textcoords="offset points",
        xytext=(-9, -16),
        ha="right",
        fontsize=9,
    )
    # Pareto frontier (lower-left better) through the non-dominated points
    front = sorted([(pts[0][0], pts[0][1]), (pts[1][0], pts[1][1])])
    ax.plot(
        [p[0] for p in front],
        [p[1] for p in front],
        color="#888888",
        lw=1.2,
        ls="--",
        zorder=1,
    )
    # points are annotated directly, so a legend would only duplicate labels
    ax.annotate(
        "Pareto frontier",
        (front[0][0], (front[0][1] + front[1][1]) / 2),
        textcoords="offset points",
        xytext=(6, 0),
        fontsize=8.5,
        color="#666666",
        va="center",
    )
    ax.set_xlabel("inference latency  (ms / window)")
    ax.set_ylabel("test MSE  (lower better)")
    ax.set_xlim(back_ms - 0.06, back_ms + retr_ms + 0.12)
    ax.set_title("ScaleRAG is Pareto-dominated on ETTm2 (slower and less accurate)", loc="left")
    fig.savefig(FIG / "fig5_pareto.pdf")
    plt.close(fig)


# ---- fig6: sensitivity --------------------------------------------------------------
# M5 restored-retrieval RMSSE top-k sweep — source: docs/ablation-report.md
M5_TOPK = {5: 0.7708, 10: 0.7511, 20: 0.7425}


def fig6_sensitivity() -> None:
    grid = json.loads((P11 / "scalerag_native_ettm2_test.json").read_text())
    ks = [5, 10, 20]
    restored = {
        r["k"]: r["mse"] for r in grid["scalerag_restored_retrieval"] if r["scale"] == "mean"
    }
    fusion = {
        r["k"]: r["mse"]
        for r in grid["scalerag_restored_fixed_fusion"]
        if r["scale"] == "mean" and r["weight"] == 0.25
    }
    chronos = grid["chronos_bolt_target"]["mse"]

    fig, ax_l = plt.subplots(figsize=(7.2, 4.6))
    ax_l.plot(
        ks,
        [restored[k] for k in ks],
        "-o",
        color=C_SCALERAG,
        lw=1.8,
        label="ETTm2 restored retrieval",
    )
    ax_l.plot(
        ks,
        [fusion[k] for k in ks],
        "-s",
        color="#ff7f0e",
        lw=1.8,
        label="ETTm2 restored fusion (w=0.25)",
    )
    ax_l.axhline(chronos, color=C_BACKBONE, lw=1.4, ls="--", label="ETTm2 Chronos-Bolt target-only")
    ax_l.set_xlabel("number of retrieved sequences $k$")
    ax_l.set_ylabel("ETTm2 test MSE")
    ax_l.set_xticks(ks)
    ax_l.set_title("Larger $k$ improves retrieval but fusion stays above the backbone", loc="left")

    ax_r = ax_l.twinx()
    ax_r.plot(
        ks,
        [M5_TOPK[k] for k in ks],
        "-^",
        color="#2ca02c",
        lw=1.6,
        label="M5 restored retrieval (RMSSE)",
    )
    ax_r.set_ylabel("M5 RMSSE", color="#2ca02c")
    ax_r.tick_params(axis="y", labelcolor="#2ca02c")
    ax_r.grid(visible=False)

    lines = ax_l.get_lines() + ax_r.get_lines()
    labels = [str(ln.get_label()) for ln in lines]
    ax_l.legend(lines, labels, frameon=False, loc="center right", fontsize=9)
    fig.savefig(FIG / "fig6_sensitivity.pdf")
    plt.close(fig)


def main() -> None:
    _style()
    FIG.mkdir(parents=True, exist_ok=True)
    fig1_motivation()
    fig2_ablation()
    fig3_qualitative()
    fig4_regimes()
    fig5_pareto()
    fig6_sensitivity()
    print(f"wrote 6 figures to {FIG}")
    for f in sorted(FIG.glob("fig*.pdf")):
        print("  ", f.name, f"{f.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
