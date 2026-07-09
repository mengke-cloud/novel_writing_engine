#!/usr/bin/env python3
"""Build a phase-aware, budgeted context package for novel-writing-engine."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
import re
import sys


PHASES = {
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

GENRE_ROUTES = [
    (("无限流", "副本"), "knowledge/genre-guides/infinite-flow.md"),
    (("同人", "衍生"), "knowledge/genre-guides/fanfiction.md"),
    (("末世", "灾变"), "knowledge/genre-guides/apocalypse.md"),
    (("科幻", "太空", "赛博"), "knowledge/genre-guides/science-fiction.md"),
    (("言情", "爱情", "恋爱"), "knowledge/genre-guides/romance.md"),
    (("历史", "古代", "架空历史"), "knowledge/genre-guides/historical.md"),
    (("玄幻", "仙侠", "修仙"), "knowledge/genre-guides/xuanhuan-xianxia.md"),
    (("都市",), "knowledge/genre-guides/urban.md"),
    (("悬疑", "推理", "刑侦"), "knowledge/genre-guides/suspense.md"),
]

PHASE_FILES = {
    "setup": [
        ("settings/world-setting.md", "当前世界观"),
        ("settings/genre-setting.md", "当前类型"),
        ("settings/writing-style.md", "当前文风"),
        ("memory/world-memory.md", "世界观长期记忆"),
        ("memory/character-memory.md", "人物长期记忆"),
    ],
    "outline": [
        ("settings/world-setting.md", "大纲约束"),
        ("settings/genre-setting.md", "类型承诺"),
        ("memory/world-memory.md", "世界观事实"),
        ("memory/character-memory.md", "人物事实"),
        ("memory/plot-memory.md", "剧情进展"),
        ("memory/promise-ledger.md", "活跃剧情承诺"),
    ],
    "volume": [
        ("settings/world-setting.md", "分卷约束"),
        ("settings/genre-setting.md", "类型承诺"),
        ("memory/character-memory.md", "人物状态"),
        ("memory/plot-memory.md", "主线进展"),
        ("memory/promise-ledger.md", "跨卷承诺"),
    ],
    "chapter": [
        ("settings/world-setting.md", "章节世界规则"),
        ("settings/writing-style.md", "章节文风"),
        ("memory/character-state-ledger.md", "人物最新状态"),
        ("memory/timeline.md", "事件时间线"),
        ("memory/plot-memory.md", "剧情进展"),
        ("memory/promise-ledger.md", "本章可推进承诺"),
        ("memory/reader-feedback.md", "追读反馈"),
    ],
    "draft": [
        ("settings/world-setting.md", "正文世界规则"),
        ("settings/writing-style.md", "正文文风"),
        ("memory/character-state-ledger.md", "人物最新状态"),
        ("memory/timeline.md", "连续性时间线"),
        ("memory/plot-memory.md", "剧情进展"),
        ("memory/style-memory.md", "文风记忆"),
        ("memory/promise-ledger.md", "正文承诺约束"),
    ],
    "revision": [
        ("settings/world-setting.md", "改稿事实约束"),
        ("settings/writing-style.md", "改稿文风"),
        ("memory/character-state-ledger.md", "人物一致性"),
        ("memory/timeline.md", "时间线一致性"),
        ("memory/plot-memory.md", "剧情事实"),
        ("memory/style-memory.md", "语言偏好"),
        ("memory/promise-ledger.md", "承诺一致性"),
    ],
    "retention": [
        ("settings/genre-setting.md", "类型承诺"),
        ("memory/plot-memory.md", "剧情进展"),
        ("memory/promise-ledger.md", "钩子与承诺"),
        ("memory/reader-feedback.md", "历史追读反馈"),
    ],
    "archive": [
        ("memory/timeline.md", "待更新时间线"),
        ("memory/character-state-ledger.md", "待更新人物状态"),
        ("memory/plot-memory.md", "待更新剧情记忆"),
        ("memory/foreshadowing-memory.md", "待更新伏笔"),
        ("memory/unresolved-threads.md", "待更新线索"),
        ("memory/promise-ledger.md", "待更新剧情承诺"),
        ("memory/reader-feedback.md", "待更新追读反馈"),
    ],
    "paused": [],
}

SKILL_FILES = {
    "setup": [
        ("modules/01_worldbuilding.md", "世界观工作流"),
        ("modules/03_character.md", "人物工作流"),
        ("knowledge/format-specs/world-setting.md", "世界观格式"),
        ("knowledge/format-specs/character-setting.md", "人物格式"),
    ],
    "outline": [
        ("modules/02_outline.md", "大纲工作流"),
        ("modules/11_promise_tracking.md", "剧情承诺工作流"),
        ("knowledge/format-specs/story-arc.md", "主线格式"),
        ("knowledge/plot-craft/conflict-and-escalation.md", "冲突升级"),
    ],
    "volume": [
        ("modules/02_outline.md", "分卷工作流"),
        ("modules/11_promise_tracking.md", "跨卷承诺"),
        ("knowledge/format-specs/volume-outline.md", "卷纲格式"),
    ],
    "chapter": [
        ("modules/04_chapter_design.md", "章纲工作流"),
        ("modules/10_continuity.md", "连续性工作流"),
        ("modules/11_promise_tracking.md", "承诺工作流"),
        ("knowledge/format-specs/chapter-outline.md", "章纲格式"),
        ("knowledge/scene-craft/scene-engine.md", "场景结构"),
        ("knowledge/plot-craft/hooks-and-payoffs.md", "钩子与兑现"),
    ],
    "draft": [
        ("modules/05_prose_writing.md", "正文工作流"),
        ("modules/08_anti_ai_style.md", "去 AI 化工作流"),
        ("modules/10_continuity.md", "连续性工作流"),
        ("knowledge/format-specs/prose-output.md", "正文格式"),
        ("knowledge/anti-ai/common-rules.md", "通用去 AI 化"),
    ],
    "revision": [
        ("modules/06_revision.md", "改稿工作流"),
        ("modules/08_anti_ai_style.md", "去 AI 化工作流"),
        ("modules/09_quality_gate.md", "质量门禁"),
        ("modules/10_continuity.md", "连续性工作流"),
        ("knowledge/format-specs/chapter-quality-checklist.md", "章节验收"),
    ],
    "retention": [
        ("modules/07_reader_retention.md", "追读工作流"),
        ("modules/09_quality_gate.md", "质量门禁"),
        ("modules/11_promise_tracking.md", "承诺检查"),
        ("knowledge/plot-craft/hooks-and-payoffs.md", "钩子兑现"),
    ],
    "archive": [
        ("modules/00_state_management.md", "状态更新规则"),
        ("modules/09_quality_gate.md", "归档门禁"),
        ("modules/10_continuity.md", "连续性归档"),
        ("modules/11_promise_tracking.md", "承诺归档"),
        ("agents/updater.md", "归档更新边界"),
    ],
    "paused": [("modules/00_state_management.md", "暂停与恢复规则")],
}


@dataclass
class ContextItem:
    path: str
    source: str
    reason: str
    priority: int
    status: str
    original_chars: int
    included_chars: int


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_field(text: str, field: str) -> str:
    match = re.search(rf"(?m)^{re.escape(field)}:\s*(.*?)\s*$", text)
    return match.group(1).strip() if match else ""


def recent_markdown(directory: Path, limit: int) -> list[Path]:
    if not directory.exists():
        return []
    files = [path for path in directory.rglob("*.md") if path.is_file()]
    return sorted(files, key=lambda path: (path.stat().st_mtime, path.name), reverse=True)[:limit]


def add_candidate(
    candidates: list[tuple[Path, str, str, int]],
    seen: set[Path],
    path: Path,
    source: str,
    reason: str,
    priority: int,
) -> None:
    resolved = path.resolve()
    if resolved not in seen:
        candidates.append((resolved, source, reason, priority))
        seen.add(resolved)


def collect_candidates(
    project: Path,
    skill_root: Path,
    phase: str,
    chapter_plan: Path | None,
    draft: Path | None,
) -> list[tuple[Path, str, str, int]]:
    candidates: list[tuple[Path, str, str, int]] = []
    seen: set[Path] = set()
    add_candidate(candidates, seen, project / ".agent/status.md", "project", "唯一状态源", 0)
    add_candidate(candidates, seen, project / "story.md", "project", "项目索引", 0)

    if chapter_plan:
        add_candidate(candidates, seen, chapter_plan, "explicit", "当前章节细纲", 0)
    if draft:
        add_candidate(candidates, seen, draft, "explicit", "当前章节正文", 0)
    add_candidate(candidates, seen, skill_root / "modules/00_state_management.md", "skill", "阶段规则", 0)

    for relative, reason in PHASE_FILES[phase]:
        add_candidate(candidates, seen, project / relative, "project", reason, 1)
    for relative, reason in SKILL_FILES[phase]:
        add_candidate(candidates, seen, skill_root / relative, "skill", reason, 1)

    genre_text = ""
    for path in (project / "settings/genre-setting.md", project / "story.md"):
        if path.exists():
            genre_text += "\n" + read_text(path)
    for keywords, relative in GENRE_ROUTES:
        if any(keyword in genre_text for keyword in keywords):
            add_candidate(candidates, seen, skill_root / relative, "skill", "匹配的类型指南", 1)
            break

    if phase in {"chapter", "draft", "revision", "retention", "archive"}:
        for path in recent_markdown(project / "archives", 2):
            add_candidate(candidates, seen, path, "project", "最近归档章节", 2)
    if phase in {"chapter", "draft"} and chapter_plan is None:
        for path in recent_markdown(project / "chapters", 1):
            add_candidate(candidates, seen, path, "project", "最近章节细纲", 1)
    if phase in {"revision", "retention", "archive"} and draft is None:
        for path in recent_markdown(project / "drafts", 1):
            add_candidate(candidates, seen, path, "project", "最近正文草稿", 1)
    return sorted(candidates, key=lambda item: item[3])


def build_context(
    project: Path,
    phase: str,
    max_chars: int,
    chapter_plan: Path | None = None,
    draft: Path | None = None,
) -> dict[str, object]:
    skill_root = Path(__file__).resolve().parents[1]
    items: list[ContextItem] = []
    sections: list[str] = []
    used = 0
    for path, source, reason, priority in collect_candidates(project, skill_root, phase, chapter_plan, draft):
        display = (
            path.relative_to(project).as_posix()
            if source == "project"
            else path.relative_to(skill_root).as_posix()
            if source == "skill"
            else str(path)
        )
        if not path.exists():
            items.append(ContextItem(display, source, reason, priority, "missing", 0, 0))
            continue
        text = read_text(path)
        remaining = max_chars - used
        if remaining <= 0:
            items.append(ContextItem(display, source, reason, priority, "skipped_budget", len(text), 0))
            continue
        included = text[:remaining]
        status = "included" if len(included) == len(text) else "truncated"
        sections.append(f"## {display}\n\n> 选择原因：{reason}\n\n{included}")
        used += len(included)
        items.append(ContextItem(display, source, reason, priority, status, len(text), len(included)))

    status_text = read_text(project / ".agent/status.md") if (project / ".agent/status.md").exists() else ""
    return {
        "project_path": str(project),
        "phase": phase,
        "task": read_field(status_text, "current_task"),
        "built_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "max_chars": max_chars,
        "used_chars": used,
        "items": [asdict(item) for item in items],
        "content": "\n\n".join(sections),
    }


def render_markdown(result: dict[str, object]) -> str:
    lines = [
        "# 小说任务上下文包",
        "",
        f"- 阶段：{result['phase']}",
        f"- 当前任务：{result['task'] or '未填写'}",
        f"- 字符预算：{result['used_chars']} / {result['max_chars']}",
        f"- 生成时间：{result['built_at']}",
        "",
        "## 文件清单",
        "",
        "| 文件 | 原因 | 优先级 | 状态 | 纳入字符 |",
        "|---|---|---:|---|---:|",
    ]
    for item in result["items"]:
        lines.append(
            f"| `{item['path']}` | {item['reason']} | {item['priority']} | {item['status']} | {item['included_chars']} |"
        )
    lines.extend(["", "## 上下文内容", "", result["content"], ""])
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Build a phase-aware novel context package.")
    parser.add_argument("project_path", nargs="?", default=".")
    parser.add_argument("--phase", default="auto", choices=("auto", *sorted(PHASES)))
    parser.add_argument("--chapter-plan")
    parser.add_argument("--draft")
    parser.add_argument("--max-chars", type=int, default=30000)
    parser.add_argument("--output", help="Write Markdown context package.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.max_chars < 1000:
        parser.error("--max-chars must be at least 1000")

    project = Path(args.project_path).resolve()
    status_path = project / ".agent" / "status.md"
    status_text = read_text(status_path) if status_path.exists() else ""
    phase = read_field(status_text, "phase") if args.phase == "auto" else args.phase
    if phase not in PHASES:
        print(f"invalid or missing phase: {phase or '-'}", file=sys.stderr)
        return 2

    result = build_context(
        project,
        phase,
        args.max_chars,
        Path(args.chapter_plan).resolve() if args.chapter_plan else None,
        Path(args.draft).resolve() if args.draft else None,
    )
    markdown = render_markdown(result)
    if args.output:
        output = Path(args.output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown, encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
