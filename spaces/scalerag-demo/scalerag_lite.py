"""Self-contained, lightweight ScaleRAG-TS method for the demo Space.

A faithful but dependency-light reimplementation of the paper's frozen retrieval
+ gated-fusion path, so the Hugging Face Space does not depend on the research
repository being installed. NOT the exact frozen artefacts used for the reported
numbers — it is a demonstration. The scientific results live in the paper/repo.

Method (see docs/scalerag-ts-method.md in the code repo):
- scale-aware temporal retrieval: mean-normalise context windows, exact L2 k-NN
  over candidate windows that end strictly before the forecast origin (leakage
  guard ``t_r + H < origin``), then restore each retrieved continuation to the
  target's scale;
- uncertainty-aware gate: a small logistic gate over {retrieval nn-distance,
  retrieval disagreement, intermittency, log-volume, Chronos uncertainty,
  scale-spread}, fit on the uploaded corpus's own historical origin, produces a
  per-series retrieval weight alpha;
- fusion: forecast = (1 - alpha) * Chronos2(target) + alpha * Retrieval(target).

No graph/relational features (that hypothesis was falsified in the study). No
retrieved future labels enter the Chronos input.
"""

from __future__ import annotations

# ruff: noqa: N806, N803  # L,H (time-series) and X (design matrix) are standard notation
from dataclasses import dataclass, field

import numpy as np


@dataclass
class Window:
    series: str
    t_r: int  # 1-based context end index
    context: np.ndarray  # (L,)
    continuation: np.ndarray  # (H,)


@dataclass
class RetrievalOutput:
    point: np.ndarray  # (H,)
    lo: np.ndarray  # (H,) 10th pct
    hi: np.ndarray  # (H,) 90th pct
    neighbours: list[Window] = field(default_factory=list)
    restored: list[np.ndarray] = field(default_factory=list)  # scale-restored conts
    nn_dist: float = 0.0
    disagreement: float = 0.0


def _mean_scale(x: np.ndarray) -> float:
    m = float(np.mean(x))
    return m if m != 0.0 else 1.0


def build_windows(
    corpus: dict[str, np.ndarray], origin: int, L: int, H: int, stride: int = 7
) -> list[Window]:
    """All windows whose continuation ends at or before ``origin`` (leakage-safe)."""
    out: list[Window] = []
    for name, series in corpus.items():
        n = len(series)
        limit = min(n, origin)  # never look at/after the forecast origin
        for t_r in range(L, limit - H + 1, stride):
            out.append(
                Window(
                    name,
                    t_r,
                    series[t_r - L : t_r].astype(float),
                    series[t_r : t_r + H].astype(float),
                )
            )
    return out


def retrieve(query: np.ndarray, windows: list[Window], k: int) -> RetrievalOutput:
    """Scale-aware k-NN retrieval forecast for a single query context.

    ``windows`` are already leakage-safe (built with ``t_r + H <= origin``), so
    the whole pool is a valid candidate set.
    """
    if not windows:
        base = np.full(len(query), float(np.mean(query)))
        return RetrievalOutput(base, base, base, [], [], 1e6, 0.0)
    q_scale = _mean_scale(query)
    qv = query / q_scale
    dists = np.array(
        [float(np.sum((w.context / _mean_scale(w.context) - qv) ** 2)) for w in windows]
    )
    order = np.argsort(dists)[:k]
    chosen = [windows[i] for i in order]
    restored = [w.continuation / _mean_scale(w.context) * q_scale for w in chosen]
    stack = np.clip(np.stack(restored), 0.0, None)
    return RetrievalOutput(
        point=stack.mean(0),
        lo=np.quantile(stack, 0.1, axis=0),
        hi=np.quantile(stack, 0.9, axis=0),
        neighbours=chosen,
        restored=[np.clip(r, 0.0, None) for r in restored],
        nn_dist=float(dists[order[0]]),
        disagreement=float(stack.std(0).mean()),
    )


def gate_feature_row(
    context: np.ndarray,
    nn_dist: float,
    disagreement: float,
    chronos_lo: np.ndarray,
    chronos_hi: np.ndarray,
) -> np.ndarray:
    mean = float(np.mean(context))
    std = float(np.std(context))
    return np.array(
        [
            nn_dist,
            disagreement,
            float(np.mean(context == 0)),  # intermittency
            float(np.log(mean + 1.0)),  # log volume
            float(np.mean(chronos_hi - chronos_lo)),  # chronos uncertainty
            std / (mean + 1e-6),  # scale spread
        ]
    )


class LogisticGate:
    """Tiny logistic-regression gate (lightweight stand-in for the paper's LGBM gate)."""

    def __init__(self) -> None:
        self.w: np.ndarray | None = None
        self.mu: np.ndarray | None = None
        self.sd: np.ndarray | None = None
        self.fixed_alpha = 0.5
        self.fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 400, lr: float = 0.1) -> None:
        if len(np.unique(y)) < 2 or X.shape[0] < 20:
            self.fitted = False
            return
        self.mu, self.sd = X.mean(0), X.std(0) + 1e-9
        Xs = (X - self.mu) / self.sd
        Xs = np.hstack([Xs, np.ones((Xs.shape[0], 1))])
        w = np.zeros(Xs.shape[1])
        for _ in range(epochs):
            p = 1.0 / (1.0 + np.exp(-Xs @ w))
            w -= lr * (Xs.T @ (p - y)) / len(y)
        self.w = w
        self.fitted = True

    def alpha(self, x: np.ndarray) -> float:
        if not self.fitted or self.w is None:
            return self.fixed_alpha
        xs = (x - self.mu) / self.sd
        xs = np.append(xs, 1.0)
        return float(1.0 / (1.0 + np.exp(-xs @ self.w)))


def fuse(chronos_pt: np.ndarray, retr_pt: np.ndarray, alpha: float) -> np.ndarray:
    return np.clip((1.0 - alpha) * chronos_pt + alpha * retr_pt, 0.0, None)
