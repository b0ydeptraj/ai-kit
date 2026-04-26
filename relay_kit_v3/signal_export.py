"""Local signal export for Relay-kit Pulse and evidence data."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from relay_kit_v3.evidence_ledger import LEDGER_PATH, read_events, utc_timestamp
from relay_kit_v3.pulse import DEFAULT_OUTPUT_DIR as PULSE_OUTPUT_DIR


SCHEMA_VERSION = "relay-kit.signal-export.v1"
DEFAULT_OUTPUT_DIR = Path(".relay-kit") / "signals"
DEFAULT_JSON_OUTPUT = "relay-signals.json"
DEFAULT_JSONL_OUTPUT = "relay-signals.jsonl"
DEFAULT_PULSE_FILE = PULSE_OUTPUT_DIR / "pulse-report.json"


def build_signal_export(
    project_root: Path | str,
    *,
    pulse_file: Path | str | None = None,
    event_limit: int = 50,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    pulse_path = _resolve_project_path(root, pulse_file or DEFAULT_PULSE_FILE)
    pulse_report = _read_json(pulse_path)
    events = _tail(read_events(root), event_limit)
    resource = build_resource(root, pulse_report)
    signals = [
        *metric_signals(pulse_report),
        *evidence_event_signals(events),
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_timestamp(),
        "project_path": str(root),
        "resource": resource,
        "sources": {
            "pulse_file": str(pulse_path),
            "evidence_ledger": str(root / LEDGER_PATH),
            "event_limit": event_limit,
        },
        "summary": {
            "metric_count": sum(1 for signal in signals if signal["kind"] == "metric"),
            "event_count": sum(1 for signal in signals if signal["kind"] == "event"),
            "signal_count": len(signals),
        },
        "signals": signals,
    }


def write_signal_export(
    project_root: Path | str,
    payload: Mapping[str, Any],
    *,
    output_dir: Path | str | None = None,
) -> dict[str, Path]:
    root = Path(project_root).resolve()
    target_dir = _resolve_output_dir(root, output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    json_path = target_dir / DEFAULT_JSON_OUTPUT
    jsonl_path = target_dir / DEFAULT_JSONL_OUTPUT
    json_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

    resource = _mapping(payload.get("resource"))
    lines = [
        json.dumps({"resource": resource, "signal": signal}, ensure_ascii=True, sort_keys=True)
        for signal in payload.get("signals", [])
        if isinstance(signal, Mapping)
    ]
    jsonl_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return {"json": json_path, "jsonl": jsonl_path}


def build_resource(root: Path, pulse_report: Mapping[str, Any]) -> dict[str, str]:
    return {
        "service.name": "relay-kit",
        "service.namespace": "relay-kit",
        "service.version": str(_mapping(pulse_report.get("package")).get("version", "")),
        "relay.project_path": str(root),
        "relay.profile": str(pulse_report.get("profile", "")),
        "relay.schema_version": str(pulse_report.get("schema_version", "")),
    }


def metric_signals(pulse_report: Mapping[str, Any]) -> list[dict[str, Any]]:
    workflow_eval = _mapping(pulse_report.get("workflow_eval"))
    quality = _mapping(workflow_eval.get("quality"))
    readiness = _mapping(pulse_report.get("readiness"))
    evidence = _mapping(pulse_report.get("evidence"))
    status_counts = _mapping(evidence.get("status_counts"))
    recent_status_counts = _mapping(evidence.get("recent_status_counts"))
    base_attrs = {
        "relay.status": str(pulse_report.get("status", "")),
        "relay.profile": str(pulse_report.get("profile", "")),
    }

    metrics = [
        metric("relay.pulse.score", _number(pulse_report.get("pulse_score")), "1", base_attrs),
        metric("relay.workflow.pass_rate", _number(workflow_eval.get("pass_rate")), "1", base_attrs),
        metric("relay.workflow.scenario_count", _number(workflow_eval.get("scenario_count")), "1", base_attrs),
        metric("relay.workflow.failed_count", _number(workflow_eval.get("failed")), "1", base_attrs),
        metric("relay.workflow.evidence_coverage", _number(quality.get("evidence_term_coverage")), "1", base_attrs),
        metric("relay.workflow.average_route_margin", _number(quality.get("average_route_margin")), "1", base_attrs),
        metric("relay.workflow.min_route_margin", _number(quality.get("min_route_margin")), "1", base_attrs),
        metric("relay.evidence.total_events", _number(evidence.get("total_events")), "1", base_attrs),
        metric("relay.evidence.failures_total", _number(status_counts.get("fail")), "1", base_attrs),
        metric("relay.evidence.failures_recent", _number(recent_status_counts.get("fail")), "1", base_attrs),
        metric(
            "relay.readiness.ready",
            1 if readiness.get("verdict") == "commercial-ready-candidate" else 0,
            "1",
            {**base_attrs, "relay.readiness_verdict": str(readiness.get("verdict", "not-run"))},
        ),
    ]
    return [item for item in metrics if item["value"] is not None]


def evidence_event_signals(events: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    for event in events:
        signals.append(
            {
                "kind": "event",
                "name": "relay.evidence.event",
                "time_unix_nano": timestamp_to_unix_nano(event.get("timestamp")),
                "attributes": {
                    "relay.command": str(event.get("command", "")),
                    "relay.gate": str(event.get("gate", event.get("command", ""))),
                    "relay.status": str(event.get("status", "")),
                    "relay.run_id": str(event.get("run_id", "")),
                    "relay.exit_code": event.get("exit_code"),
                    "relay.findings_count": event.get("findings_count"),
                    "relay.elapsed_ms": event.get("elapsed_ms"),
                },
            }
        )
    return signals


def metric(name: str, value: int | float | None, unit: str, attributes: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "kind": "metric",
        "name": name,
        "value": value,
        "unit": unit,
        "time_unix_nano": timestamp_to_unix_nano(utc_timestamp()),
        "attributes": dict(attributes),
    }


def timestamp_to_unix_nano(value: Any) -> int | None:
    if not value:
        return None
    text = str(value)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp() * 1_000_000_000)


def _read_json(path: Path) -> Mapping[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"Signal source must be a JSON object: {path}")
    return payload


def _resolve_output_dir(root: Path, output_dir: Path | str | None) -> Path:
    target_dir = Path(output_dir) if output_dir is not None else root / DEFAULT_OUTPUT_DIR
    if not target_dir.is_absolute():
        target_dir = root / target_dir
    return target_dir


def _resolve_project_path(root: Path, path: Path | str) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = root / resolved
    return resolved.resolve()


def _tail(items: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    if limit <= 0:
        return []
    return items[-limit:]


def _number(value: Any) -> int | float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return value
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
