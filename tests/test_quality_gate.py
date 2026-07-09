from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "scripts" / "init_project.py"
GATE = ROOT / "scripts" / "quality_gate.py"


class QualityGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.project = Path(self.tempdir.name) / "novel"
        result = subprocess.run(
            [sys.executable, str(INIT), str(self.project), "--name", "测试小说", "--genre", "悬疑"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def run_gate(self, *args: str) -> tuple[int, dict[str, object]]:
        result = subprocess.run(
            [sys.executable, str(GATE), str(self.project), *args, "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        return result.returncode, json.loads(result.stdout)

    def write_plan(self) -> Path:
        path = self.project / "chapters" / "chapter-1.md"
        path.write_text(
            "# 第 1 章细纲\n\n"
            "## 本章功能\n推进调查。\n\n"
            "## 主要冲突\n主角被阻拦。\n\n"
            "## 场景序列\n### 场景 1\n主角寻找证据。\n\n"
            "## 章尾钩子\n发现第二枚钥匙。\n",
            encoding="utf-8",
        )
        return path

    def test_new_project_passes_project_gate(self) -> None:
        code, result = self.run_gate("--target", "project")
        self.assertEqual(code, 0)
        self.assertTrue(result["passed"])
        self.assertEqual(result["counts"]["阻断"], 0)

    def test_placeholder_blocks_archive(self) -> None:
        plan = self.write_plan()
        draft = self.project / "drafts" / "chapter-1.md"
        draft.write_text("# 第 1 章\n\n正文内容……\n", encoding="utf-8")

        code, result = self.run_gate(
            "--target", "archive", "--chapter-plan", str(plan), "--draft", str(draft)
        )

        self.assertEqual(code, 1)
        self.assertFalse(result["passed"])
        self.assertIn("DRAFT_PLACEHOLDER", {item["code"] for item in result["findings"]})

    def test_complete_draft_passes_archive(self) -> None:
        plan = self.write_plan()
        draft = self.project / "drafts" / "chapter-1.md"
        draft.write_text("# 第 1 章\n\n" + "他沿着雨后的街道继续寻找线索。停下观察后，又改变了方向。\n" * 30, encoding="utf-8")

        code, result = self.run_gate(
            "--target", "archive", "--chapter-plan", str(plan), "--draft", str(draft)
        )

        self.assertEqual(code, 0)
        self.assertTrue(result["passed"])
        self.assertEqual(result["counts"]["阻断"], 0)

    def test_archive_requires_chapter_plan(self) -> None:
        draft = self.project / "drafts" / "chapter-1.md"
        draft.write_text("# 第 1 章\n\n" + "完整正文内容用于质量门禁测试。\n" * 50, encoding="utf-8")

        code, result = self.run_gate("--target", "archive", "--draft", str(draft))

        self.assertEqual(code, 1)
        self.assertIn("CHAPTER_PLAN_MISSING", {item["code"] for item in result["findings"]})

    def test_consistency_error_blocks_archive(self) -> None:
        plan = self.write_plan()
        draft = self.project / "drafts" / "chapter-1.md"
        draft.write_text("# 第 1 章\n\n" + "完整正文内容用于质量门禁测试。\n" * 50, encoding="utf-8")
        (self.project / "memory" / "promise-ledger.md").write_text(
            "# 剧情承诺台账\n\n"
            "### PRM-0001\n"
            "type: 伏笔\nsummary: 钥匙用途\nstatus: resolved\nintroduced_chapter: 1\n"
            "last_advanced_chapter: 1\ndue_chapter: 3\nresolved_chapter:\nsource: 第1章\n"
            "payoff_requirement: 解释钥匙用途\nconfirmation: 【用户已确认】\n",
            encoding="utf-8",
        )

        code, result = self.run_gate(
            "--target", "archive", "--chapter-plan", str(plan), "--draft", str(draft)
        )

        self.assertEqual(code, 1)
        self.assertIn(
            "CONSISTENCY_PROMISE_RESOLUTION_MISSING",
            {item["code"] for item in result["findings"]},
        )


if __name__ == "__main__":
    unittest.main()
