# Environment Audit

Machine and toolchain audit for GraphRoute-TS. Captured at project setup. No
secrets, tokens, hostnames, or serial numbers are recorded here.

## System

| Item | Value |
|------|-------|
| OS | CachyOS Linux (Arch-based, rolling) |
| Kernel | 7.1.3-2-cachyos (x86_64) |
| Desktop | KDE Plasma (Wayland) |
| Login shell | zsh (`fish 4.8.0` also installed and used for activation docs) |
| CPU | AMD Ryzen 7 7700 — 8 cores / 16 threads |
| RAM | ~30 GiB + 30 GiB swap |
| Disk (project fs) | ~729 GiB free of 952 GiB on `/home` |

## GPU / CUDA

| Item | Value |
|------|-------|
| GPU | NVIDIA GeForce RTX 5070 Ti (GB203, Blackwell, **sm_120**) |
| VRAM | 16 GiB (16303 MiB) |
| Driver | 610.43.03 |
| CUDA (driver/UMD) | 13.3 |
| iGPU present | AMD Raphael (unused for compute) |

**Note:** The driver is newer than any release known at the assistant's knowledge
cutoff. NVIDIA drivers are forward-compatible with older CUDA runtimes, so a
`cu130` (CUDA 13.0) PyTorch wheel is the native match for this driver and GPU.

## Toolchain

| Tool | Version | Notes |
|------|---------|-------|
| Python (system) | 3.14.6 | Only system Python; **no 3.11 present** |
| Python (project) | 3.11 (uv-managed) | Pinned via `.python-version` |
| uv | installed via `pacman` (`extra/uv`) | Env & dependency manager |
| Git | 2.55.0 | identity: `Nidan73` (see ⚠️ below) |
| Node.js / npm | 24.17.0 / 11.13.0 | For Claude Code / tooling |
| Docker | not installed | GitHub MCP uses the hosted HTTP server instead |
| Claude Code | 2.1.207 | |
| gcc / make | 16.1.1 / 4.4.1 | `cmake` absent (not needed for wheels) |
| conda / poetry / pipx | none | uv is the single env manager |
| notify-send | available | Used by the notification hook |

## Selected build

- **Python 3.11** (uv-managed, project-local) — broad wheel support incl. PyTorch.
- **PyTorch from the `cu130` index** — matches the Blackwell GPU + CUDA 13.3 driver;
  newest stable at setup was `torch 2.13.0`. Verified against the official wheel
  index before selection (never a blind CUDA wheel).

## Warnings / follow-ups

- ⚠️ **Git email looks malformed:** `git config --global user.email` is
  a malformed value (missing the `@`). Fix before committing:
  `git config --global user.email "you@example.com"`.
- ⚠️ Login shell is **zsh**, not fish; `fish` is installed, so Fish activation
  instructions in the README remain valid.
- No secrets, Kaggle, or Hugging Face credentials were read or recorded.
