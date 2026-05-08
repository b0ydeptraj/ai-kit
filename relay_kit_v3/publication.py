"""Publication planning checks for Relay-kit package releases."""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Mapping

from relay_kit_v3.release_lane import build_release_lane_report

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    tomllib = None  # type: ignore[assignment]


SCHEMA_VERSION = "relay-kit.publication-plan.v1"
EVIDENCE_SCHEMA_VERSION = "relay-kit.publication-evidence.v1"
TRAIL_SCHEMA_VERSION = "relay-kit.publication-trail.v1"
TRAIL_STATUS_SCHEMA_VERSION = "relay-kit.publication-trail-status.v1"
INDEX_CHECK_SCHEMA_VERSION = "relay-kit.package-index-check.v1"
CHANNELS = {"pypi", "testpypi", "internal"}
SHELLS = {"powershell", "bash"}
DEFAULT_OUTPUT = Path(".relay-kit") / "release" / "publication-plan.json"
DEFAULT_EVIDENCE_OUTPUT = Path(".relay-kit") / "release" / "publication-evidence.json"
DEFAULT_TRAIL_OUTPUT = Path(".relay-kit") / "release" / "publication-trail.json"
DEFAULT_TRAIL_MARKDOWN = Path(".relay-kit") / "release" / "publication-trail.md"
DEFAULT_INDEX_CHECK_OUTPUT = Path(".relay-kit") / "release" / "package-index-check.json"
PackageIndexFetcher = Callable[[str, float], tuple[int, Mapping[str, Any]]]


def build_publication_plan(
    project_root: Path | str,
    *,
    channel: str = "pypi",
    target_version: str | None = None,
    dist_dir: Path | str | None = None,
    ci_url: str | None = None,
    release_url: str | None = None,
    package_url: str | None = None,
    allow_dev: bool = False,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    selected_channel = channel.lower()
    package = read_package_metadata(root)
    version = str(package.get("version") or "")
    name = str(package.get("name") or "")
    dist_root = _resolve_dist_dir(root, dist_dir)

    checks = [
        package_metadata_check(package),
        version_channel_check(version, selected_channel, target_version=target_version, allow_dev=allow_dev),
        release_lane_check(root),
        distribution_artifacts_check(dist_root, name=name, version=version),
        external_evidence_check(selected_channel, ci_url=ci_url, release_url=release_url, package_url=package_url),
    ]
    findings = [
        {
            "gate": check["id"],
            "status": check["status"],
            "summary": check.get("summary", ""),
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
        "package_name": name,
        "version": version,
        "dist_dir": str(dist_root),
        "checks": checks,
        "findings": findings,
        "next_commands": publication_commands(root, selected_channel),
        "residual_risks": [
            "This plan does not upload packages or verify package-index ownership.",
            "External URLs are evidence pointers and are not fetched by this local command.",
        ],
    }


def write_publication_plan(
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


def build_publication_evidence(
    project_root: Path | str,
    *,
    channel: str = "pypi",
    dist_dir: Path | str | None = None,
    ci_url: str | None = None,
    release_url: str | None = None,
    package_url: str | None = None,
    twine_check_file: Path | str | None = None,
    upload_log_file: Path | str | None = None,
    publication_plan_file: Path | str | None = None,
    allow_dev: bool = False,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    selected_channel = channel.lower()
    package = read_package_metadata(root)
    version = str(package.get("version") or "")
    name = str(package.get("name") or "")
    dist_root = _resolve_dist_dir(root, dist_dir)
    twine_path = _resolve_optional_path(root, twine_check_file)
    upload_path = _resolve_optional_path(root, upload_log_file)
    plan_path = _resolve_optional_path(root, publication_plan_file)

    checks = [
        package_metadata_check(package),
        version_channel_check(version, selected_channel, target_version=None, allow_dev=allow_dev),
        release_lane_check(root),
        distribution_artifacts_check(dist_root, name=name, version=version),
        external_evidence_check(selected_channel, ci_url=ci_url, release_url=release_url, package_url=package_url),
        text_evidence_file_check(
            "twine-check",
            "twine check",
            twine_path,
            required_text="passed",
            failure_tokens=("failed", "error"),
        ),
        text_evidence_file_check(
            "upload-log",
            "upload log",
            upload_path,
            required_text=None,
            failure_tokens=("failed", "error", "traceback"),
        ),
    ]
    if plan_path is not None:
        checks.append(publication_plan_file_check(plan_path))

    findings = [
        {
            "gate": check["id"],
            "status": check["status"],
            "summary": check.get("summary", ""),
        }
        for check in checks
        if check["status"] != "pass"
    ]
    artifacts = distribution_artifacts(dist_root, name=name, version=version)
    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "status": "published" if not findings else "hold",
        "project_path": str(root),
        "channel": selected_channel,
        "package_name": name,
        "version": version,
        "dist_dir": str(dist_root),
        "external_evidence": {
            "ci_url": ci_url,
            "release_url": release_url,
            "package_url": package_url,
        },
        "evidence_files": {
            "twine_check_file": str(twine_path) if twine_path is not None else None,
            "upload_log_file": str(upload_path) if upload_path is not None else None,
            "publication_plan_file": str(plan_path) if plan_path is not None else None,
        },
        "distribution": {
            "artifact_count": len(artifacts),
            "artifacts": artifacts,
        },
        "checks": checks,
        "checks_by_id": {str(check["id"]): check for check in checks},
        "findings": findings,
        "residual_risks": [
            "External URLs are evidence pointers and are not fetched by this local command.",
            "Package-index ownership and account controls remain external operational controls.",
        ],
    }


def write_publication_evidence(
    project_root: Path | str,
    report: Mapping[str, Any],
    *,
    output_file: Path | str | None = None,
) -> Path:
    root = Path(project_root).resolve()
    output_path = Path(output_file) if output_file is not None else root / DEFAULT_EVIDENCE_OUTPUT
    if not output_path.is_absolute():
        output_path = root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return output_path


def build_publication_trail(
    project_root: Path | str,
    *,
    channel: str = "pypi",
    target_version: str | None = None,
    dist_dir: Path | str | None = None,
    evidence_dir: Path | str | None = None,
    ci_url: str | None = None,
    release_url: str | None = None,
    package_url: str | None = None,
    shell: str = "powershell",
    allow_dev: bool = False,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    selected_channel = channel.lower()
    selected_shell = shell.lower()
    package = read_package_metadata(root)
    version = str(package.get("version") or "")
    name = str(package.get("name") or "")
    dist_root = _resolve_dist_dir(root, dist_dir)
    evidence_root = _resolve_evidence_dir(root, evidence_dir, version=target_version or version)
    twine_check = evidence_root / "twine-check.txt"
    upload_log = evidence_root / "upload-log.txt"
    plan_file = root / DEFAULT_OUTPUT
    evidence_file = root / DEFAULT_EVIDENCE_OUTPUT

    checks = [
        package_metadata_check(package),
        version_channel_check(version, selected_channel, target_version=target_version, allow_dev=allow_dev),
        release_lane_check(root),
        external_evidence_check(selected_channel, ci_url=ci_url, release_url=release_url, package_url=package_url),
        shell_check(selected_shell),
    ]
    findings = [
        {
            "gate": check["id"],
            "status": check["status"],
            "summary": check.get("summary", ""),
        }
        for check in checks
        if check["status"] != "pass"
    ]
    return {
        "schema_version": TRAIL_SCHEMA_VERSION,
        "status": "ready" if not findings else "hold",
        "project_path": str(root),
        "channel": selected_channel,
        "shell": selected_shell,
        "package_name": name,
        "version": version,
        "dist_dir": str(dist_root),
        "evidence_dir": str(evidence_root),
        "external_evidence": {
            "ci_url": ci_url,
            "release_url": release_url,
            "package_url": package_url,
        },
        "evidence_paths": {
            "publication_plan_file": str(plan_file),
            "twine_check_file": str(twine_check),
            "upload_log_file": str(upload_log),
            "publication_evidence_file": str(evidence_file),
        },
        "checks": checks,
        "findings": findings,
        "steps": publication_trail_steps(
            root,
            selected_channel,
            selected_shell,
            dist_root=dist_root,
            twine_check_file=twine_check,
            upload_log_file=upload_log,
            publication_plan_file=plan_file,
            publication_evidence_file=evidence_file,
            ci_url=ci_url,
            release_url=release_url,
            package_url=package_url,
            allow_dev=allow_dev,
        ),
        "residual_risks": [
            "Trail commands are local instructions; they do not verify package-index account ownership.",
            "Upload commands should be run only after the plan step returns ready.",
        ],
    }


def build_publication_trail_status(
    project_root: Path | str,
    *,
    trail_file: Path | str | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    path = _resolve_optional_path(root, trail_file) if trail_file is not None else root / DEFAULT_TRAIL_OUTPUT

    trail = read_json_object(path)
    if trail is None:
        return {
            "schema_version": TRAIL_STATUS_SCHEMA_VERSION,
            "status": "hold",
            "project_path": str(root),
            "trail_file": str(path),
            "summary": {"complete": 0, "pending": 0, "not_observable": 0, "failed": 1, "total": 1},
            "steps": [
                {
                    "id": "publication-trail",
                    "label": "Publication trail",
                    "status": "fail",
                    "summary": f"publication trail file is missing or invalid: {path}",
                }
            ],
            "findings": [
                {
                    "gate": "publication-trail",
                    "status": "fail",
                    "summary": f"publication trail file is missing or invalid: {path}",
                }
            ],
        }

    if trail.get("schema_version") != TRAIL_SCHEMA_VERSION:
        return {
            "schema_version": TRAIL_STATUS_SCHEMA_VERSION,
            "status": "hold",
            "project_path": str(root),
            "trail_file": str(path),
            "summary": {"complete": 0, "pending": 0, "not_observable": 0, "failed": 1, "total": 1},
            "steps": [
                {
                    "id": "publication-trail",
                    "label": "Publication trail",
                    "status": "fail",
                    "summary": "publication trail schema does not match",
                }
            ],
            "findings": [
                {
                    "gate": "publication-trail",
                    "status": "fail",
                    "summary": "publication trail schema does not match",
                }
            ],
        }

    package = read_package_metadata(root)
    channel = str(trail.get("channel") or "")
    version = str(trail.get("version") or package.get("version") or "")
    name = str(trail.get("package_name") or package.get("name") or "")
    dist_dir = Path(str(trail.get("dist_dir") or root / "dist"))
    if not dist_dir.is_absolute():
        dist_dir = root / dist_dir
    evidence_paths = _mapping(trail.get("evidence_paths"))
    step_reports = [
        publication_trail_step_status(
            step,
            root=root,
            dist_dir=dist_dir,
            package_name=name,
            channel=channel,
            version=version,
            evidence_paths=evidence_paths,
        )
        for step in trail.get("steps", [])
        if isinstance(step, Mapping)
    ]
    summary = count_step_statuses(step_reports)
    findings: list[dict[str, str]] = []
    if trail.get("status") != "ready":
        findings.append(
            {
                "gate": "publication-trail",
                "status": str(trail.get("status", "hold")),
                "summary": "publication trail is not ready",
            }
        )
    findings.extend(
        {
            "gate": str(step.get("id", "publication-step")),
            "status": str(step.get("status", "")),
            "summary": str(step.get("summary", "")),
        }
        for step in step_reports
        if step.get("status") in {"fail", "pending"}
    )
    if summary["failed"] or trail.get("status") != "ready":
        status = "hold"
    elif summary["pending"]:
        status = "in-progress"
    else:
        status = "complete"

    return {
        "schema_version": TRAIL_STATUS_SCHEMA_VERSION,
        "status": status,
        "project_path": str(root),
        "trail_file": str(path),
        "channel": channel,
        "package_name": name,
        "version": version,
        "summary": summary,
        "steps": step_reports,
        "findings": findings,
        "residual_risks": [
            "This status reads local files only and does not query package-index state.",
            "Readiness and release-verify steps are command-only unless their outputs are captured elsewhere.",
        ],
    }


def build_package_index_check(
    project_root: Path | str,
    *,
    channel: str = "pypi",
    target_version: str | None = None,
    package_url: str | None = None,
    timeout_seconds: float = 10.0,
    fetcher: PackageIndexFetcher | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    selected_channel = channel.lower()
    package = read_package_metadata(root)
    package_name = str(package.get("name") or "")
    local_version = str(package.get("version") or "")
    expected_version = target_version or local_version
    index_url = package_index_json_url(selected_channel, package_name)

    checks: list[dict[str, Any]] = [
        package_metadata_check(package),
        version_channel_check(local_version, selected_channel, target_version=target_version, allow_dev=False),
    ]
    index_payload: Mapping[str, Any] = {}
    http_status: int | None = None
    fetch_error = ""

    if index_url:
        try:
            http_status, index_payload = (fetcher or fetch_package_index_json)(index_url, timeout_seconds)
        except Exception as exc:  # pragma: no cover - concrete branches are covered through fake fetchers
            fetch_error = str(exc)
    else:
        fetch_error = f"unsupported package index channel: {selected_channel}"

    index_check = package_index_reachable_check(index_url, http_status=http_status, error=fetch_error)
    checks.append(index_check)

    releases = _mapping(index_payload.get("releases"))
    info = _mapping(index_payload.get("info"))
    latest_version = str(info.get("version") or "")
    release_versions = sorted(str(version) for version in releases.keys())
    target_files = releases.get(expected_version, [])
    target_file_count = len(target_files) if isinstance(target_files, list) else 0

    checks.append(
        package_index_version_check(
            expected_version,
            latest_version=latest_version,
            release_versions=release_versions,
            target_file_count=target_file_count,
        )
    )
    checks.append(package_url_check(package_url, package_name=package_name, version=expected_version, channel=selected_channel))

    findings = [
        {
            "gate": check["id"],
            "status": check["status"],
            "summary": check.get("summary", ""),
        }
        for check in checks
        if check["status"] != "pass"
    ]
    return {
        "schema_version": INDEX_CHECK_SCHEMA_VERSION,
        "status": "published" if not findings else "hold",
        "project_path": str(root),
        "channel": selected_channel,
        "package_name": package_name,
        "local_version": local_version,
        "target_version": expected_version,
        "package_url": package_url,
        "index_url": index_url,
        "http_status": http_status,
        "latest_version": latest_version,
        "release_versions": release_versions,
        "target_file_count": target_file_count,
        "checks": checks,
        "findings": findings,
        "residual_risks": [
            "This check verifies package-index metadata only; it does not prove install smoke or owner controls.",
            "Internal package indexes need a channel-specific implementation before strict use.",
        ],
    }


def write_package_index_check(
    project_root: Path | str,
    report: Mapping[str, Any],
    *,
    output_file: Path | str | None = None,
) -> Path:
    root = Path(project_root).resolve()
    output_path = Path(output_file) if output_file is not None else root / DEFAULT_INDEX_CHECK_OUTPUT
    if not output_path.is_absolute():
        output_path = root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return output_path


def write_publication_trail(
    project_root: Path | str,
    report: Mapping[str, Any],
    *,
    output_file: Path | str | None = None,
) -> Path:
    root = Path(project_root).resolve()
    output_path = Path(output_file) if output_file is not None else root / DEFAULT_TRAIL_OUTPUT
    if not output_path.is_absolute():
        output_path = root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return output_path


def render_publication_trail_status(report: Mapping[str, Any]) -> str:
    summary = _mapping(report.get("summary"))
    lines = [
        "Relay-kit publication trail status",
        f"- project: {report.get('project_path')}",
        f"- channel: {report.get('channel')}",
        f"- version: {report.get('version')}",
        f"- status: {report.get('status')}",
        (
            "- steps: "
            f"complete={summary.get('complete', 0)}, "
            f"pending={summary.get('pending', 0)}, "
            f"not_observable={summary.get('not_observable', 0)}, "
            f"failed={summary.get('failed', 0)}"
        ),
    ]
    for step in report.get("steps", []):
        if isinstance(step, Mapping):
            lines.append(f"  - {step.get('id')}: {step.get('status')} - {step.get('summary')}")
    return "\n".join(lines)


def render_package_index_check(report: Mapping[str, Any]) -> str:
    lines = [
        "Relay-kit package index check",
        f"- project: {report.get('project_path')}",
        f"- channel: {report.get('channel')}",
        f"- package: {report.get('package_name')}",
        f"- target version: {report.get('target_version')}",
        f"- latest version: {report.get('latest_version')}",
        f"- status: {report.get('status')}",
        f"- findings: {len(report.get('findings', []))}",
    ]
    for check_result in report.get("checks", []):
        if isinstance(check_result, Mapping):
            lines.append(f"  - {check_result.get('label', check_result.get('id'))}: {check_result.get('status')} - {check_result.get('summary')}")
    return "\n".join(lines)


def write_publication_trail_markdown(
    project_root: Path | str,
    report: Mapping[str, Any],
    *,
    output_file: Path | str | None = None,
) -> Path:
    root = Path(project_root).resolve()
    output_path = Path(output_file) if output_file is not None else root / DEFAULT_TRAIL_MARKDOWN
    if not output_path.is_absolute():
        output_path = root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_publication_trail_markdown(report) + "\n", encoding="utf-8")
    return output_path


def render_publication_plan(report: Mapping[str, Any]) -> str:
    lines = [
        "Relay-kit publication plan",
        f"- project: {report.get('project_path')}",
        f"- channel: {report.get('channel')}",
        f"- version: {report.get('version')}",
        f"- status: {report.get('status')}",
        f"- checks: {len(report.get('checks', []))}",
        f"- findings: {len(report.get('findings', []))}",
    ]
    checks = report.get("checks", [])
    if checks:
        lines.append("- check results:")
        for check in checks:
            if isinstance(check, Mapping):
                lines.append(f"  - {check.get('label', check.get('id'))}: {check.get('status')}")
                if check.get("summary") and check.get("status") != "pass":
                    lines.append(f"    {check['summary']}")
    commands = report.get("next_commands", [])
    if commands:
        lines.append("- next commands:")
        lines.extend(f"  - {command}" for command in commands)
    return "\n".join(lines)


def render_publication_evidence(report: Mapping[str, Any]) -> str:
    lines = [
        "Relay-kit publication evidence",
        f"- project: {report.get('project_path')}",
        f"- channel: {report.get('channel')}",
        f"- version: {report.get('version')}",
        f"- status: {report.get('status')}",
        f"- artifacts: {report.get('distribution', {}).get('artifact_count', 0)}",
        f"- findings: {len(report.get('findings', []))}",
    ]
    checks = report.get("checks", [])
    if checks:
        lines.append("- check results:")
        for check in checks:
            if isinstance(check, Mapping):
                lines.append(f"  - {check.get('label', check.get('id'))}: {check.get('status')}")
                if check.get("summary") and check.get("status") != "pass":
                    lines.append(f"    {check['summary']}")
    return "\n".join(lines)


def render_publication_trail(report: Mapping[str, Any]) -> str:
    lines = [
        "Relay-kit publication trail",
        f"- project: {report.get('project_path')}",
        f"- channel: {report.get('channel')}",
        f"- version: {report.get('version')}",
        f"- shell: {report.get('shell')}",
        f"- status: {report.get('status')}",
        f"- steps: {len(report.get('steps', []))}",
        f"- findings: {len(report.get('findings', []))}",
    ]
    for finding in report.get("findings", []):
        if isinstance(finding, Mapping):
            lines.append(f"  - {finding.get('gate')}: {finding.get('summary')}")
    return "\n".join(lines)


def render_publication_trail_markdown(report: Mapping[str, Any]) -> str:
    shell = str(report.get("shell") or "bash")
    code_fence = "powershell" if shell == "powershell" else "bash"
    lines = [
        "# Relay-kit Publication Trail",
        "",
        f"- Project: `{report.get('project_path')}`",
        f"- Channel: `{report.get('channel')}`",
        f"- Version: `{report.get('version')}`",
        f"- Status: `{report.get('status')}`",
        "",
        "## Evidence Paths",
        "",
    ]
    paths = report.get("evidence_paths", {})
    if isinstance(paths, Mapping):
        for key, value in paths.items():
            lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Steps", ""])
    for step in report.get("steps", []):
        if isinstance(step, Mapping):
            lines.extend(
                [
                    f"### {step.get('label', step.get('id'))}",
                    "",
                    f"- Purpose: {step.get('purpose', '')}",
                    "",
                    f"```{code_fence}",
                    str(step.get("command", "")),
                    "```",
                    "",
                ]
            )
    return "\n".join(lines).rstrip()


def package_index_json_url(channel: str, package_name: str) -> str:
    if not package_name:
        return ""
    if channel == "pypi":
        return f"https://pypi.org/pypi/{package_name}/json"
    if channel == "testpypi":
        return f"https://test.pypi.org/pypi/{package_name}/json"
    return ""


def fetch_package_index_json(url: str, timeout_seconds: float) -> tuple[int, Mapping[str, Any]]:
    request = urllib.request.Request(url, headers={"User-Agent": "relay-kit-publication-check/1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            status = int(getattr(response, "status", response.getcode()))
            raw = response.read()
    except urllib.error.HTTPError as exc:
        return int(exc.code), {}
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("package index response is not a JSON object")
    return status, payload


def read_package_metadata(root: Path) -> dict[str, Any]:
    path = root / "pyproject.toml"
    if not path.exists() or tomllib is None:
        return {"name": "", "version": "", "exists": path.exists(), "path": str(path)}
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"name": "", "version": "", "exists": True, "path": str(path), "error": str(exc)}
    project = _mapping(payload.get("project"))
    return {
        "name": str(project.get("name") or ""),
        "version": str(project.get("version") or ""),
        "exists": True,
        "path": str(path),
    }


def package_metadata_check(package: Mapping[str, Any]) -> dict[str, Any]:
    missing: list[str] = []
    if not package.get("exists"):
        missing.append("pyproject.toml")
    if package.get("name") != "relay-kit":
        missing.append("project.name=relay-kit")
    if not package.get("version"):
        missing.append("project.version")
    if package.get("error"):
        missing.append(f"pyproject parse error: {package['error']}")
    return check(
        "package-metadata",
        "package metadata",
        "fail" if missing else "pass",
        "missing: " + ", ".join(missing) if missing else "package metadata ready",
        details={"missing": missing, "path": package.get("path"), "version": package.get("version", "")},
    )


def version_channel_check(
    version: str,
    channel: str,
    *,
    target_version: str | None,
    allow_dev: bool,
) -> dict[str, Any]:
    findings: list[str] = []
    if channel not in CHANNELS:
        findings.append(f"unknown channel {channel}")
    if target_version and version != target_version:
        findings.append(f"target version {target_version} does not match package version {version}")
    if channel == "pypi" and _is_dev_version(version) and not allow_dev:
        findings.append("pypi channel requires a non-dev version unless --allow-dev is set")
    return check(
        "version-channel",
        "version channel",
        "fail" if findings else "pass",
        "; ".join(findings) if findings else "version is publishable for channel",
        details={"channel": channel, "target_version": target_version, "allow_dev": allow_dev},
    )


def release_lane_check(root: Path) -> dict[str, Any]:
    report = build_release_lane_report(root)
    status = "pass" if report.get("status") == "pass" else "fail"
    return check(
        "release-lane",
        "release lane",
        status,
        f"release lane status: {report.get('status')}",
        details={
            "findings": report.get("findings", []),
            "checks_count": len(report.get("checks", [])),
        },
    )


def distribution_artifacts_check(dist_dir: Path, *, name: str, version: str) -> dict[str, Any]:
    missing: list[str] = []
    wheel_paths, sdist_paths = matching_distribution_artifact_paths(dist_dir, name=name, version=version)
    wheel_files = [path.name for path in wheel_paths]
    sdist_files = [path.name for path in sdist_paths]
    if not wheel_files:
        missing.append("wheel")
    if not sdist_files:
        missing.append("sdist")
    return check(
        "distribution-artifacts",
        "distribution artifacts",
        "hold" if missing else "pass",
        "missing: " + ", ".join(missing) if missing else "wheel and sdist artifacts present",
        details={"missing": missing, "wheel_files": wheel_files, "sdist_files": sdist_files, "dist_dir": str(dist_dir)},
    )


def distribution_artifacts(dist_dir: Path, *, name: str, version: str) -> list[dict[str, Any]]:
    wheel_paths, sdist_paths = matching_distribution_artifact_paths(dist_dir, name=name, version=version)
    artifacts: list[dict[str, Any]] = []
    for kind, paths in (("wheel", wheel_paths), ("sdist", sdist_paths)):
        for path in paths:
            artifacts.append(
                {
                    "kind": kind,
                    "name": path.name,
                    "path": str(path),
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    return artifacts


def matching_distribution_artifact_paths(dist_dir: Path, *, name: str, version: str) -> tuple[list[Path], list[Path]]:
    if not dist_dir.exists():
        return [], []
    dist_name = normalize_distribution_name(name)
    wheel_paths = sorted(dist_dir.glob(f"{dist_name}-{version}-*.whl"))
    sdist_paths = sorted(dist_dir.glob(f"{dist_name}-{version}.tar.gz"))
    return wheel_paths, sdist_paths


def external_evidence_check(
    channel: str,
    *,
    ci_url: str | None,
    release_url: str | None,
    package_url: str | None,
) -> dict[str, Any]:
    required = ["ci_url", "package_url"]
    if channel == "pypi":
        required.append("release_url")
    values = {
        "ci_url": ci_url,
        "release_url": release_url,
        "package_url": package_url,
    }
    missing = [key for key in required if not values.get(key)]
    invalid = [key for key, value in values.items() if value and not _looks_like_url(value)]
    status = "pass" if not missing and not invalid else "hold"
    summary_parts: list[str] = []
    if missing:
        summary_parts.append("missing: " + ", ".join(missing))
    if invalid:
        summary_parts.append("invalid URLs: " + ", ".join(invalid))
    return check(
        "external-evidence",
        "external evidence",
        status,
        "; ".join(summary_parts) if summary_parts else "external evidence URLs recorded",
        details={"missing": missing, "invalid": invalid, "ci_url": ci_url, "release_url": release_url, "package_url": package_url},
    )


def package_index_reachable_check(index_url: str, *, http_status: int | None, error: str) -> dict[str, Any]:
    findings: list[str] = []
    if not index_url:
        findings.append("missing package index URL")
    if error:
        findings.append(error)
    if http_status is None:
        findings.append("package index was not reached")
    elif http_status != 200:
        findings.append(f"package index returned HTTP {http_status}")
    return check(
        "package-index-reachable",
        "package index reachable",
        "pass" if not findings else "hold",
        "; ".join(findings) if findings else "package index metadata fetched",
        details={"index_url": index_url, "http_status": http_status, "error": error},
    )


def package_index_version_check(
    expected_version: str,
    *,
    latest_version: str,
    release_versions: list[str],
    target_file_count: int,
) -> dict[str, Any]:
    findings: list[str] = []
    if not expected_version:
        findings.append("missing target version")
    elif expected_version not in release_versions:
        findings.append(f"target version {expected_version} is not present")
    elif target_file_count <= 0:
        findings.append(f"target version {expected_version} has no release files")
    if expected_version and latest_version and latest_version != expected_version:
        findings.append(f"latest version {latest_version} does not match target {expected_version}")
    if not latest_version:
        findings.append("missing latest version in package index metadata")
    return check(
        "package-index-version",
        "package index version",
        "pass" if not findings else "hold",
        "; ".join(findings) if findings else "target version is latest and has files",
        details={
            "target_version": expected_version,
            "latest_version": latest_version,
            "release_versions": release_versions,
            "target_file_count": target_file_count,
        },
    )


def package_url_check(package_url: str | None, *, package_name: str, version: str, channel: str) -> dict[str, Any]:
    if not package_url:
        return check("package-url", "package URL", "hold", "missing package URL", details={"package_url": None})
    findings: list[str] = []
    if not _looks_like_url(package_url):
        findings.append("package URL is not http(s)")
    expected_fragment = f"/project/{package_name}/{version}/"
    if channel in {"pypi", "testpypi"} and expected_fragment not in package_url:
        findings.append(f"package URL does not include {expected_fragment}")
    return check(
        "package-url",
        "package URL",
        "pass" if not findings else "hold",
        "; ".join(findings) if findings else "package URL matches target version",
        details={"package_url": package_url, "expected_fragment": expected_fragment},
    )


def text_evidence_file_check(
    check_id: str,
    label: str,
    path: Path | None,
    *,
    required_text: str | None,
    failure_tokens: tuple[str, ...],
) -> dict[str, Any]:
    if path is None:
        return check(check_id, label, "hold", f"missing {label} file", details={"path": None})
    if not path.exists():
        return check(check_id, label, "hold", f"missing {label} file", details={"path": str(path)})
    text = read_evidence_text(path)
    lowered = text.lower()
    failures = [token for token in failure_tokens if token in lowered]
    if not text.strip():
        return check(check_id, label, "hold", f"{label} file is empty", details={"path": str(path), "size_bytes": 0})
    if failures:
        return check(
            check_id,
            label,
            "hold",
            f"{label} contains failure tokens: {', '.join(failures)}",
            details={"path": str(path), "size_bytes": path.stat().st_size, "failure_tokens": failures},
        )
    if required_text and required_text.lower() not in lowered:
        return check(
            check_id,
            label,
            "hold",
            f"{label} does not contain required text: {required_text}",
            details={"path": str(path), "size_bytes": path.stat().st_size, "required_text": required_text},
        )
    return check(
        check_id,
        label,
        "pass",
        f"{label} evidence recorded",
        details={"path": str(path), "size_bytes": path.stat().st_size},
    )


def publication_plan_file_check(path: Path) -> dict[str, Any]:
    if not path.exists():
        return check("publication-plan", "publication plan", "hold", "missing publication plan file", details={"path": str(path)})
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return check(
            "publication-plan",
            "publication plan",
            "hold",
            f"publication plan is not valid JSON: {exc}",
            details={"path": str(path)},
        )
    status = payload.get("status")
    if payload.get("schema_version") != SCHEMA_VERSION:
        return check(
            "publication-plan",
            "publication plan",
            "hold",
            "publication plan schema does not match",
            details={"path": str(path), "schema_version": payload.get("schema_version")},
        )
    if status != "ready":
        return check(
            "publication-plan",
            "publication plan",
            "hold",
            f"publication plan status is {status}",
            details={"path": str(path), "status": status},
        )
    return check("publication-plan", "publication plan", "pass", "publication plan is ready", details={"path": str(path)})


def publication_evidence_file_check(
    path: Path,
    *,
    expected_channel: str | None = None,
    expected_name: str | None = None,
    expected_version: str | None = None,
) -> dict[str, Any]:
    if not path.exists():
        return check("publication-evidence", "publication evidence", "hold", "missing publication evidence file", details={"path": str(path)})
    payload = read_json_object(path)
    if payload is None:
        return check("publication-evidence", "publication evidence", "hold", "publication evidence is not valid JSON", details={"path": str(path)})
    if payload.get("schema_version") != EVIDENCE_SCHEMA_VERSION:
        return check(
            "publication-evidence",
            "publication evidence",
            "hold",
            "publication evidence schema does not match",
            details={"path": str(path), "schema_version": payload.get("schema_version")},
        )
    if payload.get("status") != "published":
        return check(
            "publication-evidence",
            "publication evidence",
            "hold",
            f"publication evidence status is {payload.get('status')}",
            details={"path": str(path), "status": payload.get("status")},
        )
    mismatches: list[dict[str, str | None]] = []
    expected_values = {
        "channel": expected_channel,
        "package_name": expected_name,
        "version": expected_version,
    }
    for field, expected in expected_values.items():
        if expected and payload.get(field) != expected:
            mismatches.append({"field": field, "expected": expected, "actual": str(payload.get(field))})
    if mismatches:
        return check(
            "publication-evidence",
            "publication evidence",
            "hold",
            "publication evidence does not match trail",
            details={"path": str(path), "mismatches": mismatches},
        )
    return check("publication-evidence", "publication evidence", "pass", "publication evidence is published", details={"path": str(path)})


def publication_trail_step_status(
    step: Mapping[str, Any],
    *,
    root: Path,
    dist_dir: Path,
    package_name: str,
    channel: str,
    version: str,
    evidence_paths: Mapping[str, Any],
) -> dict[str, Any]:
    step_id = str(step.get("id", "publication-step"))
    label = str(step.get("label", step_id))
    if step_id == "build":
        check_result = distribution_artifacts_check(dist_dir, name=package_name, version=version)
        return step_status_from_check(step_id, label, check_result, pending_status="pending")
    if step_id == "twine-check":
        path = _path_from_evidence(root, evidence_paths, "twine_check_file")
        check_result = text_evidence_file_check("twine-check", "twine check", path, required_text="passed", failure_tokens=("failed", "error"))
        return step_status_from_check(step_id, label, check_result, pending_status="pending")
    if step_id == "publication-plan":
        path = _path_from_evidence(root, evidence_paths, "publication_plan_file")
        check_result = publication_plan_file_check(path)
        return step_status_from_check(step_id, label, check_result, pending_status="pending")
    if step_id == "upload":
        path = _path_from_evidence(root, evidence_paths, "upload_log_file")
        check_result = text_evidence_file_check("upload-log", "upload log", path, required_text=None, failure_tokens=("failed", "error", "traceback"))
        return step_status_from_check(step_id, label, check_result, pending_status="pending")
    if step_id == "publication-evidence":
        path = _path_from_evidence(root, evidence_paths, "publication_evidence_file")
        check_result = publication_evidence_file_check(
            path,
            expected_channel=channel,
            expected_name=package_name,
            expected_version=version,
        )
        return step_status_from_check(step_id, label, check_result, pending_status="pending")
    return {
        "id": step_id,
        "label": label,
        "status": "not-observable",
        "summary": "step has no local evidence file to inspect",
        "details": {"command": step.get("command", "")},
    }


def step_status_from_check(
    step_id: str,
    label: str,
    check_result: Mapping[str, Any],
    *,
    pending_status: str,
) -> dict[str, Any]:
    check_status = str(check_result.get("status", "hold"))
    status = "complete" if check_status == "pass" else pending_status
    if check_status == "fail":
        status = "fail"
    return {
        "id": step_id,
        "label": label,
        "status": status,
        "summary": check_result.get("summary", ""),
        "details": check_result.get("details", {}),
    }


def read_evidence_text(path: Path) -> str:
    raw = path.read_bytes()
    if not raw:
        return ""
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16", errors="replace")
    text = raw.decode("utf-8", errors="replace")
    if "\x00" in text:
        try:
            utf16_text = raw.decode("utf-16")
        except UnicodeError:
            return text
        if utf16_text.count("\x00") < text.count("\x00"):
            return utf16_text
    return text


def count_step_statuses(steps: list[dict[str, Any]]) -> dict[str, int]:
    summary = {"complete": 0, "pending": 0, "not_observable": 0, "failed": 0, "total": len(steps)}
    for step in steps:
        status = str(step.get("status", ""))
        if status == "complete":
            summary["complete"] += 1
        elif status == "pending":
            summary["pending"] += 1
        elif status == "not-observable":
            summary["not_observable"] += 1
        else:
            summary["failed"] += 1
    return summary


def shell_check(shell: str) -> dict[str, Any]:
    return check(
        "shell",
        "shell",
        "pass" if shell in SHELLS else "hold",
        "shell is supported" if shell in SHELLS else f"unsupported shell: {shell}",
        details={"shell": shell, "supported": sorted(SHELLS)},
    )


def publication_trail_steps(
    root: Path,
    channel: str,
    shell: str,
    *,
    dist_root: Path,
    twine_check_file: Path,
    upload_log_file: Path,
    publication_plan_file: Path,
    publication_evidence_file: Path,
    ci_url: str | None,
    release_url: str | None,
    package_url: str | None,
    allow_dev: bool,
) -> list[dict[str, str]]:
    project = _shell_arg(root)
    dist_arg = _shell_arg(dist_root)
    twine_arg = _shell_arg(twine_check_file)
    upload_arg = _shell_arg(upload_log_file)
    plan_arg = _shell_arg(publication_plan_file)
    evidence_arg = _shell_arg(publication_evidence_file)
    plan_command = _publish_plan_command(
        project,
        channel,
        ci_url=ci_url,
        release_url=release_url,
        package_url=package_url,
        output_file=plan_arg,
        allow_dev=allow_dev,
    )
    evidence_command = _publish_evidence_command(
        project,
        channel,
        ci_url=ci_url,
        release_url=release_url,
        package_url=package_url,
        twine_check_file=twine_arg,
        upload_log_file=upload_arg,
        publication_plan_file=plan_arg,
        output_file=evidence_arg,
        allow_dev=allow_dev,
    )
    return [
        {
            "id": "readiness",
            "label": "Readiness gate",
            "purpose": "Verify commercial readiness gates before building artifacts.",
            "command": f"relay-kit readiness check {project} --profile enterprise --json",
        },
        {
            "id": "release-verify",
            "label": "Release lane gate",
            "purpose": "Verify release-lane prerequisites and clean final-cut policy.",
            "command": f"relay-kit release verify {project} --require-clean --json",
        },
        {
            "id": "build",
            "label": "Build distributions",
            "purpose": "Create the wheel and sdist that will be hashed in publication evidence.",
            "command": f"python -m build --sdist --wheel --outdir {dist_arg}",
        },
        {
            "id": "twine-check",
            "label": "Capture twine check",
            "purpose": "Capture package metadata validation output for the evidence artifact.",
            "command": capture_command(f"python -m twine check {dist_arg}/*", twine_check_file, shell),
        },
        {
            "id": "publication-plan",
            "label": "Write publication plan",
            "purpose": "Confirm the package is ready before upload.",
            "command": plan_command,
        },
        {
            "id": "upload",
            "label": "Capture upload confirmation",
            "purpose": "Run the package upload and capture the confirmation log.",
            "command": capture_command(upload_command(channel), upload_log_file, shell),
        },
        {
            "id": "publication-evidence",
            "label": "Write publication evidence",
            "purpose": "Bind dist hashes, twine output, upload log, and external URLs into one artifact.",
            "command": evidence_command,
        },
    ]


def capture_command(command: str, output_file: Path, shell: str) -> str:
    output = _shell_arg(output_file)
    if shell == "bash":
        return f"{command} 2>&1 | tee {output}"
    return f"& {command} 2>&1 | Tee-Object -FilePath {output}"


def publication_commands(root: Path, channel: str) -> list[str]:
    project = _shell_arg(root)
    upload_command = "python -m twine upload dist/*"
    if channel == "testpypi":
        upload_command = "python -m twine upload --repository testpypi dist/*"
    if channel == "internal":
        upload_command = "python -m twine upload --repository-url <internal-index-url> dist/*"
    return [
        f"relay-kit readiness check {project} --profile enterprise --json",
        f"relay-kit release verify {project} --require-clean --json",
        "python -m build --sdist --wheel --outdir dist",
        "python -m twine check dist/*",
        upload_command,
    ]


def upload_command(channel: str) -> str:
    if channel == "testpypi":
        return "python -m twine upload --repository testpypi dist/*"
    if channel == "internal":
        return "python -m twine upload --repository-url <internal-index-url> dist/*"
    return "python -m twine upload dist/*"


def _publish_plan_command(
    project: str,
    channel: str,
    *,
    ci_url: str | None,
    release_url: str | None,
    package_url: str | None,
    output_file: str,
    allow_dev: bool,
) -> str:
    parts = ["relay-kit publish plan", project, "--channel", channel]
    parts.extend(_url_args(ci_url=ci_url, release_url=release_url, package_url=package_url))
    parts.extend(["--output-file", output_file, "--strict", "--json"])
    if allow_dev:
        parts.append("--allow-dev")
    return " ".join(parts)


def _publish_evidence_command(
    project: str,
    channel: str,
    *,
    ci_url: str | None,
    release_url: str | None,
    package_url: str | None,
    twine_check_file: str,
    upload_log_file: str,
    publication_plan_file: str,
    output_file: str,
    allow_dev: bool,
) -> str:
    parts = ["relay-kit publish evidence", project, "--channel", channel]
    parts.extend(_url_args(ci_url=ci_url, release_url=release_url, package_url=package_url))
    parts.extend(
        [
            "--twine-check-file",
            twine_check_file,
            "--upload-log-file",
            upload_log_file,
            "--publication-plan-file",
            publication_plan_file,
            "--output-file",
            output_file,
            "--strict",
            "--json",
        ]
    )
    if allow_dev:
        parts.append("--allow-dev")
    return " ".join(parts)


def _url_args(*, ci_url: str | None, release_url: str | None, package_url: str | None) -> list[str]:
    args: list[str] = []
    if ci_url:
        args.extend(["--ci-url", _shell_value(ci_url)])
    if release_url:
        args.extend(["--release-url", _shell_value(release_url)])
    if package_url:
        args.extend(["--package-url", _shell_value(package_url)])
    return args


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


def normalize_distribution_name(name: str) -> str:
    return name.replace("-", "_")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_dist_dir(root: Path, dist_dir: Path | str | None) -> Path:
    path = Path(dist_dir) if dist_dir is not None else root / "dist"
    return path if path.is_absolute() else root / path


def _resolve_optional_path(root: Path, value: Path | str | None) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    return path if path.is_absolute() else root / path


def _path_from_evidence(root: Path, evidence_paths: Mapping[str, Any], key: str) -> Path:
    value = evidence_paths.get(key)
    if not value:
        return root / DEFAULT_TRAIL_OUTPUT.parent / f"missing-{key}"
    path = Path(str(value))
    return path if path.is_absolute() else root / path


def _resolve_evidence_dir(root: Path, value: Path | str | None, *, version: str) -> Path:
    path = Path(value) if value is not None else root / ".tmp" / "relay-publication" / version
    return path if path.is_absolute() else root / path


def _is_dev_version(version: str) -> bool:
    lowered = version.lower()
    return ".dev" in lowered or "+" in lowered


def _looks_like_url(value: str) -> bool:
    return value.startswith("https://") or value.startswith("http://")


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def read_json_object(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _shell_arg(path: Path) -> str:
    value = str(path)
    if any(char.isspace() for char in value):
        return f'"{value}"'
    return value


def _shell_value(value: str) -> str:
    if any(char.isspace() for char in value):
        return f'"{value}"'
    return value
