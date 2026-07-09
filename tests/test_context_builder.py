from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "scripts" / "init_project.py"
BUILDER = ROOT / "scripts" / "context_builder.py"


class ContextBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.project = Path(self.tempdir.name) / "novel"
        result = subprocess.run(
            [sys.executable, str(INIT), str(self.project), "--name", "上下文测试"],
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def run_builder(self, *args: str) -> tuple[int, dict[str, object]]:
        result = subprocess.run(
            [sys.executable, str(BUILDER), str(self.project), *args, "--json"],
            capture_output=True,
            check=False,
        )
        return result.returncode, json.loads(result.stdout.decode("utf-8"))

    def test_auto_phase_uses_status(self) -> None:
        code, result = self.run_builder("--max-chars", "12000")
        self.assertEqual(code, 0)
        self.assertEqual(result["phase"], "setup")
        paths = {item["path"] for item in result["items"]}
        self.assertIn(".agent/status.md", paths)
        self.assertIn("knowledge/format-specs/world-setting.md", paths)

    def test_budget_is_never_exceeded(self) -> None:
        code, result = self.run_builder("--phase", "draft", "--max-chars", "1000")
        self.assertEqual(code, 0)
        self.assertLessEqual(result["used_chars"], 1000)
        self.assertTrue(any(item["status"] in {"truncated", "skipped_budget"} for item in result["items"]))

    def test_explicit_current_files_have_highest_priority(self) -> None:
        plan = self.project / "chapters" / "chapter-1.md"
        draft = self.project / "drafts" / "chapter-1.md"
        plan.write_text("# 章纲\n\n本章调查仓库。\n", encoding="utf-8")
        draft.write_text("# 第一章\n\n主角进入仓库。\n", encoding="utf-8")
        code, result = self.run_builder(
            "--phase",
            "revision",
            "--chapter-plan",
            str(plan),
            "--draft",
            str(draft),
            "--max-chars",
            "12000",
        )
        self.assertEqual(code, 0)
        explicit = [item for item in result["items"] if item["source"] == "explicit"]
        self.assertEqual(len(explicit), 2)
        self.assertTrue(all(item["priority"] == 0 for item in explicit))
        self.assertTrue(all(item["status"] == "included" for item in explicit))

    def test_does_not_load_entire_knowledge_library(self) -> None:
        code, result = self.run_builder("--phase", "chapter", "--max-chars", "30000")
        self.assertEqual(code, 0)
        knowledge = [item for item in result["items"] if item["path"].startswith("knowledge/")]
        self.assertLessEqual(len(knowledge), 3)
        self.assertFalse(any(item["path"] == "knowledge/README.md" for item in knowledge))


if __name__ == "__main__":
    unittest.main()
