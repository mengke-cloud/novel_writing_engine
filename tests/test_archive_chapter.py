from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "scripts" / "init_project.py"
ARCHIVE = ROOT / "scripts" / "archive_chapter.py"


class ArchiveChapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.project = Path(self.tempdir.name) / "novel"
        result = subprocess.run(
            [sys.executable, str(INIT), str(self.project), "--name", "归档测试"],
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.plan = self.project / "chapters" / "chapter-1.md"
        self.draft = self.project / "drafts" / "chapter-1.md"
        self.plan.write_text(
            "# 第 1 章细纲\n\n## 本章功能\n推进调查。\n\n## 主要冲突\n进入受阻。\n\n"
            "## 场景序列\n### 场景 1\n寻找线索。\n\n## 章尾钩子\n发现钥匙。\n",
            encoding="utf-8",
        )
        self.draft.write_text(
            "# 第 1 章\n\n" + "林默沿着仓库墙面寻找线索，确认门锁并非唯一入口。\n" * 40,
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def set_archive_phase(self) -> None:
        path = self.project / ".agent" / "status.md"
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"(?m)^phase:.*$", "phase: archive", text)
        text = re.sub(r"(?m)^current_phase:.*$", "current_phase: archive", text)
        text = re.sub(r"(?m)^current_chapter:.*$", "current_chapter: 1", text)
        path.write_text(text, encoding="utf-8")

    def run_archive(self, *extra: str) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            [
                sys.executable,
                str(ARCHIVE),
                str(self.project),
                "--chapter-plan",
                str(self.plan),
                "--draft",
                str(self.draft),
                *extra,
            ],
            capture_output=True,
            check=False,
        )

    def test_wrong_phase_is_rejected(self) -> None:
        result = self.run_archive()
        self.assertEqual(result.returncode, 3)
        self.assertFalse((self.project / "archives" / "chapter-0001.md").exists())

    def test_dry_run_does_not_write(self) -> None:
        self.set_archive_phase()
        result = self.run_archive("--dry-run")
        self.assertEqual(result.returncode, 0)
        self.assertFalse((self.project / "archives" / "chapter-0001.md").exists())

    def test_archive_writes_outputs_and_advances_status(self) -> None:
        self.set_archive_phase()
        result = self.run_archive()
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
        self.assertTrue((self.project / "archives" / "chapter-0001.md").exists())
        self.assertTrue((self.project / ".agent" / "reports" / "chapter-0001-quality.md").exists())
        self.assertTrue((self.project / ".agent" / "task" / "chapter-0001-archive-update.md").exists())
        status = (self.project / ".agent" / "status.md").read_text(encoding="utf-8")
        self.assertIn("phase: archive", status)
        self.assertIn("current_chapter: 1", status)
        self.assertIn("current_task: confirm_archive_updates_chapter_1", status)
        self.assertIn("last_task: archived_chapter_1", status)


if __name__ == "__main__":
    unittest.main()
