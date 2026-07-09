from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "novel.py"


class MigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.project = Path(self.tempdir.name) / "legacy"
        self.project.mkdir()
        (self.project / "story.yaml").write_text(
            "title: 旧城谜案\ngenre: 悬疑\ncurrent_phase: outline\ncurrent_volume: 1\ncurrent_chapter: 3\n",
            encoding="utf-8",
        )
        (self.project / "character-state.md").write_text("# 旧人物状态\n\n林默：受伤。\n", encoding="utf-8")
        (self.project / "plot-hooks.md").write_text("# 旧剧情钩子\n\n第二枚钥匙。\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, check=False)

    def test_dry_run_does_not_write(self) -> None:
        result = self.run_cli("migrate", str(self.project), "--dry-run", "--json")
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout.decode("utf-8"))
        self.assertTrue(payload["dry_run"])
        self.assertFalse((self.project / "story.md").exists())
        self.assertFalse((self.project / ".migration-backups").exists())

    def test_migration_preserves_legacy_and_validates(self) -> None:
        result = self.run_cli("migrate", str(self.project), "--json")
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
        payload = json.loads(result.stdout.decode("utf-8"))
        self.assertTrue(payload["validation"]["passed"])
        self.assertTrue((self.project / "story.yaml").exists())
        self.assertTrue((self.project / "story.md").exists())
        self.assertTrue((self.project / ".agent" / "migration-report.md").exists())
        self.assertTrue((self.project / "memory" / "legacy-character-state.md").exists())
        self.assertTrue((self.project / "memory" / "legacy-plot-hooks.md").exists())
        backups = list((self.project / ".migration-backups").glob("*.zip"))
        self.assertEqual(len(backups), 1)
        with zipfile.ZipFile(backups[0]) as archive:
            self.assertIn("story.yaml", archive.namelist())
            self.assertIn("character-state.md", archive.namelist())

    def test_migration_maps_legacy_fields(self) -> None:
        self.assertEqual(self.run_cli("migrate", str(self.project)).returncode, 0)
        status = (self.project / ".agent" / "status.md").read_text(encoding="utf-8")
        story = (self.project / "story.md").read_text(encoding="utf-8")
        self.assertIn("project_name: 旧城谜案", status)
        self.assertIn("phase: outline", status)
        self.assertIn("current_volume: 1", status)
        self.assertIn("current_chapter: 3", status)
        self.assertIn("# 旧城谜案", story)
        self.assertIn("genre: 悬疑", story)

    def test_existing_story_is_not_overwritten(self) -> None:
        original = "# 用户已有的新入口\n"
        (self.project / "story.md").write_text(original, encoding="utf-8")
        self.assertEqual(self.run_cli("migrate", str(self.project)).returncode, 0)
        self.assertEqual((self.project / "story.md").read_text(encoding="utf-8"), original)

    def test_existing_incomplete_status_is_repaired(self) -> None:
        (self.project / ".agent").mkdir()
        (self.project / ".agent" / "status.md").write_text(
            "# Agent Status\n\nproject_name: 旧城谜案\ncurrent_phase: outline\n",
            encoding="utf-8",
        )
        result = self.run_cli("migrate", str(self.project), "--json")
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout.decode("utf-8"))
        self.assertEqual(payload["validation"]["repair"], 0)
        status = (self.project / ".agent" / "status.md").read_text(encoding="utf-8")
        self.assertIn("engine_version:", status)
        self.assertIn("phase: outline", status)

    def test_skill_root_is_rejected(self) -> None:
        result = self.run_cli("migrate", str(ROOT))
        self.assertEqual(result.returncode, 3)


if __name__ == "__main__":
    unittest.main()
