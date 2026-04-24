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
        "policy_guard.py",
        "srs_guard.py",
        "skill_gauntlet.py",
    }
    skill_gauntlet_call = next(call for call in calls if Path(call[1]).name == "skill_gauntlet.py")
    assert "--semantic" in skill_gauntlet_call
    assert all(call[0] == sys.executable for call in calls)


def test_public_cli_doctor_returns_failure_when_a_gate_fails(monkeypatch) -> None:
    def fake_run(command, cwd, text, capture_output, check):  # noqa: ANN001
        exit_code = 1 if Path(command[1]).name == "migration_guard.py" else 0
        return subprocess.CompletedProcess(command, exit_code, stdout="", stderr="failed\n")

    monkeypatch.setattr(relay_kit_public_cli.subprocess, "run", fake_run)

    assert relay_kit_public_cli.main(["doctor", ".", "--skip-tests"]) == 1


def test_public_cli_forwards_srs_policy_flags() -> None:
    args = relay_kit_public_cli._parse_args(
        ["C:/tmp/project", "--codex", "--enable-srs-first", "--srs-gate", "hard", "--srs-scope", "all"]
    )

    relay_argv = relay_kit_public_cli._build_relay_argv(args)

    assert "--enable-srs-first" in relay_argv
    assert relay_argv[relay_argv.index("--srs-gate") + 1] == "hard"
    assert relay_argv[relay_argv.index("--srs-scope") + 1] == "all"
