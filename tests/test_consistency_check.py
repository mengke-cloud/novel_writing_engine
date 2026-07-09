from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "scripts" / "init_project.py"
CHECK = ROOT / "scripts" / "consistency_check.py"


class ConsistencyCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.project = Path(self.tempdir.name) / "novel"
        result = subprocess.run(
            [sys.executable, str(INIT), str(self.project), "--name", "一致性测试"],
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def run_check(self, chapter: int) -> tuple[int, dict[str, object]]:
        result = subprocess.run(
            [sys.executable, str(CHECK), str(self.project), "--chapter", str(chapter), "--json"],
            capture_output=True,
            check=False,
        )
        return result.returncode, json.loads(result.stdout.decode("utf-8"))

    def test_empty_ledgers_pass(self) -> None:
        code, result = self.run_check(1)
        self.assertEqual(code, 0)
        self.assertTrue(result["passed"])

    def test_reversed_timeline_blocks(self) -> None:
        (self.project / "memory" / "timeline.md").write_text(
            "# 故事时间线\n\n"
            "### EVT-0001\nchapter: 3\nstory_time: 第三天\nlocation: 城南\nevent: 到达\nconfirmation: 【用户已确认】\n\n"
            "### EVT-0002\nchapter: 2\nstory_time: 第二天\nlocation: 城北\nevent: 出发\nconfirmation: 【用户已确认】\n",
            encoding="utf-8",
        )
        code, result = self.run_check(3)
        self.assertEqual(code, 1)
        self.assertIn("TIMELINE_CHAPTER_REVERSED", {item["code"] for item in result["issues"]})

    def test_future_character_state_blocks(self) -> None:
        (self.project / "memory" / "character-state-ledger.md").write_text(
            "# 人物状态台账\n\n"
            "### CHAR-林默\nchapter: 8\nlocation: 仓库\nphysical_state: 正常\ninventory: 钥匙\n"
            "knows: 仓库编号\ncurrent_goal: 找到失踪者\nconfirmation: 【用户已确认】\n",
            encoding="utf-8",
        )
        code, result = self.run_check(5)
        self.assertEqual(code, 1)
        self.assertIn("CHARACTER_STATE_FROM_FUTURE", {item["code"] for item in result["issues"]})

    def test_overdue_promise_is_important_not_blocking(self) -> None:
        (self.project / "memory" / "promise-ledger.md").write_text(
            "# 剧情承诺台账\n\n"
            "### PRM-0001\n"
            "type: 伏笔\nsummary: 第二枚钥匙用途\nstatus: active\nintroduced_chapter: 1\n"
            "last_advanced_chapter: 2\ndue_chapter: 4\nresolved_chapter:\nsource: 第1章\n"
            "payoff_requirement: 解释钥匙对应的门\nconfirmation: 【用户已确认】\n",
            encoding="utf-8",
        )
        code, result = self.run_check(7)
        self.assertEqual(code, 0)
        self.assertTrue(result["passed"])
        codes = {item["code"] for item in result["issues"]}
        self.assertIn("PROMISE_OVERDUE", codes)
        self.assertIn("PROMISE_STALE", codes)

    def test_resolved_promise_without_chapter_blocks(self) -> None:
        (self.project / "memory" / "promise-ledger.md").write_text(
            "# 剧情承诺台账\n\n"
            "### PRM-0001\n"
            "type: 悬念\nsummary: 失踪者去向\nstatus: resolved\nintroduced_chapter: 1\n"
            "last_advanced_chapter: 3\ndue_chapter: 5\nresolved_chapter:\nsource: 第1章\n"
            "payoff_requirement: 揭示去向\nconfirmation: 【用户已确认】\n",
            encoding="utf-8",
        )
        code, result = self.run_check(5)
        self.assertEqual(code, 1)
        self.assertIn("PROMISE_RESOLUTION_MISSING", {item["code"] for item in result["issues"]})


if __name__ == "__main__":
    unittest.main()
