#!/usr/bin/env python3
"""Unified command-line entry point for novel-writing-engine."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


COMMANDS = {
    "init": "init_project.py",
    "detect": "detect_project.py",
    "repair": "repair_status.py",
    "context": "context_builder.py",
    "consistency": "consistency_check.py",
    "quality": "quality_gate.py",
    "archive": "archive_chapter.py",
    "status": "detect_project.py",
    "next": "context_builder.py",
    "test": "test_engine.py",
    "migrate": "migrate_project.py",
    "analytics": "analyze_project.py",
    "example": "create_example_project.py",
    "release": "release_check.py",
}


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Unified CLI for novel-writing-engine.",
        epilog=(
            "Commands forward remaining arguments to the underlying script. "
            "Example: novel.py quality PROJECT --target archive --chapter-plan PLAN --draft DRAFT"
        ),
    )
    parser.add_argument("command", choices=COMMANDS)
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    script = Path(__file__).resolve().with_name(COMMANDS[args.command])
    command = [sys.executable, str(script), *args.arguments]
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(command, check=False, env=environment).returncode


if __name__ == "__main__":
    raise SystemExit(main())
