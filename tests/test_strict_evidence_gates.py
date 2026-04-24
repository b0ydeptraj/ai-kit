from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "strict_gates"


def run_command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_release_readiness_strict_requires_signals_file() -> None:
    result = run_command("scripts/release_readiness.py", ".", "--phase", "pre", "--strict", "--json")

    assert result.returncode == 2
    assert "strict mode requires --signals-file" in result.stderr


def test_release_readiness_strict_passes_with_signal_fixture() -> None:
    result = run_command(
        "scripts/release_readiness.py",
        ".",
        "--phase",
        "both",
        "--signals-file",
        str(FIXTURES / "release_signals_pass.json"),
        "--strict",
        "--json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert '"passed": true' in result.stdout


def test_release_readiness_strict_fails_failed_signal_fixture() -> None:
    result = run_command(
        "scripts/release_readiness.py",
        ".",
        "--phase",
        "pre",
        "--signals-file",
        str(FIXTURES / "release_signals_fail.json"),
        "--strict",
        "--json",
    )

    assert result.returncode == 2
    assert "tests_passed" in result.stdout


def test_accessibility_review_strict_requires_report_file() -> None:
    result = run_command("scripts/accessibility_review.py", ".", "--strict", "--json")

    assert result.returncode == 2
    assert "strict mode requires --report-file" in result.stderr


def test_accessibility_review_strict_passes_with_report_fixture() -> None:
    result = run_command(
        "scripts/accessibility_review.py",
        ".",
        "--report-file",
        str(FIXTURES / "a11y_report_pass.json"),
        "--strict",
        "--json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert '"passed": true' in result.stdout


def test_accessibility_review_strict_fails_failed_report_fixture() -> None:
    result = run_command(
        "scripts/accessibility_review.py",
        ".",
        "--report-file",
        str(FIXTURES / "a11y_report_fail.json"),
        "--strict",
        "--json",
    )

    assert result.returncode == 2
    assert "form_labels" in result.stdout
