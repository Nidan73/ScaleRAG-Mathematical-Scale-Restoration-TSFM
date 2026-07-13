#!/usr/bin/env python3
"""SessionStart hook: print a fast status banner for GraphRoute-TS.

Shows repo path, git branch/status, active Python env + version, PyTorch version,
CUDA availability, and the current project phase. Fast and read-only — no network,
no heavy imports beyond an optional torch probe guarded by a short timeout budget.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PHASE = "Phase 1 — environment & scaffolding (no training yet)"


def sh(cmd: list[str]) -> str:
    try:
        p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=5)
        return p.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def torch_probe() -> str:
    py = REPO / ".venv" / "bin" / "python"
    if not py.exists():
        return "torch: (venv not created yet)"
    code = 'import torch;print(f"torch {torch.__version__} | cuda={torch.cuda.is_available()}")'
    try:
        p = subprocess.run([str(py), "-c", code], capture_output=True, text=True, timeout=20)
        return p.stdout.strip() or "torch: not installed"
    except (OSError, subprocess.SubprocessError):
        return "torch: probe skipped"


def main() -> int:
    branch = sh(["git", "branch", "--show-current"]) or "(no git / detached)"
    status = sh(["git", "status", "--porcelain"])
    n_changes = len([ln for ln in status.splitlines() if ln.strip()])
    dirty = f"{n_changes} changes" if status else "clean"
    venv = os.environ.get("VIRTUAL_ENV", "(none active)")

    lines = [
        "──────── GraphRoute-TS ────────",
        f" repo   : {REPO}",
        f" git    : {branch} ({dirty})",
        f" venv   : {venv}",
        f" python : {sys.version.split()[0]} (session)",
        f" {torch_probe()}",
        f" phase  : {PHASE}",
        "───────────────────────────────",
    ]
    # SessionStart hooks surface stdout to the session context.
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
