from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3 import bundle_manifest, support_bundle
from relay_kit_v3.evidence_ledger import append_event


ROOT = Path(__file__).resolve().parents[1]


def test_support_bundle_contains_required_diagnostics(tmp_path: Path) -> None:
    bundle_manifest.write_manifest(tmp_path)
    append_event(
        tmp_path,
        {
            "run_id": "run-1",
            "command": "doctor",
            "gate": "policy guard",
            "status": "pass",
            "findings_count": 0,
        },
    )

    payload = support_bundle.build_support_bundle(tmp_path, policy_pack="baseline")

    assert payload["schema_version"] == "relay-kit.support-bundle.v1"
    assert payload["package"]["name"] == "relay-kit"
    assert payload["diagnostics"]["evidence_summary"]["total_events"] == 1
    assert payload["diagnostics"]["upgrade_report"]["schema_version"] == "relay-kit.upgrade-report.v1"
    assert payload["diagnostics"]["manifest"]["status"] == "valid"
    assert payload["diagnostics"]["policy"]["pack"] == "baseline"
    assert payload["diagnostics"]["workflow_eval"]["schema_version"] == "relay-kit.workflow-eval.v1"
    assert "relay-kit doctor" in payload["support"]["required_commands"][0]


def test_support_bundle_enterprise_requires_trusted_manifest_diagnostic(tmp_path: Path) -> None:
    payload = support_bundle.build_support_bundle(tmp_path, policy_pack="enterprise")
    commands = payload["support"]["required_commands"]

    assert f"relay-kit manifest verify {tmp_path} --trusted" in commands


def test_support_bundle_redacts_obvious_secret_strings(tmp_path: Path) -> None:
    append_event(
        tmp_path,
        {
            "run_id": "run-1",
            "command": "doctor",
            "gate": "custom",
            "status": "fail",
            "note": "leaked sk-test_abcdefghijklmnopqrstuvwxyz123456",
        },
    )

    payload = support_bundle.build_support_bundle(tmp_path, policy_pack="baseline")
    encoded = json.dumps(payload, ensure_ascii=True)

    assert "sk-test_abcdefghijklmnopqrstuvwxyz123456" not in encoded
    assert "[REDACTED]" in encoded


def test_support_bundle_writes_default_output(tmp_path: Path) -> None:
    output_path = support_bundle.write_support_bundle(tmp_path, policy_pack="baseline")

    assert output_path == tmp_path / ".relay-kit" / "support" / "support-bundle.json"
    assert json.loads(output_path.read_text(encoding="utf-8"))["schema_version"] == "relay-kit.support-bundle.v1"


def test_public_cli_support_bundle_json_and_output_file(tmp_path: Path, capsys) -> None:
    output_file = tmp_path / "support.json"

    exit_code = relay_kit_public_cli.main(
        [
            "support",
            "bundle",
            str(tmp_path),
            "--policy-pack",
            "baseline",
            "--output-file",
            str(output_file),
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output_file.exists()
    assert payload["output_file"] == str(output_file)
    assert payload["bundle"]["schema_version"] == "relay-kit.support-bundle.v1"


def test_support_request_contract_is_checked_in() -> None:
    contract = ROOT / ".relay-kit" / "contracts" / "support-request.md"

    assert contract.exists()
    text = contract.read_text(encoding="utf-8")
    assert "Severity" in text
    assert "Required diagnostics" in text
    assert "relay-kit support bundle" in text
