#!/usr/bin/env python3
"""Notification hook: desktop notification via notify-send when available.

Fires when Claude Code needs attention or finishes a long approved task. No-op if
`notify-send` is not installed. Never includes secrets — only a generic message.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys


def main() -> int:
    notify = shutil.which("notify-send")
    if not notify:
        return 0  # nothing to do on headless / no libnotify

    raw = sys.stdin.read()
    message = "Claude Code needs your attention"
    try:
        payload = json.loads(raw) if raw.strip() else {}
        message = payload.get("message") or message
    except json.JSONDecodeError:
        pass

    # Keep it generic: never echo command content or secrets.
    subprocess.run(
        [notify, "-a", "Claude Code", "-u", "normal", "GraphRoute-TS", str(message)[:200]],
        capture_output=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
