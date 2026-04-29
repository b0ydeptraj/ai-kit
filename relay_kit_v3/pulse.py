"""Static Pulse report generation for Relay-kit quality signals."""

from __future__ import annotations

import json
from collections import Counter
from html import escape
from pathlib import Path
from typing import Any, Callable, Mapping

from relay_kit_v3.evidence_ledger import LedgerSummary, summarize_events, utc_timestamp
from relay_kit_v3.publication import build_publication_plan
from relay_kit_v3.readiness import build_readiness_report
from scripts import eval_workflows


SCHEMA_VERSION = "relay-kit.pulse-report.v1"
HISTORY_SCHEMA_VERSION = "relay-kit.pulse-history.v1"
DEFAULT_OUTPUT_DIR = Path(".relay-kit") / "pulse"
HISTORY_FILE = "history.jsonl"

WorkflowEvalBuilder = Callable[[Path], Mapping[str, Any]]
ReadinessBuilder = Callable[[Path, str, bool], Mapping[str, Any]]
PublicationBuilder = Callable[[Path], Mapping[str, Any]]
EvidenceSummarizer = Callable[[Path, int], LedgerSummary]


def build_pulse_report(
    project_root: Path | str,
    *,
    profile: str = "enterprise",
    evidence_limit: int = 20,
    include_readiness: bool = False,
    skip_tests: bool = True,
    workflow_eval_file: Path | str | None = None,
    readiness_file: Path | str | None = None,
    publication_file: Path | str | None = None,
    include_publication: bool = False,
    output_dir: Path | str | None = None,
    history_limit: int = 20,
    workflow_eval_builder: WorkflowEvalBuilder | None = None,
    readiness_builder: ReadinessBuilder | None = None,
    publication_builder: PublicationBuilder | None = None,
    evidence_summarizer: EvidenceSummarizer | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    eval_report = _load_or_build_workflow_eval(root, workflow_eval_file, workflow_eval_builder)
    readiness_report = _load_or_build_readiness(
        root,
        profile=profile,
        include_readiness=include_readiness,
        skip_tests=skip_tests,
        readiness_file=readiness_file,
        readiness_builder=readiness_builder,
    )
    publication_report = _load_or_build_publication(
        root,
        include_publication=include_publication,
        publication_file=publication_file,
        publication_builder=publication_builder,
    )
    evidence = _evidence_payload(root, evidence_limit, evidence_summarizer)
    status = pulse_status(eval_report, readiness_report, publication_report, evidence)
    score = pulse_score(eval_report, readiness_report, publication_report, evidence)
    trend = build_trend(
        root,
        output_dir=output_dir,
        current_snapshot=snapshot_from_values(
            status=status,
            pulse_score=score,
            profile=profile,
            workflow_eval=eval_report,
            readiness=readiness_report,
            publication=publication_report,
            evidence=evidence,
        ),
        limit=history_limit,
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "pulse_score": score,
        "project_path": str(root),
        "profile": profile,
        "workflow_eval": eval_report,
        "readiness": readiness_report,
        "publication": publication_report,
        "evidence": evidence,
        "trend": trend,
        "outputs": {
            "default_dir": str(_resolve_output_dir(root, output_dir)),
        },
    }


def write_pulse_report(
    project_root: Path | str,
    report: Mapping[str, Any],
    *,
    output_dir: Path | str | None = None,
    record_history: bool = True,
) -> dict[str, Path]:
    root = Path(project_root).resolve()
    target_dir = _resolve_output_dir(root, output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    json_path = target_dir / "pulse-report.json"
    html_path = target_dir / "index.html"
    json_path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(render_pulse_html(report), encoding="utf-8")
    history_path = target_dir / HISTORY_FILE
    if record_history:
        append_pulse_history(history_path, report)
    return {"json": json_path, "html": html_path, "history": history_path}


def render_pulse_html(report: Mapping[str, Any]) -> str:
    workflow_eval = _mapping(report.get("workflow_eval"))
    quality = _mapping(workflow_eval.get("quality"))
    readiness = _mapping(report.get("readiness"))
    publication = _mapping(report.get("publication"))
    evidence = _mapping(report.get("evidence"))
    trend = _mapping(report.get("trend"))
    status_counts = _mapping(evidence.get("recent_status_counts"))
    recent_events = evidence.get("recent_events", [])
    if not isinstance(recent_events, list):
        recent_events = []

    cards = [
        ("Pulse score", str(report.get("pulse_score", "-"))),
        ("Status", str(report.get("status", "-"))),
        ("Eval pass rate", _percent(workflow_eval.get("pass_rate"))),
        ("Evidence coverage", _percent(quality.get("evidence_term_coverage"))),
        ("Min route margin", str(quality.get("min_route_margin", "-"))),
        ("Readiness", str(readiness.get("verdict", "not-run"))),
        ("Publication", str(publication.get("status", "not-run"))),
        ("Score delta", _signed(trend.get("pulse_score_delta"))),
        ("Ledger events", str(evidence.get("total_events", 0))),
        ("Recent failures", str(status_counts.get("fail", 0))),
    ]

    card_html = "\n".join(
        f'<section class="metric"><span>{escape(label)}</span><strong>{escape(value)}</strong></section>'
        for label, value in cards
    )
    rows = "\n".join(_event_row(event) for event in recent_events[-12:])
    if not rows:
        rows = '<tr><td colspan="4">No recent evidence events.</td></tr>'
    trend_rows = _trend_rows(trend)
    publication_rows = _publication_rows(publication)

    report_json = escape(json.dumps(report, ensure_ascii=True, indent=2))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Relay-kit Pulse</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --ink: #17202a;
      --muted: #5d6876;
      --line: #d9dee7;
      --accent: #126b5f;
      --hold: #b42318;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
    }}
    header, main {{
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
    }}
    header {{
      padding: 32px 0 18px;
      border-bottom: 1px solid var(--line);
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 32px;
      line-height: 1.1;
      letter-spacing: 0;
    }}
    .subtle {{ color: var(--muted); margin: 0; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin: 24px 0;
    }}
    .metric {{
      min-height: 92px;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 10px;
    }}
    .metric strong {{
      display: block;
      font-size: 24px;
      line-height: 1.15;
      color: var(--accent);
      word-break: break-word;
    }}
    section.panel {{
      margin: 24px 0;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }}
    h2 {{
      margin: 0 0 14px;
      font-size: 18px;
      letter-spacing: 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      padding: 10px 8px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    th {{ color: var(--muted); font-weight: 600; }}
    pre {{
      overflow: auto;
      max-height: 520px;
      padding: 14px;
      background: #111820;
      color: #f3f6fa;
      border-radius: 8px;
      font-size: 12px;
      line-height: 1.5;
    }}
  </style>
</head>
<body>
  <header>
    <h1>Relay-kit Pulse</h1>
    <p class="subtle">{escape(str(report.get("project_path", "")))}</p>
  </header>
  <main>
    <div class="grid">
      {card_html}
    </div>
    <section class="panel">
      <h2>Workflow quality</h2>
      <table>
        <tr><th>Signal</th><th>Value</th></tr>
        <tr><td>Scenario count</td><td>{escape(str(workflow_eval.get("scenario_count", 0)))}</td></tr>
        <tr><td>Average route margin</td><td>{escape(str(quality.get("average_route_margin", "-")))}</td></tr>
        <tr><td>Mean route confidence</td><td>{escape(str(quality.get("mean_route_confidence", "-")))}</td></tr>
        <tr><td>Expected skills</td><td>{escape(", ".join(_mapping(quality.get("expected_skill_counts")).keys()))}</td></tr>
      </table>
    </section>
    <section class="panel">
      <h2>Trend</h2>
      <table>
        <tr><th>Signal</th><th>Delta</th></tr>
        {trend_rows}
      </table>
    </section>
    <section class="panel">
      <h2>Publication readiness</h2>
      <table>
        <tr><th>Signal</th><th>Value</th></tr>
        {publication_rows}
      </table>
    </section>
    <section class="panel">
      <h2>Recent evidence</h2>
      <table>
        <tr><th>Time</th><th>Gate</th><th>Status</th><th>Findings</th></tr>
        {rows}
      </table>
    </section>
    <section class="panel">
      <h2>Raw report</h2>
      <pre>{report_json}</pre>
    </section>
  </main>
</body>
</html>
"""


def pulse_status(
    workflow_eval: Mapping[str, Any],
    readiness: Mapping[str, Any] | None,
    publication: Mapping[str, Any] | None,
    evidence: Mapping[str, Any],
) -> str:
    if workflow_eval.get("status") != "pass":
        return "hold"
    if readiness is not None and readiness.get("status") != "pass":
        return "hold"
    if readiness is not None and readiness.get("verdict") not in {None, "commercial-ready-candidate"}:
        return "attention"
    if publication is not None and publication.get("status") != "ready":
        return "attention"
    recent_status_counts = _mapping(evidence.get("recent_status_counts"))
    if int(recent_status_counts.get("fail", 0) or 0) > 0:
        return "attention"
    return "pass"


def pulse_score(
    workflow_eval: Mapping[str, Any],
    readiness: Mapping[str, Any] | None,
    publication: Mapping[str, Any] | None,
    evidence: Mapping[str, Any],
) -> int:
    quality = _mapping(workflow_eval.get("quality"))
    pass_rate = _float(workflow_eval.get("pass_rate"))
    evidence_coverage = _float(quality.get("evidence_term_coverage"), default=1.0)
    if readiness is None:
        readiness_score = 8
    elif readiness.get("status") == "pass" and readiness.get("verdict") == "commercial-ready-candidate":
        readiness_score = 15
    elif readiness.get("status") == "pass":
        readiness_score = 10
    else:
        readiness_score = 0
    if publication is None:
        publication_score = 5
    elif publication.get("status") == "ready":
        publication_score = 5
    else:
        publication_score = 0
    fail_count = int(_mapping(evidence.get("recent_status_counts")).get("fail", 0) or 0)
    evidence_score = max(0, 5 - (fail_count * 2))
    score = round((pass_rate * 65) + (evidence_coverage * 10) + readiness_score + publication_score + evidence_score)
    return max(0, min(100, int(score)))


def build_trend(
    root: Path,
    *,
    output_dir: Path | str | None,
    current_snapshot: Mapping[str, Any],
    limit: int = 20,
) -> dict[str, Any]:
    history_path = _resolve_output_dir(root, output_dir) / HISTORY_FILE
    history = read_pulse_history(history_path, limit=limit)
    previous = history[-1] if history else None
    trend: dict[str, Any] = {
        "history_path": str(history_path),
        "history_count": len(history),
        "previous": previous,
        "recent": history,
        "pulse_score_delta": None,
        "pass_rate_delta": None,
        "evidence_coverage_delta": None,
        "average_route_margin_delta": None,
        "status_changed": False,
    }
    if previous is None:
        return trend

    trend.update(
        {
            "pulse_score_delta": _delta(current_snapshot.get("pulse_score"), previous.get("pulse_score"), digits=0),
            "pass_rate_delta": _delta(current_snapshot.get("pass_rate"), previous.get("pass_rate")),
            "evidence_coverage_delta": _delta(
                current_snapshot.get("evidence_coverage"),
                previous.get("evidence_coverage"),
            ),
            "average_route_margin_delta": _delta(
                current_snapshot.get("average_route_margin"),
                previous.get("average_route_margin"),
            ),
            "status_changed": current_snapshot.get("status") != previous.get("status"),
        }
    )
    return trend


def append_pulse_history(history_path: Path, report: Mapping[str, Any]) -> Path:
    history_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot = pulse_history_snapshot(report)
    with history_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(snapshot, ensure_ascii=True, sort_keys=True))
        handle.write("\n")
    return history_path


def read_pulse_history(history_path: Path, *, limit: int = 20) -> list[dict[str, Any]]:
    if not history_path.exists():
        return []
    snapshots: list[dict[str, Any]] = []
    for line in history_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            snapshots.append(payload)
    if limit <= 0:
        return []
    return snapshots[-limit:]


def pulse_history_snapshot(report: Mapping[str, Any]) -> dict[str, Any]:
    workflow_eval = _mapping(report.get("workflow_eval"))
    readiness = _mapping(report.get("readiness"))
    publication = _mapping(report.get("publication"))
    evidence = _mapping(report.get("evidence"))
    return {
        "schema_version": HISTORY_SCHEMA_VERSION,
        "timestamp": utc_timestamp(),
        **snapshot_from_values(
            status=str(report.get("status", "unknown")),
            pulse_score=int(report.get("pulse_score", 0) or 0),
            profile=str(report.get("profile", "")),
            workflow_eval=workflow_eval,
            readiness=readiness if readiness else None,
            publication=publication if publication else None,
            evidence=evidence,
        ),
    }


def snapshot_from_values(
    *,
    status: str,
    pulse_score: int,
    profile: str,
    workflow_eval: Mapping[str, Any],
    readiness: Mapping[str, Any] | None,
    publication: Mapping[str, Any] | None,
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    quality = _mapping(workflow_eval.get("quality"))
    recent_status_counts = _mapping(evidence.get("recent_status_counts"))
    return {
        "status": status,
        "pulse_score": pulse_score,
        "profile": profile,
        "pass_rate": _float(workflow_eval.get("pass_rate")),
        "scenario_count": int(workflow_eval.get("scenario_count", 0) or 0),
        "failed": int(workflow_eval.get("failed", 0) or 0),
        "evidence_coverage": _float(quality.get("evidence_term_coverage"), default=1.0),
        "average_route_margin": _float(quality.get("average_route_margin")),
        "min_route_margin": int(quality.get("min_route_margin", 0) or 0),
        "readiness_status": readiness.get("status") if readiness else None,
        "readiness_verdict": readiness.get("verdict") if readiness else None,
        "publication_status": publication.get("status") if publication else None,
        "publication_findings": len(publication.get("findings", [])) if publication else None,
        "recent_failures": int(recent_status_counts.get("fail", 0) or 0),
    }


def _load_or_build_workflow_eval(
    root: Path,
    workflow_eval_file: Path | str | None,
    workflow_eval_builder: WorkflowEvalBuilder | None,
) -> Mapping[str, Any]:
    if workflow_eval_file is not None:
        return _read_json(root, workflow_eval_file)
    builder = workflow_eval_builder or (lambda project_root: eval_workflows.build_report(project_root))
    return builder(root)


def _load_or_build_readiness(
    root: Path,
    *,
    profile: str,
    include_readiness: bool,
    skip_tests: bool,
    readiness_file: Path | str | None,
    readiness_builder: ReadinessBuilder | None,
) -> Mapping[str, Any] | None:
    if readiness_file is not None:
        return _read_json(root, readiness_file)
    if not include_readiness:
        return None
    builder = readiness_builder or (
        lambda project_root, selected_profile, should_skip_tests: build_readiness_report(
            project_root,
            profile=selected_profile,
            skip_tests=should_skip_tests,
        )
    )
    return builder(root, profile, skip_tests)


def _load_or_build_publication(
    root: Path,
    *,
    include_publication: bool,
    publication_file: Path | str | None,
    publication_builder: PublicationBuilder | None,
) -> Mapping[str, Any] | None:
    if publication_file is not None:
        return _read_json(root, publication_file)
    if not include_publication:
        return None
    builder = publication_builder or (lambda project_root: build_publication_plan(project_root, channel="pypi"))
    return builder(root)


def _evidence_payload(
    root: Path,
    evidence_limit: int,
    evidence_summarizer: EvidenceSummarizer | None,
) -> dict[str, Any]:
    summarizer = evidence_summarizer or (lambda project_root, limit: summarize_events(project_root, limit=limit))
    summary = summarizer(root, evidence_limit)
    recent_status_counts = Counter(str(event.get("status", "unknown")) for event in summary.recent_events)
    return {
        "ledger_path": str(summary.ledger_path),
        "total_events": summary.total_events,
        "status_counts": summary.status_counts,
        "recent_status_counts": dict(sorted(recent_status_counts.items())),
        "gate_counts": summary.gate_counts,
        "recent_events": summary.recent_events,
    }


def _read_json(root: Path, path: Path | str) -> Mapping[str, Any]:
    source = Path(path)
    if not source.is_absolute():
        source = root / source
    payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"Pulse source must be a JSON object: {source}")
    return payload


def _resolve_output_dir(root: Path, output_dir: Path | str | None = None) -> Path:
    target_dir = Path(output_dir) if output_dir is not None else root / DEFAULT_OUTPUT_DIR
    if not target_dir.is_absolute():
        target_dir = root / target_dir
    return target_dir


def _event_row(event: Mapping[str, Any]) -> str:
    gate = str(event.get("gate", event.get("command", "unknown")))
    return (
        "<tr>"
        f"<td>{escape(str(event.get('timestamp', '-')))}</td>"
        f"<td>{escape(gate)}</td>"
        f"<td>{escape(str(event.get('status', 'unknown')))}</td>"
        f"<td>{escape(str(event.get('findings_count', '-')))}</td>"
        "</tr>"
    )


def _trend_rows(trend: Mapping[str, Any]) -> str:
    rows = [
        ("History snapshots", str(trend.get("history_count", 0))),
        ("Pulse score", _signed(trend.get("pulse_score_delta"))),
        ("Pass rate", _signed_percent(trend.get("pass_rate_delta"))),
        ("Evidence coverage", _signed_percent(trend.get("evidence_coverage_delta"))),
        ("Average route margin", _signed(trend.get("average_route_margin_delta"))),
        ("Status changed", "yes" if trend.get("status_changed") else "no"),
    ]
    return "\n".join(
        f"<tr><td>{escape(label)}</td><td>{escape(value)}</td></tr>"
        for label, value in rows
    )


def _publication_rows(publication: Mapping[str, Any]) -> str:
    if not publication:
        rows = [("Status", "not-run")]
    else:
        findings = publication.get("findings", [])
        rows = [
            ("Status", str(publication.get("status", "-"))),
            ("Channel", str(publication.get("channel", "-"))),
            ("Version", str(publication.get("version", "-"))),
            ("Findings", str(len(findings) if isinstance(findings, list) else 0)),
        ]
    return "\n".join(
        f"<tr><td>{escape(label)}</td><td>{escape(value)}</td></tr>"
        for label, value in rows
    )


def _delta(current: Any, previous: Any, *, digits: int = 4) -> float | int:
    value = _float(current) - _float(previous)
    if digits == 0:
        return int(round(value))
    return round(value, digits)


def _signed(value: Any) -> str:
    if value is None:
        return "-"
    number = _float(value)
    if number > 0:
        return f"+{number:g}"
    return f"{number:g}"


def _signed_percent(value: Any) -> str:
    if value is None:
        return "-"
    number = _float(value)
    sign = "+" if number > 0 else ""
    return f"{sign}{number * 100:.0f}%"


def _percent(value: Any) -> str:
    return f"{_float(value) * 100:.0f}%"


def _float(value: Any, *, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
