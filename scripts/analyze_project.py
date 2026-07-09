#!/usr/bin/env python3
"""Generate explainable writing metrics for a novel project."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import re
import statistics
import sys

from consistency_check import parse_entries


CONFLICT_SIGNALS = (
    "但是",
    "却",
    "阻止",
    "拒绝",
    "冲突",
    "危险",
    "失败",
    "代价",
    "威胁",
    "争",
    "打",
    "逃",
    "杀",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def body_length(text: str) -> int:
    text = re.sub(r"(?m)^#{1,6}\s+.*$", "", text)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return len(re.sub(r"\s+", "", text))


def chapter_number(path: Path, text: str) -> int | None:
    for source in (path.stem, text[:200]):
        match = re.search(r"\d+", source)
        if match:
            return int(match.group())
    return None


def character_names(project: Path) -> list[str]:
    ledger = project / "memory" / "character-state-ledger.md"
    names: set[str] = set()
    if ledger.exists():
        entries, _ = parse_entries(ledger, "CHAR-")
        names.update(item["id"].removeprefix("CHAR-") for item in entries)
    settings = project / "settings" / "character-setting"
    if settings.exists():
        names.update(path.stem for path in settings.glob("*.md"))
    return sorted(name for name in names if name and name not in {"人物名", "unknown"})


def analyze_chapters(project: Path) -> tuple[list[dict[str, object]], Counter[str]]:
    archives = sorted((project / "archives").glob("*.md")) if (project / "archives").exists() else []
    source = "archives"
    files = archives
    if not files:
        files = sorted((project / "drafts").glob("*.md")) if (project / "drafts").exists() else []
        source = "drafts"
    names = character_names(project)
    appearances: Counter[str] = Counter()
    chapters: list[dict[str, object]] = []
    for path in files:
        text = read_text(path)
        length = body_length(text)
        counts = {name: text.count(name) for name in names if name in text}
        appearances.update({name: 1 for name, count in counts.items() if count > 0})
        signals = sum(text.count(signal) for signal in CONFLICT_SIGNALS)
        chapters.append(
            {
                "chapter": chapter_number(path, text),
                "file": str(path),
                "source": source,
                "characters": length,
                "conflict_signals": signals,
                "conflict_signals_per_1000": round(signals * 1000 / length, 2) if length else 0,
                "character_mentions": counts,
            }
        )
    return chapters, appearances


def analyze_promises(project: Path) -> dict[str, object]:
    path = project / "memory" / "promise-ledger.md"
    entries, issues = parse_entries(path, "PRM-")
    statuses = Counter(item.get("status", "unknown") for item in entries)
    total = len(entries)
    resolved = statuses.get("resolved", 0)
    return {
        "total": total,
        "active": statuses.get("active", 0),
        "resolved": resolved,
        "abandoned": statuses.get("abandoned", 0),
        "unknown": statuses.get("unknown", 0),
        "resolution_rate": round(resolved / total * 100, 2) if total else 0,
        "parse_issues": len(issues),
    }


def analyze_quality(project: Path) -> list[dict[str, object]]:
    reports = sorted((project / ".agent" / "reports").glob("*.md")) if (project / ".agent" / "reports").exists() else []
    results: list[dict[str, object]] = []
    for path in reports:
        text = read_text(path)
        score_match = re.search(r"质量分数：\s*(\d+)", text)
        blocking_match = re.search(r"阻断项：\s*(\d+)", text)
        if score_match:
            results.append(
                {
                    "file": str(path),
                    "score": int(score_match.group(1)),
                    "blocking": int(blocking_match.group(1)) if blocking_match else 0,
                }
            )
    return results


def analyze(project: Path) -> dict[str, object]:
    chapters, appearances = analyze_chapters(project)
    lengths = [item["characters"] for item in chapters]
    conflict_rates = [item["conflict_signals_per_1000"] for item in chapters]
    quality = analyze_quality(project)
    scores = [item["score"] for item in quality]
    return {
        "project_path": str(project),
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "chapter_summary": {
            "count": len(chapters),
            "total_characters": sum(lengths),
            "average_characters": round(statistics.mean(lengths), 2) if lengths else 0,
            "median_characters": round(statistics.median(lengths), 2) if lengths else 0,
            "shortest": min(lengths) if lengths else 0,
            "longest": max(lengths) if lengths else 0,
            "average_conflict_signals_per_1000": round(statistics.mean(conflict_rates), 2) if conflict_rates else 0,
        },
        "chapters": chapters,
        "character_appearances": dict(appearances.most_common()),
        "promises": analyze_promises(project),
        "quality": {
            "report_count": len(quality),
            "average_score": round(statistics.mean(scores), 2) if scores else 0,
            "latest_score": scores[-1] if scores else None,
            "reports": quality,
        },
        "limitations": [
            "冲突密度仅统计词语信号，不代表真实戏剧张力。",
            "人物出场按姓名文本匹配，别名和代称需要人工合并。",
            "质量分数来自确定性门禁，不等同于文学评价。",
        ],
    }


def render_markdown(result: dict[str, object]) -> str:
    summary = result["chapter_summary"]
    promises = result["promises"]
    quality = result["quality"]
    lines = [
        "# 创作数据分析报告",
        "",
        f"- 生成时间：{result['generated_at']}",
        f"- 统计章节：{summary['count']}",
        f"- 总有效字符：{summary['total_characters']}",
        f"- 平均章节字符：{summary['average_characters']}",
        f"- 章节中位数：{summary['median_characters']}",
        f"- 平均冲突信号/千字：{summary['average_conflict_signals_per_1000']}",
        "",
        "## 章节统计",
        "",
        "| 章节 | 有效字符 | 冲突信号/千字 | 文件 |",
        "|---:|---:|---:|---|",
    ]
    for item in result["chapters"]:
        lines.append(
            f"| {item['chapter'] or '-'} | {item['characters']} | {item['conflict_signals_per_1000']} | `{item['file']}` |"
        )
    lines.extend(["", "## 人物出场", ""])
    lines.extend(
        [f"- {name}：{count} 章" for name, count in result["character_appearances"].items()]
        or ["- 暂无可识别人物"]
    )
    lines.extend(
        [
            "",
            "## 剧情承诺",
            "",
            f"- 总数：{promises['total']}",
            f"- 活跃：{promises['active']}",
            f"- 已回收：{promises['resolved']}",
            f"- 已放弃：{promises['abandoned']}",
            f"- 回收率：{promises['resolution_rate']}%",
            "",
            "## 质量趋势",
            "",
            f"- 报告数量：{quality['report_count']}",
            f"- 平均分：{quality['average_score']}",
            f"- 最近分数：{quality['latest_score'] if quality['latest_score'] is not None else '暂无'}",
            "",
            "## 使用限制",
            "",
            *[f"- {item}" for item in result["limitations"]],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Analyze novel project writing metrics.")
    parser.add_argument("project_path")
    parser.add_argument("--output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    project = Path(args.project_path).resolve()
    if not (project / "story.md").exists():
        print("not a novel-writing-engine project", file=sys.stderr)
        return 2
    result = analyze(project)
    markdown = render_markdown(result)
    if args.output:
        output = Path(args.output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown, encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
