#!/usr/bin/env python3
"""PreToolUse(Bash) safety guard for GraphRoute-TS.

Reads the hook JSON on stdin, inspects the proposed Bash command, and BLOCKS
(exit code 2, reason on stderr) dangerous operations. It only inspects strings —
it never executes anything, so nothing is ever deleted or modified by this guard.

Blocks: destructive recursive deletion, `git reset --hard`, force pushes,
deletion of `.git` or datasets, touching credential files, `curl|sh` style remote
execution, writes into system directories, undeclared full-dataset training, and
bulk dataset/model downloads. Harmless inspection commands pass through.
"""

from __future__ import annotations

import json
import re
import sys

# (compiled pattern, human reason). First match wins.
RULES: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"\brm\b[^|;&]*\s-\w*r\w*f|\brm\b[^|;&]*\s-\w*f\w*r|\brm\s+-rf|\brm\s+-fr"),
        "destructive recursive force deletion (rm -rf)",
    ),
    (re.compile(r"\brm\b[^|;&\n]*\b\.git\b"), "deletion targeting the .git directory"),
    (
        re.compile(r"\brm\b[^|;&\n]*\bdata/(raw|interim|processed)\b"),
        "deletion targeting dataset directories",
    ),
    (
        re.compile(r"\bgit\s+reset\s+--hard\b"),
        "git reset --hard (irreversible working-tree/history reset)",
    ),
    (
        re.compile(r"\bgit\s+push\b[^\n]*(--force(?!-with-lease)|\s-f\b|--force-with-lease)"),
        "force push",
    ),
    (
        re.compile(r"\bgit\s+(checkout|restore)\b[^\n]*--\s*\.(\s|$)"),
        "wholesale discard of working-tree changes",
    ),
    (
        re.compile(r"(curl|wget)\b[^\n]*\|\s*(sudo\s+)?(sh|bash|zsh|fish)\b"),
        "remote script piped into a shell (curl|sh)",
    ),
    (
        re.compile(
            r"(^|[\s;&|])(cat|less|more|head|tail|bat|nano|vim|vi|cp|mv|rm|tee|echo)\b[^\n]*"
            r"(\.env(\.\w+)?|kaggle\.json|\.kaggle|id_rsa|id_ed25519|\.netrc|"
            r"hf_token|\.huggingface|credentials|secrets/|\.pem\b|\.key\b)"
        ),
        "access/modification of a credential or secrets file",
    ),
    (
        re.compile(
            r"(>|>>|\btee\b|\brm\b|\bmv\b|\bcp\b)\s+/(etc|usr|bin|sbin|boot|lib|opt|root)\b"
        ),
        "write/delete inside a system directory",
    ),
    (
        re.compile(r"(--full-dataset|--all-series|\bfull_train\b|train_all\b)"),
        "undeclared full-dataset training run (use /baseline-run + explicit approval)",
    ),
    (
        re.compile(
            r"\b(kaggle\s+(datasets|competitions)\s+download|"
            r"huggingface-cli\s+download|hf\s+download|git\s+lfs\s+pull)\b"
        ),
        "bulk dataset/model download (requires explicit approval this phase)",
    ),
]


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        # Can't parse — do not block; fail open for inspection-only guard.
        return 0

    command = (payload.get("tool_input", {}) or {}).get("command", "")
    if not command:
        return 0

    for pattern, reason in RULES:
        if pattern.search(command):
            sys.stderr.write(
                f"BLOCKED by pre_bash_guard: {reason}.\n"
                f"Command: {command}\n"
                "If this is genuinely required, ask the user to run it themselves "
                "or explicitly approve it.\n"
            )
            return 2  # exit code 2 → Claude Code blocks the tool call

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
