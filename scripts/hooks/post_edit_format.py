#!/usr/bin/env python3
"""PostToolUse(Edit|Write|MultiEdit) formatter for GraphRoute-TS.

After a Python file is written/edited, run `ruff format` on it and a targeted
`ruff check`. Non-blocking: it formats in place and surfaces remaining lint
findings as feedback, but never runs the full test suite and never fails the edit.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def ruff_cmd() -> list[str] | None:
    local = REPO / ".venv" / "bin" / "ruff"
    if local.exists():
        return [str(local)]
    from shutil import which

    found = which("ruff")
    return [found] if found else None


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0

    fp = (payload.get("tool_input", {}) or {}).get("file_path", "")
    if not fp or not fp.endswith(".py"):
        return 0
    path = Path(fp)
    if not path.is_file():
        return 0

    ruff = ruff_cmd()
    if ruff is None:
        return 0  # ruff not installed yet — nothing to do

    subprocess.run([*ruff, "format", str(path)], cwd=REPO, capture_output=True, text=True)
    check = subprocess.run(
        [*ruff, "check", "--quiet", str(path)], cwd=REPO, capture_output=True, text=True
    )
    if check.returncode != 0 and (check.stdout.strip() or check.stderr.strip()):
        sys.stderr.write(
            "ruff check found issues in the edited file (non-blocking):\n"
            + (check.stdout or check.stderr)
        )
        return 2  # surface as feedback to Claude without failing the workflow

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
