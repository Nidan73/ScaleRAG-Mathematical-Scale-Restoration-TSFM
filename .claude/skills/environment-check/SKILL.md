---
name: environment-check
description: Use to verify the GraphRoute-TS dev environment is healthy — active .venv, Python 3.11, uv.lock consistency, PyTorch + CUDA + GPU, required directories, git tree, and disk space. Read-only; produces a pass/fail report and never modifies the environment.
---

# environment-check

Verify the development environment before running anything. **Read-only** — this
skill must never install, upgrade, or mutate the environment without explicit
user permission.

## Steps

1. Run the backing checker:
   ```bash
   uv run python scripts/environment_check.py         # table
   uv run python scripts/environment_check.py --json   # machine-readable
   ```
2. Report the pass/fail table verbatim. Hard failures (Python version, missing
   required directories) exit non-zero and mean the environment is NOT ready.
3. Soft warnings (no active venv, CUDA unavailable, dirty git tree, low disk) are
   surfaced but do not by themselves fail the check.
4. If a check fails, state the specific remediation (e.g. `uv sync`, activate the
   venv) — do **not** auto-run fixes unless the user approves.

Do not download packages or checkpoints as part of this check.
