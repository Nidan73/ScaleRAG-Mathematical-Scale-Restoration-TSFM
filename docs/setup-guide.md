# Setup Guide

Reproduce the GraphRoute-TS development environment from a clean checkout.

## 0. Prerequisites

- CachyOS/Arch Linux, NVIDIA driver installed (`nvidia-smi` works).
- `uv` installed: `sudo pacman -S --needed uv` (or the standalone installer).
- `git`, and Node.js if you use Claude Code MCP tooling.

## 1. Clone & enter

```bash
git clone <repo-url> graphroute-ts
cd graphroute-ts
```

## 2. Create the environment

`uv` reads `.python-version` (3.11), provisions that interpreter, and installs the
locked dependency set into a project-local `.venv`:

```bash
uv sync --extra ml --extra retrieval --extra tsfm
```

- Core + dev groups always install.
- `ml` = torch, transformers, accelerate, datasets, peft, safetensors, lightgbm,
  statsmodels, huggingface-hub.
- `tsfm` = chronos-forecasting (official). `retrieval` = faiss-cpu.
- `torch` resolves from the `cu130` index (Blackwell / CUDA 13.x) — configured in
  `pyproject.toml`, never installed as a blind wheel.

Heavy optional groups are **defined but not installed**: `graph` (torch-geometric),
`gpu-retrieval` (faiss-gpu). Enable later with `--extra graph` etc., only once the
baseline pipeline is verified.

## 3. Activate

```fish
# Fish
source .venv/bin/activate.fish
```
```bash
# bash / zsh
source .venv/bin/activate
```
Or use `uv run <cmd>` without activating.

## 4. Verify

```bash
make verify                 # environment health (read-only)
uv run python scripts/environment_check.py --json
make check                  # format + lint + type + unit + leakage
make smoke                  # environment smoke tests
```

Confirm GPU:
```bash
uv run python -c "import torch;print(torch.__version__,torch.cuda.is_available(),torch.cuda.get_device_name(0))"
```

## 5. Secrets

Copy `.env.example` → `.env` and fill locally. `.env` is gitignored and denied to
Claude via `.claude/settings.json`. Never commit or print credentials.

## Troubleshooting

- **`torch.cuda.is_available()` is False:** confirm `nvidia-smi` works and the
  installed wheel is a `cu*` build (`uv run python -c "import torch;print(torch.version.cuda)"`).
  If the `cu130` wheel misbehaves, fall back to the `cu129` index (edit the
  `[[tool.uv.index]]` URL) and re-`uv sync`.
- **Wrong Python:** `uv python pin 3.11` then `uv sync`.
- **Lock drift:** `uv lock` to regenerate, review the diff, commit `uv.lock`.
