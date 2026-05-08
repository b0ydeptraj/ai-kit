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
            "expected_layer_counts": {
                "layer-1-orchestrators": 1,
                "layer-4-specialists-and-standalones": 1,
            },
            "expected_skill_counts": {"developer": 1, "qa-governor": 1},
            "weak_route_threshold": 3,
            "weak_route_count": 1,
            "weak_routes": [
                {
                    "id": "developer-implementation-ready",
                    "expected_skill": "developer",
                    "predicted_skill": "developer",
                    "route_margin": 1,
                    "route_confidence": 0.51,
                }
            ],
            "coverage_gaps": {
                "missing_layers": [],
                "missing_roles": ["debug-hub"],
                "missing_skills": ["debug-hub"],
                "covered_skill_count": 2,
                "registry_skill_count": 46,
                "covered_skill_ratio": 0.0435,
            },
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


def sample_support_request(*, status: str = "ready") -> dict[str, object]:
    findings = [] if status == "ready" else [{"gate": "diagnostics", "status": "hold", "summary": "missing diagnostics"}]
    return {
        "schema_version": "relay-kit.support-request.v1",
        "status": status,
        "severity": "P1",
        "summary": "Enterprise doctor fails after manifest trust metadata drift.",
        "environment": {
            "package_version": "3.4.0",
            "installed_bundle": "enterprise",
            "adapter_target": "codex",
            "policy_pack": "enterprise",
        },
        "diagnostics": [
            {"path": ".relay-kit/support/support-bundle.json", "status": "present", "size_bytes": 10},
        ],
        "findings": findings,
    }


def sample_commercial_dossier(*, status: str = "ready") -> dict[str, object]:
    findings = [] if status == "ready" else [{"gate": "publication-status", "status": "hold", "summary": "publication trail status=hold"}]
    return {
        "schema_version": "relay-kit.commercial-dossier.v1",
        "status": status,
        "channel": "pypi",
        "external_proof": {
            "ci_url": "https://github.com/b0ydeptraj/Relay-kit/actions/runs/1",
            "release_url": "https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.3.0",
            "package_url": "https://pypi.org/project/relay-kit/3.3.0/",
            "sla_url": "https://example.com/sla",
            "support_url": "https://example.com/support",
            "legal_owner": "ops@example.com",
            "support_owner": "support@example.com",
        },
        "findings": findings,
        "checks": [
            {"id": "readiness", "status": "pass"},
            {"id": "publication-status", "status": "pass" if status == "ready" else "hold", "summary": "publication trail status=hold"},
            {"id": "support-triage", "status": "pass"},
            {"id": "support-soak", "status": "pass"},
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
    assert report["workflow_focus"]["weak_route_count"] == 1
    assert report["workflow_focus"]["coverage_gap_count"] == 1
    assert report["readiness"]["verdict"] == "commercial-ready-candidate"
    assert report["evidence"]["status_counts"]["fail"] == 1


def test_pulse_workflow_focus_surfaces_support_evidence_contract_gaps(tmp_path: Path) -> None:
    eval_report = sample_eval_report()
    quality = eval_report["quality"]  # type: ignore[index]
    quality["support_evidence_contract_review"] = {
        "term_gap_count": 1,
        "prompt_gap_count": 2,
        "term_gaps": [{"id": "thin-api", "expected_skill": "api-integration"}],
        "prompt_gaps": [{"id": "thin-browser", "expected_skill": "browser-inspector"}],
    }

    report = pulse.build_pulse_report(
        tmp_path,
        workflow_eval_builder=lambda root: eval_report,
    )

    assert report["workflow_focus"]["support_evidence_gap_count"] == 3
    assert any(
        action["kind"] == "support-evidence-contract"
        for action in report["workflow_focus"]["next_actions"]
    )


def test_pulse_workflow_focus_surfaces_support_fixture_depth_gaps(tmp_path: Path) -> None:
    eval_report = sample_eval_report()
    quality = eval_report["quality"]  # type: ignore[index]
    quality["support_fixture_depth_review"] = {
        "depth_gap_count": 2,
        "depth_gaps": [
            {"check": "support-fixture-skill-count", "expected_skill": "api-integration"},
            {"check": "support-fixture-prompt-depth", "id": "thin-browser"},
        ],
    }

    report = pulse.build_pulse_report(
        tmp_path,
        workflow_eval_builder=lambda root: eval_report,
    )

    assert report["workflow_focus"]["support_fixture_depth_gap_count"] == 2
    assert report["workflow_focus"]["support_fixture_depth"]["depth_gap_count"] == 2
    assert any(
        action["kind"] == "support-fixture-depth"
        for action in report["workflow_focus"]["next_actions"]
    )


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


def test_pulse_report_includes_support_request_when_requested(tmp_path: Path) -> None:
    report = pulse.build_pulse_report(
        tmp_path,
        workflow_eval_builder=lambda root: sample_eval_report(),
        support_request_builder=lambda root: sample_support_request(status="ready"),
        include_support_request=True,
    )

    assert report["support_request"]["schema_version"] == "relay-kit.support-request.v1"
    assert report["support_request"]["status"] == "ready"
    assert report["support_request"]["severity"] == "P1"
    assert report["status"] == "pass"


def test_pulse_report_includes_commercial_dossier_when_requested(tmp_path: Path) -> None:
    report = pulse.build_pulse_report(
        tmp_path,
        workflow_eval_builder=lambda root: sample_eval_report(),
        commercial_dossier_builder=lambda root: sample_commercial_dossier(status="ready"),
        include_commercial_dossier=True,
    )

    assert report["commercial_dossier"]["schema_version"] == "relay-kit.commercial-dossier.v1"
    assert report["commercial_dossier"]["status"] == "ready"
    assert report["gate_summary"]["gates"][4]["id"] == "commercial-dossier"
    assert report["status"] == "pass"


def test_pulse_report_marks_support_request_hold_as_attention(tmp_path: Path) -> None:
    report = pulse.build_pulse_report(
        tmp_path,
        workflow_eval_builder=lambda root: sample_eval_report(),
        support_request_builder=lambda root: sample_support_request(status="hold"),
        include_support_request=True,
    )

    assert report["status"] == "attention"
    assert report["support_request"]["findings"][0]["gate"] == "diagnostics"


def test_pulse_report_marks_publication_hold_as_attention(tmp_path: Path) -> None:
    report = pulse.build_pulse_report(
        tmp_path,
        workflow_eval_builder=lambda root: sample_eval_report(),
        publication_builder=lambda root: sample_publication_plan(status="hold"),
        include_publication=True,
    )

    assert report["status"] == "attention"
    assert report["publication"]["findings"][0]["gate"] == "distribution-artifacts"


def test_pulse_report_marks_commercial_dossier_hold_as_attention(tmp_path: Path) -> None:
    report = pulse.build_pulse_report(
        tmp_path,
        workflow_eval_builder=lambda root: sample_eval_report(),
        commercial_dossier_builder=lambda root: sample_commercial_dossier(status="hold"),
        include_commercial_dossier=True,
    )

    assert report["status"] == "attention"
    assert report["commercial_dossier"]["findings"][0]["gate"] == "publication-status"
    gate = next(item for item in report["gate_summary"]["gates"] if item["id"] == "commercial-dossier")
    assert gate["status"] == "attention"
    assert gate["drilldown"][0]["id"] == "publication-status"


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
    assert "Layer coverage" in html
    assert "Gate summary" in html
    assert "Workflow focus" in html
    assert "developer-implementation-ready" in html
    assert "Publication readiness" in html
    assert "Support request" in html
    assert "Commercial dossier" in html
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


def test_pulse_report_includes_gate_summary_and_next_actions(tmp_path: Path) -> None:
    append_event(tmp_path, {"command": "doctor", "gate": "policy guard", "status": "fail", "findings_count": 1})
    limited_readiness = {
        **sample_readiness_report(),
        "verdict": "limited-beta",
    }

    report = pulse.build_pulse_report(
        tmp_path,
        include_readiness=True,
        include_publication=True,
        include_support_request=True,
        workflow_eval_builder=lambda root: sample_eval_report(),
        readiness_builder=lambda root, profile, skip_tests: limited_readiness,
        publication_builder=lambda root: sample_publication_plan(status="hold"),
        support_request_builder=lambda root: sample_support_request(status="hold"),
    )

    summary = report["gate_summary"]
    gate_statuses = {gate["id"]: gate["status"] for gate in summary["gates"]}
    next_action_gates = {action["gate"] for action in summary["next_actions"]}

    assert summary["status_counts"] == {"pass": 1, "attention": 4, "hold": 0, "not-run": 1}
    assert gate_statuses["workflow-eval"] == "pass"
    assert gate_statuses["readiness"] == "attention"
    assert gate_statuses["publication"] == "attention"
    assert gate_statuses["support-request"] == "attention"
    assert gate_statuses["commercial-dossier"] == "not-run"
    assert gate_statuses["evidence"] == "attention"
    assert {"readiness", "publication", "support-request", "evidence"} <= next_action_gates


def test_pulse_report_includes_gate_drilldowns(tmp_path: Path) -> None:
    append_event(
        tmp_path,
        {
            "command": "doctor",
            "gate": "policy guard",
            "status": "fail",
            "findings_count": 1,
        },
    )
    eval_report = {
        **sample_eval_report(),
        "status": "fail",
        "passed": 1,
        "failed": 1,
        "pass_rate": 0.5,
        "results": [
            {
                "id": "developer-routing",
                "passed": False,
                "expected_skill": "developer",
                "predicted_skill": "pm",
                "findings": [{"summary": "expected developer but routed to pm"}],
            }
        ],
    }
    readiness_report = {
        **sample_readiness_report(),
        "status": "fail",
        "verdict": "hold",
        "findings": [{"gate": "pytest", "status": "fail", "summary": "pytest failed"}],
        "gates": [{"id": "pytest", "status": "fail", "summary": "pytest failed"}],
    }

    report = pulse.build_pulse_report(
        tmp_path,
        include_readiness=True,
        include_publication=True,
        include_support_request=True,
        workflow_eval_builder=lambda root: eval_report,
        readiness_builder=lambda root, profile, skip_tests: readiness_report,
        publication_builder=lambda root: sample_publication_plan(status="hold"),
        support_request_builder=lambda root: sample_support_request(status="hold"),
    )

    gates = {gate["id"]: gate for gate in report["gate_summary"]["gates"]}

    assert report["gate_summary"]["drilldown_item_count"] >= 5
    assert gates["workflow-eval"]["drilldown"][0]["id"] == "developer-routing"
    assert gates["readiness"]["drilldown"][0]["id"] == "pytest"
    assert gates["publication"]["drilldown"][0]["id"] == "distribution-artifacts"
    assert gates["support-request"]["drilldown"][0]["id"] == "diagnostics"
    assert gates["evidence"]["drilldown"][0]["id"] == "policy guard"

    html = pulse.render_pulse_html(report)
    assert "Gate details" in html
    assert "developer-routing" in html
    assert "pytest failed" in html


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


def test_public_cli_pulse_build_accepts_support_request_file(tmp_path: Path, capsys) -> None:
    support_request_file = tmp_path / "support-request.json"
    support_request_file.write_text(json.dumps(sample_support_request(status="ready")), encoding="utf-8")

    exit_code = relay_kit_public_cli.main(
        [
            "pulse",
            "build",
            str(tmp_path),
            "--support-request-file",
            str(support_request_file),
            "--json",
            "--no-history",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["report"]["support_request"]["status"] == "ready"


def test_public_cli_pulse_build_accepts_commercial_dossier_file(tmp_path: Path, capsys) -> None:
    dossier_file = tmp_path / "commercial-dossier.json"
    dossier_file.write_text(json.dumps(sample_commercial_dossier(status="ready")), encoding="utf-8")

    exit_code = relay_kit_public_cli.main(
        [
            "pulse",
            "build",
            str(tmp_path),
            "--commercial-dossier-file",
            str(dossier_file),
            "--json",
            "--no-history",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["report"]["commercial_dossier"]["status"] == "ready"
