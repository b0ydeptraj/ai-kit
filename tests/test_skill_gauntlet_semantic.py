from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from relay_kit_v3.registry.skills import ALL_V3_SKILLS, render_skill
from scripts.skill_gauntlet import (
    DEFAULT_SCENARIO_FIXTURE,
    REQUIRED_TOOL_PROFILE_SKILLS,
    check_semantic_skill_file,
    collect_optional_alias_findings,
    collect_scenario_findings,
    collect_tool_profile_findings,
    load_scenario_fixtures,
)


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SCENARIO_FIXTURES = 37


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
    assert f"Scenario fixtures: {EXPECTED_SCENARIO_FIXTURES}" in result.stdout
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


def test_semantic_skill_gauntlet_flags_missing_high_risk_tool_profile(tmp_path: Path) -> None:
    spec = ALL_V3_SKILLS["policy-guard"]
    skill_path = tmp_path / ".codex" / "skills" / "policy-guard" / "SKILL.md"
    skill_path.parent.mkdir(parents=True)
    rendered = "\n".join(
        line for line in render_skill(spec).splitlines() if not line.startswith("allowed-tools:")
    )
    skill_path.write_text(rendered + "\n", encoding="utf-8")

    findings = collect_tool_profile_findings(tmp_path, [skill_path], ALL_V3_SKILLS)

    assert any(finding.check == "missing-tool-profile" for finding in findings)


def test_semantic_skill_gauntlet_flags_tool_profile_drift(tmp_path: Path) -> None:
    spec = ALL_V3_SKILLS["developer"]
    skill_path = tmp_path / ".codex" / "skills" / "developer" / "SKILL.md"
    skill_path.parent.mkdir(parents=True)
    skill_path.write_text(
        render_skill(spec).replace(
            'allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]',
            'allowed-tools: ["Read", "Grep"]',
        ),
        encoding="utf-8",
    )

    findings = collect_tool_profile_findings(tmp_path, [skill_path], ALL_V3_SKILLS)

    assert any(finding.check == "tool-profile-drift" for finding in findings)


def test_high_risk_skills_have_registry_tool_profiles() -> None:
    missing = [
        skill_name
        for skill_name in sorted(REQUIRED_TOOL_PROFILE_SKILLS)
        if not ALL_V3_SKILLS[skill_name].allowed_tools
    ]

    assert missing == []


def test_risk_sensitive_skill_profiles_cover_browser_media_api_dependency() -> None:
    expected = {
        "api-integration",
        "browser-inspector",
        "data-persistence",
        "dependency-management",
        "media-tooling",
        "multimodal-evidence",
    }

    assert expected.issubset(REQUIRED_TOOL_PROFILE_SKILLS)
    assert ALL_V3_SKILLS["api-integration"].allowed_tools == ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
    assert ALL_V3_SKILLS["data-persistence"].allowed_tools == ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
    assert ALL_V3_SKILLS["dependency-management"].allowed_tools == ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
    assert ALL_V3_SKILLS["media-tooling"].allowed_tools == ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
    assert ALL_V3_SKILLS["browser-inspector"].allowed_tools == ["Read", "Grep", "Glob", "Bash"]
    assert ALL_V3_SKILLS["multimodal-evidence"].allowed_tools == ["Read", "Grep", "Glob", "Bash"]


def test_default_scenarios_cover_profiled_support_skills() -> None:
    scenarios = load_scenario_fixtures(ROOT, DEFAULT_SCENARIO_FIXTURE)
    covered = {str(item.get("expected_skill", "")) for item in scenarios}

    assert {
        "api-integration",
        "browser-inspector",
        "data-persistence",
        "dependency-management",
        "media-tooling",
        "multimodal-evidence",
    }.issubset(covered)


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


def test_semantic_skill_gauntlet_routes_skill_upgrade_to_skill_evolution(tmp_path: Path) -> None:
    fixture_dir = tmp_path / "tests" / "fixtures" / "skill_gauntlet"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "scenarios.json").write_text(
        """
        [
          {
            "id": "skill-evolution-upgrade",
            "prompt": "Create or upgrade a Relay-kit SKILL.md by auditing trigger descriptions, paths frontmatter, allowed tools, handoff contract, and scenario fixtures.",
            "expected_skill": "skill-evolution",
            "expected_terms": ["trigger", "frontmatter", "scenario"]
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
