"""Static Pulse report generation for Relay-kit quality signals."""

from __future__ import annotations

import json
from collections import Counter
from html import escape
from pathlib import Path
from typing import Any, Callable, Mapping

from relay_kit_v3.commercial_dossier import DEFAULT_OUTPUT as DEFAULT_COMMERCIAL_DOSSIER_OUTPUT
from relay_kit_v3.evidence_ledger import LedgerSummary, summarize_events, utc_timestamp
from relay_kit_v3.publication import DEFAULT_INDEX_CHECK_OUTPUT, build_publication_plan
from relay_kit_v3.readiness import build_readiness_report
from relay_kit_v3.support_request import DEFAULT_OUTPUT as DEFAULT_SUPPORT_REQUEST_OUTPUT
from scripts import eval_workflows


SCHEMA_VERSION = "relay-kit.pulse-report.v1"
HISTORY_SCHEMA_VERSION = "relay-kit.pulse-history.v1"
DEFAULT_OUTPUT_DIR = Path(".relay-kit") / "pulse"
HISTORY_FILE = "history.jsonl"
DRILLDOWN_LIMIT = 8

WorkflowEvalBuilder = Callable[[Path], Mapping[str, Any]]
ReadinessBuilder = Callable[[Path, str, bool], Mapping[str, Any]]
PublicationBuilder = Callable[[Path], Mapping[str, Any]]
PackageIndexBuilder = Callable[[Path], Mapping[str, Any]]
SupportRequestBuilder = Callable[[Path], Mapping[str, Any]]
CommercialDossierBuilder = Callable[[Path], Mapping[str, Any]]
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
    package_index_file: Path | str | None = None,
    support_request_file: Path | str | None = None,
    commercial_dossier_file: Path | str | None = None,
    include_publication: bool = False,
    include_package_index: bool = False,
    include_support_request: bool = False,
    include_commercial_dossier: bool = False,
    output_dir: Path | str | None = None,
    history_limit: int = 20,
    workflow_eval_builder: WorkflowEvalBuilder | None = None,
    readiness_builder: ReadinessBuilder | None = None,
    publication_builder: PublicationBuilder | None = None,
    package_index_builder: PackageIndexBuilder | None = None,
    support_request_builder: SupportRequestBuilder | None = None,
    commercial_dossier_builder: CommercialDossierBuilder | None = None,
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
    package_index = _load_or_build_package_index(
        root,
        include_package_index=include_package_index,
        package_index_file=package_index_file,
        package_index_builder=package_index_builder,
    )
    support_request = _load_or_build_support_request(
        root,
        include_support_request=include_support_request,
        support_request_file=support_request_file,
        support_request_builder=support_request_builder,
    )
    commercial_dossier = _load_or_build_commercial_dossier(
        root,
        include_commercial_dossier=include_commercial_dossier,
        commercial_dossier_file=commercial_dossier_file,
        commercial_dossier_builder=commercial_dossier_builder,
    )
    evidence = _evidence_payload(root, evidence_limit, evidence_summarizer)
    status = pulse_status(eval_report, readiness_report, publication_report, package_index, support_request, commercial_dossier, evidence)
    score = pulse_score(eval_report, readiness_report, publication_report, package_index, support_request, commercial_dossier, evidence)
    gate_summary = build_gate_summary(eval_report, readiness_report, publication_report, package_index, support_request, commercial_dossier, evidence)
    workflow_focus = build_workflow_focus(eval_report)
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
            package_index=package_index,
            support_request=support_request,
            commercial_dossier=commercial_dossier,
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
        "package_index": package_index,
        "support_request": support_request,
        "commercial_dossier": commercial_dossier,
        "workflow_focus": workflow_focus,
        "gate_summary": gate_summary,
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
    package_index = _mapping(report.get("package_index"))
    support_request = _mapping(report.get("support_request"))
    commercial_dossier = _mapping(report.get("commercial_dossier"))
    gate_summary = _mapping(report.get("gate_summary"))
    workflow_focus = _mapping(report.get("workflow_focus"))
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
        ("Weak routes", str(workflow_focus.get("weak_route_count", 0))),
        ("Coverage gaps", str(workflow_focus.get("coverage_gap_count", 0))),
        ("Fixture depth gaps", str(workflow_focus.get("support_fixture_depth_gap_count", 0))),
        ("Layer coverage", str(len(_mapping(quality.get("expected_layer_counts"))))),
        ("Readiness", str(readiness.get("verdict", "not-run"))),
        ("Publication", str(publication.get("status", "not-run"))),
        ("Package index", str(package_index.get("status", "not-run"))),
        ("Support request", str(support_request.get("status", "not-run"))),
        ("Commercial dossier", str(commercial_dossier.get("status", "not-run"))),
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
    workflow_focus_rows = _workflow_focus_rows(workflow_focus)
    gate_summary_rows = _gate_summary_rows(gate_summary)
    gate_drilldown_rows = _gate_drilldown_rows(gate_summary)
    publication_rows = _publication_rows(publication)
    package_index_rows = _package_index_rows(package_index)
    support_request_rows = _support_request_rows(support_request)
    commercial_dossier_rows = _commercial_dossier_rows(commercial_dossier)

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
        <tr><td>Expected layers</td><td>{escape(", ".join(_mapping(quality.get("expected_layer_counts")).keys()))}</td></tr>
        <tr><td>Expected skills</td><td>{escape(", ".join(_mapping(quality.get("expected_skill_counts")).keys()))}</td></tr>
      </table>
    </section>
    <section class="panel">
      <h2>Workflow focus</h2>
      <table>
        <tr><th>Type</th><th>Item</th><th>Signal</th><th>Action</th></tr>
        {workflow_focus_rows}
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
      <h2>Gate summary</h2>
      <table>
        <tr><th>Gate</th><th>Status</th><th>Summary</th></tr>
        {gate_summary_rows}
      </table>
    </section>
    <section class="panel">
      <h2>Gate details</h2>
      <table>
        <tr><th>Gate</th><th>Item</th><th>Status</th><th>Summary</th></tr>
        {gate_drilldown_rows}
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
      <h2>Package index</h2>
      <table>
        <tr><th>Signal</th><th>Value</th></tr>
        {package_index_rows}
      </table>
    </section>
    <section class="panel">
      <h2>Support request</h2>
      <table>
        <tr><th>Signal</th><th>Value</th></tr>
        {support_request_rows}
      </table>
    </section>
    <section class="panel">
      <h2>Commercial dossier</h2>
      <table>
        <tr><th>Signal</th><th>Value</th></tr>
        {commercial_dossier_rows}
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
    package_index: Mapping[str, Any] | None,
    support_request: Mapping[str, Any] | None,
    commercial_dossier: Mapping[str, Any] | None,
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
    if package_index is not None and package_index.get("status") != "published":
        return "attention"
    if support_request is not None and support_request.get("status") != "ready":
        return "attention"
    if commercial_dossier is not None and commercial_dossier.get("status") != "ready":
        return "attention"
    recent_status_counts = _mapping(evidence.get("recent_status_counts"))
    if int(recent_status_counts.get("fail", 0) or 0) > 0:
        return "attention"
    return "pass"


def pulse_score(
    workflow_eval: Mapping[str, Any],
    readiness: Mapping[str, Any] | None,
    publication: Mapping[str, Any] | None,
    package_index: Mapping[str, Any] | None,
    support_request: Mapping[str, Any] | None,
    commercial_dossier: Mapping[str, Any] | None,
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
    package_index_penalty = 0
    if package_index is not None and package_index.get("status") != "published":
        package_index_penalty = 5
    support_penalty = 0
    if support_request is not None and support_request.get("status") != "ready":
        support_penalty = 5
    commercial_penalty = 0
    if commercial_dossier is not None and commercial_dossier.get("status") != "ready":
        commercial_penalty = 5
    fail_count = int(_mapping(evidence.get("recent_status_counts")).get("fail", 0) or 0)
    evidence_score = max(0, 5 - (fail_count * 2))
    score = round((pass_rate * 65) + (evidence_coverage * 10) + readiness_score + publication_score + evidence_score - support_penalty - commercial_penalty - package_index_penalty)
    return max(0, min(100, int(score)))


def build_gate_summary(
    workflow_eval: Mapping[str, Any],
    readiness: Mapping[str, Any] | None,
    publication: Mapping[str, Any] | None,
    package_index: Mapping[str, Any] | None,
    support_request: Mapping[str, Any] | None,
    commercial_dossier: Mapping[str, Any] | None,
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    gates = [
        _workflow_eval_gate(workflow_eval),
        _readiness_gate(readiness),
        _publication_gate(publication),
        _package_index_gate(package_index),
        _support_request_gate(support_request),
        _commercial_dossier_gate(commercial_dossier),
        _evidence_gate(evidence),
    ]
    counts = {"pass": 0, "attention": 0, "hold": 0, "not-run": 0}
    for gate in gates:
        status = str(gate.get("status", "not-run"))
        counts[status] = counts.get(status, 0) + 1
    drilldown_item_count = sum(len(_list(gate.get("drilldown"))) for gate in gates)
    return {
        "status_counts": counts,
        "drilldown_item_count": drilldown_item_count,
        "gates": gates,
        "next_actions": _gate_next_actions(gates),
    }


def build_workflow_focus(workflow_eval: Mapping[str, Any]) -> dict[str, Any]:
    quality = _mapping(workflow_eval.get("quality"))
    weak_routes = [
        item
        for item in _list(quality.get("weak_routes"))
        if isinstance(item, Mapping)
    ]
    coverage_gaps = _mapping(quality.get("coverage_gaps"))
    support_evidence_contract = _mapping(quality.get("support_evidence_contract_review"))
    support_fixture_depth = _mapping(quality.get("support_fixture_depth_review"))
    missing_layers = _list(coverage_gaps.get("missing_layers"))
    missing_roles = _list(coverage_gaps.get("missing_roles"))
    missing_skills = _list(coverage_gaps.get("missing_skills"))
    coverage_gap_count = len(missing_layers) + len(missing_roles)
    term_gap_count = int(support_evidence_contract.get("term_gap_count", 0) or 0)
    prompt_gap_count = int(support_evidence_contract.get("prompt_gap_count", 0) or 0)
    support_evidence_gap_count = term_gap_count + prompt_gap_count
    support_fixture_depth_gap_count = int(support_fixture_depth.get("depth_gap_count", 0) or 0)
    next_actions: list[dict[str, str]] = []
    if weak_routes:
        next_actions.append(
            {
                "kind": "weak-route",
                "action": "Review low-margin route fixtures and strengthen trigger wording before they regress.",
            }
        )
    if missing_layers:
        next_actions.append(
            {
                "kind": "coverage-gap",
                "action": "Add workflow eval scenarios for missing layers: " + ", ".join(str(item) for item in missing_layers[:5]),
            }
        )
    if missing_roles:
        next_actions.append(
            {
                "kind": "coverage-gap",
                "action": "Add scenarios for uncovered roles, starting with: " + ", ".join(str(item) for item in missing_roles[:5]),
            }
        )
    if support_evidence_gap_count:
        next_actions.append(
            {
                "kind": "support-evidence-contract",
                "action": "Strengthen profiled support-skill scenario prompts and expected_terms so evidence contracts stay explicit.",
            }
        )
    if support_fixture_depth_gap_count:
        next_actions.append(
            {
                "kind": "support-fixture-depth",
                "action": "Broaden profiled support-skill fixtures so each report has enough distinct, evidence-rich cases.",
            }
        )
    return {
        "weak_route_count": len(weak_routes),
        "coverage_gap_count": coverage_gap_count,
        "support_evidence_gap_count": support_evidence_gap_count,
        "support_fixture_depth_gap_count": support_fixture_depth_gap_count,
        "weak_routes": weak_routes[:DRILLDOWN_LIMIT],
        "coverage_gaps": {
            "missing_layers": missing_layers,
            "missing_roles": missing_roles,
            "missing_skills": missing_skills[:DRILLDOWN_LIMIT],
            "covered_skill_count": coverage_gaps.get("covered_skill_count", 0),
            "registry_skill_count": coverage_gaps.get("registry_skill_count", 0),
            "covered_skill_ratio": coverage_gaps.get("covered_skill_ratio", 0.0),
        },
        "support_evidence_contract": {
            "term_gap_count": term_gap_count,
            "prompt_gap_count": prompt_gap_count,
            "term_gaps": _list(support_evidence_contract.get("term_gaps"))[:DRILLDOWN_LIMIT],
            "prompt_gaps": _list(support_evidence_contract.get("prompt_gaps"))[:DRILLDOWN_LIMIT],
        },
        "support_fixture_depth": {
            "depth_gap_count": support_fixture_depth_gap_count,
            "depth_gaps": _list(support_fixture_depth.get("depth_gaps"))[:DRILLDOWN_LIMIT],
            "duplicate_prompt_pair_count": int(support_fixture_depth.get("duplicate_prompt_pair_count", 0) or 0),
            "duplicate_prompt_pairs": _list(support_fixture_depth.get("duplicate_prompt_pairs"))[:DRILLDOWN_LIMIT],
        },
        "next_actions": next_actions,
    }


def _workflow_eval_gate(workflow_eval: Mapping[str, Any]) -> dict[str, Any]:
    scenario_count = int(workflow_eval.get("scenario_count", 0) or 0)
    failed = int(workflow_eval.get("failed", 0) or 0)
    passed = int(workflow_eval.get("passed", max(0, scenario_count - failed)) or 0)
    status = "pass" if workflow_eval.get("status") == "pass" else "hold"
    return {
        "id": "workflow-eval",
        "label": "Workflow eval",
        "status": status,
        "summary": f"{passed}/{scenario_count} scenarios passed",
        "details": {
            "pass_rate": _float(workflow_eval.get("pass_rate")),
            "failed": failed,
        },
        "drilldown": _workflow_eval_drilldown(workflow_eval),
    }


def _readiness_gate(readiness: Mapping[str, Any] | None) -> dict[str, Any]:
    if readiness is None:
        return {
            "id": "readiness",
            "label": "Readiness",
            "status": "not-run",
            "summary": "Readiness check was not included.",
            "details": {},
            "drilldown": [],
        }
    findings = readiness.get("findings", [])
    if readiness.get("status") != "pass":
        status = "hold"
    elif readiness.get("verdict") == "commercial-ready-candidate":
        status = "pass"
    else:
        status = "attention"
    return {
        "id": "readiness",
        "label": "Readiness",
        "status": status,
        "summary": str(readiness.get("verdict", readiness.get("status", "-"))),
        "details": {
            "profile": readiness.get("profile"),
            "findings": len(findings) if isinstance(findings, list) else 0,
        },
        "drilldown": _readiness_drilldown(readiness),
    }


def _publication_gate(publication: Mapping[str, Any] | None) -> dict[str, Any]:
    if publication is None:
        return {
            "id": "publication",
            "label": "Publication",
            "status": "not-run",
            "summary": "Publication status was not included.",
            "details": {},
            "drilldown": [],
        }
    findings = publication.get("findings", [])
    status = "pass" if publication.get("status") == "ready" else "attention"
    return {
        "id": "publication",
        "label": "Publication",
        "status": status,
        "summary": str(publication.get("status", "-")),
        "details": {
            "channel": publication.get("channel"),
            "version": publication.get("version"),
            "findings": len(findings) if isinstance(findings, list) else 0,
        },
        "drilldown": _publication_drilldown(publication),
    }


def _package_index_gate(package_index: Mapping[str, Any] | None) -> dict[str, Any]:
    if package_index is None:
        return {
            "id": "package-index",
            "label": "Package index",
            "status": "not-run",
            "summary": "Package-index metadata check was not included.",
            "details": {},
            "drilldown": [],
        }
    findings = package_index.get("findings", [])
    status = "pass" if package_index.get("status") == "published" else "attention"
    return {
        "id": "package-index",
        "label": "Package index",
        "status": status,
        "summary": str(package_index.get("status", "-")),
        "details": {
            "channel": package_index.get("channel"),
            "target_version": package_index.get("target_version"),
            "latest_version": package_index.get("latest_version"),
            "target_file_count": package_index.get("target_file_count"),
            "findings": len(findings) if isinstance(findings, list) else 0,
        },
        "drilldown": _package_index_drilldown(package_index),
    }


def _support_request_gate(support_request: Mapping[str, Any] | None) -> dict[str, Any]:
    if support_request is None:
        return {
            "id": "support-request",
            "label": "Support request",
            "status": "not-run",
            "summary": "Support request status was not included.",
            "details": {},
            "drilldown": [],
        }
    findings = support_request.get("findings", [])
    status = "pass" if support_request.get("status") == "ready" else "attention"
    return {
        "id": "support-request",
        "label": "Support request",
        "status": status,
        "summary": str(support_request.get("status", "-")),
        "details": {
            "severity": support_request.get("severity"),
            "findings": len(findings) if isinstance(findings, list) else 0,
        },
        "drilldown": _support_request_drilldown(support_request),
    }


def _commercial_dossier_gate(commercial_dossier: Mapping[str, Any] | None) -> dict[str, Any]:
    if commercial_dossier is None:
        return {
            "id": "commercial-dossier",
            "label": "Commercial dossier",
            "status": "not-run",
            "summary": "Commercial dossier was not included.",
            "details": {},
            "drilldown": [],
        }
    findings = commercial_dossier.get("findings", [])
    status = "pass" if commercial_dossier.get("status") == "ready" else "attention"
    return {
        "id": "commercial-dossier",
        "label": "Commercial dossier",
        "status": status,
        "summary": str(commercial_dossier.get("status", "-")),
        "details": {
            "channel": commercial_dossier.get("channel"),
            "findings": len(findings) if isinstance(findings, list) else 0,
        },
        "drilldown": _commercial_dossier_drilldown(commercial_dossier),
    }


def _evidence_gate(evidence: Mapping[str, Any]) -> dict[str, Any]:
    recent_status_counts = _mapping(evidence.get("recent_status_counts"))
    fail_count = int(recent_status_counts.get("fail", 0) or 0)
    total_events = int(evidence.get("total_events", 0) or 0)
    status = "attention" if fail_count > 0 else "pass"
    return {
        "id": "evidence",
        "label": "Evidence ledger",
        "status": status,
        "summary": f"{fail_count} recent failures across {total_events} ledger events",
        "details": {
            "recent_failures": fail_count,
            "total_events": total_events,
        },
        "drilldown": _evidence_drilldown(evidence),
    }


def _gate_next_actions(gates: list[Mapping[str, Any]]) -> list[dict[str, str]]:
    action_by_gate = {
        "workflow-eval": "Fix failing workflow scenarios before trusting the Pulse score.",
        "readiness": "Run or fix readiness check until the enterprise verdict is commercial-ready-candidate.",
        "publication": "Resolve publication findings or generate a fresh publication status before release.",
        "package-index": "Run relay-kit publish index-check and confirm the package index exposes the target version.",
        "support-request": "Complete support request diagnostics and clear support findings before paid handoff.",
        "commercial-dossier": "Complete commercial dossier proof before making a commercial-ready claim.",
        "evidence": "Inspect recent failing evidence events and rerun the affected gate.",
    }
    actions: list[dict[str, str]] = []
    for gate in gates:
        status = str(gate.get("status", "not-run"))
        gate_id = str(gate.get("id", ""))
        if status not in {"attention", "hold"}:
            continue
        actions.append(
            {
                "gate": gate_id,
                "status": status,
                "action": action_by_gate.get(gate_id, "Review this gate before release."),
            }
        )
    return actions


def _workflow_eval_drilldown(workflow_eval: Mapping[str, Any]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for result in _list(workflow_eval.get("results")):
        if not isinstance(result, Mapping) or result.get("passed") is not False:
            continue
        expected = str(result.get("expected_skill", "-"))
        predicted = str(result.get("predicted_skill", "-"))
        items.append(
            {
                "kind": "scenario",
                "id": str(result.get("id", "workflow-scenario")),
                "status": "fail",
                "summary": f"expected {expected}, predicted {predicted}",
            }
        )
    for finding in _list(workflow_eval.get("findings")):
        if not isinstance(finding, Mapping):
            continue
        items.append(
            {
                "kind": "finding",
                "id": str(finding.get("gate", finding.get("id", "workflow-eval"))),
                "status": str(finding.get("status", "attention")),
                "summary": str(finding.get("summary", finding.get("message", "workflow eval finding"))),
            }
        )
    return items[:DRILLDOWN_LIMIT]


def _readiness_drilldown(readiness: Mapping[str, Any]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for gate in _list(readiness.get("gates")):
        if not isinstance(gate, Mapping):
            continue
        status = str(gate.get("status", "unknown"))
        if status == "pass":
            continue
        gate_id = str(gate.get("id", gate.get("gate", "readiness")))
        items.append(
            {
                "kind": "gate",
                "id": gate_id,
                "status": status,
                "summary": str(gate.get("summary", gate_id)),
            }
        )
    items.extend(_finding_drilldown_items(readiness.get("findings"), default_id="readiness"))
    return _dedupe_drilldown(items)[:DRILLDOWN_LIMIT]


def _publication_drilldown(publication: Mapping[str, Any]) -> list[dict[str, str]]:
    items = _finding_drilldown_items(publication.get("findings"), default_id="publication")
    for check in _list(publication.get("checks")):
        if not isinstance(check, Mapping):
            continue
        status = str(check.get("status", "unknown"))
        if status == "pass":
            continue
        check_id = str(check.get("id", check.get("gate", "publication")))
        items.append(
            {
                "kind": "check",
                "id": check_id,
                "status": status,
                "summary": str(check.get("summary", check_id)),
            }
        )
    return _dedupe_drilldown(items)[:DRILLDOWN_LIMIT]


def _package_index_drilldown(package_index: Mapping[str, Any]) -> list[dict[str, str]]:
    items = _finding_drilldown_items(package_index.get("findings"), default_id="package-index")
    for check in _list(package_index.get("checks")):
        if not isinstance(check, Mapping):
            continue
        status = str(check.get("status", "unknown"))
        if status == "pass":
            continue
        check_id = str(check.get("id", check.get("gate", "package-index")))
        items.append(
            {
                "kind": "check",
                "id": check_id,
                "status": status,
                "summary": str(check.get("summary", check_id)),
            }
        )
    return _dedupe_drilldown(items)[:DRILLDOWN_LIMIT]


def _support_request_drilldown(support_request: Mapping[str, Any]) -> list[dict[str, str]]:
    items = _finding_drilldown_items(support_request.get("findings"), default_id="support-request")
    for diagnostic in _list(support_request.get("diagnostics")):
        if not isinstance(diagnostic, Mapping):
            continue
        status = str(diagnostic.get("status", "unknown"))
        if status == "present":
            continue
        path = str(diagnostic.get("path", "diagnostic"))
        items.append(
            {
                "kind": "diagnostic",
                "id": path,
                "status": status,
                "summary": path,
            }
        )
    return _dedupe_drilldown(items)[:DRILLDOWN_LIMIT]


def _commercial_dossier_drilldown(commercial_dossier: Mapping[str, Any]) -> list[dict[str, str]]:
    items = _finding_drilldown_items(commercial_dossier.get("findings"), default_id="commercial-dossier")
    for check in _list(commercial_dossier.get("checks")):
        if not isinstance(check, Mapping):
            continue
        status = str(check.get("status", "unknown"))
        if status == "pass":
            continue
        check_id = str(check.get("id", check.get("gate", "commercial-dossier")))
        items.append(
            {
                "kind": "check",
                "id": check_id,
                "status": status,
                "summary": str(check.get("summary", check_id)),
            }
        )
    return _dedupe_drilldown(items)[:DRILLDOWN_LIMIT]


def _evidence_drilldown(evidence: Mapping[str, Any]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for event in _list(evidence.get("recent_events")):
        if not isinstance(event, Mapping) or str(event.get("status", "")).lower() != "fail":
            continue
        gate = str(event.get("gate", event.get("command", "evidence")))
        findings_count = event.get("findings_count", "-")
        items.append(
            {
                "kind": "event",
                "id": gate,
                "status": "fail",
                "summary": f"recent failure, findings: {findings_count}",
            }
        )
    return items[-DRILLDOWN_LIMIT:]


def _finding_drilldown_items(value: Any, *, default_id: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for finding in _list(value):
        if not isinstance(finding, Mapping):
            continue
        finding_id = str(finding.get("gate", finding.get("id", default_id)))
        items.append(
            {
                "kind": "finding",
                "id": finding_id,
                "status": str(finding.get("status", "attention")),
                "summary": str(finding.get("summary", finding.get("message", finding_id))),
            }
        )
    return items


def _dedupe_drilldown(items: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[tuple[str, str]] = set()
    deduped: list[dict[str, str]] = []
    for item in items:
        key = (item.get("id", ""), item.get("summary", ""))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


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
    package_index = _mapping(report.get("package_index"))
    support_request = _mapping(report.get("support_request"))
    commercial_dossier = _mapping(report.get("commercial_dossier"))
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
            package_index=package_index if package_index else None,
            support_request=support_request if support_request else None,
            commercial_dossier=commercial_dossier if commercial_dossier else None,
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
    package_index: Mapping[str, Any] | None,
    support_request: Mapping[str, Any] | None,
    commercial_dossier: Mapping[str, Any] | None,
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
        "package_index_status": package_index.get("status") if package_index else None,
        "package_index_latest_version": package_index.get("latest_version") if package_index else None,
        "package_index_target_version": package_index.get("target_version") if package_index else None,
        "package_index_findings": len(package_index.get("findings", [])) if package_index else None,
        "support_request_status": support_request.get("status") if support_request else None,
        "support_request_severity": support_request.get("severity") if support_request else None,
        "support_request_findings": len(support_request.get("findings", [])) if support_request else None,
        "commercial_dossier_status": commercial_dossier.get("status") if commercial_dossier else None,
        "commercial_dossier_channel": commercial_dossier.get("channel") if commercial_dossier else None,
        "commercial_dossier_findings": len(commercial_dossier.get("findings", [])) if commercial_dossier else None,
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


def _load_or_build_package_index(
    root: Path,
    *,
    include_package_index: bool,
    package_index_file: Path | str | None,
    package_index_builder: PackageIndexBuilder | None,
) -> Mapping[str, Any] | None:
    if package_index_file is not None:
        return _read_json(root, package_index_file)
    if not include_package_index:
        return None
    builder = package_index_builder or (lambda project_root: _read_json(project_root, DEFAULT_INDEX_CHECK_OUTPUT))
    return builder(root)


def _load_or_build_support_request(
    root: Path,
    *,
    include_support_request: bool,
    support_request_file: Path | str | None,
    support_request_builder: SupportRequestBuilder | None,
) -> Mapping[str, Any] | None:
    if support_request_file is not None:
        return _read_json(root, support_request_file)
    if not include_support_request:
        return None
    builder = support_request_builder or (lambda project_root: _read_json(project_root, DEFAULT_SUPPORT_REQUEST_OUTPUT))
    return builder(root)


def _load_or_build_commercial_dossier(
    root: Path,
    *,
    include_commercial_dossier: bool,
    commercial_dossier_file: Path | str | None,
    commercial_dossier_builder: CommercialDossierBuilder | None,
) -> Mapping[str, Any] | None:
    if commercial_dossier_file is not None:
        return _read_json(root, commercial_dossier_file)
    if not include_commercial_dossier:
        return None
    builder = commercial_dossier_builder or (lambda project_root: _read_json(project_root, DEFAULT_COMMERCIAL_DOSSIER_OUTPUT))
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


def _gate_summary_rows(gate_summary: Mapping[str, Any]) -> str:
    gates = gate_summary.get("gates", [])
    if not isinstance(gates, list) or not gates:
        return '<tr><td colspan="3">No gate summary available.</td></tr>'
    rows = []
    for gate in gates:
        if not isinstance(gate, Mapping):
            continue
        rows.append(
            "<tr>"
            f"<td>{escape(str(gate.get('label', gate.get('id', '-'))))}</td>"
            f"<td>{escape(str(gate.get('status', '-')))}</td>"
            f"<td>{escape(str(gate.get('summary', '-')))}</td>"
            "</tr>"
        )
    if not rows:
        return '<tr><td colspan="3">No gate summary available.</td></tr>'
    return "\n".join(rows)


def _workflow_focus_rows(workflow_focus: Mapping[str, Any]) -> str:
    rows: list[str] = []
    for route in _list(workflow_focus.get("weak_routes")):
        if not isinstance(route, Mapping):
            continue
        route_id = str(route.get("id", "weak-route"))
        signal = f"margin {route.get('route_margin', '-')}, confidence {route.get('route_confidence', '-')}"
        action = f"expected {route.get('expected_skill', '-')}, predicted {route.get('predicted_skill', '-')}"
        rows.append(
            "<tr>"
            "<td>Weak route</td>"
            f"<td>{escape(route_id)}</td>"
            f"<td>{escape(signal)}</td>"
            f"<td>{escape(action)}</td>"
            "</tr>"
        )
    gaps = _mapping(workflow_focus.get("coverage_gaps"))
    missing_layers = [str(item) for item in _list(gaps.get("missing_layers"))]
    missing_roles = [str(item) for item in _list(gaps.get("missing_roles"))]
    if missing_layers:
        rows.append(
            "<tr>"
            "<td>Coverage gap</td>"
            "<td>Layers</td>"
            f"<td>{escape(str(len(missing_layers)))}</td>"
            f"<td>{escape(', '.join(missing_layers[:6]))}</td>"
            "</tr>"
        )
    if missing_roles:
        rows.append(
            "<tr>"
            "<td>Coverage gap</td>"
            "<td>Roles</td>"
            f"<td>{escape(str(len(missing_roles)))}</td>"
            f"<td>{escape(', '.join(missing_roles[:6]))}</td>"
            "</tr>"
        )
    support_fixture_depth = _mapping(workflow_focus.get("support_fixture_depth"))
    depth_gaps = _list(support_fixture_depth.get("depth_gaps"))
    for gap in depth_gaps[:DRILLDOWN_LIMIT]:
        if not isinstance(gap, Mapping):
            continue
        item = str(gap.get("id") or gap.get("expected_skill") or gap.get("check", "support-fixture-depth"))
        signal = str(gap.get("check", "support-fixture-depth"))
        action = str(gap.get("detail", "Broaden profiled support fixture coverage."))
        rows.append(
            "<tr>"
            "<td>Fixture depth</td>"
            f"<td>{escape(item)}</td>"
            f"<td>{escape(signal)}</td>"
            f"<td>{escape(action)}</td>"
            "</tr>"
        )
    for action in _list(workflow_focus.get("next_actions")):
        if not isinstance(action, Mapping):
            continue
        rows.append(
            "<tr>"
            "<td>Next action</td>"
            f"<td>{escape(str(action.get('kind', '-')))}</td>"
            "<td>-</td>"
            f"<td>{escape(str(action.get('action', '-')))}</td>"
            "</tr>"
        )
    if not rows:
        return '<tr><td colspan="4">No workflow focus items.</td></tr>'
    return "\n".join(rows)


def _gate_drilldown_rows(gate_summary: Mapping[str, Any]) -> str:
    gates = gate_summary.get("gates", [])
    if not isinstance(gates, list) or not gates:
        return '<tr><td colspan="4">No gate details available.</td></tr>'
    rows = []
    for gate in gates:
        if not isinstance(gate, Mapping):
            continue
        gate_label = str(gate.get("label", gate.get("id", "-")))
        for item in _list(gate.get("drilldown")):
            if not isinstance(item, Mapping):
                continue
            rows.append(
                "<tr>"
                f"<td>{escape(gate_label)}</td>"
                f"<td>{escape(str(item.get('id', item.get('kind', '-'))))}</td>"
                f"<td>{escape(str(item.get('status', '-')))}</td>"
                f"<td>{escape(str(item.get('summary', '-')))}</td>"
                "</tr>"
            )
    if not rows:
        return '<tr><td colspan="4">No degraded gate details.</td></tr>'
    return "\n".join(rows)


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


def _package_index_rows(package_index: Mapping[str, Any]) -> str:
    if not package_index:
        rows = [("Status", "not-run")]
    else:
        findings = package_index.get("findings", [])
        rows = [
            ("Status", str(package_index.get("status", "-"))),
            ("Channel", str(package_index.get("channel", "-"))),
            ("Target version", str(package_index.get("target_version", "-"))),
            ("Latest version", str(package_index.get("latest_version", "-"))),
            ("Release files", str(package_index.get("target_file_count", "-"))),
            ("Findings", str(len(findings) if isinstance(findings, list) else 0)),
        ]
    return "\n".join(
        f"<tr><td>{escape(label)}</td><td>{escape(value)}</td></tr>"
        for label, value in rows
    )


def _support_request_rows(support_request: Mapping[str, Any]) -> str:
    if not support_request:
        rows = [("Status", "not-run")]
    else:
        findings = support_request.get("findings", [])
        diagnostics = support_request.get("diagnostics", [])
        rows = [
            ("Status", str(support_request.get("status", "-"))),
            ("Severity", str(support_request.get("severity", "-"))),
            ("Diagnostics", str(len(diagnostics) if isinstance(diagnostics, list) else 0)),
            ("Findings", str(len(findings) if isinstance(findings, list) else 0)),
        ]
    return "\n".join(
        f"<tr><td>{escape(label)}</td><td>{escape(value)}</td></tr>"
        for label, value in rows
    )


def _commercial_dossier_rows(commercial_dossier: Mapping[str, Any]) -> str:
    if not commercial_dossier:
        rows = [("Status", "not-run")]
    else:
        findings = commercial_dossier.get("findings", [])
        external_proof = _mapping(commercial_dossier.get("external_proof"))
        present_external = sum(1 for value in external_proof.values() if str(value or "").strip())
        rows = [
            ("Status", str(commercial_dossier.get("status", "-"))),
            ("Channel", str(commercial_dossier.get("channel", "-"))),
            ("External proof fields", str(present_external)),
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


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
