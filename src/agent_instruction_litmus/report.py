from __future__ import annotations

import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Finding:
    status: str
    fixture: str
    expected_path: str
    expected_marker: str
    message: str


def render_terminal(finding: Finding) -> str:
    return (
        f"{finding.status} {finding.fixture}\n"
        f"- expected file: {finding.expected_path}\n"
        f"- expected marker: {finding.expected_marker}\n"
        f"- result: {finding.message}\n"
    )


def render_json(finding: Finding) -> str:
    return json.dumps(asdict(finding), indent=2, sort_keys=True) + "\n"


def render_markdown(finding: Finding) -> str:
    return (
        f"# agent-instruction-litmus: {finding.fixture}\n\n"
        f"- Status: `{finding.status}`\n"
        f"- Expected file: `{finding.expected_path}`\n"
        f"- Expected marker: `{finding.expected_marker}`\n"
        f"- Result: {finding.message}\n"
    )


def render(finding: Finding, output_format: str) -> str:
    if output_format == "terminal":
        return render_terminal(finding)
    if output_format == "json":
        return render_json(finding)
    if output_format == "markdown":
        return render_markdown(finding)
    raise ValueError(f"unsupported output format: {output_format}")
