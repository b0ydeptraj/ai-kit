from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3 import support_request


def write_support_diagnostics(root: Path) -> list[Path]:
    support = root / ".relay-kit" / "support"
    support.mkdir(parents=True, exist_ok=True)
    bundle = support / "support-bundle.json"
    bundle.write_text('{"schema_version":"relay-kit.support-bundle.v1"}\n', encoding="utf-8")
    signals = root / ".relay-kit" / "signals"
    signals.mkdir(parents=True, exist_ok=True)
    signal_json = signals / "relay-signals.json"
    signal_jsonl = signals / "relay-signals.jsonl"
    signal_otlp = signals / "relay-signals-otlp.json"
    signal_json.write_text('{"schema_version":"relay-kit.signal-export.v1"}\n', encoding="utf-8")
    signal_jsonl.write_text("{}\n", encoding="utf-8")
    signal_otlp.write_text('{"resourceMetrics":[],"resourceLogs":[]}\n', encoding="utf-8")
    return [bundle, signal_json, signal_jsonl, signal_otlp]


def support_request_kwargs(root: Path) -> dict[str, object]:
    return {
        "severity": "P1",
        "summary": "Enterprise doctor fails after manifest trust metadata drift.",
        "package_version": "3.4.0.dev0",
        "operating_system": "Windows",
        "shell": "PowerShell",
        "installed_bundle": "enterprise",
        "adapter_target": "codex",
        "policy_pack": "enterprise",
        "expected_behavior": "Enterprise doctor should pass with trusted manifest metadata.",
        "actual_behavior": "Trusted manifest verification fails after a local skill edit.",
        "recent_changes": "Regenerated skills and edited manifest metadata.",
        "workaround": "Run baseline policy pack while the manifest is regenerated.",
        "diagnostic_files": write_support_diagnostics(root),
    }


def test_support_request_ready_with_required_fields_and_diagnostics(tmp_path: Path) -> None:
    report = support_request.build_support_request(tmp_path, **support_request_kwargs(tmp_path))

    assert report["schema_version"] == "relay-kit.support-request.v1"
    assert report["status"] == "ready"
    assert report["severity"] == "P1"
    assert report["findings"] == []
    assert {item["status"] for item in report["diagnostics"]} == {"present"}


def test_support_request_holds_missing_fields_and_diagnostics(tmp_path: Path) -> None:
    report = support_request.build_support_request(
        tmp_path,
        severity="P4",
        summary="TBD",
        expected_behavior="",
        actual_behavior="",
    )

    assert report["status"] == "hold"
    gates = {finding["gate"] for finding in report["findings"]}
    assert {"severity", "summary", "expected_behavior", "actual_behavior", "diagnostics"} <= gates


def test_support_request_redacts_secret_like_values(tmp_path: Path) -> None:
    kwargs = support_request_kwargs(tmp_path)
    kwargs["actual_behavior"] = "Command output included sk-test_abcdefghijklmnopqrstuvwxyz123456"

    report = support_request.build_support_request(tmp_path, **kwargs)
    encoded = json.dumps(report, ensure_ascii=True)

    assert "sk-test_abcdefghijklmnopqrstuvwxyz123456" not in encoded
    assert "[REDACTED]" in encoded


def test_public_cli_support_request_json_and_default_output(tmp_path: Path, capsys) -> None:
    diagnostics = write_support_diagnostics(tmp_path)

    exit_code = relay_kit_public_cli.main(
        [
            "support",
            "request",
            str(tmp_path),
            "--severity",
            "P1",
            "--summary",
            "Enterprise doctor fails after manifest trust metadata drift.",
            "--package-version",
            "3.4.0.dev0",
            "--os",
            "Windows",
            "--shell",
            "PowerShell",
            "--bundle",
            "enterprise",
            "--adapter",
            "codex",
            "--policy-pack",
            "enterprise",
            "--expected",
            "Enterprise doctor should pass with trusted manifest metadata.",
            "--actual",
            "Trusted manifest verification fails after a local skill edit.",
            "--recent-changes",
            "Regenerated skills and edited manifest metadata.",
            "--workaround",
            "Run baseline policy pack while the manifest is regenerated.",
            "--diagnostic-file",
            str(diagnostics[0]),
            "--diagnostic-file",
            str(diagnostics[1]),
            "--diagnostic-file",
            str(diagnostics[2]),
            "--diagnostic-file",
            str(diagnostics[3]),
            "--strict",
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    output_path = tmp_path / ".relay-kit" / "support" / "support-request.json"

    assert exit_code == 0
    assert payload["output_file"] == str(output_path)
    assert output_path.exists()
    assert payload["request"]["status"] == "ready"
