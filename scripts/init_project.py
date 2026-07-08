#!/usr/bin/env python3
"""Initialize a novel-writing project for novel-writing-engine."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import sys


SKILL_VERSION = "0.5.0"

DIRECTORIES = [
    "settings/character-setting",
    "volumes",
    "chapters",
    "drafts",
    "archives",
    "memory",
    ".agent/task",
]

TEMPLATE_MAP = {
    "story.md.template": "story.md",
    "status.md.template": ".agent/status.md",
    "world-setting.md.template": "settings/world-setting.md",
    "genre-setting.md.template": "settings/genre-setting.md",
    "writing-style.md.template": "settings/writing-style.md",
    "user-preferences.md.template": "memory/user-preferences.md",
    "character-state.md.template": "memory/character-memory.md",
    "plot-hooks.md.template": "memory/foreshadowing-memory.md",
}

STATIC_FILES = {
    "memory/world-memory.md": """# 世界观记忆

## 已确认世界规则

```text
暂无。
```

## 待确认世界规则

```text
暂无。
```
""",
    "memory/plot-memory.md": """# 剧情记忆

## 已发生事件

```text
暂无。
```

## 当前主线进展

```text
暂无。
```
""",
    "memory/style-memory.md": """# 文风记忆

## 已确认文风

```text
暂无。
```

## 禁用表达

```text
暂无。
```
""",
    "memory/unresolved-threads.md": """# 未解决线索

## 悬念

```text
暂无。
```

## 待回收事项

```text
暂无。
```
""",
    "memory/reader-feedback.md": """# 读者反馈记忆

## 追读风险

```text
暂无。
```

## 爽点与疲劳点

```text
暂无。
```
""",
}


def is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def render_template(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def write_from_template(template_path: Path, target_path: Path, values: dict[str, str], force: bool) -> str:
    if target_path.exists() and not force:
        return f"skipped existing: {target_path}"
    target_path.parent.mkdir(parents=True, exist_ok=True)
    template_text = template_path.read_text(encoding="utf-8")
    target_path.write_text(render_template(template_text, values), encoding="utf-8", newline="\n")
    return f"written: {target_path}"


def write_static_file(target_path: Path, text: str, force: bool) -> str:
    if target_path.exists() and not force:
        return f"skipped existing: {target_path}"
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(text, encoding="utf-8", newline="\n")
    return f"written: {target_path}"


def touch_keep(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    keep = directory / ".gitkeep"
    if not keep.exists():
        keep.write_text("", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a novel-writing-engine project.")
    parser.add_argument("project_path", nargs="?", default=".", help="Target project directory. Defaults to current directory.")
    parser.add_argument("--name", default=None, help="Novel project name. Defaults to directory name.")
    parser.add_argument("--genre", default="未设定", help="Initial genre label.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing template files.")
    parser.add_argument("--dry-run", action="store_true", help="Print the planned project skeleton without writing files.")
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    skill_root = script_path.parents[1]
    template_root = skill_root / "templates"
    project_root = Path(args.project_path).resolve()

    if project_root == skill_root or is_relative_to(project_root, skill_root):
        print("refusing to initialize inside the skill directory:", project_root, file=sys.stderr)
        return 2

    protected_files = [
        project_root / "story.md",
        project_root / ".agent" / "status.md",
    ]
    existing_protected = [path for path in protected_files if path.exists()]
    if existing_protected and not args.force:
        print("refusing to initialize because protected project files already exist:", file=sys.stderr)
        for path in existing_protected:
            print(f"- {path}", file=sys.stderr)
        print("use --force only if you intentionally want to overwrite template-managed files.", file=sys.stderr)
        return 4

    values = {
        "project_name": args.name or project_root.name,
        "created_date": date.today().isoformat(),
        "skill_version": SKILL_VERSION,
        "genre": args.genre,
    }

    planned_files = list(TEMPLATE_MAP.values()) + list(STATIC_FILES)

    print(f"target project: {project_root}")
    print("directories to ensure:")
    for relative in DIRECTORIES:
        print(f"- {relative}")
    print("files to create:")
    for relative in planned_files:
        print(f"- {relative}")

    if args.dry_run:
        print("dry run complete; no files were written.")
        return 0

    project_root.mkdir(parents=True, exist_ok=True)

    for relative in DIRECTORIES:
        touch_keep(project_root / relative)

    results: list[str] = []
    for template_name, target_name in TEMPLATE_MAP.items():
        template_path = template_root / template_name
        if not template_path.exists():
            print(f"missing template: {template_path}", file=sys.stderr)
            return 3
        results.append(write_from_template(template_path, project_root / target_name, values, args.force))
    for target_name, text in STATIC_FILES.items():
        results.append(write_static_file(project_root / target_name, text, args.force))

    print("\n".join(results))
    print(f"initialized novel project: {project_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
