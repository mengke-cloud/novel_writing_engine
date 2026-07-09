#!/usr/bin/env python3
"""Validate a novel-writing-engine release candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


REQUIRED_PATHS = (
    "SKILL.md",
    "README.md",
    "CHANGELOG.md",
    "VERSION",
    "COMPATIBILITY.md",
    "install.ps1",
    "install.sh",
    "agents/openai.yaml",
    "scripts/novel.py",
    "scripts/test_engine.py",
    "scripts/create_example_project.py",
    "modules/00_state_management.md",
    "modules/18_release.md",
    ".github/workflows/tests.yml",
)


def extract(pattern: str, text: str) -> str:
    match = re.search(pattern, text, re.M)
    return match.group(1).strip() if match else ""


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Validate a stable release candidate.")
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    issues: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (root / relative).exists():
            issues.append(f"missing required path: {relative}")

    skill = (root / "SKILL.md").read_text(encoding="utf-8-sig")
    readme = (root / "README.md").read_text(encoding="utf-8-sig")
    init_text = (root / "scripts" / "init_project.py").read_text(encoding="utf-8")
    repair_text = (root / "scripts" / "repair_status.py").read_text(encoding="utf-8")
    versions = {
        "VERSION": version,
        "SKILL.md": extract(r"^当前版本：([0-9.]+)$", skill),
        "README.md": extract(r"^version:\s*([0-9.]+)$", readme),
        "init_project.py": extract(r'^SKILL_VERSION\s*=\s*"([0-9.]+)"$', init_text),
        "repair_status.py": extract(r'^ENGINE_VERSION\s*=\s*"([0-9.]+)"$', repair_text),
    }
    for source, value in versions.items():
        if value != version:
            issues.append(f"version mismatch: {source}={value or 'missing'} expected={version}")

    parts = skill.split("---", 2)
    if len(parts) != 3 or not re.search(r"(?m)^name:\s*novel-writing-engine$", parts[1]):
        issues.append("invalid SKILL.md frontmatter")

    for path in (root / "knowledge" / "genre-guides").glob("*.md"):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        for section in ("适用范围", "核心原则", "常见错误", "检查清单"):
            if section not in text:
                issues.append(f"genre guide missing {section}: {path.name}")

    test_code = 0
    if not args.skip_tests:
        test_code = subprocess.run(
            [sys.executable, str(root / "scripts" / "test_engine.py"), "--verbosity", "1"],
            capture_output=True,
            check=False,
        ).returncode
        if test_code:
            issues.append(f"test suite failed: exit {test_code}")

    example_code = 0
    example_quality_code = 0
    with tempfile.TemporaryDirectory() as temporary:
        example = Path(temporary) / "example"
        example_code = subprocess.run(
            [sys.executable, str(root / "scripts" / "create_example_project.py"), str(example)],
            capture_output=True,
            check=False,
        ).returncode
        if example_code == 0:
            example_quality_code = subprocess.run(
                [sys.executable, str(root / "scripts" / "quality_gate.py"), str(example), "--target", "project", "--json"],
                capture_output=True,
                check=False,
            ).returncode
        if example_code or example_quality_code:
            issues.append(f"example validation failed: create={example_code} quality={example_quality_code}")

    result = {
        "version": version,
        "passed": not issues,
        "versions": versions,
        "tests_skipped": args.skip_tests,
        "test_exit_code": test_code,
        "example_create_exit_code": example_code,
        "example_quality_exit_code": example_quality_code,
        "issues": issues,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"release {version}: {'PASS' if result['passed'] else 'FAIL'}")
        for issue in issues:
            print(f"- {issue}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
