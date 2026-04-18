from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _run(*args: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == expect, (
        f"command failed: {args}\n"
        f"expected rc={expect}, got rc={result.returncode}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    return result


def _generate_baseline(project: Path) -> None:
    _run(
        str(REPO_ROOT / "relay_kit.py"),
        str(project),
        "--bundle",
        "baseline",
        "--ai",
        "all",
        "--emit-contracts",
        "--emit-docs",
        "--emit-reference-templates",
    )


def test_runtime_doctor_live_strict_no_false_positive_for_baseline_bundle(tmp_path: Path) -> None:
    project = tmp_path / "baseline-project"
    project.mkdir(parents=True, exist_ok=True)
    _generate_baseline(project)

    result = _run(
        str(REPO_ROOT / "scripts" / "runtime_doctor.py"),
        str(project),
        "--state-mode",
        "live",
        "--strict",
        expect=0,
    )

    assert "expected bundle: baseline" in result.stdout
    assert "missing expected skills" not in result.stdout


def test_runtime_doctor_live_placeholder_strict_can_fail_when_requested(tmp_path: Path) -> None:
    project = tmp_path / "baseline-project"
    project.mkdir(parents=True, exist_ok=True)
    _generate_baseline(project)

    result = _run(
        str(REPO_ROOT / "scripts" / "runtime_doctor.py"),
        str(project),
        "--state-mode",
        "live",
        "--state-placeholder-mode",
        "strict",
        "--strict",
        expect=1,
    )

    assert "State artifact contains TBD placeholder markers" in result.stdout
