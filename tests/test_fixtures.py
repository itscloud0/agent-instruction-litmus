from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_instruction_litmus.fixtures import NESTED_MARKER, NESTED_ROOT_MARKER, ROOT_MARKER, create_fixture, list_fixtures
from agent_instruction_litmus.score import score_fixture


class FixtureTests(unittest.TestCase):
    def test_list_fixtures_has_initial_cases(self) -> None:
        names = {fixture.name for fixture in list_fixtures()}
        self.assertIn("root-agents-md", names)
        self.assertIn("review-loads-agents-md", names)
        self.assertIn("nested-scope-precedence", names)

    def test_root_fixture_scores_fail_then_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            create_fixture("root-agents-md", workspace)

            initial = score_fixture("root-agents-md", workspace)
            self.assertEqual(initial.status, "FAIL")

            (workspace / "result.txt").write_text(f"done {ROOT_MARKER}\n", encoding="utf-8")
            passed = score_fixture("root-agents-md", workspace)
            self.assertEqual(passed.status, "PASS")

    def test_review_fixture_scores_missing_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            create_fixture("review-loads-agents-md", workspace)
            (workspace / "agent-output.txt").write_text("Looks fine.\n", encoding="utf-8")

            finding = score_fixture("review-loads-agents-md", workspace)
            self.assertEqual(finding.status, "FAIL")
            self.assertIn("expected marker is absent", finding.message)

    def test_fixture_ignores_local_codex_capture_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            create_fixture("review-loads-agents-md", workspace)

            gitignore = (workspace / ".gitignore").read_text(encoding="utf-8")
            self.assertIn(".litmus/", gitignore)
            self.assertIn("codex-*.jsonl", gitignore)
            self.assertIn("codex-*.txt", gitignore)

    def test_nested_fixture_rejects_root_fallback_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            create_fixture("nested-scope-precedence", workspace)

            result = workspace / "pkg" / "result.txt"
            result.write_text(f"{NESTED_MARKER}\n{NESTED_ROOT_MARKER}\n", encoding="utf-8")
            failed = score_fixture("nested-scope-precedence", workspace)
            self.assertEqual(failed.status, "FAIL")
            self.assertIn("forbidden marker", failed.message)

            result.write_text(f"{NESTED_MARKER}\n", encoding="utf-8")
            passed = score_fixture("nested-scope-precedence", workspace)
            self.assertEqual(passed.status, "PASS")


if __name__ == "__main__":
    unittest.main()
