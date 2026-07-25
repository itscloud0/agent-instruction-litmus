from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from agent_instruction_litmus import cli
from agent_instruction_litmus.fixtures import (
    GEMINI_RELOAD_MARKER,
    NESTED_MARKER,
    REVIEW_MARKER,
    ROOT_MARKER,
    TRUNCATION_MARKER,
)


class CliTests(unittest.TestCase):
    def test_score_returns_zero_on_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            self.assertEqual(
                cli.main(["init", "--fixture", "root-agents-md", "--output", str(workspace)]),
                0,
            )
            (workspace / "result.txt").write_text(ROOT_MARKER, encoding="utf-8")
            self.assertEqual(
                cli.main(["score", "--fixture", "root-agents-md", "--workspace", str(workspace), "--format", "json"]),
                0,
            )

    def test_codex_adapter_is_feasibility_stub(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            self.assertEqual(
                cli.main(["run", "--adapter", "codex-cli", "--fixture", "root-agents-md", "--output", str(workspace)]),
                2,
            )

    def test_codex_adapter_runs_with_explicit_live_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "fixture"
            fake_codex = _write_fake_codex(Path(tmp) / "fake-codex")

            self.assertEqual(
                cli.main(
                    [
                        "run",
                        "--adapter",
                        "codex-cli",
                        "--allow-live",
                        "--codex-bin",
                        str(fake_codex),
                        "--fixture",
                        "root-agents-md",
                        "--output",
                        str(workspace),
                    ]
                ),
                0,
            )

            self.assertIn(ROOT_MARKER, (workspace / "result.txt").read_text(encoding="utf-8"))
            self.assertTrue((workspace / ".litmus" / "codex-stdout.jsonl").exists())
            self.assertTrue((workspace / ".litmus" / "codex-stderr.txt").exists())

    def test_codex_review_adapter_prepares_git_baseline_and_scores_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "fixture"
            fake_codex = _write_fake_codex(Path(tmp) / "fake-codex")

            self.assertEqual(
                cli.main(
                    [
                        "run",
                        "--adapter",
                        "codex-cli",
                        "--allow-live",
                        "--codex-bin",
                        str(fake_codex),
                        "--fixture",
                        "review-loads-agents-md",
                        "--output",
                        str(workspace),
                    ]
                ),
                0,
            )

            self.assertTrue((workspace / ".git").exists())
            self.assertIn(REVIEW_MARKER, (workspace / "agent-output.txt").read_text(encoding="utf-8"))

    def test_opencode_adapter_requires_explicit_live_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            self.assertEqual(
                cli.main(
                    ["run", "--adapter", "opencode-cli", "--fixture", "root-agents-md", "--output", str(workspace)]
                ),
                2,
            )

    def test_gemini_adapter_requires_explicit_live_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            self.assertEqual(
                cli.main(
                    ["run", "--adapter", "gemini-cli", "--fixture", "gemini-memory-reload", "--output", str(workspace)]
                ),
                2,
            )

    def test_gemini_adapter_runs_with_explicit_live_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "fixture"
            fake_gemini = _write_fake_gemini(Path(tmp) / "fake-gemini")

            self.assertEqual(
                cli.main(
                    [
                        "run",
                        "--adapter",
                        "gemini-cli",
                        "--allow-live",
                        "--gemini-bin",
                        str(fake_gemini),
                        "--fixture",
                        "gemini-memory-reload",
                        "--output",
                        str(workspace),
                    ]
                ),
                0,
            )

            self.assertIn(GEMINI_RELOAD_MARKER, (workspace / "result.txt").read_text(encoding="utf-8"))
            self.assertTrue((workspace / ".litmus" / "gemini-stdout.json").exists())
            self.assertTrue((workspace / ".litmus" / "gemini-stderr.txt").exists())

    def test_gemini_adapter_reports_account_block_separately(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "fixture"
            fake_gemini = _write_blocked_gemini(Path(tmp) / "blocked-gemini")

            self.assertEqual(
                cli.main(
                    [
                        "run",
                        "--adapter",
                        "gemini-cli",
                        "--allow-live",
                        "--gemini-bin",
                        str(fake_gemini),
                        "--fixture",
                        "gemini-memory-reload",
                        "--output",
                        str(workspace),
                    ]
                ),
                1,
            )

    def test_opencode_adapter_runs_with_explicit_live_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "fixture"
            fake_opencode = _write_fake_opencode(Path(tmp) / "fake-opencode")

            self.assertEqual(
                cli.main(
                    [
                        "run",
                        "--adapter",
                        "opencode-cli",
                        "--allow-live",
                        "--opencode-bin",
                        str(fake_opencode),
                        "--fixture",
                        "root-agents-md",
                        "--output",
                        str(workspace),
                    ]
                ),
                0,
            )

            self.assertIn(ROOT_MARKER, (workspace / "result.txt").read_text(encoding="utf-8"))
            self.assertTrue((workspace / ".litmus" / "opencode-stdout.jsonl").exists())
            self.assertTrue((workspace / ".litmus" / "opencode-stderr.txt").exists())

    def test_opencode_review_adapter_preserves_agent_written_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "fixture"
            fake_opencode = _write_fake_opencode(Path(tmp) / "fake-opencode")

            self.assertEqual(
                cli.main(
                    [
                        "run",
                        "--adapter",
                        "opencode-cli",
                        "--allow-live",
                        "--opencode-bin",
                        str(fake_opencode),
                        "--fixture",
                        "review-loads-agents-md",
                        "--output",
                        str(workspace),
                    ]
                ),
                0,
            )

            agent_output = (workspace / "agent-output.txt").read_text(encoding="utf-8")
            self.assertIn(REVIEW_MARKER, agent_output)
            self.assertNotIn('"type":"text"', agent_output)


def _write_fake_codex(path: Path) -> Path:
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "from pathlib import Path\n"
        f"root_marker = {ROOT_MARKER!r}\n"
        f"review_marker = {REVIEW_MARKER!r}\n"
        f"nested_marker = {NESTED_MARKER!r}\n"
        f"truncation_marker = {TRUNCATION_MARKER!r}\n"
        "args = sys.argv[1:]\n"
        "out = args[args.index('-o') + 1]\n"
        "if 'review' in args:\n"
        "    Path(out).write_text(f'{review_marker}\\n', encoding='utf-8')\n"
        "else:\n"
        "    workspace = Path(args[args.index('-C') + 1])\n"
        "    if (workspace / 'pkg' / 'result.txt').exists():\n"
        "        (workspace / 'pkg' / 'result.txt').write_text(f'{nested_marker}\\n', encoding='utf-8')\n"
        "    elif 'Boundary Sentinel Instruction' in (workspace / 'AGENTS.md').read_text(encoding='utf-8'):\n"
        "        (workspace / 'result.txt').write_text(f'{truncation_marker}\\n', encoding='utf-8')\n"
        "    else:\n"
        "        (workspace / 'result.txt').write_text(f'{root_marker}\\n', encoding='utf-8')\n"
        "    Path(out).write_text('done\\n', encoding='utf-8')\n"
        "print('{\"event\":\"complete\"}')\n",
        encoding="utf-8",
    )
    os.chmod(path, 0o755)
    return path


def _write_fake_opencode(path: Path) -> Path:
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "import sys\n"
        "from pathlib import Path\n"
        f"root_marker = {ROOT_MARKER!r}\n"
        f"review_marker = {REVIEW_MARKER!r}\n"
        f"nested_marker = {NESTED_MARKER!r}\n"
        f"truncation_marker = {TRUNCATION_MARKER!r}\n"
        "args = sys.argv[1:]\n"
        "workspace = Path(args[args.index('--dir') + 1])\n"
        "message = args[-1]\n"
        "if 'Review' in message:\n"
        "    (workspace / 'agent-output.txt').write_text(f'{review_marker}\\nLooks fine.\\n', encoding='utf-8')\n"
        "    text = 'Done. Review saved.'\n"
        "elif (workspace / 'pkg' / 'result.txt').exists():\n"
        "    (workspace / 'pkg' / 'result.txt').write_text(f'{nested_marker}\\n', encoding='utf-8')\n"
        "    text = 'Done.'\n"
        "elif 'Boundary Sentinel Instruction' in (workspace / 'AGENTS.md').read_text(encoding='utf-8'):\n"
        "    (workspace / 'result.txt').write_text(f'{truncation_marker}\\n', encoding='utf-8')\n"
        "    text = 'Done.'\n"
        "else:\n"
        "    (workspace / 'result.txt').write_text(f'{root_marker}\\n', encoding='utf-8')\n"
        "    text = 'Done.'\n"
        "print(json.dumps({'type': 'text', 'part': {'type': 'text', 'text': text}}))\n",
        encoding="utf-8",
    )
    os.chmod(path, 0o755)
    return path


def _write_fake_gemini(path: Path) -> Path:
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "from pathlib import Path\n"
        f"marker = {GEMINI_RELOAD_MARKER!r}\n"
        "(Path.cwd() / 'result.txt').write_text(f'{marker}\\n', encoding='utf-8')\n"
        "print(json.dumps({'response': 'Done.'}))\n",
        encoding="utf-8",
    )
    os.chmod(path, 0o755)
    return path


def _write_blocked_gemini(path: Path) -> Path:
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "print('IneligibleTierError: UNSUPPORTED_LOCATION', file=sys.stderr)\n"
        "raise SystemExit(1)\n",
        encoding="utf-8",
    )
    os.chmod(path, 0o755)
    return path


if __name__ == "__main__":
    unittest.main()
