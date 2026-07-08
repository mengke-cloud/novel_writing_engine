#!/usr/bin/env python3
"""Detect novel-writing-engine project status."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_DIRS = [
    "settings",
    "volumes",
    "chapters",
    "drafts",
    "archives",
    "memory",
    ".agent",
]

SKILL_ROOT_MARKERS = [
    "SKILL.md",
    "agents",
    "modules",
    "scripts",
    "templates",
]

REQUIRED_STATUS_FIELDS = [
    "project_name:",
    "engine_version:",
    "skill_version:",
    "created_at:",
    "updated_at:",
    "phase:",
    "current_phase:",
    "current_volume:",
    "current_chapter:",
    "current_task:",
    "last_task:",
    "next_action:",
    "blocked_reason:",
]


def is_skill_root(project_root: Path) -> bool:
    return all((project_root / marker).exists() for marker in SKILL_ROOT_MARKERS)


def missing_status_fields(status_path: Path) -> list[str]:
    if not status_path.exists():
        return REQUIRED_STATUS_FIELDS

    text = status_path.read_text(encoding="utf-8", errors="replace")
    return [field for field in REQUIRED_STATUS_FIELDS if field not in text]


def detect(project_root: Path) -> dict[str, object]:
    story = project_root / "story.md"
    status = project_root / ".agent" / "status.md"
    legacy_story = project_root / "story.yaml"
    present_dirs = [directory for directory in REQUIRED_DIRS if (project_root / directory).is_dir()]
    missing_dirs = [directory for directory in REQUIRED_DIRS if directory not in present_dirs]
    status_missing_fields = missing_status_fields(status)

    if is_skill_root(project_root):
        state = "skill_root"
        action = "当前目录是 novel-writing-engine 技能目录，禁止在此处初始化小说项目。"
    elif story.exists() and status.exists() and not status_missing_fields:
        state = "existing"
        action = "继续读取 .agent/status.md，并进入 agents/novel-agent.md 调度流程。"
    elif story.exists() and status.exists() and status_missing_fields:
        state = "needs_repair"
        action = ".agent/status.md 缺少关键字段，应修复状态文件后再继续。"
    elif legacy_story.exists() and not story.exists():
        state = "legacy"
        action = "检测到旧版 story.yaml，后续应进入迁移流程。"
    elif story.exists() and not status.exists():
        state = "needs_repair"
        action = "story.md 存在但 .agent/status.md 缺失，应补建状态文件后再继续。"
    elif present_dirs:
        state = "partial"
        action = "发现部分小说项目目录，但缺少 story.md；应询问用户是修复、迁移还是重新初始化。"
    else:
        state = "new"
        action = "当前目录不是小说项目；如用户确认，可运行 scripts/init_project.py 初始化。"

    return {
        "project_path": str(project_root),
        "state": state,
        "story_md": story.exists(),
        "status_md": status.exists(),
        "legacy_story_yaml": legacy_story.exists(),
        "present_dirs": present_dirs,
        "missing_dirs": missing_dirs,
        "missing_status_fields": status_missing_fields,
        "recommended_action": action,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect novel-writing-engine project status.")
    parser.add_argument("project_path", nargs="?", default=".", help="Project directory. Defaults to current directory.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    result = detect(Path(args.project_path).resolve())
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"project_path: {result['project_path']}")
        print(f"state: {result['state']}")
        print(f"story_md: {result['story_md']}")
        print(f"status_md: {result['status_md']}")
        print(f"legacy_story_yaml: {result['legacy_story_yaml']}")
        print(f"present_dirs: {', '.join(result['present_dirs']) if result['present_dirs'] else '-'}")
        print(f"missing_dirs: {', '.join(result['missing_dirs']) if result['missing_dirs'] else '-'}")
        print(
            "missing_status_fields: "
            f"{', '.join(result['missing_status_fields']) if result['missing_status_fields'] else '-'}"
        )
        print(f"recommended_action: {result['recommended_action']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
