from __future__ import annotations

from pathlib import Path

from .fixtures import get_fixture
from .report import Finding


def score_fixture(name: str, workspace: Path) -> Finding:
    fixture = get_fixture(name)
    target = workspace / fixture.expected_path
    if not target.exists():
        return Finding(
            status="MISSING",
            fixture=fixture.name,
            expected_path=fixture.expected_path,
            expected_marker=fixture.expected_marker,
            message=f"{fixture.expected_path} does not exist",
        )

    content = target.read_text(encoding="utf-8", errors="replace")
    if fixture.expected_marker in content and fixture.forbidden_marker and fixture.forbidden_marker in content:
        return Finding(
            status="FAIL",
            fixture=fixture.name,
            expected_path=fixture.expected_path,
            expected_marker=fixture.expected_marker,
            message=f"expected marker found, but forbidden marker {fixture.forbidden_marker} is also present",
        )

    if fixture.expected_marker in content:
        return Finding(
            status="PASS",
            fixture=fixture.name,
            expected_path=fixture.expected_path,
            expected_marker=fixture.expected_marker,
            message="expected marker found",
        )

    if content.strip():
        message = "artifact exists but expected marker is absent"
    else:
        message = "artifact is empty and expected marker is absent"

    return Finding(
        status="FAIL",
        fixture=fixture.name,
        expected_path=fixture.expected_path,
        expected_marker=fixture.expected_marker,
        message=message,
    )
