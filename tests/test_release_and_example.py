from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "scripts" / "create_example_project.py"
QUALITY = ROOT / "scripts" / "quality_gate.py"
CONTEXT = ROOT / "scripts" / "context_builder.py"
RELEASE = ROOT / "scripts" / "release_check.py"


class ReleaseAndExampleTests(unittest.TestCase):
    def test_example_project_is_runnable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "example"
            created = subprocess.run(
                [sys.executable, str(EXAMPLE), str(project)],
                capture_output=True,
                check=False,
            )
            self.assertEqual(created.returncode, 0)
            quality = subprocess.run(
                [sys.executable, str(QUALITY), str(project), "--target", "project", "--json"],
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality.returncode, 0)
            self.assertTrue(json.loads(quality.stdout.decode("utf-8"))["passed"])
            context = subprocess.run(
                [sys.executable, str(CONTEXT), str(project), "--json"],
                capture_output=True,
                check=False,
            )
            self.assertEqual(context.returncode, 0)

    def test_example_refuses_nonempty_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "example"
            project.mkdir()
            (project / "user-file.txt").write_text("keep", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(EXAMPLE), str(project)],
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual((project / "user-file.txt").read_text(encoding="utf-8"), "keep")

    def test_release_structure_check_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(RELEASE), "--skip-tests", "--json"],
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
        self.assertTrue(json.loads(result.stdout.decode("utf-8"))["passed"])


if __name__ == "__main__":
    unittest.main()
