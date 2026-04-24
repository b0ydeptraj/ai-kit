from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


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


def test_root_pytest_collection_is_limited_to_root_tests() -> None:
    result = run_command("-m", "pytest", "--collect-only", "-q")

    assert_success(result)
    assert "templates/skills" not in result.stdout
    assert "test_runtime_smoke.py" in result.stdout


def test_validate_runtime_script_passes() -> None:
    result = run_command("scripts/validate_runtime.py")

    assert_success(result)
    assert "Runtime validation passed." in result.stdout


def test_runtime_doctor_template_mode_passes() -> None:
    result = run_command("scripts/runtime_doctor.py", ".", "--strict")

    assert_success(result)
    assert "- findings: 0" in result.stdout


def test_migration_guard_strict_passes() -> None:
    result = run_command("scripts/migration_guard.py", ".", "--strict")

    assert_success(result)
    assert "- findings: 0" in result.stdout


def test_skill_gauntlet_strict_passes() -> None:
    result = run_command("scripts/skill_gauntlet.py", ".", "--strict")

    assert_success(result)
    assert "Findings: 0" in result.stdout


def test_public_cli_help_passes() -> None:
    result = run_command("relay_kit_public_cli.py", "--help")

    assert_success(result)
    assert "Public Relay-kit installer" in result.stdout
