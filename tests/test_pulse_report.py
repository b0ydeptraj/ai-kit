from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3 import pulse
from relay_kit_v3.evidence_ledger import append_event


def sample_eval_report() -> dict[str, object]:
    return {
        "schema_version": "relay-kit.workflow-eval.v1",
        "status": "pass",
        "scenario_count": 2,
        "passed": 2,
        "failed": 0,
        "pass_rate": 1.0,
        "quality": {
            "min_route_margin": 3,
            "average_route_margin": 8.5,
            "evidence_term_coverage": 1.0,
            "expected_skill_counts": {"developer": 1, "qa-governor": 1},
        },
        "findings_count": 0,
        "findings": [],
    }


def eval_report_with_score_inputs(*, pass_rate: float, evidence_coverage: float, margin: float = 8.5) -> dict[str, object]:
    report = sample_eval_report()
    report["pass_rate"] = pass_rate
    report["quality"] = {
        **report["quality"],  # type: ignore[index]
        "average_route_margin": margin,
        "evidence_term_coverage": evidence_coverage,
    }
    return report


def sample_readiness_report() -> dict[str, object]:
    return {
        "schema_version": "relay-kit.readiness-report.v1",
        "status": "pass",
        "verdict": "commercial-ready-candidate",
        "profile": "enterprise",
        "findings": [],
        "gates": [
            {"id": "pytest", "status": "pass"},
            {"id": "workflow-eval", "status": "pass"},
        ],
    }


def sample_publication_plan(*, status: str = "ready") -> dict[str, object]:
    findings = [] if status == "ready" else [{"gate": "distribution-artifacts", "status": "hold", "summary": "missing: wheel"}]
    return {
        "schema_version": "relay-kit.publication-plan.v1",
        "status": status,
        "channel": "pypi",
        "version": "3.3.0",
        "findings": findings,
        "checks": [
            {"id": "release-lane", "status": "pass"},
            {"id": "distribution-artifacts", "status": "pass" if status == "ready" else "hold"},
        ],
    }


def test_pulse_report_summarizes_eval_readiness_and_evidence(tmp_path: Path) -> None:
    append_event(tmp_path, {"command": "doctor", "gate": "policy guard", "status": "pass"})
    append_event(tmp_path, {"command": "doctor", "gate": "workflow eval", "status": "fail"})

    report = pulse.build_pulse_report(
        tmp_path,
        include_readiness=True,
        workflow_eval_builder=lambda root: sample_eval_report(),
        readiness_builder=lambda root, profile, skip_tests: sample_readiness_report(),
    )

    assert report["schema_version"] == "relay-kit.pulse-report.v1"
    assert report["status"] == "attention"
    assert report["pulse_score"] < 100
    assert report["workflow_eval"]["quality"]["average_route_margin"] == 8.5
    assert report["readiness"]["verdict"] == "commercial-ready-candidate"
    assert report["evidence"]["status_counts"]["fail"] == 1


def test_pulse_report_includes_publication_plan_when_requested(tmp_path: Path) -> None:
    report = pulse.build_pulse_report(
        tmp_path,
        workflow_eval_builder=lambda root: sample_eval_report(),
        publication_builder=lambda root: sample_publication_plan(status="ready"),
        include_publication=True,
    )

    assert report["publication"]["schema_version"] == "relay-kit.publication-plan.v1"
    assert report["publication"]["status"] == "ready"
    assert report["status"] == "pass"


def test_pulse_report_marks_publication_hold_as_attention(tmp_path: Path) -> None:
    report = pulse.build_pulse_report(
        tmp_path,
        workflow_eval_builder=lambda root: sample_eval_report(),
        publication_builder=lambda root: sample_publication_plan(status="hold"),
        include_publication=True,
    )

    assert report["status"] == "attention"
    assert report["publication"]["findings"][0]["gate"] == "distribution-artifacts"


def test_pulse_report_writes_json_and_html(tmp_path: Path) -> None:
    report = pulse.build_pulse_report(
        tmp_path,
        workflow_eval_builder=lambda root: sample_eval_report(),
    )

    outputs = pulse.write_pulse_report(tmp_path, report, output_dir=tmp_path / "pulse")

    assert outputs["json"].exists()
    assert outputs["html"].exists()
    assert json.loads(outputs["json"].read_text(encoding="utf-8"))["schema_version"] == "relay-kit.pulse-report.v1"
    html = outputs["html"].read_text(encoding="utf-8")
    assert "Relay-kit Pulse" in html
    assert "Workflow quality" in html
    assert "Publication readiness" in html
    assert "Trend" in html


def test_pulse_report_records_history_and_reports_delta(tmp_path: Path) -> None:
    output_dir = tmp_path / "pulse"
    first = pulse.build_pulse_report(
        tmp_path,
        output_dir=output_dir,
        workflow_eval_builder=lambda root: eval_report_with_score_inputs(pass_rate=0.75, evidence_coverage=0.5),
    )
    pulse.write_pulse_report(tmp_path, first, output_dir=output_dir)

    second = pulse.build_pulse_report(
        tmp_path,
        output_dir=output_dir,
        workflow_eval_builder=lambda root: eval_report_with_score_inputs(pass_rate=1.0, evidence_coverage=1.0),
    )
    outputs = pulse.write_pulse_report(tmp_path, second, output_dir=output_dir)

    history_path = outputs["history"]
    history_lines = history_path.read_text(encoding="utf-8").splitlines()

    assert len(history_lines) == 2
    assert second["trend"]["history_count"] == 1
    assert second["trend"]["pulse_score_delta"] > 0
    assert second["trend"]["pass_rate_delta"] == 0.25
    assert second["trend"]["evidence_coverage_delta"] == 0.5


def test_pulse_report_marks_limited_beta_readiness_as_attention(tmp_path: Path) -> None:
    limited_readiness = {
        **sample_readiness_report(),
        "verdict": "limited-beta",
    }

    report = pulse.build_pulse_report(
        tmp_path,
        include_readiness=True,
        workflow_eval_builder=lambda root: sample_eval_report(),
        readiness_builder=lambda root, profile, skip_tests: limited_readiness,
    )

    assert report["status"] == "attention"
    assert report["pulse_score"] < 100


def test_public_cli_pulse_build_json(tmp_path: Path, capsys) -> None:
    exit_code = relay_kit_public_cli.main(["pulse", "build", str(tmp_path), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["report"]["schema_version"] == "relay-kit.pulse-report.v1"
    assert Path(payload["outputs"]["json"]).exists()
    assert Path(payload["outputs"]["html"]).exists()
    assert Path(payload["outputs"]["history"]).exists()


def test_public_cli_pulse_build_accepts_publication_file(tmp_path: Path, capsys) -> None:
    publication_file = tmp_path / "publication.json"
    publication_file.write_text(json.dumps(sample_publication_plan(status="ready")), encoding="utf-8")

    exit_code = relay_kit_public_cli.main(
        [
            "pulse",
            "build",
            str(tmp_path),
            "--publication-file",
            str(publication_file),
            "--json",
            "--no-history",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["report"]["publication"]["status"] == "ready"
