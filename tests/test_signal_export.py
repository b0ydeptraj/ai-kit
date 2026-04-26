from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3 import signal_export
from relay_kit_v3.evidence_ledger import append_event


def write_pulse_report(root: Path) -> Path:
    pulse_dir = root / ".relay-kit" / "pulse"
    pulse_dir.mkdir(parents=True, exist_ok=True)
    pulse_file = pulse_dir / "pulse-report.json"
    pulse_file.write_text(
        json.dumps(
            {
                "schema_version": "relay-kit.pulse-report.v1",
                "status": "pass",
                "pulse_score": 97,
                "profile": "enterprise",
                "workflow_eval": {
                    "status": "pass",
                    "pass_rate": 1.0,
                    "scenario_count": 12,
                    "failed": 0,
                    "quality": {
                        "evidence_term_coverage": 1.0,
                        "average_route_margin": 10.5,
                        "min_route_margin": 2,
                    },
                },
                "readiness": {
                    "status": "pass",
                    "verdict": "commercial-ready-candidate",
                },
            }
        ),
        encoding="utf-8",
    )
    return pulse_file


def test_signal_export_builds_metrics_and_events(tmp_path: Path) -> None:
    pulse_file = write_pulse_report(tmp_path)
    append_event(tmp_path, {"command": "doctor", "gate": "policy guard", "status": "pass", "findings_count": 0})
    append_event(tmp_path, {"command": "doctor", "gate": "workflow eval", "status": "fail", "findings_count": 1})

    payload = signal_export.build_signal_export(tmp_path, pulse_file=pulse_file, event_limit=10)

    metric_names = {signal["name"] for signal in payload["signals"] if signal["kind"] == "metric"}
    event_names = {signal["name"] for signal in payload["signals"] if signal["kind"] == "event"}

    assert payload["schema_version"] == "relay-kit.signal-export.v1"
    assert payload["resource"]["service.name"] == "relay-kit"
    assert "relay.pulse.score" in metric_names
    assert "relay.workflow.pass_rate" in metric_names
    assert "relay.workflow.evidence_coverage" in metric_names
    assert "relay.evidence.event" in event_names
    assert payload["summary"]["signal_count"] == len(payload["signals"])


def test_signal_export_writes_json_and_jsonl(tmp_path: Path) -> None:
    pulse_file = write_pulse_report(tmp_path)
    payload = signal_export.build_signal_export(tmp_path, pulse_file=pulse_file)

    outputs = signal_export.write_signal_export(tmp_path, payload, output_dir=tmp_path / "signals")

    assert outputs["json"].exists()
    assert outputs["jsonl"].exists()
    assert json.loads(outputs["json"].read_text(encoding="utf-8"))["schema_version"] == "relay-kit.signal-export.v1"
    jsonl_lines = outputs["jsonl"].read_text(encoding="utf-8").splitlines()
    assert len(jsonl_lines) == payload["summary"]["signal_count"]
    assert json.loads(jsonl_lines[0])["resource"]["service.name"] == "relay-kit"


def test_public_cli_signal_export_json(tmp_path: Path, capsys) -> None:
    write_pulse_report(tmp_path)

    exit_code = relay_kit_public_cli.main(["signal", "export", str(tmp_path), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["export"]["schema_version"] == "relay-kit.signal-export.v1"
    assert Path(payload["outputs"]["json"]).exists()
    assert Path(payload["outputs"]["jsonl"]).exists()
