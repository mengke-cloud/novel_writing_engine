from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "novel.py"


class UnifiedCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.project = Path(self.tempdir.name) / "novel"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, check=False)

    def test_init_and_detect(self) -> None:
        initialized = self.run_cli("init", str(self.project), "--name", "CLI测试")
        self.assertEqual(initialized.returncode, 0)
        detected = self.run_cli("detect", str(self.project), "--json")
        self.assertEqual(detected.returncode, 0)
        result = json.loads(detected.stdout.decode("utf-8"))
        self.assertEqual(result["state"], "existing")

    def test_next_builds_context(self) -> None:
        self.assertEqual(self.run_cli("init", str(self.project)).returncode, 0)
        output = self.project / ".agent" / "task" / "context.md"
        result = self.run_cli("next", str(self.project), "--max-chars", "4000", "--output", str(output))
        self.assertEqual(result.returncode, 0)
        self.assertTrue(output.exists())

    def test_failure_exit_code_is_forwarded(self) -> None:
        result = self.run_cli("archive", str(self.project), "--chapter-plan", "missing", "--draft", "missing")
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
