#!/usr/bin/env python3
"""Safely archive a completed chapter and advance project status."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re
import shutil
import subprocess
import sys


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_field(text: str, field: str) -> str:
    match = re.search(rf"(?m)^{re.escape(field)}:\s*(.*?)\s*$", text)
    return match.group(1).strip() if match else ""


def write_field(text: str, field: str, value: str) -> str:
    pattern = rf"(?m)^({re.escape(field)}:)\s*.*$"
    replacement = rf"\g<1> {value}"
    if re.search(pattern, text):
        return re.sub(pattern, replacement, text, count=1)
    return text.rstrip() + f"\n{field}: {value}\n"


def chapter_number(status_text: str, draft: Path) -> int | None:
    value = read_field(status_text, "current_chapter")
    match = re.search(r"\d+", value)
    if match and int(match.group()) > 0:
        return int(match.group())
    match = re.search(r"\d+", draft.stem)
    return int(match.group()) if match else None


def render_template(path: Path, values: dict[str, str]) -> str:
    text = read_text(path)
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Archive a chapter after quality gates pass.")
    parser.add_argument("project_path")
    parser.add_argument("--chapter-plan", required=True)
    parser.add_argument("--draft", required=True)
    parser.add_argument("--force", action="store_true", help="Overwrite an existing archive and report.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project = Path(args.project_path).resolve()
    plan = Path(args.chapter_plan).resolve()
    draft = Path(args.draft).resolve()
    status_path = project / ".agent" / "status.md"
    if not status_path.exists() or not plan.exists() or not draft.exists():
        print("missing status, chapter plan, or draft", file=sys.stderr)
        return 2

    status_text = read_text(status_path)
    if read_field(status_text, "phase") != "archive":
        print("refusing to archive unless phase is archive", file=sys.stderr)
        return 3
    number = chapter_number(status_text, draft)
    if number is None:
        print("cannot determine chapter number", file=sys.stderr)
        return 4

    archive_path = project / "archives" / f"chapter-{number:04d}.md"
    report_path = project / ".agent" / "reports" / f"chapter-{number:04d}-quality.md"
    update_path = project / ".agent" / "task" / f"chapter-{number:04d}-archive-update.md"
    protected = [archive_path, update_path]
    existing = [path for path in protected if path.exists()]
    if existing and not args.force:
        print("refusing to overwrite existing archive outputs:", file=sys.stderr)
        for path in existing:
            print(f"- {path}", file=sys.stderr)
        return 5

    print(f"chapter: {number}")
    print(f"quality_report: {report_path}")
    print(f"archive: {archive_path}")
    print(f"update_suggestion: {update_path}")
    print(f"next_chapter: {number + 1}")
    if args.dry_run:
        print("dry run complete; no files were written.")
        return 0

    quality_script = Path(__file__).resolve().with_name("quality_gate.py")
    command = [
        sys.executable,
        str(quality_script),
        str(project),
        "--target",
        "archive",
        "--chapter-plan",
        str(plan),
        "--draft",
        str(draft),
        "--report",
        str(report_path),
    ]
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        print("archive aborted because quality gate failed", file=sys.stderr)
        return 10

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    update_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(draft, archive_path)
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    template = Path(__file__).resolve().parents[1] / "templates" / "archive-update.md.template"
    update_text = render_template(
        template,
        {
            "chapter": str(number),
            "archive_path": str(archive_path),
            "draft_path": str(draft),
            "quality_report": str(report_path),
            "updated_at": now,
        },
    )
    update_path.write_text(update_text, encoding="utf-8", newline="\n")

    updated = status_text
    for field, value in {
        "updated_at": now,
        "phase": "archive",
        "current_phase": "archive",
        "current_chapter": str(number),
        "current_task": f"confirm_archive_updates_chapter_{number}",
        "last_task": f"archived_chapter_{number}",
        "next_action": f"确认第 {number} 章记忆更新建议；写入后进入第 {number + 1} 章。",
        "blocked_reason": "",
    }.items():
        updated = write_field(updated, field, value)
    status_path.write_text(updated, encoding="utf-8", newline="\n")

    print("archive complete")
    print("status updated to await memory-update confirmation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
