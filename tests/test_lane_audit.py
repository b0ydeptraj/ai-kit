from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3 import lane_audit
from relay_kit_v3.registry.workflows import render_handoff_log, render_lane_registry, render_team_board
from scripts import runtime_doctor


def write_lane_project(root: Path) -> None:
    state = root / ".relay-kit" / "state"
    state.mkdir(parents=True)
    (state / "team-board.md").write_text(
        "\n".join(
            [
                "# team-board",
                "",
                "## Lanes",
                "| Lane | Owner skill | Current hub | Current artifact | Lock scope | Status | depends_on | wave_id | resume_condition | Handoff status | Notes |",
                "|---|---|---|---|---|---|---|---|---|---|---|",
                "| primary | developer | fix-hub | lane audit | relay_kit_v3/lane_audit.py | active | none | wave-1 | active | test-hub next | implementation lane |",
                "| lane-2 | unassigned | none | none | none | parked | primary | wave-2 | explicitly routed by team | none | empty lane |",
                "| lane-3 | unassigned | none | none | none | parked | primary | wave-2 | explicitly routed by team | none | empty lane |",
                "",
                "## Merge order",
                "wave-1 before wave-2; later lanes depend_on primary unless explicitly rerouted.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (state / "lane-registry.md").write_text(
        "\n".join(
            [
                "# lane-registry",
                "",
                "## Active lanes",
                "| Lane | Owner skill | Source orchestrator | Target hub | Primary artifact | Lock scope | depends_on | wave_id | resume_condition | Merge prerequisite | Status |",
                "|---|---|---|---|---|---|---|---|---|---|---|",
                "| primary | developer | workflow-router | test-hub | lane audit | relay_kit_v3/lane_audit.py | none | wave-1 | active | full gates | active |",
                "| lane-2 | unassigned | team | none | none | none | primary | wave-2 | explicitly routed by team | none | parked |",
                "| lane-3 | unassigned | team | none | none | none | primary | wave-2 | explicitly routed by team | none | parked |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (state / "handoff-log.md").write_text(
        "\n".join(
            [
                "# handoff-log",
                "",
                "## Handoff entries",
                "| From | To | Lane | Trigger | Artifact touched | Evidence linked | Expected return condition |",
                "|---|---|---|---|---|---|---|",
                "| workflow-router | developer | primary | slice selected | workflow-state | context audit pass | return through test-hub after full gates |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_lane_audit_passes_single_active_lane_with_coordination_metadata(tmp_path: Path) -> None:
    write_lane_project(tmp_path)

    report = lane_audit.build_lane_audit(tmp_path)

    assert report["schema_version"] == "relay-kit.lane-audit.v1"
    assert report["status"] == "pass"
    assert report["summary"]["active_lanes"] == 1
    assert report["summary"]["parked_lanes"] == 2
    assert report["findings"] == []


def test_lane_audit_flags_duplicate_active_lock_scope(tmp_path: Path) -> None:
    write_lane_project(tmp_path)
    registry = tmp_path / ".relay-kit" / "state" / "lane-registry.md"
    content = registry.read_text(encoding="utf-8")
    content = content.replace(
        "| lane-2 | unassigned | team | none | none | none | primary | wave-2 | explicitly routed by team | none | parked |",
        "| lane-2 | developer | team | test-hub | lane audit docs | relay_kit_v3/lane_audit.py | primary | wave-1 | active | full gates | active |",
    )
    registry.write_text(content, encoding="utf-8")

    report = lane_audit.build_lane_audit(tmp_path)

    assert report["status"] == "hold"
    assert any(finding["id"] == "lane-lock-conflict" for finding in report["findings"])


def test_lane_audit_flags_broad_lock_scope(tmp_path: Path) -> None:
    write_lane_project(tmp_path)
    registry = tmp_path / ".relay-kit" / "state" / "lane-registry.md"
    registry.write_text(registry.read_text(encoding="utf-8").replace("relay_kit_v3/lane_audit.py", "whole repo"), encoding="utf-8")

    report = lane_audit.build_lane_audit(tmp_path)

    assert report["status"] == "hold"
    assert any(finding["id"] == "broad-lock-scope" for finding in report["findings"])


def test_lane_audit_flags_parked_lane_without_resume_condition(tmp_path: Path) -> None:
    write_lane_project(tmp_path)
    registry = tmp_path / ".relay-kit" / "state" / "lane-registry.md"
    registry.write_text(registry.read_text(encoding="utf-8").replace("explicitly routed by team", "none", 1), encoding="utf-8")

    report = lane_audit.build_lane_audit(tmp_path)

    assert report["status"] == "hold"
    assert any(finding["id"] == "missing-resume-condition" for finding in report["findings"])


def test_lane_audit_flags_handoff_without_expected_return_condition(tmp_path: Path) -> None:
    write_lane_project(tmp_path)
    handoff = tmp_path / ".relay-kit" / "state" / "handoff-log.md"
    handoff.write_text(handoff.read_text(encoding="utf-8").replace("return through test-hub after full gates", "none"), encoding="utf-8")

    report = lane_audit.build_lane_audit(tmp_path)

    assert report["status"] == "hold"
    assert any(finding["id"] == "missing-handoff-return-condition" for finding in report["findings"])


def test_public_cli_lane_audit_outputs_json_and_strict_status(tmp_path: Path, capsys) -> None:
    write_lane_project(tmp_path)

    exit_code = relay_kit_public_cli.main(["lane", "audit", str(tmp_path), "--strict", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "pass"
    assert payload["summary"]["active_lanes"] == 1


def test_rendered_lane_templates_pass_lane_audit(tmp_path: Path) -> None:
    state = tmp_path / ".relay-kit" / "state"
    state.mkdir(parents=True)
    (state / "team-board.md").write_text(render_team_board(), encoding="utf-8")
    (state / "lane-registry.md").write_text(render_lane_registry(), encoding="utf-8")
    (state / "handoff-log.md").write_text(render_handoff_log(), encoding="utf-8")

    report = lane_audit.build_lane_audit(tmp_path)

    assert report["status"] == "pass"


def test_runtime_doctor_live_reports_lane_audit_findings(tmp_path: Path) -> None:
    write_lane_project(tmp_path)
    registry = tmp_path / ".relay-kit" / "state" / "lane-registry.md"
    registry.write_text(registry.read_text(encoding="utf-8").replace("relay_kit_v3/lane_audit.py", "whole repo"), encoding="utf-8")
    findings: list[str] = []

    runtime_doctor.check_lane_audit(tmp_path, findings, mode="live")

    assert any("Lane audit broad-lock-scope" in finding for finding in findings)
