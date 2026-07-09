#!/usr/bin/env python3
"""Check timeline, character-state, and story-promise ledgers."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys


@dataclass
class Issue:
    severity: str
    code: str
    message: str
    file: str = ""
    entry_id: str = ""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def parse_entries(path: Path, prefix: str) -> tuple[list[dict[str, str]], list[Issue]]:
    if not path.exists():
        return [], [Issue("阻断", "LEDGER_MISSING", f"缺少台账文件：{path.name}", str(path))]

    text = re.sub(r"(?ms)^```.*?^```\s*", "", read_text(path))
    pattern = rf"(?ms)^###\s+({re.escape(prefix)}[^\s]+)\s*$\s*(.*?)(?=^###\s+|\Z)"
    entries: list[dict[str, str]] = []
    issues: list[Issue] = []
    seen: set[str] = set()
    for match in re.finditer(pattern, text):
        entry_id = match.group(1).strip()
        if entry_id in seen:
            issues.append(Issue("阻断", "DUPLICATE_ID", f"重复条目 ID：{entry_id}", str(path), entry_id))
        seen.add(entry_id)
        fields = {"id": entry_id}
        for line in match.group(2).splitlines():
            field_match = re.match(r"^([a-z_]+):\s*(.*?)\s*$", line)
            if field_match:
                fields[field_match.group(1)] = field_match.group(2)
        entries.append(fields)
    return entries, issues


def chapter_number(value: str) -> int | None:
    if not value:
        return None
    match = re.search(r"\d+", value)
    return int(match.group()) if match else None


def check_required(
    entries: list[dict[str, str]],
    fields: tuple[str, ...],
    path: Path,
    issues: list[Issue],
) -> None:
    for entry in entries:
        for field in fields:
            if not entry.get(field):
                issues.append(
                    Issue("阻断", "FIELD_MISSING", f"{entry['id']} 缺少字段：{field}", str(path), entry["id"])
                )


def check_timeline(path: Path, issues: list[Issue]) -> list[dict[str, str]]:
    entries, parse_issues = parse_entries(path, "EVT-")
    issues.extend(parse_issues)
    check_required(entries, ("chapter", "story_time", "location", "event", "confirmation"), path, issues)
    previous = -1
    for entry in entries:
        number = chapter_number(entry.get("chapter", ""))
        if number is None:
            issues.append(Issue("阻断", "CHAPTER_INVALID", f"{entry['id']} 的章节号无效", str(path), entry["id"]))
        elif number < previous:
            issues.append(
                Issue("阻断", "TIMELINE_CHAPTER_REVERSED", f"{entry['id']} 出现在更早章节之后，记录顺序倒置", str(path), entry["id"])
            )
        else:
            previous = number
        causes = [item.strip() for item in entry.get("causes", "").split(",") if item.strip()]
        known = {item["id"] for item in entries}
        for cause in causes:
            if cause not in known and cause not in {"none", "无"}:
                issues.append(
                    Issue("重要", "TIMELINE_CAUSE_UNKNOWN", f"{entry['id']} 引用了不存在的原因事件：{cause}", str(path), entry["id"])
                )
    return entries


def check_characters(path: Path, current_chapter: int, issues: list[Issue]) -> list[dict[str, str]]:
    entries, parse_issues = parse_entries(path, "CHAR-")
    issues.extend(parse_issues)
    check_required(
        entries,
        ("chapter", "location", "physical_state", "inventory", "knows", "current_goal", "confirmation"),
        path,
        issues,
    )
    for entry in entries:
        number = chapter_number(entry.get("chapter", ""))
        if number is None:
            issues.append(Issue("阻断", "CHARACTER_CHAPTER_INVALID", f"{entry['id']} 的章节号无效", str(path), entry["id"]))
        elif current_chapter and number > current_chapter:
            issues.append(
                Issue("阻断", "CHARACTER_STATE_FROM_FUTURE", f"{entry['id']} 使用了未来章节状态", str(path), entry["id"])
            )
        elif current_chapter and number < current_chapter - 3:
            issues.append(
                Issue("重要", "CHARACTER_STATE_STALE", f"{entry['id']} 已超过三章未更新", str(path), entry["id"])
            )
    return entries


def check_promises(path: Path, current_chapter: int, issues: list[Issue]) -> list[dict[str, str]]:
    entries, parse_issues = parse_entries(path, "PRM-")
    issues.extend(parse_issues)
    check_required(
        entries,
        ("type", "summary", "status", "introduced_chapter", "source", "payoff_requirement", "confirmation"),
        path,
        issues,
    )
    valid_status = {"active", "resolved", "abandoned"}
    for entry in entries:
        status = entry.get("status", "")
        if status and status not in valid_status:
            issues.append(Issue("阻断", "PROMISE_STATUS_INVALID", f"{entry['id']} 状态非法：{status}", str(path), entry["id"]))
        introduced = chapter_number(entry.get("introduced_chapter", ""))
        advanced = chapter_number(entry.get("last_advanced_chapter", ""))
        due = chapter_number(entry.get("due_chapter", ""))
        resolved = chapter_number(entry.get("resolved_chapter", ""))
        if introduced is None:
            issues.append(Issue("阻断", "PROMISE_CHAPTER_INVALID", f"{entry['id']} 缺少有效提出章节", str(path), entry["id"]))
        if due is not None and introduced is not None and due < introduced:
            issues.append(Issue("阻断", "PROMISE_DUE_BEFORE_START", f"{entry['id']} 的预计回收章节早于提出章节", str(path), entry["id"]))
        if status == "active" and current_chapter:
            if due is not None and current_chapter > due:
                issues.append(Issue("重要", "PROMISE_OVERDUE", f"{entry['id']} 已超过预计回收章节 {due}", str(path), entry["id"]))
            if advanced is not None and current_chapter - advanced >= 5:
                issues.append(Issue("重要", "PROMISE_STALE", f"{entry['id']} 已连续五章未推进", str(path), entry["id"]))
        if status == "resolved" and resolved is None:
            issues.append(Issue("阻断", "PROMISE_RESOLUTION_MISSING", f"{entry['id']} 已回收但缺少回收章节", str(path), entry["id"]))
        if status == "resolved" and resolved is not None and introduced is not None and resolved < introduced:
            issues.append(Issue("阻断", "PROMISE_RESOLVED_BEFORE_START", f"{entry['id']} 的回收章节早于提出章节", str(path), entry["id"]))
    return entries


def run_checks(project: Path, current_chapter: int = 0) -> dict[str, object]:
    memory = project / "memory"
    issues: list[Issue] = []
    timeline = check_timeline(memory / "timeline.md", issues)
    characters = check_characters(memory / "character-state-ledger.md", current_chapter, issues)
    promises = check_promises(memory / "promise-ledger.md", current_chapter, issues)
    counts = {severity: sum(issue.severity == severity for issue in issues) for severity in ("阻断", "重要", "优化")}
    return {
        "project_path": str(project),
        "current_chapter": current_chapter,
        "passed": counts["阻断"] == 0,
        "counts": counts,
        "entry_counts": {
            "timeline": len(timeline),
            "characters": len(characters),
            "promises": len(promises),
        },
        "issues": [asdict(issue) for issue in issues],
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Check long-form novel consistency and promises.")
    parser.add_argument("project_path", nargs="?", default=".")
    parser.add_argument("--chapter", type=int, default=0, help="Current chapter number.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_checks(Path(args.project_path).resolve(), args.chapter)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("一致性检查：" + ("通过" if result["passed"] else "未通过"))
        print(f"阻断：{result['counts']['阻断']}")
        print(f"重要：{result['counts']['重要']}")
        print(f"优化：{result['counts']['优化']}")
        for issue in result["issues"]:
            print(f"- [{issue['severity']}] {issue['code']}: {issue['message']}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
