from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import relay_kit_public_cli


def test_public_cli_doctor_runs_core_gates(monkeypatch, capsys) -> None:
    calls: list[list[str]] = []

    def fake_run(command, cwd, text, capture_output, check):  # noqa: ANN001
        calls.append([str(part) for part in command])
        return subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr="")

    monkeypatch.setattr(relay_kit_public_cli.subprocess, "run", fake_run)

    exit_code = relay_kit_public_cli.main(["doctor", ".", "--skip-tests"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Relay-kit doctor" in output

    script_names = {Path(call[1]).name for call in calls}
    assert script_names == {
        "validate_runtime.py",
        "runtime_doctor.py",
        "migration_guard.py",
        "skill_gauntlet.py",
    }
    assert all(call[0] == sys.executable for call in calls)


def test_public_cli_doctor_returns_failure_when_a_gate_fails(monkeypatch) -> None:
    def fake_run(command, cwd, text, capture_output, check):  # noqa: ANN001
        exit_code = 1 if Path(command[1]).name == "migration_guard.py" else 0
        return subprocess.CompletedProcess(command, exit_code, stdout="", stderr="failed\n")

    monkeypatch.setattr(relay_kit_public_cli.subprocess, "run", fake_run)

    assert relay_kit_public_cli.main(["doctor", ".", "--skip-tests"]) == 1
