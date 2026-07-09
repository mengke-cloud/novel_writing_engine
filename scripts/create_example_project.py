#!/usr/bin/env python3
"""Create a deterministic, runnable example novel project."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a runnable example novel project.")
    parser.add_argument("destination")
    args = parser.parse_args()
    destination = Path(args.destination).resolve()
    if destination.exists() and any(destination.iterdir()):
        print("destination must be empty or absent", file=sys.stderr)
        return 2

    init_script = Path(__file__).resolve().with_name("init_project.py")
    result = subprocess.run(
        [
            sys.executable,
            str(init_script),
            str(destination),
            "--name",
            "雾港第二把钥匙",
            "--genre",
            "悬疑",
        ],
        check=False,
    )
    if result.returncode != 0:
        return result.returncode

    status = destination / ".agent" / "status.md"
    text = status.read_text(encoding="utf-8")
    replacements = {
        "phase: setup": "phase: chapter",
        "current_phase: setup": "current_phase: chapter",
        "current_volume: 0": "current_volume: 1",
        "current_chapter: 0": "current_chapter: 1",
        "current_task: confirm_foundation_settings": "current_task: design_chapter_1",
        "last_task: initialized": "last_task: example_project_created",
        "next_action: 与用户确认题材、世界观、主角目标、核心卖点和写作风格。": "next_action: 检查第一章细纲并开始正文。",
    }
    for old, new in replacements.items():
        text = text.replace(old, new, 1)
    status.write_text(text, encoding="utf-8", newline="\n")

    write(
        destination / "settings" / "world-setting.md",
        "# 世界观设定\n\n## 【用户已确认】\n\n- 现代沿海城市雾港。\n- 三年前发生过未解决的南站失踪案。\n\n"
        "## 核心规则\n\n- 调查必须遵守现实证据和警方程序。\n",
    )
    write(
        destination / "settings" / "genre-setting.md",
        "# 题材设定\n\ngenre: 悬疑\n\n## 【用户已确认】\n\n- 核心承诺：通过可回溯证据查明第二枚钥匙的用途。\n",
    )
    write(
        destination / "memory" / "timeline.md",
        "# 故事时间线\n\n### EVT-0001\nchapter: 0\nstory_time: 第一天 07:30\nduration: 10分钟\n"
        "location: 失踪者出租屋\nparticipants: 林默\nevent: 林默发现刻有仓库编号的铝牌\n"
        "causes: 无\nconsequences: 林默前往十三号仓库\nconfirmation: 【用户已确认】\n",
    )
    write(
        destination / "memory" / "character-state-ledger.md",
        "# 人物状态台账\n\n### CHAR-林默\nchapter: 0\nlocation: 十三号仓库外\nphysical_state: 正常\n"
        "emotional_state: 警惕\ninventory: 仓库编号铝牌\nabilities: 调查与现场观察\n"
        "knows: 铝牌来自失踪者房间\nrelationships: 与值守人员互不信任\n"
        "current_goal: 进入仓库寻找线索\nconfirmation: 【用户已确认】\n",
    )
    write(
        destination / "memory" / "promise-ledger.md",
        "# 剧情承诺台账\n\n### PRM-0001\ntype: 悬念\nsummary: 第二枚钥匙用于打开什么\nstatus: active\n"
        "introduced_chapter: 1\nlast_advanced_chapter: 1\ndue_chapter: 8\nresolved_chapter:\n"
        "source: 第一章细纲\npayoff_requirement: 钥匙用途必须由前置证据推导\n"
        "related_characters: 林默\nconfirmation: 【用户已确认】\n",
    )
    write(
        destination / "chapters" / "chapter-1.md",
        "# 第 1 章细纲\n\n## 本章功能\n\n林默确认仓库与失踪案相关。\n\n## 主要冲突\n\n"
        "值守人员拒绝林默进入封锁现场。\n\n## 场景序列\n\n### 场景 1\n\n林默以旧案线索换取五分钟调查时间。\n\n"
        "## 章尾钩子\n\n货架下出现与登记钥匙齿形不同的第二枚钥匙。\n",
    )
    print(f"example project created: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
