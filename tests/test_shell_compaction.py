from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

import relay_kit_public_cli
from relay_kit_v3.shell_compaction import ShellCompactionError, compact_shell_output, run_compacted_command


def test_run_compacted_command_writes_raw_log_and_reports_savings(tmp_path: Path) -> None:
    result = run_compacted_command(
        [sys.executable, "-c", "print('hello from stdout')"],
        project_root=tmp_path,
        cwd=tmp_path,
        strict=True,
    )

    raw_path = Path(result["raw_path"])
    assert result["returncode"] == 0
    assert raw_path.is_file()
    assert raw_path.parent == tmp_path / ".relay-kit" / "evidence" / "raw"
    assert result["estimated_raw_tokens"] > 0
    assert result["estimated_compact_tokens"] > 0
    assert result["saved_tokens"] >= 0
    assert 0.0 <= result["savings_ratio"] <= 1.0
    assert result["signal_retention"] == 1.0
    assert str(raw_path) in result["compact_output"]

    payload = json.loads(raw_path.read_text(encoding="utf-8"))
    assert payload["stdout"] == "hello from stdout\n"
    assert payload["stderr"] == ""
    assert payload["returncode"] == 0


def test_failure_output_retains_raw_required_lines(tmp_path: Path) -> None:
    command = [
        sys.executable,
        "-c",
        (
            "import sys; "
            "print('setup line'); "
            "print('AssertionError: expected pass', file=sys.stderr); "
            "print('Traceback (most recent call last):', file=sys.stderr); "
            "sys.exit(3)"
        ),
    ]

    result = run_compacted_command(command, project_root=tmp_path, cwd=tmp_path, strict=True)

    assert result["returncode"] == 3
    assert result["signal_retention"] == 1.0
    assert result["raw_required_line_count"] >= 2
    assert "stderr: AssertionError: expected pass" in result["compact_output"]
    assert "stderr: Traceback (most recent call last):" in result["compact_output"]


def test_marker_lines_are_raw_required_on_success(tmp_path: Path) -> None:
    result = run_compacted_command(
        [sys.executable, "-c", "print('error: dry-run found one issue')"],
        project_root=tmp_path,
        cwd=tmp_path,
        strict=True,
    )

    assert result["returncode"] == 0
    assert result["raw_required_line_count"] == 1
    assert "stdout: error: dry-run found one issue" in result["compact_output"]


def test_long_failing_output_keeps_error_signal_without_retaining_progress_noise(tmp_path: Path) -> None:
    command = [
        sys.executable,
        "-c",
        (
            "import sys; "
            "[print(f'progress line {i:03d} ok details details details') for i in range(250)]; "
            "print('AssertionError: final important failure', file=sys.stderr); "
            "print('Traceback (most recent call last):', file=sys.stderr); "
            "sys.exit(2)"
        ),
    ]

    result = run_compacted_command(command, project_root=tmp_path, cwd=tmp_path, strict=True)

    assert result["returncode"] == 2
    assert result["signal_retention"] == 1.0
    assert result["raw_required_line_count"] == 2
    assert result["retained_raw_required_line_count"] == 2
    assert result["saved_tokens"] > 0
    assert result["savings_ratio"] > 0.5
    assert "stderr: AssertionError: final important failure" in result["compact_output"]
    assert "stderr: Traceback (most recent call last):" in result["compact_output"]
    assert "progress line 001" not in result["compact_output"]


def test_strict_mode_fails_when_required_signal_is_dropped() -> None:
    with pytest.raises(ShellCompactionError):
        compact_shell_output(
            stdout="AssertionError: expected pass\n",
            stderr="Traceback (most recent call last):\n",
            returncode=1,
            raw_path=Path("raw.json"),
            strict=True,
            max_raw_required_lines=1,
        )


def test_public_cli_shell_compact_emits_json(tmp_path: Path, capsys) -> None:
    exit_code = relay_kit_public_cli.main(
        [
            "shell",
            "compact",
            str(tmp_path),
            "--json",
            "--",
            sys.executable,
            "-c",
            "print('compact cli')",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["schema_version"] == "relay-kit.shell-compact.v1"
    assert payload["returncode"] == 0
    assert payload["signal_retention"] == 1.0
    assert Path(payload["raw_path"]).is_file()
