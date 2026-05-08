"""Commercial proof dossier for Relay-kit paid readiness."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Mapping

from relay_kit_v3.publication import build_package_index_check, build_publication_trail_status
from relay_kit_v3.readiness import build_readiness_report
from relay_kit_v3.support_triage import build_support_soak_report, build_support_triage


SCHEMA_VERSION = "relay-kit.commercial-dossier.v1"
DEFAULT_OUTPUT = Path(".relay-kit") / "commercial" / "commercial-dossier.json"
CHANNELS = {"pypi", "testpypi", "internal"}
PLACEHOLDER_VALUES = {"", "tbd", "todo", "n/a", "none", "owner", "unknown"}

ReadinessBuilder = Callable[[Path, str, bool], Mapping[str, Any]]
PublicationStatusBuilder = Callable[[Path, str | None], Mapping[str, Any]]
PackageIndexBuilder = Callable[[Path, str, str | None], Mapping[str, Any]]
SupportTriageBuilder = Callable[[Path, str | None, str | None], Mapping[str, Any]]
SupportSoakBuilder = Callable[[Path, str | None], Mapping[str, Any]]


def build_commercial_dossier(
    project_root: Path | str,
    *,
    channel: str = "pypi",
    ci_url: str | None = None,
    release_url: str | None = None,
    package_url: str | None = None,
    sla_url: str | None = None,
    support_url: str | None = None,
    legal_owner: str | None = None,
    support_owner: str | None = None,
    readiness_profile: str = "enterprise",
    skip_readiness_tests: bool = False,
    publication_trail_file: Path | str | None = None,
    support_request_file: Path | str | None = None,
    support_bundle_file: Path | str | None = None,
    readiness_builder: ReadinessBuilder | None = None,
    publication_status_builder: PublicationStatusBuilder | None = None,
    package_index_builder: PackageIndexBuilder | None = None,
    support_triage_builder: SupportTriageBuilder | None = None,
    support_soak_builder: SupportSoakBuilder | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    selected_channel = channel.lower()
    trail_file_text = str(publication_trail_file) if publication_trail_file is not None else None
    request_file_text = str(support_request_file) if support_request_file is not None else None
    bundle_file_text = str(support_bundle_file) if support_bundle_file is not None else None

    readiness = _call_readiness_builder(
        root,
        readiness_profile,
        skip_readiness_tests,
        readiness_builder or _default_readiness_builder,
    )
    publication_status = _call_publication_builder(
        root,
        trail_file_text,
        publication_status_builder or _default_publication_status_builder,
    )
    package_index = _call_package_index_builder(
        root,
        selected_channel,
        package_url,
        package_index_builder or _default_package_index_builder,
    )
    support_triage = _call_support_triage_builder(
        root,
        request_file_text,
        bundle_file_text,
        support_triage_builder or _default_support_triage_builder,
    )
    support_soak = _call_support_soak_builder(
        root,
        bundle_file_text,
        support_soak_builder or _default_support_soak_builder,
    )

    checks = [
        channel_check(selected_channel),
        url_check("external-ci", "external CI", ci_url),
        url_check("release-url", "release evidence", release_url, required=selected_channel == "pypi"),
        url_check("package-url", "package index", package_url),
        url_check("sla-url", "SLA policy", sla_url),
        url_check("support-url", "support intake", support_url),
        owner_check("legal-owner", "legal owner", legal_owner),
        owner_check("support-owner", "support owner", support_owner),
        readiness_check(readiness),
        publication_status_check(publication_status),
        package_index_check(package_index, required=selected_channel in {"pypi", "testpypi"}),
        support_triage_check(support_triage),
        support_soak_check(support_soak),
    ]
    findings = [
        {
            "gate": str(check["id"]),
            "status": str(check["status"]),
            "summary": str(check["summary"]),
        }
        for check in checks
        if check["status"] != "pass"
    ]
    status = "ready" if not findings else "hold"
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "project_path": str(root),
        "channel": selected_channel,
        "readiness_profile": readiness_profile,
        "external_proof": {
            "ci_url": ci_url,
            "release_url": release_url,
            "package_url": package_url,
            "sla_url": sla_url,
            "support_url": support_url,
            "legal_owner": _clean(legal_owner),
            "support_owner": _clean(support_owner),
        },
        "local_reports": {
            "readiness": compact_report(readiness, keys=("schema_version", "status", "verdict", "profile")),
            "publication_status": compact_report(publication_status, keys=("schema_version", "status", "summary", "trail_file")),
            "package_index": compact_report(package_index, keys=("schema_version", "status", "target_version", "latest_version", "index_url")),
            "support_triage": compact_report(support_triage, keys=("schema_version", "status", "severity", "request_file", "bundle_file")),
            "support_soak": compact_report(support_soak, keys=("schema_version", "status", "case_count", "bundle_file")),
        },
        "checks": checks,
        "checks_by_id": {str(check["id"]): check for check in checks},
        "findings": findings,
        "next_actions": next_actions(checks),
        "residual_risks": [
            "External URLs are evidence pointers; this command does not authenticate remote systems.",
            "Legal SLA commitments, package-index ownership, and customer support staffing remain external operational controls.",
        ],
    }


def write_commercial_dossier(
    project_root: Path | str,
    report: Mapping[str, Any],
    *,
    output_file: Path | str | None = None,
) -> Path:
    root = Path(project_root).resolve()
    output_path = Path(output_file) if output_file is not None else root / DEFAULT_OUTPUT
    if not output_path.is_absolute():
        output_path = root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return output_path


def render_commercial_dossier(report: Mapping[str, Any]) -> str:
    lines = [
        "Relay-kit commercial dossier",
        f"- project: {report.get('project_path')}",
        f"- channel: {report.get('channel')}",
        f"- status: {report.get('status')}",
        f"- findings: {len(report.get('findings', []))}",
    ]
    checks = report.get("checks", [])
    if checks:
        lines.append("- gate results:")
        for check in checks:
            if isinstance(check, Mapping):
                lines.append(f"  - {check.get('label', check.get('id'))}: {check.get('status')}")
                if check.get("summary") and check.get("status") != "pass":
                    lines.append(f"    {check['summary']}")
    actions = report.get("next_actions", [])
    if actions:
        lines.append("- next actions:")
        lines.extend(f"  - {action}" for action in actions)
    return "\n".join(lines)


def channel_check(channel: str) -> dict[str, Any]:
    return check(
        "channel",
        "publication channel",
        "pass" if channel in CHANNELS else "hold",
        "publication channel is supported" if channel in CHANNELS else f"unsupported channel: {channel}",
        details={"channel": channel, "supported": sorted(CHANNELS)},
    )


def url_check(check_id: str, label: str, value: str | None, *, required: bool = True) -> dict[str, Any]:
    text = _clean(value)
    if not text:
        status = "hold" if required else "pass"
        summary = f"missing {label} URL" if required else f"{label} URL is optional for this channel"
        return check(check_id, label, status, summary, details={"url": text, "required": required})
    if not _looks_like_url(text):
        return check(check_id, label, "hold", f"invalid {label} URL", details={"url": text, "required": required})
    return check(check_id, label, "pass", f"{label} URL recorded", details={"url": text, "required": required})


def owner_check(check_id: str, label: str, value: str | None) -> dict[str, Any]:
    text = _clean(value)
    status = "pass" if text.lower() not in PLACEHOLDER_VALUES else "hold"
    return check(
        check_id,
        label,
        status,
        f"{label} recorded" if status == "pass" else f"missing {label}",
        details={"owner": text},
    )


def readiness_check(report: Mapping[str, Any]) -> dict[str, Any]:
    status = str(report.get("status") or "")
    verdict = str(report.get("verdict") or "")
    passed = status == "pass" and verdict == "commercial-ready-candidate"
    summary = f"readiness status={status or 'unknown'}, verdict={verdict or 'unknown'}"
    return check(
        "readiness",
        "readiness gate",
        "pass" if passed else "hold",
        summary if not passed else "commercial-ready candidate verified",
        details={"status": status, "verdict": verdict, "findings_count": _findings_count(report)},
    )


def publication_status_check(report: Mapping[str, Any]) -> dict[str, Any]:
    status = str(report.get("status") or "")
    passed = status == "complete"
    summary = f"publication trail status={status or 'unknown'}"
    return check(
        "publication-status",
        "publication trail status",
        "pass" if passed else "hold",
        summary if not passed else "publication trail is complete",
        details={"status": status, "findings_count": _findings_count(report), "summary": report.get("summary", {})},
    )


def package_index_check(report: Mapping[str, Any], *, required: bool) -> dict[str, Any]:
    status = str(report.get("status") or "")
    if not required:
        return check(
            "package-index",
            "package index metadata",
            "pass",
            "package index metadata check is optional for this channel",
            details={"status": status, "required": required},
        )
    passed = status == "published"
    summary = f"package index status={status or 'unknown'}"
    return check(
        "package-index",
        "package index metadata",
        "pass" if passed else "hold",
        summary if not passed else "package index target version is published",
        details={
            "status": status,
            "target_version": report.get("target_version"),
            "latest_version": report.get("latest_version"),
            "target_file_count": report.get("target_file_count"),
            "findings_count": _findings_count(report),
        },
    )


def support_triage_check(report: Mapping[str, Any]) -> dict[str, Any]:
    status = str(report.get("status") or "")
    passed = status == "ready"
    summary = f"support triage status={status or 'unknown'}"
    return check(
        "support-triage",
        "support triage",
        "pass" if passed else "hold",
        summary if not passed else "support triage is ready",
        details={"status": status, "severity": report.get("severity"), "findings_count": _findings_count(report)},
    )


def support_soak_check(report: Mapping[str, Any]) -> dict[str, Any]:
    status = str(report.get("status") or "")
    passed = status == "pass"
    summary = f"support soak status={status or 'unknown'}"
    return check(
        "support-soak",
        "support soak",
        "pass" if passed else "hold",
        summary if not passed else "support soak passed",
        details={"status": status, "case_count": report.get("case_count"), "findings_count": _findings_count(report)},
    )


def check(
    check_id: str,
    label: str,
    status: str,
    summary: str,
    *,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": check_id,
        "label": label,
        "status": status,
        "summary": summary,
        "details": dict(details or {}),
    }


def compact_report(report: Mapping[str, Any], *, keys: tuple[str, ...]) -> dict[str, Any]:
    payload = {key: report.get(key) for key in keys if key in report}
    payload["findings_count"] = _findings_count(report)
    if report.get("error"):
        payload["error"] = report.get("error")
    return payload


def next_actions(checks: list[Mapping[str, Any]]) -> list[str]:
    if all(check.get("status") == "pass" for check in checks):
        return ["Attach the dossier JSON to the commercial release handoff and keep referenced external proof URLs immutable."]
    action_by_gate = {
        "channel": "Select one supported publication channel: pypi, testpypi, or internal.",
        "external-ci": "Attach green remote CI URL with the release or candidate commit.",
        "release-url": "Attach the release page or release-note URL for the published version.",
        "package-url": "Attach the package-index URL or internal registry URL for the published artifact.",
        "sla-url": "Attach the approved SLA/support policy URL.",
        "support-url": "Attach the paid-support intake or escalation workflow URL.",
        "legal-owner": "Record the owner who approved the SLA/legal support commitments.",
        "support-owner": "Record the support owner accountable for triage targets.",
        "readiness": "Run relay-kit readiness check with tests enabled until it returns commercial-ready-candidate.",
        "publication-status": "Complete relay-kit publish trail/status with local dist, twine, upload, and evidence files.",
        "package-index": "Run relay-kit publish index-check until the package index confirms the target version is published and latest.",
        "support-triage": "Run relay-kit support request, support bundle, and support triage until triage is ready.",
        "support-soak": "Run relay-kit support soak with a healthy support bundle until P0/P1/P2 fixtures pass.",
    }
    return [action_by_gate[str(check["id"])] for check in checks if check.get("status") != "pass"]


def _default_readiness_builder(root: Path, profile: str, skip_tests: bool) -> Mapping[str, Any]:
    return build_readiness_report(root, profile=profile, skip_tests=skip_tests)


def _default_publication_status_builder(root: Path, trail_file: str | None) -> Mapping[str, Any]:
    return build_publication_trail_status(root, trail_file=trail_file)


def _default_package_index_builder(root: Path, channel: str, package_url: str | None) -> Mapping[str, Any]:
    if channel not in {"pypi", "testpypi"}:
        return {"schema_version": "relay-kit.package-index-check.v1", "status": "not-required", "findings": []}
    return build_package_index_check(root, channel=channel, package_url=package_url)


def _default_support_triage_builder(root: Path, request_file: str | None, bundle_file: str | None) -> Mapping[str, Any]:
    return build_support_triage(root, request_file=request_file, bundle_file=bundle_file)


def _default_support_soak_builder(root: Path, bundle_file: str | None) -> Mapping[str, Any]:
    return build_support_soak_report(root, bundle_file=bundle_file)


def _call_readiness_builder(root: Path, profile: str, skip_tests: bool, builder: ReadinessBuilder) -> Mapping[str, Any]:
    try:
        return builder(root, profile, skip_tests)
    except Exception as exc:  # pragma: no cover - defensive gate payload
        return {"schema_version": "relay-kit.readiness-report.v1", "status": "error", "verdict": "hold", "error": str(exc), "findings": [str(exc)]}


def _call_publication_builder(root: Path, trail_file: str | None, builder: PublicationStatusBuilder) -> Mapping[str, Any]:
    try:
        return builder(root, trail_file)
    except Exception as exc:  # pragma: no cover - defensive gate payload
        return {"schema_version": "relay-kit.publication-trail-status.v1", "status": "error", "error": str(exc), "findings": [str(exc)]}


def _call_package_index_builder(root: Path, channel: str, package_url: str | None, builder: PackageIndexBuilder) -> Mapping[str, Any]:
    try:
        return builder(root, channel, package_url)
    except Exception as exc:  # pragma: no cover - defensive gate payload
        return {"schema_version": "relay-kit.package-index-check.v1", "status": "error", "error": str(exc), "findings": [str(exc)]}


def _call_support_triage_builder(
    root: Path,
    request_file: str | None,
    bundle_file: str | None,
    builder: SupportTriageBuilder,
) -> Mapping[str, Any]:
    try:
        return builder(root, request_file, bundle_file)
    except Exception as exc:  # pragma: no cover - defensive gate payload
        return {"schema_version": "relay-kit.support-triage.v1", "status": "error", "error": str(exc), "findings": [str(exc)]}


def _call_support_soak_builder(root: Path, bundle_file: str | None, builder: SupportSoakBuilder) -> Mapping[str, Any]:
    try:
        return builder(root, bundle_file)
    except Exception as exc:  # pragma: no cover - defensive gate payload
        return {"schema_version": "relay-kit.support-soak.v1", "status": "error", "error": str(exc), "findings": [str(exc)]}


def _findings_count(report: Mapping[str, Any]) -> int:
    findings = report.get("findings", [])
    return len(findings) if isinstance(findings, list) else 0


def _looks_like_url(value: str) -> bool:
    lowered = value.lower()
    return lowered.startswith("https://") or lowered.startswith("http://")


def _clean(value: object) -> str:
    return str(value or "").strip()
