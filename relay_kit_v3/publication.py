"""Publication planning checks for Relay-kit package releases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from relay_kit_v3.release_lane import build_release_lane_report

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    tomllib = None  # type: ignore[assignment]


SCHEMA_VERSION = "relay-kit.publication-plan.v1"
CHANNELS = {"pypi", "testpypi", "internal"}
DEFAULT_OUTPUT = Path(".relay-kit") / "release" / "publication-plan.json"


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
    wheel_files: list[str] = []
    sdist_files: list[str] = []
    if dist_dir.exists():
        dist_name = normalize_distribution_name(name)
        wheel_files = sorted(path.name for path in dist_dir.glob(f"{dist_name}-{version}-*.whl"))
        sdist_files = sorted(path.name for path in dist_dir.glob(f"{dist_name}-{version}.tar.gz"))
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


def _resolve_dist_dir(root: Path, dist_dir: Path | str | None) -> Path:
    path = Path(dist_dir) if dist_dir is not None else root / "dist"
    return path if path.is_absolute() else root / path


def _is_dev_version(version: str) -> bool:
    lowered = version.lower()
    return ".dev" in lowered or "+" in lowered


def _looks_like_url(value: str) -> bool:
    return value.startswith("https://") or value.startswith("http://")


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _shell_arg(path: Path) -> str:
    value = str(path)
    if any(char.isspace() for char in value):
        return f'"{value}"'
    return value
