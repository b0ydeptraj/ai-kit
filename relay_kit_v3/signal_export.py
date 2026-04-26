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
DEFAULT_OTLP_OUTPUT = "relay-signals-otlp.json"
DEFAULT_PULSE_FILE = PULSE_OUTPUT_DIR / "pulse-report.json"
OTLP_SCOPE_NAME = "relay-kit.signal-export"


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
    include_otlp: bool = False,
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

    outputs = {"json": json_path, "jsonl": jsonl_path}
    if include_otlp:
        otlp_path = target_dir / DEFAULT_OTLP_OUTPUT
        otlp_path.write_text(json.dumps(build_otlp_export(payload), ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
        outputs["otlp"] = otlp_path
    return outputs


def build_otlp_export(payload: Mapping[str, Any]) -> dict[str, Any]:
    resource = _otlp_attributes(_mapping(payload.get("resource")))
    metric_records = [
        _otlp_metric(signal)
        for signal in payload.get("signals", [])
        if isinstance(signal, Mapping) and signal.get("kind") == "metric"
    ]
    log_records = [
        _otlp_log_record(signal)
        for signal in payload.get("signals", [])
        if isinstance(signal, Mapping) and signal.get("kind") == "event"
    ]

    return {
        "resourceMetrics": [
            {
                "resource": {"attributes": resource},
                "scopeMetrics": [
                    {
                        "scope": {"name": OTLP_SCOPE_NAME, "version": str(payload.get("schema_version", SCHEMA_VERSION))},
                        "metrics": [item for item in metric_records if item is not None],
                    }
                ],
            }
        ],
        "resourceLogs": [
            {
                "resource": {"attributes": resource},
                "scopeLogs": [
                    {
                        "scope": {"name": OTLP_SCOPE_NAME, "version": str(payload.get("schema_version", SCHEMA_VERSION))},
                        "logRecords": [item for item in log_records if item is not None],
                    }
                ],
            }
        ],
    }


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


def _otlp_metric(signal: Mapping[str, Any]) -> dict[str, Any] | None:
    name = str(signal.get("name", ""))
    if not name:
        return None
    value = signal.get("value")
    if value is None:
        return None
    point: dict[str, Any] = {
        "attributes": _otlp_attributes(_mapping(signal.get("attributes"))),
    }
    time_unix_nano = signal.get("time_unix_nano")
    if time_unix_nano:
        point["timeUnixNano"] = str(time_unix_nano)
    if isinstance(value, bool):
        point["asInt"] = "1" if value else "0"
    elif isinstance(value, int):
        point["asInt"] = str(value)
    elif isinstance(value, float):
        point["asDouble"] = value
    else:
        numeric = _number(value)
        if numeric is None:
            return None
        point["asDouble"] = numeric
    return {
        "name": name,
        "unit": str(signal.get("unit", "1")),
        "gauge": {"dataPoints": [point]},
    }


def _otlp_log_record(signal: Mapping[str, Any]) -> dict[str, Any] | None:
    name = str(signal.get("name", ""))
    if not name:
        return None
    attributes = _mapping(signal.get("attributes"))
    record: dict[str, Any] = {
        "severityText": _severity_for_status(str(attributes.get("relay.status", ""))),
        "body": {"stringValue": name},
        "attributes": _otlp_attributes(attributes),
    }
    time_unix_nano = signal.get("time_unix_nano")
    if time_unix_nano:
        record["timeUnixNano"] = str(time_unix_nano)
    return record


def _otlp_attributes(attributes: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {"key": str(key), "value": _otlp_value(value)}
        for key, value in sorted(attributes.items(), key=lambda item: str(item[0]))
        if value is not None
    ]


def _otlp_value(value: Any) -> dict[str, Any]:
    if isinstance(value, bool):
        return {"boolValue": value}
    if isinstance(value, int):
        return {"intValue": str(value)}
    if isinstance(value, float):
        return {"doubleValue": value}
    return {"stringValue": str(value)}


def _severity_for_status(status: str) -> str:
    normalized = status.lower()
    if normalized in {"fail", "failed", "error"}:
        return "ERROR"
    if normalized in {"warn", "warning", "attention"}:
        return "WARN"
    return "INFO"


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
