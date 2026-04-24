from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from relay_kit_v3.registry.workflows import (
    render_handoff_log,
    render_lane_registry,
    render_team_board,
    render_workflow_state,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_FILES = [
    ".relay-kit/state/workflow-state.md",
    ".relay-kit/state/team-board.md",
    ".relay-kit/state/lane-registry.md",
    ".relay-kit/state/handoff-log.md",
]


def run_command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def assert_success(result: subprocess.CompletedProcess[str]) -> None:
    assert result.returncode == 0, (
        f"command failed with exit code {result.returncode}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


def test_checked_in_live_state_has_no_tbd_markers() -> None:
    for rel_path in STATE_FILES:
        content = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
        assert "TBD" not in content, rel_path


def test_rendered_state_templates_have_safe_empty_values() -> None:
    rendered = [
        render_workflow_state(),
        render_team_board(),
        render_lane_registry(),
        render_handoff_log(),
    ]

    for content in rendered:
        assert "TBD" not in content


def test_runtime_doctor_live_mode_passes_for_checked_in_state() -> None:
    result = run_command("scripts/runtime_doctor.py", ".", "--strict", "--state-mode", "live")

    assert_success(result)
    assert "- findings: 0" in result.stdout
