from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "scripts" / "init_project.py"
QUALITY = ROOT / "scripts" / "quality_gate.py"
CONTEXT = ROOT / "scripts" / "context_builder.py"
CONSISTENCY = ROOT / "scripts" / "consistency_check.py"


class CorruptedProjectTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.project = Path(self.tempdir.name) / "novel"
        result = subprocess.run(
            [sys.executable, str(INIT), str(self.project), "--name", "损坏测试"],
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def run_json(self, script: Path, *args: str) -> tuple[int, dict[str, object]]:
        result = subprocess.run(
            [sys.executable, str(script), str(self.project), *args, "--json"],
            capture_output=True,
            check=False,
        )
        return result.returncode, json.loads(result.stdout.decode("utf-8"))

    def modify_status(self, field: str, value: str) -> None:
        path = self.project / ".agent" / "status.md"
        text = path.read_text(encoding="utf-8")
        text = re.sub(rf"(?m)^{re.escape(field)}:.*$", f"{field}: {value}", text)
        path.write_text(text, encoding="utf-8")

    def test_missing_ledger_blocks_project_gate(self) -> None:
        (self.project / "memory" / "timeline.md").unlink()
        code, result = self.run_json(QUALITY, "--target", "project")
        self.assertEqual(code, 1)
        self.assertIn("PROJECT_FILE_MISSING", {item["code"] for item in result["findings"]})

    def test_invalid_phase_blocks_project_gate(self) -> None:
        self.modify_status("phase", "unknown")
        self.modify_status("current_phase", "unknown")
        code, result = self.run_json(QUALITY, "--target", "project")
        self.assertEqual(code, 1)
        self.assertIn("STATUS_PHASE_INVALID", {item["code"] for item in result["findings"]})

    def test_phase_mismatch_blocks_project_gate(self) -> None:
        self.modify_status("phase", "draft")
        self.modify_status("current_phase", "chapter")
        code, result = self.run_json(QUALITY, "--target", "project")
        self.assertEqual(code, 1)
        self.assertIn("STATUS_PHASE_MISMATCH", {item["code"] for item in result["findings"]})

    def test_invalid_phase_prevents_context_build(self) -> None:
        self.modify_status("phase", "unknown")
        result = subprocess.run(
            [sys.executable, str(CONTEXT), str(self.project), "--json"],
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)

    def test_duplicate_promise_ids_block_consistency(self) -> None:
        entry = (
            "### PRM-0001\n"
            "type: 伏笔\nsummary: 钥匙\nstatus: active\nintroduced_chapter: 1\n"
            "source: 第1章\npayoff_requirement: 解释用途\nconfirmation: 【用户已确认】\n"
        )
        (self.project / "memory" / "promise-ledger.md").write_text(
            "# 剧情承诺台账\n\n" + entry + "\n" + entry,
            encoding="utf-8",
        )
        code, result = self.run_json(CONSISTENCY, "--chapter", "1")
        self.assertEqual(code, 1)
        self.assertIn("DUPLICATE_ID", {item["code"] for item in result["issues"]})


if __name__ == "__main__":
    unittest.main()
