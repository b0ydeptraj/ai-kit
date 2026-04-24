from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from relay_kit_v3.srs_policy import write_srs_policy
from scripts import srs_guard


ROOT = Path(__file__).resolve().parents[1]


def run_command(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_srs_guard_skips_when_policy_is_off(tmp_path: Path) -> None:
    meta, findings = srs_guard.collect_findings(tmp_path)

    assert meta["status"] == "skipped"
    assert meta["enforced"] is False
    assert findings == []


def test_srs_guard_hard_gate_fails_when_srs_contract_is_missing(tmp_path: Path) -> None:
    write_srs_policy(tmp_path, enabled=True, gate="hard", scope="all")

    result = run_command(tmp_path, "scripts/srs_guard.py", str(tmp_path), "--strict")

    assert result.returncode == 2
    assert "Missing required SRS contract file" in result.stdout


def test_srs_guard_passes_with_traceable_srs_prd_story_and_qa(tmp_path: Path) -> None:
    write_srs_policy(tmp_path, enabled=True, gate="hard", scope="all")
    contracts = tmp_path / ".relay-kit" / "contracts"
    stories = contracts / "stories"
    stories.mkdir(parents=True)

    srs_sections = "\n\n".join(
        f"## {section}\nUC-CHECKOUT-01 verifies checkout traceability."
        for section in srs_guard.REQUIRED_SECTIONS
    )
    (contracts / "srs-spec.md").write_text(f"# srs-spec\n\n{srs_sections}\n", encoding="utf-8")
    (contracts / "PRD.md").write_text(
        "# PRD\n\n## SRS Traceability\nUC-CHECKOUT-01 -> FR-1 -> AC-1\n",
        encoding="utf-8",
    )
    (stories / "story-001.md").write_text("# Story\n\nsrs_uc_ids: UC-CHECKOUT-01\n", encoding="utf-8")
    (contracts / "qa-report.md").write_text(
        "# QA\n\n## SRS coverage table\nUC-CHECKOUT-01 -> pytest evidence\n",
        encoding="utf-8",
    )

    meta, findings = srs_guard.collect_findings(tmp_path)

    assert meta["status"] == "ok"
    assert findings == []


def test_relay_kit_cli_updates_srs_policy(tmp_path: Path) -> None:
    result = run_command(
        tmp_path,
        "relay_kit.py",
        str(tmp_path),
        "--enable-srs-first",
        "--srs-gate",
        "hard",
        "--srs-scope",
        "all",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    policy = json.loads((tmp_path / ".relay-kit" / "state" / "srs-policy.json").read_text(encoding="utf-8"))
    assert policy["enabled"] is True
    assert policy["gate"] == "hard"
    assert policy["scope"] == "all"
