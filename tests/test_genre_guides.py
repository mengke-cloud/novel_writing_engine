from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
GUIDES = ROOT / "knowledge" / "genre-guides"
INIT = ROOT / "scripts" / "init_project.py"
CONTEXT = ROOT / "scripts" / "context_builder.py"

EXPANDED_GUIDES = {
    "言情": "romance.md",
    "历史": "historical.md",
    "科幻": "science-fiction.md",
    "末世": "apocalypse.md",
    "无限流": "infinite-flow.md",
    "同人": "fanfiction.md",
}


class GenreGuideTests(unittest.TestCase):
    def test_all_expanded_guides_have_required_sections(self) -> None:
        required = ("适用范围", "核心原则", "执行方法", "常见错误", "检查清单")
        for filename in EXPANDED_GUIDES.values():
            text = (GUIDES / filename).read_text(encoding="utf-8")
            for section in required:
                self.assertIn(section, text, f"{filename} missing {section}")

    def test_guide_index_lists_all_expanded_guides(self) -> None:
        index = (GUIDES / "README.md").read_text(encoding="utf-8")
        routing = (GUIDES / "routing.md").read_text(encoding="utf-8")
        for genre, filename in EXPANDED_GUIDES.items():
            self.assertIn(filename, index)
            self.assertIn(genre, routing)

    def test_context_selects_matching_guide(self) -> None:
        for genre, filename in EXPANDED_GUIDES.items():
            with self.subTest(genre=genre), tempfile.TemporaryDirectory() as temporary:
                project = Path(temporary) / "novel"
                initialized = subprocess.run(
                    [sys.executable, str(INIT), str(project), "--genre", genre],
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(initialized.returncode, 0)
                built = subprocess.run(
                    [sys.executable, str(CONTEXT), str(project), "--phase", "outline", "--max-chars", "30000", "--json"],
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(built.returncode, 0)
                result = json.loads(built.stdout.decode("utf-8"))
                paths = {item["path"] for item in result["items"]}
                self.assertIn(f"knowledge/genre-guides/{filename}", paths)


if __name__ == "__main__":
    unittest.main()
