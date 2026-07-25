from __future__ import annotations

import argparse
import shutil
import shlex
import sys
from pathlib import Path

from .adapters import run_codex_cli, run_gemini_cli, run_opencode_cli
from .fixtures import create_fixture, get_fixture, list_fixtures
from .report import render
from .score import score_fixture


FORMATS = ("terminal", "json", "markdown")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-instruction-litmus",
        description="Create and score coding-agent instruction-file behavior fixtures.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("fixtures", help="List available fixtures.")

    init_parser = subparsers.add_parser("init", help="Create a disposable fixture repository.")
    init_parser.add_argument("--fixture", required=True, help="Fixture name.")
    init_parser.add_argument("--output", required=True, type=Path, help="Output directory.")
    init_parser.add_argument("--force", action="store_true", help="Overwrite fixture files in a non-empty directory.")

    score_parser = subparsers.add_parser("score", help="Score a completed fixture repository.")
    score_parser.add_argument("--fixture", required=True, help="Fixture name.")
    score_parser.add_argument("--workspace", required=True, type=Path, help="Fixture workspace.")
    score_parser.add_argument("--format", choices=FORMATS, default="terminal", help="Output format.")

    run_parser = subparsers.add_parser("run", help="Prepare a fixture for a supported adapter.")
    run_parser.add_argument(
        "--adapter",
        required=True,
        choices=("manual", "codex-cli", "opencode-cli", "gemini-cli"),
        help="Adapter name.",
    )
    run_parser.add_argument("--fixture", required=True, help="Fixture name.")
    run_parser.add_argument("--output", required=True, type=Path, help="Output directory.")
    run_parser.add_argument("--force", action="store_true", help="Overwrite fixture files in a non-empty directory.")
    run_parser.add_argument("--allow-live", action="store_true", help="Allow the adapter to make live agent/model calls.")
    run_parser.add_argument("--codex-bin", default="codex", help="Codex executable for the codex-cli adapter.")
    run_parser.add_argument("--opencode-bin", default="opencode", help="opencode executable for the opencode-cli adapter.")
    run_parser.add_argument("--gemini-bin", default="gemini", help="Gemini executable for the gemini-cli adapter.")
    run_parser.add_argument(
        "--timeout-seconds",
        default=600,
        type=int,
        help="Maximum seconds to wait for a live adapter run.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "fixtures":
            for fixture in list_fixtures():
                print(f"{fixture.name}\t{fixture.summary}")
            return 0

        if args.command == "init":
            fixture = create_fixture(args.fixture, args.output, force=args.force)
            print(f"created {fixture.name} at {args.output}")
            print(f"prompt: {args.output / 'TASK.md'}")
            print(f"score: agent-instruction-litmus score --fixture {fixture.name} --workspace {args.output}")
            return 0

        if args.command == "score":
            finding = score_fixture(args.fixture, args.workspace)
            sys.stdout.write(render(finding, args.format))
            return 0 if finding.status == "PASS" else 1

        if args.command == "run":
            fixture = create_fixture(args.fixture, args.output, force=args.force)
            if args.adapter == "manual":
                print_manual_instructions(fixture.name, args.output)
                return 0
            if args.adapter == "codex-cli":
                if not args.allow_live:
                    print_codex_instructions(fixture.name, args.output)
                    return 2
                result = run_codex_cli(
                    fixture.name,
                    args.output,
                    codex_bin=args.codex_bin,
                    timeout_seconds=args.timeout_seconds,
                )
                print_adapter_result(result)
                return 0 if result.returncode == 0 and result.finding.status == "PASS" else 1
            if args.adapter == "opencode-cli":
                if not args.allow_live:
                    print_opencode_instructions(fixture.name, args.output)
                    return 2
                result = run_opencode_cli(
                    fixture.name,
                    args.output,
                    opencode_bin=args.opencode_bin,
                    timeout_seconds=args.timeout_seconds,
                )
                print_adapter_result(result)
                return 0 if result.returncode == 0 and result.finding.status == "PASS" else 1
            if args.adapter == "gemini-cli":
                if not args.allow_live:
                    print_gemini_instructions(fixture.name, args.output)
                    return 2
                result = run_gemini_cli(
                    fixture.name,
                    args.output,
                    gemini_bin=args.gemini_bin,
                    timeout_seconds=args.timeout_seconds,
                )
                print_adapter_result(result)
                return 0 if result.returncode == 0 and result.finding.status == "PASS" else 1

    except Exception as exc:
        parser.exit(2, f"error: {exc}\n")

    parser.exit(2, "error: unreachable command state\n")
    return 2


def print_manual_instructions(fixture_name: str, output: Path) -> None:
    fixture = get_fixture(fixture_name)
    print(f"created {fixture.name} at {output}")
    print()
    print("Manual adapter:")
    print(f"1. Open a fresh agent session in: {output}")
    print("2. Paste the contents of TASK.md as the task.")
    if fixture.expected_path == "agent-output.txt":
        print("3. Save the full agent response to agent-output.txt.")
    else:
        print(f"3. Let the agent update {fixture.expected_path}.")
    print(f"4. Score with: agent-instruction-litmus score --fixture {fixture.name} --workspace {output}")


def print_codex_instructions(fixture_name: str, output: Path) -> None:
    fixture = get_fixture(fixture_name)
    codex_path = shutil.which("codex")
    print(f"created {fixture.name} at {output}")
    if codex_path is None:
        print("codex executable was not found on PATH.")
    else:
        print(f"codex executable: {codex_path}")
    print("Automated Codex execution requires explicit opt-in because it may consume Codex/ChatGPT quota.")
    print("Re-run with --allow-live to execute Codex, store captures under .litmus/, and score the fixture.")


def print_opencode_instructions(fixture_name: str, output: Path) -> None:
    fixture = get_fixture(fixture_name)
    opencode_path = shutil.which("opencode")
    print(f"created {fixture.name} at {output}")
    if opencode_path is None:
        print("opencode executable was not found on PATH.")
    else:
        print(f"opencode executable: {opencode_path}")
    print("Automated opencode execution requires explicit opt-in because it may consume provider quota.")
    print("Re-run with --allow-live to execute opencode, store captures under .litmus/, and score the fixture.")


def print_gemini_instructions(fixture_name: str, output: Path) -> None:
    fixture = get_fixture(fixture_name)
    gemini_path = shutil.which("gemini")
    print(f"created {fixture.name} at {output}")
    if gemini_path is None:
        print("Gemini executable was not found on PATH.")
    else:
        print(f"Gemini executable: {gemini_path}")
    print("Automated Gemini execution requires explicit opt-in because it may consume model-provider quota.")
    print("A blocked account or unsupported location is reported as BLOCKED, not as an instruction failure.")
    print("Re-run with --allow-live to execute Gemini, store captures under .litmus/, and score the fixture.")


def print_adapter_result(result) -> None:
    print(f"adapter: {result.adapter}")
    print(f"fixture: {result.fixture}")
    print(f"command: {shlex.join(result.command)}")
    print(f"returncode: {result.returncode}")
    if result.timed_out:
        print("timeout: yes")
    print(f"stdout: {result.stdout_path}")
    print(f"stderr: {result.stderr_path}")
    print(f"last message: {result.last_message_path}")
    print()
    sys.stdout.write(render(result.finding, "terminal"))
