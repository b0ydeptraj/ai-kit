from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3 import support_request, support_triage
from relay_kit_v3.support_bundle import SCHEMA_VERSION as SUPPORT_BUNDLE_SCHEMA_VERSION


def write_ready_support_artifacts(root: Path, *, include_bundle: bool = True) -> None:
    support_dir = root / ".relay-kit" / "support"
    support_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = support_dir / "support-bundle.json"
    if include_bundle:
        bundle_path.write_text(
            json.dumps(
                {
                    "schema_version": SUPPORT_BUNDLE_SCHEMA_VERSION,
                    "diagnostics": {
                        "manifest": {"status": "valid"},
                        "policy": {"findings_count": 0},
                        "workflow_eval": {"status": "pass"},
                        "signal_export": {"status": "pass", "summary": {"signal_count": 3}},
                        "release_lane": {"status": "pass"},
                    },
                }
            )
            + "\n",
            encoding="utf-8",
        )
    signal_dir = root / ".relay-kit" / "signals"
    signal_dir.mkdir(parents=True, exist_ok=True)
    signal_json = signal_dir / "relay-signals.json"
    signal_jsonl = signal_dir / "relay-signals.jsonl"
    signal_otlp = signal_dir / "relay-signals-otlp.json"
    signal_json.write_text('{"schema_version":"relay-kit.signal-export.v1"}\n', encoding="utf-8")
    signal_jsonl.write_text("{}\n", encoding="utf-8")
    signal_otlp.write_text('{"resourceMetrics":[],"resourceLogs":[]}\n', encoding="utf-8")
    request = support_request.build_support_request(
        root,
        severity="P1",
        summary="Enterprise doctor fails after manifest trust metadata drift.",
        package_version="3.4.0",
        operating_system="Windows",
        shell="PowerShell",
        installed_bundle="enterprise",
        adapter_target="codex",
        policy_pack="enterprise",
        expected_behavior="Enterprise doctor should pass with trusted manifest metadata.",
        actual_behavior="Trusted manifest verification fails after a local skill edit.",
        recent_changes="Regenerated skills and edited manifest metadata.",
        workaround="Regenerate manifest trust metadata before release.",
        diagnostic_files=([bundle_path] if include_bundle else []) + [signal_json, signal_jsonl, signal_otlp],
    )
    support_request.write_support_request(root, request)


def test_support_triage_ready_with_request_and_bundle(tmp_path: Path) -> None:
    write_ready_support_artifacts(tmp_path)

    report = support_triage.build_support_triage(tmp_path)

    assert report["schema_version"] == "relay-kit.support-triage.v1"
    assert report["status"] == "ready"
    assert report["severity"] == "P1"
    assert report["findings"] == []
    assert report["checks_by_id"]["support-request"]["status"] == "pass"
    assert report["checks_by_id"]["support-bundle"]["status"] == "pass"
    assert "next business day" in report["sla"]["target"]


def test_support_triage_holds_without_support_bundle(tmp_path: Path) -> None:
    write_ready_support_artifacts(tmp_path, include_bundle=False)

    report = support_triage.build_support_triage(tmp_path)

    assert report["status"] == "hold"
    assert any(finding["gate"] == "support-bundle" for finding in report["findings"])
    assert any("support bundle" in action for action in report["next_actions"])


def test_support_triage_holds_when_bundle_diagnostics_are_degraded(tmp_path: Path) -> None:
    write_ready_support_artifacts(tmp_path)
    bundle_path = tmp_path / ".relay-kit" / "support" / "support-bundle.json"
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    payload["diagnostics"]["policy"]["findings_count"] = 1
    payload["diagnostics"]["workflow_eval"]["status"] = "fail"
    bundle_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    report = support_triage.build_support_triage(tmp_path)

    assert report["status"] == "hold"
    bundle_check = report["checks_by_id"]["support-bundle"]
    assert bundle_check["status"] == "hold"
    assert bundle_check["details"]["findings_count"] == 2
    assert any("policy findings" in action for action in report["next_actions"])


def test_support_soak_report_exercises_p0_p1_p2_cases(tmp_path: Path) -> None:
    write_ready_support_artifacts(tmp_path)

    report = support_triage.build_support_soak_report(tmp_path)

    assert report["schema_version"] == "relay-kit.support-soak.v1"
    assert report["status"] == "pass"
    assert [case["severity"] for case in report["cases"]] == ["P0", "P1", "P2"]
    assert {case["status"] for case in report["cases"]} == {"pass"}
    assert all(case["request_check"]["status"] == "pass" for case in report["cases"])
    assert all(case["bundle_check"]["status"] == "pass" for case in report["cases"])
    assert all(case["sla"]["target"] for case in report["cases"])


def test_public_cli_support_soak_json_and_strict(tmp_path: Path, capsys) -> None:
    write_ready_support_artifacts(tmp_path)

    exit_code = relay_kit_public_cli.main(["support", "soak", str(tmp_path), "--strict", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["schema_version"] == "relay-kit.support-soak.v1"
    assert payload["status"] == "pass"
    assert payload["case_count"] == 3


def test_public_cli_support_triage_json_and_strict(tmp_path: Path, capsys) -> None:
    exit_code = relay_kit_public_cli.main(["support", "triage", str(tmp_path), "--strict", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert payload["schema_version"] == "relay-kit.support-triage.v1"
    assert payload["status"] == "hold"
