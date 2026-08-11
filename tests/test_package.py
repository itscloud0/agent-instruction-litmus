from __future__ import annotations

import re
import unittest
from pathlib import Path

from agent_instruction_litmus import __version__


class PackageMetadataTests(unittest.TestCase):
    def test_runtime_version_matches_project_metadata(self) -> None:
        project_text = (Path(__file__).parents[1] / "pyproject.toml").read_text(encoding="utf-8")
        match = re.search(r'(?m)^version = "([^"]+)"$', project_text)
        self.assertIsNotNone(match)
        self.assertEqual(__version__, match.group(1))


if __name__ == "__main__":
    unittest.main()
