from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from relay_kit_v3.registry.skills import ALL_V3_SKILLS, render_skill
from scripts.skill_gauntlet import check_semantic_skill_file, collect_optional_alias_findings, collect_scenario_findings


ROOT = Path(__file__).resolve().parents[1]


def run_command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_semantic_skill_gauntlet_passes_current_runtime() -> None:
    result = run_command("scripts/skill_gauntlet.py", ".", "--strict", "--semantic")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Semantic checks: on" in result.stdout
    assert "Scenario fixtures: 12" in result.stdout
    assert "Findings: 0" in result.stdout


def test_semantic_skill_gauntlet_flags_unknown_next_step(tmp_path: Path) -> None:
    spec = ALL_V3_SKILLS["developer"]
    skill_path = tmp_path / ".codex" / "skills" / "developer" / "SKILL.md"
    skill_path.parent.mkdir(parents=True)
    skill_path.write_text(
        render_skill(spec).replace("- qa-governor", "- missing-skill"),
        encoding="utf-8",
    )

    findings = check_semantic_skill_file(skill_path, tmp_path, spec, set(ALL_V3_SKILLS))

    assert any(finding.check == "unknown-next-step" for finding in findings)


def test_semantic_skill_gauntlet_flags_bad_scenario_route(tmp_path: Path) -> None:
    fixture_dir = tmp_path / "tests" / "fixtures" / "skill_gauntlet"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "scenarios.json").write_text(
        """
        [
          {
            "id": "bad-route",
            "prompt": "Work is about to be called done. Check acceptance criteria and write a QA report.",
            "expected_skill": "workflow-router",
            "expected_terms": ["workflow-state"]
          }
        ]
        """,
        encoding="utf-8",
    )

    findings, checked = collect_scenario_findings(
        tmp_path,
        ALL_V3_SKILLS,
        Path("tests") / "fixtures" / "skill_gauntlet" / "scenarios.json",
    )

    assert checked == 1
    assert any(finding.check == "scenario-route" for finding in findings)


def test_semantic_skill_gauntlet_routes_claim_proof_to_evidence_utility(tmp_path: Path) -> None:
    fixture_dir = tmp_path / "tests" / "fixtures" / "skill_gauntlet"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "scenarios.json").write_text(
        """
        [
          {
            "id": "completion-claim-proof",
            "prompt": "List completion claims and map each claim to fresh proof output without deciding overall readiness.",
            "expected_skill": "evidence-before-completion",
            "expected_terms": ["claim-to-evidence", "proof output", "not a readiness verdict"]
          }
        ]
        """,
        encoding="utf-8",
    )

    findings, checked = collect_scenario_findings(
        tmp_path,
        ALL_V3_SKILLS,
        Path("tests") / "fixtures" / "skill_gauntlet" / "scenarios.json",
    )

    assert checked == 1
    assert findings == []


def test_semantic_skill_gauntlet_flags_optional_alias_contract_drift(tmp_path: Path) -> None:
    skill_path = tmp_path / ".codex" / "skills" / "prove-it" / "SKILL.md"
    skill_path.parent.mkdir(parents=True)
    skill_path.write_text(
        "---\nname: prove-it\ndescription: Use when proving final work.\n---\n\n# Prove It\n\nLoose alias.\n",
        encoding="utf-8",
    )

    findings = collect_optional_alias_findings(tmp_path)

    assert any(finding.check == "optional-alias-contract" for finding in findings)
