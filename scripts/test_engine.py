#!/usr/bin/env python3
"""Compile engine scripts and run the complete unittest suite."""

from __future__ import annotations

import argparse
from datetime import datetime
import os
from pathlib import Path
import subprocess
import sys


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Run the novel-writing-engine test suite.")
    parser.add_argument("--report", help="Write a Markdown test report.")
    parser.add_argument("--verbosity", type=int, choices=(1, 2), default=2)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    scripts = sorted((root / "scripts").glob("*.py"))
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"

    compile_command = [sys.executable, "-m", "py_compile", *map(str, scripts)]
    compile_result = subprocess.run(
        compile_command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
        check=False,
    )
    test_command = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        str(root / "tests"),
        "-v" if args.verbosity == 2 else "-q",
    ]
    test_result = subprocess.run(
        test_command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
        check=False,
    )
    passed = compile_result.returncode == 0 and test_result.returncode == 0
    output = (compile_result.stdout + compile_result.stderr + test_result.stdout + test_result.stderr).strip()

    print(output)
    print("engine test suite: " + ("PASS" if passed else "FAIL"))

    if args.report:
        report = Path(args.report).resolve()
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(
            "\n".join(
                [
                    "# Engine Test Report",
                    "",
                    f"- Time: {datetime.now().astimezone().isoformat(timespec='seconds')}",
                    f"- Result: {'PASS' if passed else 'FAIL'}",
                    f"- Compile exit code: {compile_result.returncode}",
                    f"- Test exit code: {test_result.returncode}",
                    f"- Script count: {len(scripts)}",
                    "",
                    "## Output",
                    "",
                    "```text",
                    output,
                    "```",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
