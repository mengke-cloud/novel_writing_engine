#!/usr/bin/env python3
"""Repair missing .agent/status.md fields for a novel-writing-engine project."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re
import sys


ENGINE_VERSION = "0.6.0"

REQUIRED_FIELDS = [
    "project_name",
    "engine_version",
    "skill_version",
    "created_at",
    "updated_at",
    "phase",
    "current_phase",
    "current_volume",
    "current_chapter",
    "current_task",
    "last_task",
    "next_action",
    "blocked_reason",
]

DEFAULTS = {
    "engine_version": ENGINE_VERSION,
    "skill_version": ENGINE_VERSION,
    "created_at": date.today().isoformat(),
    "updated_at": date.today().isoformat(),
    "phase": "paused",
    "current_phase": "paused",
    "current_volume": "0",
    "current_chapter": "0",
    "current_task": "repair_status",
    "last_task": "status_repair",
    "next_action": "请用户确认当前小说项目阶段，并继续调度。",
    "blocked_reason": "状态文件字段缺失，已补齐基础字段；需要用户确认当前阶段。",
}


def read_field(text: str, key: str) -> str | None:
    pattern = re.compile(rf"^{re.escape(key)}:\s*(.*)$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return None
    return match.group(1).strip()


def infer_values(project_root: Path, text: str) -> dict[str, str]:
    project_name = read_field(text, "project_name") or project_root.name
    engine_version = read_field(text, "engine_version") or read_field(text, "skill_version") or ENGINE_VERSION
    skill_version = read_field(text, "skill_version") or engine_version
    phase = read_field(text, "phase") or read_field(text, "current_phase") or "paused"
    current_phase = read_field(text, "current_phase") or phase
    current_task = read_field(text, "current_task") or read_field(text, "last_task") or "repair_status"
    last_task = read_field(text, "last_task") or "status_repair"

    values = dict(DEFAULTS)
    values.update(
        {
            "project_name": project_name,
            "engine_version": engine_version,
            "skill_version": skill_version,
            "phase": phase,
            "current_phase": current_phase,
            "current_task": current_task,
            "last_task": last_task,
        }
    )

    for field in REQUIRED_FIELDS:
        existing = read_field(text, field)
        if existing is not None:
            values[field] = existing

    return values


def missing_fields(text: str) -> list[str]:
    return [field for field in REQUIRED_FIELDS if read_field(text, field) is None]


def build_field_block(values: dict[str, str], fields: list[str]) -> str:
    lines = [f"{field}: {values[field]}" for field in fields]
    return "\n".join(lines) + "\n"


def insert_after_title(text: str, block: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].lstrip("\ufeff").startswith("#"):
        return "\n".join([lines[0], "", block.rstrip(), *lines[1:]]) + "\n"
    return block + "\n" + text


def repair(project_root: Path, dry_run: bool) -> int:
    status_path = project_root / ".agent" / "status.md"
    story_path = project_root / "story.md"

    if not story_path.exists():
        print(f"refusing repair: missing story.md in {project_root}", file=sys.stderr)
        return 2

    if not status_path.exists():
        print(f"refusing repair: missing .agent/status.md in {project_root}", file=sys.stderr)
        return 3

    text = status_path.read_text(encoding="utf-8", errors="replace")
    missing = missing_fields(text)
    if not missing:
        print("status file already contains all required fields.")
        return 0

    values = infer_values(project_root, text)
    block = build_field_block(values, missing)

    print(f"status file: {status_path}")
    print("missing fields:")
    for field in missing:
        print(f"- {field}:")
    print("fields to insert:")
    print(block.rstrip())

    if dry_run:
        print("dry run complete; no files were written.")
        return 0

    repaired = insert_after_title(text, block)
    status_path.write_text(repaired, encoding="utf-8", newline="\n")
    print("status file repaired.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair missing .agent/status.md fields.")
    parser.add_argument("project_path", nargs="?", default=".", help="Project directory. Defaults to current directory.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned repairs without writing files.")
    args = parser.parse_args()

    return repair(Path(args.project_path).resolve(), args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
