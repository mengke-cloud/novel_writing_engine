#!/usr/bin/env python3
"""Migrate legacy novel projects without deleting or overwriting source files."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile

from init_project import DIRECTORIES, SKILL_VERSION, TEMPLATE_MAP, render_template


VALID_PHASES = {
    "setup",
    "outline",
    "volume",
    "chapter",
    "draft",
    "revision",
    "retention",
    "archive",
    "paused",
}


def parse_simple_yaml(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#") or raw_line[:1].isspace():
            continue
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*$", raw_line)
        if not match:
            continue
        value = match.group(2).strip().strip("\"'")
        if value not in {"", "{}", "[]", "null", "None"}:
            values[match.group(1)] = value
    return values


def replace_field(text: str, field: str, value: str) -> str:
    return re.sub(rf"(?m)^{re.escape(field)}:\s*.*$", f"{field}: {value}", text, count=1)


def normalize_counter(value: str) -> str:
    match = re.search(r"\d+", value)
    return match.group() if match else "0"


def find_legacy_file(project: Path, names: tuple[str, ...]) -> Path | None:
    for name in names:
        candidates = [project / name, project / "memory" / name]
        for candidate in candidates:
            if candidate.is_file():
                return candidate
    return None


def create_backup(project: Path, backup_path: Path) -> int:
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(backup_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(project.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(project)
            if ".git" in relative.parts or ".migration-backups" in relative.parts:
                continue
            archive.write(path, relative.as_posix())
            count += 1
    return count


def run_validation(script: Path, project: Path, *arguments: str) -> int:
    environment = dict(**__import__("os").environ)
    environment["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, str(script), str(project), *arguments],
        capture_output=True,
        env=environment,
        check=False,
    ).returncode


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Migrate a legacy novel project.")
    parser.add_argument("project_path")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    project = Path(args.project_path).resolve()
    skill_root = Path(__file__).resolve().parents[1]
    if not project.is_dir():
        print("project directory does not exist", file=sys.stderr)
        return 2
    if project == skill_root or all((project / marker).exists() for marker in ("SKILL.md", "agents", "modules", "scripts")):
        print("refusing to migrate the skill directory", file=sys.stderr)
        return 3

    legacy_story = project / "story.yaml"
    legacy_values = parse_simple_yaml(legacy_story)
    project_name = (
        legacy_values.get("project_name")
        or legacy_values.get("title")
        or legacy_values.get("name")
        or project.name
    )
    genre = legacy_values.get("genre") or legacy_values.get("type") or "未设定"
    phase = legacy_values.get("phase") or legacy_values.get("current_phase") or legacy_values.get("status") or "paused"
    if phase not in VALID_PHASES:
        phase = "paused"
    current_volume = normalize_counter(legacy_values.get("current_volume", "0"))
    current_chapter = normalize_counter(legacy_values.get("current_chapter", "0"))
    timestamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%f")
    backup_path = project / ".migration-backups" / f"pre-{SKILL_VERSION}-{timestamp}.zip"
    report_path = project / ".agent" / "migration-report.md"
    template_root = skill_root / "templates"

    planned: list[str] = []
    for directory in DIRECTORIES:
        if not (project / directory).is_dir():
            planned.append(f"create directory: {directory}")
    for target in TEMPLATE_MAP.values():
        if not (project / target).exists():
            planned.append(f"create file: {target}")
    legacy_character = find_legacy_file(project, ("character-state.md", "character_state.md"))
    legacy_hooks = find_legacy_file(project, ("plot-hooks.md", "plot_hooks.md"))
    if legacy_character:
        planned.append("preserve legacy character state: memory/legacy-character-state.md")
    if legacy_hooks:
        planned.append("preserve legacy plot hooks: memory/legacy-plot-hooks.md")

    result: dict[str, object] = {
        "project_path": str(project),
        "target_version": SKILL_VERSION,
        "legacy_story_yaml": legacy_story.exists(),
        "project_name": project_name,
        "genre": genre,
        "phase": phase,
        "backup_path": str(backup_path),
        "planned_actions": planned,
        "dry_run": args.dry_run,
    }
    if args.dry_run:
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else "\n".join(planned or ["no changes required"]))
        return 0

    backup_count = create_backup(project, backup_path)
    for directory in DIRECTORIES:
        (project / directory).mkdir(parents=True, exist_ok=True)

    values = {
        "project_name": project_name,
        "created_date": datetime.now().date().isoformat(),
        "skill_version": SKILL_VERSION,
        "genre": genre,
    }
    created: list[str] = []
    for template_name, target_name in TEMPLATE_MAP.items():
        target = project / target_name
        if target.exists():
            continue
        text = render_template((template_root / template_name).read_text(encoding="utf-8"), values)
        if target_name == ".agent/status.md":
            text = replace_field(text, "phase", phase)
            text = replace_field(text, "current_phase", phase)
            text = replace_field(text, "current_volume", current_volume)
            text = replace_field(text, "current_chapter", current_chapter)
            text = replace_field(text, "current_task", "review_migrated_project")
            text = replace_field(text, "last_task", "legacy_project_migrated")
            text = replace_field(text, "next_action", "检查迁移报告并确认旧设定、人物状态和剧情承诺。")
            text = replace_field(text, "blocked_reason", "迁移内容需要用户复核。")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
        created.append(target_name)

    preserved: list[str] = []
    for source, target_name in (
        (legacy_character, "memory/legacy-character-state.md"),
        (legacy_hooks, "memory/legacy-plot-hooks.md"),
    ):
        if source and not (project / target_name).exists():
            shutil.copyfile(source, project / target_name)
            preserved.append(target_name)

    scripts = skill_root / "scripts"
    repair_code = run_validation(scripts / "repair_status.py", project)
    detect_code = run_validation(scripts / "detect_project.py", project, "--json")
    quality_code = run_validation(scripts / "quality_gate.py", project, "--target", "project", "--json")
    consistency_code = run_validation(scripts / "consistency_check.py", project, "--chapter", current_chapter, "--json")
    validation_passed = repair_code == detect_code == quality_code == consistency_code == 0
    report_lines = [
        "# 项目迁移报告",
        "",
        f"- 目标版本：{SKILL_VERSION}",
        f"- 迁移时间：{datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"- 备份文件：{backup_path}",
        f"- 备份文件数：{backup_count}",
        f"- 原 story.yaml：{'保留' if legacy_story.exists() else '未发现'}",
        f"- 验证结果：{'通过' if validation_passed else '未通过'}",
        "",
        "## 新建文件",
        "",
        *[f"- {item}" for item in created],
        "",
        "## 保留的旧资料",
        "",
        *([f"- {item}" for item in preserved] or ["- 无"]),
        "",
        "## 验证退出码",
        "",
        f"- repair：{repair_code}",
        f"- detect：{detect_code}",
        f"- quality：{quality_code}",
        f"- consistency：{consistency_code}",
        "",
        "## 后续动作",
        "",
        "- 对照备份和 legacy 文件确认人物、剧情及伏笔内容。",
        "- 用户确认后，由 updater 将有效内容写入新版记忆台账。",
        "",
    ]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines), encoding="utf-8", newline="\n")
    result.update(
        {
            "backup_file_count": backup_count,
            "created_files": created,
            "preserved_files": preserved,
            "report_path": str(report_path),
            "validation": {
                "repair": repair_code,
                "detect": detect_code,
                "quality": quality_code,
                "consistency": consistency_code,
                "passed": validation_passed,
            },
        }
    )
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else "\n".join(report_lines))
    return 0 if validation_passed else 10


if __name__ == "__main__":
    raise SystemExit(main())
