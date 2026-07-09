#!/usr/bin/env python3
"""Run deterministic quality gates for novel-writing-engine projects."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
import re
import sys

from consistency_check import chapter_number, run_checks


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

REQUIRED_PROJECT_FILES = [
    "story.md",
    ".agent/status.md",
    "settings/world-setting.md",
    "settings/genre-setting.md",
    "settings/writing-style.md",
    "memory/README.md",
    "memory/world-memory.md",
    "memory/character-memory.md",
    "memory/plot-memory.md",
    "memory/style-memory.md",
    "memory/foreshadowing-memory.md",
    "memory/unresolved-threads.md",
    "memory/reader-feedback.md",
    "memory/timeline.md",
    "memory/character-state-ledger.md",
    "memory/promise-ledger.md",
]

REQUIRED_PROJECT_DIRS = [
    "settings",
    "volumes",
    "chapters",
    "drafts",
    "archives",
    "memory",
    ".agent",
]

PLACEHOLDERS = ("正文内容……", "正文内容...", "此处略", "TODO", "TBD", "{{", "}}")


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    file: str = ""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_field(text: str, field: str) -> str:
    match = re.search(rf"(?m)^{re.escape(field)}:\s*(.*?)\s*$", text)
    return match.group(1).strip() if match else ""


def section_content(text: str, title_pattern: str) -> str:
    match = re.search(
        rf"(?ms)^##+\s*(?:{title_pattern})\s*$\s*(.*?)(?=^##+\s|\Z)",
        text,
    )
    if not match:
        return ""
    content = match.group(1)
    content = re.sub(r"```(?:text)?|```", "", content)
    return content.strip()


def has_substantive_pending(text: str) -> bool:
    content = section_content(text, r"(?:【?系统待确认】?|待确认设定|待确认问题)")
    if not content:
        return False
    cleaned = re.sub(r"[\s*\-—：:。]", "", content)
    return cleaned not in {"", "暂无", "无", "待补充"}


def markdown_body_length(text: str) -> int:
    body = re.sub(r"(?m)^#{1,6}\s+.*$", "", text)
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    body = re.sub(r"\s+", "", body)
    return len(body)


def add(findings: list[Finding], severity: str, code: str, message: str, path: Path | None = None) -> None:
    findings.append(Finding(severity, code, message, str(path) if path else ""))


def check_project(project: Path, findings: list[Finding]) -> dict[str, str]:
    for relative in REQUIRED_PROJECT_DIRS:
        path = project / relative
        if not path.is_dir():
            add(findings, "阻断", "PROJECT_DIR_MISSING", f"缺少项目目录：{relative}", path)

    for relative in REQUIRED_PROJECT_FILES:
        path = project / relative
        if not path.is_file():
            add(findings, "阻断", "PROJECT_FILE_MISSING", f"缺少项目文件：{relative}", path)

    status_path = project / ".agent" / "status.md"
    if not status_path.exists():
        return {}

    status_text = read_text(status_path)
    fields = {
        key: read_field(status_text, key)
        for key in (
            "project_name",
            "engine_version",
            "skill_version",
            "phase",
            "current_phase",
            "current_volume",
            "current_chapter",
            "current_task",
            "next_action",
        )
    }
    for key, value in fields.items():
        if not value:
            add(findings, "阻断", "STATUS_FIELD_EMPTY", f"状态字段为空：{key}", status_path)

    phase = fields.get("phase", "")
    if phase and phase not in VALID_PHASES:
        add(findings, "阻断", "STATUS_PHASE_INVALID", f"非法阶段值：{phase}", status_path)
    if phase and fields.get("current_phase") and phase != fields["current_phase"]:
        add(findings, "阻断", "STATUS_PHASE_MISMATCH", "phase 与 current_phase 不一致", status_path)

    for relative in ("story.md", "settings/world-setting.md", "settings/genre-setting.md", "settings/writing-style.md"):
        path = project / relative
        if path.exists() and has_substantive_pending(read_text(path)):
            add(findings, "重要", "PENDING_SETTING", f"存在尚未确认的设定：{relative}", path)

    return fields


def find_chapter_file(project: Path, directory: str, chapter: str) -> Path | None:
    files = sorted((project / directory).glob("*.md"))
    if not files:
        return None
    if chapter and chapter != "0":
        number = re.escape(chapter)
        matched = [path for path in files if re.search(rf"(^|\D)0*{number}(\D|$)", path.stem)]
        if matched:
            return matched[-1]
    return files[-1]


def check_chapter_plan(path: Path | None, findings: list[Finding], required: bool) -> None:
    if path is None or not path.exists():
        severity = "阻断" if required else "重要"
        add(findings, severity, "CHAPTER_PLAN_MISSING", "未找到当前章节细纲", path)
        return

    text = read_text(path)
    if has_substantive_pending(text):
        add(findings, "阻断", "CHAPTER_PLAN_PENDING", "章节细纲仍有待确认内容", path)

    groups = {
        "章节目标或功能": ("本章功能", "本章目标", "章节目标"),
        "主要冲突": ("主要冲突", "本章冲突"),
        "场景序列": ("场景序列", "场景顺序", "场景 1", "场景1"),
        "章尾钩子": ("章尾钩子", "章尾追读"),
    }
    for label, headings in groups.items():
        if not any(heading in text for heading in headings):
            add(findings, "重要", "CHAPTER_PLAN_SECTION_MISSING", f"章纲缺少：{label}", path)


def check_draft(path: Path | None, findings: list[Finding], required: bool) -> None:
    if path is None or not path.exists():
        severity = "阻断" if required else "重要"
        add(findings, severity, "DRAFT_MISSING", "未找到当前章节正文", path)
        return

    text = read_text(path)
    length = markdown_body_length(text)
    if length == 0:
        add(findings, "阻断", "DRAFT_EMPTY", "正文为空", path)
        return
    for marker in PLACEHOLDERS:
        if marker in text:
            add(findings, "阻断", "DRAFT_PLACEHOLDER", f"正文包含未完成标记：{marker}", path)
    if has_substantive_pending(text):
        add(findings, "阻断", "DRAFT_PENDING", "正文包含尚未确认的设定区", path)
    if not re.search(r"(?m)^#\s+.+", text):
        add(findings, "优化", "DRAFT_TITLE_MISSING", "正文缺少一级章节标题", path)
    if length < 500:
        add(findings, "重要", "DRAFT_TOO_SHORT", f"正文有效长度仅 {length} 字，请确认是否完整", path)

    repeated = re.findall(r"([\u4e00-\u9fff]{2,8})[，。！？；]\s*\1", text)
    if repeated:
        add(findings, "优化", "DRAFT_NEAR_REPEAT", "正文存在紧邻重复表达，建议人工复核", path)


def calculate_score(findings: list[Finding]) -> int:
    penalties = {"阻断": 25, "重要": 10, "优化": 3}
    return max(0, 100 - sum(penalties[item.severity] for item in findings))


def build_result(project: Path, target: str, findings: list[Finding]) -> dict[str, object]:
    counts = {severity: sum(item.severity == severity for item in findings) for severity in ("阻断", "重要", "优化")}
    return {
        "project_path": str(project),
        "target": target,
        "checked_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "passed": counts["阻断"] == 0,
        "score": calculate_score(findings),
        "counts": counts,
        "findings": [asdict(item) for item in findings],
    }


def render_markdown(result: dict[str, object]) -> str:
    decision = "通过" if result["passed"] else "未通过"
    lines = [
        "# 质量门禁报告",
        "",
        f"- 检查目标：{result['target']}",
        f"- 检查时间：{result['checked_at']}",
        f"- 检查结论：{decision}",
        f"- 质量分数：{result['score']}",
        f"- 阻断项：{result['counts']['阻断']}",
        f"- 重要项：{result['counts']['重要']}",
        f"- 优化项：{result['counts']['优化']}",
        "",
    ]
    for severity in ("阻断", "重要", "优化"):
        lines.extend([f"## {severity}", ""])
        selected = [item for item in result["findings"] if item["severity"] == severity]
        if not selected:
            lines.append("- 无")
        for item in selected:
            location = f"（{item['file']}）" if item["file"] else ""
            lines.append(f"- `{item['code']}` {item['message']}{location}")
        lines.append("")
    lines.extend(
        [
            "## 门禁决定",
            "",
            "允许进入归档。" if result["passed"] else "禁止进入归档；修复全部阻断项后重新检查。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Run novel-writing-engine quality gates.")
    parser.add_argument("project_path", nargs="?", default=".", help="Novel project directory.")
    parser.add_argument("--target", choices=("auto", "project", "draft", "archive"), default="auto")
    parser.add_argument("--chapter-plan", help="Chapter outline Markdown path.")
    parser.add_argument("--draft", help="Draft Markdown path.")
    parser.add_argument("--report", help="Write a Markdown report to this path.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    project = Path(args.project_path).resolve()
    findings: list[Finding] = []
    fields = check_project(project, findings)
    phase = fields.get("phase", "")
    target = args.target
    if target == "auto":
        target = "archive" if phase == "archive" else "draft" if phase in {"draft", "revision", "retention"} else "project"

    chapter = fields.get("current_chapter", "")
    chapter_plan = Path(args.chapter_plan).resolve() if args.chapter_plan else find_chapter_file(project, "chapters", chapter)
    draft = Path(args.draft).resolve() if args.draft else find_chapter_file(project, "drafts", chapter)

    if target in {"draft", "archive"}:
        check_chapter_plan(chapter_plan, findings, required=True)
        check_draft(draft, findings, required=True)
    if target == "archive":
        for relative in ("story.md", "settings/world-setting.md", "settings/genre-setting.md", "settings/writing-style.md"):
            path = project / relative
            if path.exists() and has_substantive_pending(read_text(path)):
                add(findings, "阻断", "ARCHIVE_PENDING_SETTING", f"归档前仍有待确认设定：{relative}", path)
        current_chapter = chapter_number(fields.get("current_chapter", "")) if fields else None
        consistency = run_checks(project, current_chapter or 0)
        for issue in consistency["issues"]:
            add(
                findings,
                issue["severity"],
                "CONSISTENCY_" + issue["code"],
                issue["message"],
                Path(issue["file"]) if issue["file"] else None,
            )

    result = build_result(project, target, findings)
    markdown = render_markdown(result)
    if args.report:
        report_path = Path(args.report).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(markdown, encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else markdown)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
