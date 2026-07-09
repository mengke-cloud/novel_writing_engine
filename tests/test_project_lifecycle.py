from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "scripts" / "init_project.py"
DETECT = ROOT / "scripts" / "detect_project.py"
REPAIR = ROOT / "scripts" / "repair_status.py"


class ProjectLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.project = Path(self.tempdir.name) / "novel"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def run_script(self, script: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run([sys.executable, str(script), *args], capture_output=True, check=False)

    def detect(self) -> dict[str, object]:
        result = self.run_script(DETECT, str(self.project), "--json")
        self.assertEqual(result.returncode, 0)
        return json.loads(result.stdout.decode("utf-8", errors="replace"))

    def initialize(self) -> subprocess.CompletedProcess[bytes]:
        return self.run_script(INIT, str(self.project), "--name", "生命周期测试")

    def test_empty_directory_is_new(self) -> None:
        self.assertEqual(self.detect()["state"], "new")

    def test_dry_run_does_not_create_project(self) -> None:
        result = self.run_script(INIT, str(self.project), "--dry-run")
        self.assertEqual(result.returncode, 0)
        self.assertFalse(self.project.exists())

    def test_initialized_project_has_complete_structure(self) -> None:
        self.assertEqual(self.initialize().returncode, 0)
        result = self.detect()
        self.assertEqual(result["state"], "existing")
        self.assertTrue((self.project / ".agent" / "reports").is_dir())
        self.assertTrue((self.project / "memory" / "promise-ledger.md").is_file())

    def test_second_initialization_is_rejected(self) -> None:
        self.assertEqual(self.initialize().returncode, 0)
        result = self.initialize()
        self.assertEqual(result.returncode, 4)

    def test_partial_project_is_detected(self) -> None:
        (self.project / "memory").mkdir(parents=True)
        self.assertEqual(self.detect()["state"], "partial")

    def test_missing_status_fields_need_repair(self) -> None:
        self.assertEqual(self.initialize().returncode, 0)
        status = self.project / ".agent" / "status.md"
        status.write_text("# Agent Status\n\nproject_name: 生命周期测试\nphase: setup\n", encoding="utf-8")
        result = self.detect()
        self.assertEqual(result["state"], "needs_repair")
        self.assertIn("engine_version:", result["missing_status_fields"])

    def test_repair_dry_run_preserves_file(self) -> None:
        self.assertEqual(self.initialize().returncode, 0)
        status = self.project / ".agent" / "status.md"
        original = "# Agent Status\n\nproject_name: 生命周期测试\nphase: setup\n"
        status.write_text(original, encoding="utf-8")
        result = self.run_script(REPAIR, str(self.project), "--dry-run")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(status.read_text(encoding="utf-8"), original)

    def test_repair_preserves_legacy_version_and_adds_fields(self) -> None:
        self.assertEqual(self.initialize().returncode, 0)
        status = self.project / ".agent" / "status.md"
        status.write_text(
            "# Agent Status\n\nproject_name: 旧项目\nskill_version: 0.8.0\ncurrent_phase: outline\nlast_task: old_outline\n",
            encoding="utf-8",
        )
        result = self.run_script(REPAIR, str(self.project))
        self.assertEqual(result.returncode, 0)
        repaired = status.read_text(encoding="utf-8")
        self.assertIn("engine_version: 0.8.0", repaired)
        self.assertIn("phase: outline", repaired)
        self.assertIn("current_task: old_outline", repaired)
        self.assertEqual(self.detect()["state"], "existing")

    def test_skill_root_is_detected(self) -> None:
        result = self.run_script(DETECT, str(ROOT), "--json")
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout.decode("utf-8", errors="replace"))
        self.assertEqual(payload["state"], "skill_root")


if __name__ == "__main__":
    unittest.main()
