#!/usr/bin/env python3
"""Stop-hook fast validation for GraphRoute-TS.

When Claude reports a coding task complete, run FAST checks (format check, lint,
selected unit tests, selected leakage tests) and return failures as feedback.
Never hides failures; never runs slow/GPU/download tests. Skips silently if the
toolchain is not installed yet (setup phase).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
VENV = REPO / ".venv" / "bin"


def have(tool: str) -> str | None:
    local = VENV / tool
    if local.exists():
        return str(local)
    from shutil import which

    return which(tool)


def run(label: str, cmd: list[str]) -> tuple[str, bool, str]:
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    ok = proc.returncode == 0
    out = (proc.stdout + proc.stderr).strip()
    return label, ok, out


def main() -> int:
    ruff = have("ruff")
    pytest = have("pytest")
    if not ruff or not pytest:
        return 0  # toolchain not ready yet

    results = [
        run("ruff format --check", [ruff, "format", "--check", "src", "tests", "scripts"]),
        run("ruff check", [ruff, "check", "src", "tests", "scripts"]),
        run(
            "pytest unit+leakage",
            [pytest, "-q", "-m", "unit or leakage", "--no-header", "-p", "no:cacheprovider"],
        ),
    ]

    failures = [(label, out) for label, ok, out in results if not ok]
    if failures:
        sys.stderr.write("Post-task fast checks FAILED:\n\n")
        for label, out in failures:
            sys.stderr.write(f"--- {label} ---\n{out[-2000:]}\n\n")
        return 2  # feed failures back to Claude

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
