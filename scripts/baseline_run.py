#!/usr/bin/env python3
"""Declared, small baseline runner. Backs the `/baseline-run` skill.

Runs EXACTLY ONE small, explicitly-declared baseline configuration. Before doing
anything it prints the full declaration (model, dataset subset, split, metrics,
seed, expected outputs, approximate compute). It REFUSES to launch an undeclared
or full-scale run (CLAUDE.md research rule 12).

During the setup phase there is no trained baseline yet: `--dry-run` prints the
declaration and exits. A real run requires `--confirm` plus a declared config.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from graphroute_ts.config import load_config  # noqa: E402

# Guardrails: refuse anything that smells like a full-scale run.
MAX_SERIES = 200
MAX_STEPS = 5_000


def declare(cfg, subset: int) -> None:
    print("=" * 68)
    print("BASELINE RUN — DECLARATION (rule 12)")
    print("=" * 68)
    print(f"  experiment name : {cfg.name}")
    print(f"  model           : {cfg.model.get('kind', '<unset>')}")
    print(
        f"  dataset         : {cfg.data.dataset} (freq={cfg.data.freq}, target={cfg.data.target})"
    )
    print(f"  dataset subset  : {subset} series (cap {MAX_SERIES})")
    print(
        f"  split           : train<= {cfg.split.train_end}, val<= {cfg.split.val_end}, "
        f"H={cfg.split.horizon} (chronological)"
    )
    print("  metrics         : MAE, RMSE, (WRMSSE once M5 weights are wired)")
    print(f"  seed            : {cfg.seed}")
    print(f"  expected output : artifacts/{cfg.name}/ , reports/{cfg.name}.json")
    print("  approx compute  : CPU-only baseline, < 1 min, < 2 GiB RAM")
    print("=" * 68)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", type=Path, help="Declared baseline config YAML.")
    ap.add_argument("--subset", type=int, default=50, help="Number of series (small).")
    ap.add_argument("--dry-run", action="store_true", help="Print declaration and exit.")
    ap.add_argument("--confirm", action="store_true", help="Required to actually run.")
    args = ap.parse_args()

    if not args.config:
        print("Refusing: no declared --config provided.", file=sys.stderr)
        return 2

    cfg = load_config(args.config)

    if args.subset > MAX_SERIES:
        print(
            f"Refusing undeclared full-scale run: subset={args.subset} exceeds cap {MAX_SERIES}. "
            "Declare a large run explicitly and get approval (rule 12).",
            file=sys.stderr,
        )
        return 3

    declare(cfg, args.subset)

    if args.dry_run or not args.confirm:
        print("\n[dry-run] Declaration only. Pass --confirm to execute a declared run.")
        print("Note: no baseline is implemented yet during the setup phase.")
        return 0

    print("\nNo baseline model is implemented yet (setup phase). Nothing executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
