from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .fixtures import get_fixture
from .report import Finding
from .score import score_fixture


@dataclass(frozen=True)
class AdapterRun:
    adapter: str
    fixture: str
    command: list[str]
    returncode: int
    finding: Finding
    stdout_path: Path
    stderr_path: Path
    last_message_path: Path
    timed_out: bool = False


def run_codex_cli(
    fixture_name: str,
    workspace: Path,
    *,
    codex_bin: str = "codex",
    timeout_seconds: int = 600,
) -> AdapterRun:
    fixture = get_fixture(fixture_name)
    workspace = workspace.resolve()
    codex_path = shutil.which(codex_bin) if os.sep not in codex_bin else codex_bin
    if codex_path is None:
        raise FileNotFoundError(f"codex executable not found: {codex_bin}")

    litmus_dir = workspace / ".litmus"
    litmus_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = litmus_dir / "codex-stdout.jsonl"
    stderr_path = litmus_dir / "codex-stderr.txt"
    last_message_path = litmus_dir / "codex-last-message.txt"

    if fixture.name == "review-loads-agents-md":
        _prepare_review_workspace(workspace)
        command = [
            codex_path,
            "exec",
            "review",
            "--ephemeral",
            "--ignore-user-config",
            "--uncommitted",
            "--json",
            "-o",
            str(last_message_path),
        ]
        cwd = workspace
        stdin_text = None
    else:
        command = [
            codex_path,
            "exec",
            "--ephemeral",
            "--skip-git-repo-check",
            "--ignore-user-config",
            "-C",
            str(workspace),
            "-s",
            "workspace-write",
            "--json",
            "-o",
            str(last_message_path),
            "-",
        ]
        cwd = None
        stdin_text = (workspace / "TASK.md").read_text(encoding="utf-8")

    completed = _run(command, cwd=cwd, stdin_text=stdin_text, timeout_seconds=timeout_seconds)
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")

    if fixture.expected_path == "agent-output.txt" and last_message_path.exists():
        (workspace / fixture.expected_path).write_text(last_message_path.read_text(encoding="utf-8"), encoding="utf-8")

    finding = score_fixture(fixture.name, workspace)
    return AdapterRun(
        adapter="codex-cli",
        fixture=fixture.name,
        command=command,
        returncode=completed.returncode,
        finding=finding,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        last_message_path=last_message_path,
        timed_out=completed.timed_out,
    )


def run_opencode_cli(
    fixture_name: str,
    workspace: Path,
    *,
    opencode_bin: str = "opencode",
    timeout_seconds: int = 600,
) -> AdapterRun:
    fixture = get_fixture(fixture_name)
    workspace = workspace.resolve()
    opencode_path = shutil.which(opencode_bin) if os.sep not in opencode_bin else opencode_bin
    if opencode_path is None:
        raise FileNotFoundError(f"opencode executable not found: {opencode_bin}")

    litmus_dir = workspace / ".litmus"
    litmus_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = litmus_dir / "opencode-stdout.jsonl"
    stderr_path = litmus_dir / "opencode-stderr.txt"
    last_message_path = litmus_dir / "opencode-last-message.txt"

    command = [
        opencode_path,
        "run",
        "--dir",
        str(workspace),
        "--pure",
        "--format",
        "json",
    ]
    if fixture.expected_path != "agent-output.txt":
        command.append("--dangerously-skip-permissions")
    command.append((workspace / "TASK.md").read_text(encoding="utf-8"))

    completed = _run(command, cwd=None, stdin_text=None, timeout_seconds=timeout_seconds)
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")

    response_text = _extract_opencode_text(completed.stdout)
    last_message_path.write_text(response_text, encoding="utf-8")
    if fixture.expected_path == "agent-output.txt":
        output_path = workspace / fixture.expected_path
        if not output_path.exists() or not output_path.read_text(encoding="utf-8").strip():
            output_path.write_text(response_text, encoding="utf-8")

    finding = score_fixture(fixture.name, workspace)
    return AdapterRun(
        adapter="opencode-cli",
        fixture=fixture.name,
        command=command,
        returncode=completed.returncode,
        finding=finding,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        last_message_path=last_message_path,
        timed_out=completed.timed_out,
    )


def run_gemini_cli(
    fixture_name: str,
    workspace: Path,
    *,
    gemini_bin: str = "gemini",
    timeout_seconds: int = 600,
) -> AdapterRun:
    fixture = get_fixture(fixture_name)
    workspace = workspace.resolve()
    gemini_path = shutil.which(gemini_bin) if os.sep not in gemini_bin else gemini_bin
    if gemini_path is None:
        raise FileNotFoundError(f"Gemini executable not found: {gemini_bin}")

    litmus_dir = workspace / ".litmus"
    litmus_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = litmus_dir / "gemini-stdout.json"
    stderr_path = litmus_dir / "gemini-stderr.txt"
    last_message_path = litmus_dir / "gemini-last-message.txt"
    command = [
        gemini_path,
        "--skip-trust",
        "--approval-mode",
        "auto_edit",
        "--output-format",
        "json",
        "--prompt",
        (workspace / "TASK.md").read_text(encoding="utf-8"),
    ]

    completed = _run(command, cwd=workspace, stdin_text=None, timeout_seconds=timeout_seconds)
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    response_text = _extract_gemini_text(completed.stdout)
    last_message_path.write_text(response_text, encoding="utf-8")

    block_reason = _gemini_block_reason(completed.stdout + "\n" + completed.stderr)
    if block_reason:
        finding = Finding(
            status="BLOCKED",
            fixture=fixture.name,
            expected_path=fixture.expected_path,
            expected_marker=fixture.expected_marker,
            message=f"Gemini CLI live validation was blocked before instruction scoring: {block_reason}",
        )
    else:
        finding = score_fixture(fixture.name, workspace)

    return AdapterRun(
        adapter="gemini-cli",
        fixture=fixture.name,
        command=command,
        returncode=completed.returncode,
        finding=finding,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        last_message_path=last_message_path,
        timed_out=completed.timed_out,
    )


@dataclass(frozen=True)
class _Completed:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False


def _run(command: list[str], *, cwd: Path | None, stdin_text: str | None, timeout_seconds: int) -> _Completed:
    env = os.environ.copy()
    env.setdefault("TERM", "xterm-256color")
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            input=stdin_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            env=env,
            check=False,
        )
        return _Completed(completed.returncode, completed.stdout, completed.stderr)
    except subprocess.TimeoutExpired as exc:
        return _Completed(
            124,
            _coerce_text(exc.stdout),
            _coerce_text(exc.stderr) + f"\nTimed out after {timeout_seconds} seconds.\n",
            timed_out=True,
        )


def _coerce_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _extract_opencode_text(stdout: str) -> str:
    messages: list[str] = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        part = event.get("part")
        if not isinstance(part, dict):
            continue
        if part.get("type") != "text":
            continue
        text = part.get("text")
        if isinstance(text, str):
            messages.append(text)
    if messages:
        return "\n".join(messages).strip() + "\n"
    return stdout


def _extract_gemini_text(stdout: str) -> str:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return stdout

    if isinstance(payload, dict):
        for key in ("response", "text", "message"):
            value = payload.get(key)
            if isinstance(value, str):
                return value
    return stdout


def _gemini_block_reason(output: str) -> str | None:
    normalized = output.casefold()
    if "ineligibletiererror" in normalized or "unsupported_location" in normalized:
        return "account tier or location is unsupported (IneligibleTierError/UNSUPPORTED_LOCATION)"
    if "no code assist tier" in normalized or "not eligible" in normalized:
        return "the authenticated account is not eligible for Gemini Code Assist"
    if "401 unauthorized" in normalized or "invalid authentication" in normalized:
        return "Gemini authentication was rejected (HTTP 401)"
    return None


def _prepare_review_workspace(workspace: Path) -> None:
    if (workspace / ".git").exists():
        return

    _git(workspace, "init")
    _git(workspace, "add", ".")
    _git(
        workspace,
        "-c",
        "user.name=agent-instruction-litmus",
        "-c",
        "user.email=agent-instruction-litmus@example.invalid",
        "commit",
        "-m",
        "litmus baseline",
    )

    example = workspace / "src" / "example.py"
    example.write_text(
        "def divide(a, b):\n"
        "    if b == 0:\n"
        "        return 0\n"
        "    return a / b\n",
        encoding="utf-8",
    )


def _git(workspace: Path, *args: str) -> None:
    completed = subprocess.run(
        ["git", *args],
        cwd=workspace,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {completed.stderr.strip()}")
