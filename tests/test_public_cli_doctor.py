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
    monkeypatch.setattr(relay_kit_public_cli, "append_event", lambda project_root, event: Path(project_root))

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
        "eval_workflows.py",
    }
    skill_gauntlet_call = next(call for call in calls if Path(call[1]).name == "skill_gauntlet.py")
    assert "--semantic" in skill_gauntlet_call
    assert all(call[0] == sys.executable for call in calls)
    policy_guard_call = next(call for call in calls if Path(call[1]).name == "policy_guard.py")
    assert policy_guard_call[-2:] == ["--pack", "baseline"]
    workflow_eval_call = next(call for call in calls if Path(call[1]).name == "eval_workflows.py")
    assert "--strict" in workflow_eval_call


def test_public_cli_doctor_forwards_policy_pack(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_run(command, cwd, text, capture_output, check):  # noqa: ANN001
        calls.append([str(part) for part in command])
        return subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr="")

    monkeypatch.setattr(relay_kit_public_cli.subprocess, "run", fake_run)
    monkeypatch.setattr(relay_kit_public_cli, "append_event", lambda project_root, event: Path(project_root))

    assert relay_kit_public_cli.main(["doctor", ".", "--skip-tests", "--policy-pack", "enterprise"]) == 0

    policy_guard_call = next(call for call in calls if Path(call[1]).name == "policy_guard.py")
    assert policy_guard_call[-2:] == ["--pack", "enterprise"]
    trusted_manifest_call = next(call for call in calls if Path(call[1]).name == "relay_kit_public_cli.py")
    assert trusted_manifest_call[2:4] == ["manifest", "verify"]
    assert trusted_manifest_call[-1] == "--trusted"


def test_public_cli_doctor_enterprise_fails_without_trusted_manifest(monkeypatch, capsys) -> None:
    def fake_run(command, cwd, text, capture_output, check):  # noqa: ANN001
        if Path(command[1]).name == "relay_kit_public_cli.py":
            return subprocess.CompletedProcess(
                command,
                2,
                stdout="Trust verification failed.\n- missing trust metadata: trust.json\n",
                stderr="",
            )
        return subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr="")

    monkeypatch.setattr(relay_kit_public_cli.subprocess, "run", fake_run)
    monkeypatch.setattr(relay_kit_public_cli, "append_event", lambda project_root, event: Path(project_root))

    exit_code = relay_kit_public_cli.main(["doctor", ".", "--skip-tests", "--policy-pack", "enterprise"])

    output = capsys.readouterr().out
    assert exit_code == 1
    assert "- trusted manifest: fail" in output
    assert "missing trust metadata" in output


def test_public_cli_doctor_returns_failure_when_a_gate_fails(monkeypatch) -> None:
    def fake_run(command, cwd, text, capture_output, check):  # noqa: ANN001
        exit_code = 1 if Path(command[1]).name == "migration_guard.py" else 0
        return subprocess.CompletedProcess(command, exit_code, stdout="", stderr="failed\n")

    monkeypatch.setattr(relay_kit_public_cli.subprocess, "run", fake_run)
    monkeypatch.setattr(relay_kit_public_cli, "append_event", lambda project_root, event: Path(project_root))

    assert relay_kit_public_cli.main(["doctor", ".", "--skip-tests"]) == 1


def test_public_cli_forwards_srs_policy_flags() -> None:
    args = relay_kit_public_cli._parse_args(
        ["C:/tmp/project", "--codex", "--enable-srs-first", "--srs-gate", "hard", "--srs-scope", "all"]
    )

    relay_argv = relay_kit_public_cli._build_relay_argv(args)

    assert "--enable-srs-first" in relay_argv
    assert relay_argv[relay_argv.index("--srs-gate") + 1] == "hard"
    assert relay_argv[relay_argv.index("--srs-scope") + 1] == "all"


def test_public_cli_init_alias_generates_baseline_bundle(monkeypatch) -> None:
    captured_argv: list[str] = []

    def fake_main(invoked_as=None):  # noqa: ANN001
        captured_argv.extend(sys.argv)
        assert invoked_as == "relay-kit"
        return 0

    monkeypatch.setattr(relay_kit_public_cli.relay_core, "main", fake_main)

    exit_code = relay_kit_public_cli.main(["init", "C:/tmp/project", "--codex", "--baseline"])

    assert exit_code == 0
    assert captured_argv[:6] == [
        "relay-kit-core",
        "C:/tmp/project",
        "--ai",
        "codex",
        "--bundle",
        "baseline",
    ]
