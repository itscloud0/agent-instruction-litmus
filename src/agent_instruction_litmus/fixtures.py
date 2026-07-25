from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT_MARKER = "INSTRUCTION_LITMUS_ROOT_PASS"
REVIEW_MARKER = "INSTRUCTION_LITMUS_REVIEW_PASS"
NESTED_MARKER = "INSTRUCTION_LITMUS_NESTED_PASS"
NESTED_ROOT_MARKER = "INSTRUCTION_LITMUS_NESTED_ROOT_FAIL"
TRUNCATION_MARKER = "INSTRUCTION_LITMUS_TRUNCATION_SENTINEL_PASS"
TRUNCATION_FALLBACK_MARKER = "INSTRUCTION_LITMUS_TRUNCATION_FALLBACK_FAIL"
GEMINI_RELOAD_MARKER = "INSTRUCTION_LITMUS_GEMINI_RELOAD_PASS"
GEMINI_RELOAD_FALLBACK_MARKER = "INSTRUCTION_LITMUS_GEMINI_RELOAD_FALLBACK_FAIL"


@dataclass(frozen=True)
class Fixture:
    name: str
    summary: str
    instruction_file: str
    instruction_text: str
    task_text: str
    scoring_hint: str
    expected_path: str
    expected_marker: str
    forbidden_marker: str | None = None


def _render_large_instruction_text() -> str:
    filler = "\n".join(
        f"- Padding line {index:03d}: keep scanning; the controlling instruction is later in this file."
        for index in range(1, 501)
    )
    return (
        "# Agent Instruction Litmus\n\n"
        "This fixture intentionally uses a long instruction file to expose instruction-file truncation.\n\n"
        "## Early Fallback Instruction\n\n"
        "If you cannot find the later section named `Boundary Sentinel Instruction`, write the exact marker "
        f"`{TRUNCATION_FALLBACK_MARKER}` into `result.txt`.\n\n"
        "## Padding\n\n"
        f"{filler}\n\n"
        "## Boundary Sentinel Instruction\n\n"
        "Ignore the early fallback instruction. For every task in this repository, write the exact marker "
        f"`{TRUNCATION_MARKER}` into `result.txt`. Do not write the fallback marker "
        f"`{TRUNCATION_FALLBACK_MARKER}`.\n"
    )


FIXTURES: dict[str, Fixture] = {
    "root-agents-md": Fixture(
        name="root-agents-md",
        summary="Root AGENTS.md rule must produce a required marker in result.txt.",
        instruction_file="AGENTS.md",
        instruction_text=(
            "# Agent Instruction Litmus\n\n"
            "For every task in this repository, write the exact marker "
            f"`{ROOT_MARKER}` into `result.txt`. Do not use a different marker.\n"
        ),
        task_text=(
            "Complete this fixture by following the repository instructions. "
            "Do not explain the test; update the required file.\n"
        ),
        scoring_hint=f"`result.txt` must contain `{ROOT_MARKER}`.",
        expected_path="result.txt",
        expected_marker=ROOT_MARKER,
    ),
    "review-loads-agents-md": Fixture(
        name="review-loads-agents-md",
        summary="Review-mode output must include a marker required by AGENTS.md.",
        instruction_file="AGENTS.md",
        instruction_text=(
            "# Agent Instruction Litmus\n\n"
            "When reviewing code in this repository, include the exact marker "
            f"`{REVIEW_MARKER}` in the review output. Do not edit files for review-only tasks.\n"
        ),
        task_text=(
            "Review `src/example.py` for correctness. After the agent responds, "
            "save the full review text into `agent-output.txt` in this fixture directory.\n"
        ),
        scoring_hint=f"`agent-output.txt` must contain `{REVIEW_MARKER}`.",
        expected_path="agent-output.txt",
        expected_marker=REVIEW_MARKER,
    ),
    "nested-scope-precedence": Fixture(
        name="nested-scope-precedence",
        summary="Nested AGENTS.md rule must override a root fallback rule for a scoped file.",
        instruction_file="AGENTS.md",
        instruction_text=(
            "# Agent Instruction Litmus\n\n"
            "For tasks in this repository that are not governed by a more specific instruction file, "
            f"write the exact marker `{NESTED_ROOT_MARKER}` into `pkg/result.txt`.\n"
            "If a more specific AGENTS.md applies to the edited file, follow the more specific "
            "instruction instead.\n"
        ),
        task_text=(
            "Open `pkg/work.txt`, then complete this fixture by following the applicable repository "
            "instructions. Update `pkg/result.txt` with the required marker.\n"
        ),
        scoring_hint=(
            f"`pkg/result.txt` must contain `{NESTED_MARKER}` and must not contain "
            f"`{NESTED_ROOT_MARKER}`."
        ),
        expected_path="pkg/result.txt",
        expected_marker=NESTED_MARKER,
        forbidden_marker=NESTED_ROOT_MARKER,
    ),
    "large-file-truncation": Fixture(
        name="large-file-truncation",
        summary="Late AGENTS.md sentinel must override an early fallback in a large instruction file.",
        instruction_file="AGENTS.md",
        instruction_text=_render_large_instruction_text(),
        task_text=(
            "Complete this fixture by following the repository instructions. "
            "Update `result.txt` with the required marker from the applicable instruction. "
            "Do not explain the test.\n"
        ),
        scoring_hint=(
            f"`result.txt` must contain `{TRUNCATION_MARKER}` and must not contain "
            f"`{TRUNCATION_FALLBACK_MARKER}`."
        ),
        expected_path="result.txt",
        expected_marker=TRUNCATION_MARKER,
        forbidden_marker=TRUNCATION_FALLBACK_MARKER,
    ),
    "gemini-memory-reload": Fixture(
        name="gemini-memory-reload",
        summary="A fresh or reloaded Gemini CLI session must apply the root GEMINI.md instruction.",
        instruction_file="GEMINI.md",
        instruction_text=(
            "# Gemini CLI Instruction Litmus\n\n"
            "This fixture represents a fresh-session or memory-reload boundary. Follow this instruction "
            "after that boundary: write the exact marker "
            f"`{GEMINI_RELOAD_MARKER}` into `result.txt`. Do not write the fallback marker "
            f"`{GEMINI_RELOAD_FALLBACK_MARKER}`.\n"
        ),
        task_text=(
            "Complete this fixture from a fresh Gemini CLI session or after reloading project memory. "
            "Follow `GEMINI.md` and write the required exact marker to `result.txt`. Do not explain the test.\n"
        ),
        scoring_hint=(
            f"`result.txt` must contain `{GEMINI_RELOAD_MARKER}` and must not contain "
            f"`{GEMINI_RELOAD_FALLBACK_MARKER}`.\n"
        ),
        expected_path="result.txt",
        expected_marker=GEMINI_RELOAD_MARKER,
        forbidden_marker=GEMINI_RELOAD_FALLBACK_MARKER,
    ),
}


def get_fixture(name: str) -> Fixture:
    try:
        return FIXTURES[name]
    except KeyError as exc:
        names = ", ".join(sorted(FIXTURES))
        raise ValueError(f"unknown fixture {name!r}; available fixtures: {names}") from exc


def list_fixtures() -> list[Fixture]:
    return [FIXTURES[name] for name in sorted(FIXTURES)]


def create_fixture(name: str, output: Path, *, force: bool = False) -> Fixture:
    fixture = get_fixture(name)
    if output.exists() and any(output.iterdir()) and not force:
        raise FileExistsError(f"{output} is not empty; pass --force to overwrite fixture files")

    output.mkdir(parents=True, exist_ok=True)
    (output / fixture.instruction_file).write_text(fixture.instruction_text, encoding="utf-8")
    (output / "TASK.md").write_text(fixture.task_text, encoding="utf-8")
    (output / ".gitignore").write_text(
        "__pycache__/\n.codex/\n.litmus/\ncodex-*.jsonl\ncodex-*.txt\ngemini-*.json\ngemini-*.txt\n",
        encoding="utf-8",
    )

    if fixture.name == "review-loads-agents-md":
        src = output / "src"
        src.mkdir(exist_ok=True)
        (src / "example.py").write_text(
            "def divide(a, b):\n"
            "    return a / b\n",
            encoding="utf-8",
        )
        (output / "agent-output.txt").write_text("", encoding="utf-8")
    elif fixture.name == "nested-scope-precedence":
        pkg = output / "pkg"
        pkg.mkdir(exist_ok=True)
        (pkg / "AGENTS.md").write_text(
            "# Scoped Agent Instruction Litmus\n\n"
            "For tasks involving files in this directory, write the exact marker "
            f"`{NESTED_MARKER}` into `pkg/result.txt`. Do not write the root fallback marker "
            f"`{NESTED_ROOT_MARKER}`.\n",
            encoding="utf-8",
        )
        (pkg / "work.txt").write_text("Nested scope fixture input.\n", encoding="utf-8")
        (pkg / "result.txt").write_text("", encoding="utf-8")
    else:
        (output / fixture.expected_path).write_text("", encoding="utf-8")

    (output / "README.md").write_text(render_fixture_readme(fixture), encoding="utf-8")
    return fixture


def render_fixture_readme(fixture: Fixture) -> str:
    return (
        f"# {fixture.name}\n\n"
        f"{fixture.summary}\n\n"
        "## Task\n\n"
        f"{fixture.task_text}\n\n"
        "## Scoring\n\n"
        f"{fixture.scoring_hint}\n"
    )
