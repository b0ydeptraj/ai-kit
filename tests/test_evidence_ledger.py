from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3 import evidence_ledger


def test_evidence_ledger_appends_and_summarizes_events(tmp_path: Path) -> None:
    evidence_ledger.append_event(
        tmp_path,
        {
            "run_id": "run-1",
            "command": "doctor",
            "gate": "runtime doctor",
            "status": "pass",
            "elapsed_ms": 12,
            "findings_count": 0,
        },
    )
    evidence_ledger.append_event(
        tmp_path,
        {
            "run_id": "run-1",
            "command": "doctor",
            "gate": "naming guard",
            "status": "fail",
            "elapsed_ms": 4,
            "findings_count": 2,
        },
    )

    summary = evidence_ledger.summarize_events(tmp_path, limit=1)

    assert summary.total_events == 2
    assert summary.status_counts == {"fail": 1, "pass": 1}
    assert summary.gate_counts["naming guard"] == 1
    assert summary.recent_events[0]["gate"] == "naming guard"


def test_doctor_records_gate_events(monkeypatch) -> None:
    events: list[dict[str, object]] = []

    def fake_run(command, cwd, text, capture_output, check):  # noqa: ANN001
        return subprocess.CompletedProcess(command, 0, stdout="- findings: 0\n", stderr="")

    def fake_append_event(project_root, event):  # noqa: ANN001
        events.append(event)
        return Path(project_root) / ".relay-kit" / "evidence" / "events.jsonl"

    monkeypatch.setattr(relay_kit_public_cli.subprocess, "run", fake_run)
    monkeypatch.setattr(relay_kit_public_cli, "append_event", fake_append_event)

    exit_code = relay_kit_public_cli.main(["doctor", ".", "--skip-tests"])

    assert exit_code == 0
    assert {event["gate"] for event in events} == {
        "validate runtime",
        "runtime doctor template",
        "runtime doctor live",
        "naming guard",
        "policy guard",
        "srs guard",
        "skill gauntlet",
        "workflow eval",
    }
    assert all(event["command"] == "doctor" for event in events)
    assert all(event["status"] == "pass" for event in events)
    assert all(event["findings_count"] == 0 for event in events)


def test_doctor_json_outputs_gate_results(monkeypatch, capsys) -> None:
    def fake_run(command, cwd, text, capture_output, check):  # noqa: ANN001
        return subprocess.CompletedProcess(command, 0, stdout="- findings: 0\n", stderr="")

    monkeypatch.setattr(relay_kit_public_cli.subprocess, "run", fake_run)
    monkeypatch.setattr(relay_kit_public_cli, "append_event", lambda project_root, event: Path(project_root))

    exit_code = relay_kit_public_cli.main(["doctor", ".", "--skip-tests", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "pass"
    assert payload["results"][0]["gate"] == "validate runtime"
    assert payload["results"][0]["findings_count"] == 0


def test_evidence_summary_command_outputs_recent_gate(monkeypatch, capsys, tmp_path: Path) -> None:
    evidence_ledger.append_event(
        tmp_path,
        {
            "run_id": "run-1",
            "command": "doctor",
            "gate": "skill gauntlet",
            "status": "pass",
            "elapsed_ms": 5,
        },
    )

    exit_code = relay_kit_public_cli.main(["evidence", "summary", str(tmp_path)])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "total events: 1" in output
    assert "skill gauntlet" in output
