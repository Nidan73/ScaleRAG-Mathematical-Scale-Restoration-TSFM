# Rule: Python source (`src/graphroute_ts/**.py`)

- Target Python 3.11. Start modules with `from __future__ import annotations`.
- Full type hints on public functions/classes. Run `mypy` clean.
- Format + lint with Ruff (`make fmt`, `make lint`). No committed code fails `make check`.
- **Fail loudly:** no bare `except`, no `except Exception: pass`, no silent fallbacks
  or silent default values that hide errors.
- Keep `config.py` and `reproducibility.py` importable without torch / the ML stack.
- Small, pure, composable functions. No hidden global state; no I/O at import time.
- No network calls, downloads, or dataset reads triggered as an import side effect.
- Prefer Polars / DuckDB / PyArrow for tabular data; use pandas only where an
  external API requires it.
