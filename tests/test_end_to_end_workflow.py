from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "novel.py"


class EndToEndWorkflowTests(unittest.TestCase):
    def test_initialize_prepare_check_and_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "novel"

            initialized = subprocess.run(
                [sys.executable, str(CLI), "init", str(project), "--name", "端到端测试", "--genre", "悬疑"],
                capture_output=True,
                check=False,
            )
            self.assertEqual(initialized.returncode, 0)

            context = project / ".agent" / "task" / "context.md"
            prepared = subprocess.run(
                [sys.executable, str(CLI), "next", str(project), "--max-chars", "5000", "--output", str(context)],
                capture_output=True,
                check=False,
            )
            self.assertEqual(prepared.returncode, 0)
            self.assertTrue(context.exists())

            project_check = subprocess.run(
                [sys.executable, str(CLI), "quality", str(project), "--target", "project", "--json"],
                capture_output=True,
                check=False,
            )
            self.assertEqual(project_check.returncode, 0)
            self.assertTrue(json.loads(project_check.stdout.decode("utf-8"))["passed"])

            status_path = project / ".agent" / "status.md"
            status = status_path.read_text(encoding="utf-8")
            status = re.sub(r"(?m)^phase:.*$", "phase: archive", status)
            status = re.sub(r"(?m)^current_phase:.*$", "current_phase: archive", status)
            status = re.sub(r"(?m)^current_chapter:.*$", "current_chapter: 1", status)
            status_path.write_text(status, encoding="utf-8")

            plan = project / "chapters" / "chapter-1.md"
            draft = project / "drafts" / "chapter-1.md"
            plan.write_text(
                "# 第 1 章细纲\n\n## 本章功能\n推进主线。\n\n## 主要冲突\n调查受阻。\n\n"
                "## 场景序列\n### 场景 1\n取得线索。\n\n## 章尾钩子\n出现新证据。\n",
                encoding="utf-8",
            )
            draft.write_text(
                "# 第 1 章\n\n" + "主角沿着仓库边缘调查，在值守人员阻拦下找到新的证据。\n" * 40,
                encoding="utf-8",
            )

            archived = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "archive",
                    str(project),
                    "--chapter-plan",
                    str(plan),
                    "--draft",
                    str(draft),
                ],
                capture_output=True,
                check=False,
            )
            self.assertEqual(archived.returncode, 0, archived.stderr.decode("utf-8", errors="replace"))
            self.assertTrue((project / "archives" / "chapter-0001.md").exists())
            self.assertTrue((project / ".agent" / "reports" / "chapter-0001-quality.md").exists())
            self.assertTrue((project / ".agent" / "task" / "chapter-0001-archive-update.md").exists())
            final_status = status_path.read_text(encoding="utf-8")
            self.assertIn("current_task: confirm_archive_updates_chapter_1", final_status)


if __name__ == "__main__":
    unittest.main()
