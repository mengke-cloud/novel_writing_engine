from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "scripts" / "init_project.py"
ANALYTICS = ROOT / "scripts" / "analyze_project.py"


class AnalyticsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.project = Path(self.tempdir.name) / "novel"
        result = subprocess.run(
            [sys.executable, str(INIT), str(self.project), "--name", "分析测试"],
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        (self.project / "archives" / "chapter-0001.md").write_text(
            "# 第 1 章\n\n林默想进入仓库，但是值守人员拒绝。他承担代价后找到钥匙。\n" * 10,
            encoding="utf-8",
        )
        (self.project / "archives" / "chapter-0002.md").write_text(
            "# 第 2 章\n\n林默发现危险，却没有逃。他与周岚争论后改变计划。\n" * 12,
            encoding="utf-8",
        )
        (self.project / "memory" / "character-state-ledger.md").write_text(
            "# 人物状态台账\n\n"
            "### CHAR-林默\nchapter: 2\nlocation: 仓库\nphysical_state: 正常\ninventory: 钥匙\n"
            "knows: 门的位置\ncurrent_goal: 开门\nconfirmation: 【用户已确认】\n\n"
            "### CHAR-周岚\nchapter: 2\nlocation: 仓库\nphysical_state: 正常\ninventory: 无\n"
            "knows: 林默的计划\ncurrent_goal: 阻止开门\nconfirmation: 【用户已确认】\n",
            encoding="utf-8",
        )
        (self.project / "memory" / "promise-ledger.md").write_text(
            "# 剧情承诺台账\n\n"
            "### PRM-0001\ntype: 伏笔\nsummary: 钥匙用途\nstatus: resolved\nintroduced_chapter: 1\n"
            "resolved_chapter: 2\nsource: 第1章\npayoff_requirement: 找到门\nconfirmation: 【用户已确认】\n",
            encoding="utf-8",
        )
        (self.project / ".agent" / "reports" / "chapter-0001-quality.md").write_text(
            "# 质量门禁报告\n\n- 质量分数：90\n- 阻断项：0\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def run_analysis(self, *args: str) -> tuple[int, dict[str, object]]:
        result = subprocess.run(
            [sys.executable, str(ANALYTICS), str(self.project), *args, "--json"],
            capture_output=True,
            check=False,
        )
        return result.returncode, json.loads(result.stdout.decode("utf-8"))

    def test_chapter_statistics(self) -> None:
        code, result = self.run_analysis()
        self.assertEqual(code, 0)
        self.assertEqual(result["chapter_summary"]["count"], 2)
        self.assertGreater(result["chapter_summary"]["total_characters"], 0)
        self.assertGreater(result["chapter_summary"]["average_conflict_signals_per_1000"], 0)

    def test_character_appearances(self) -> None:
        _, result = self.run_analysis()
        self.assertEqual(result["character_appearances"]["林默"], 2)
        self.assertEqual(result["character_appearances"]["周岚"], 1)

    def test_promise_and_quality_metrics(self) -> None:
        _, result = self.run_analysis()
        self.assertEqual(result["promises"]["resolution_rate"], 100.0)
        self.assertEqual(result["quality"]["latest_score"], 90)

    def test_markdown_report_is_written(self) -> None:
        output = self.project / ".agent" / "reports" / "analytics.md"
        result = subprocess.run(
            [sys.executable, str(ANALYTICS), str(self.project), "--output", str(output)],
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("## 使用限制", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
