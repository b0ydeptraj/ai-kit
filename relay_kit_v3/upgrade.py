"""Versioned upgrade checks for installed Relay-kit runtimes."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from relay_kit_v3 import bundle_manifest


SCHEMA_VERSION = "relay-kit.runtime-version.v1"
VERSION_FILE = Path(".relay-kit") / "version.json"
DEFAULT_BUNDLE = "baseline"
DEFAULT_ADAPTERS = ["codex"]


def write_version_marker(
    project_root: Path | str,
    *,
    bundle: str = DEFAULT_BUNDLE,
    adapters: list[str] | None = None,
    manifest_file: Path | str | None = None,
) -> Path:
    root = Path(project_root).resolve()
    manifest_status = inspect_manifest(root, manifest_file)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _utc_timestamp(),
        "package": current_package(),
        "runtime": {
            "bundle": bundle,
            "adapters": _normalize_adapters(adapters or DEFAULT_ADAPTERS),
        },
        "manifest": {
            "path": str(manifest_status["path"]),
            "status": manifest_status["status"],
            "hash": manifest_status["hash"],
        },
    }

    output_path = root / VERSION_FILE
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return output_path


def build_upgrade_report(
    project_root: Path | str,
    *,
    manifest_file: Path | str | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    target_package = current_package()
    marker_path = root / VERSION_FILE
    manifest_status = inspect_manifest(root, manifest_file)
    actions: list[str] = []
    findings: list[dict[str, str]] = []
    runtime: dict[str, Any] = {}
    installed_version: str | None = None

    if marker_path.exists():
        marker, marker_findings = read_version_marker(marker_path)
        findings.extend(marker_findings)
    else:
        marker = None
        findings.append(
            {
                "check": "version-marker",
                "detail": f"Missing Relay-kit version marker: {VERSION_FILE.as_posix()}",
            }
        )

    if marker is None:
        upgrade_status = "untracked"
    elif marker.get("schema_version") != SCHEMA_VERSION:
        upgrade_status = "invalid-marker"
        findings.append(
            {
                "check": "version-marker",
                "detail": f"Unexpected schema_version: {marker.get('schema_version')!r}",
            }
        )
    else:
        package = marker.get("package", {})
        runtime = marker.get("runtime", {}) if isinstance(marker.get("runtime"), dict) else {}
        if isinstance(package, dict):
            installed_version = str(package.get("version", "")).strip() or None
        if not installed_version:
            upgrade_status = "invalid-marker"
            findings.append({"check": "version-marker", "detail": "Missing installed package.version"})
        else:
            upgrade_status = compare_installed_to_target(installed_version, target_package["version"])

    if manifest_status["status"] != "valid":
        findings.extend(manifest_status["findings"])

    actions.extend(_actions_for(upgrade_status, manifest_status["status"], root))
    status = "pass" if upgrade_status == "current" and manifest_status["status"] == "valid" and not findings else "action-required"

    return {
        "schema_version": "relay-kit.upgrade-report.v1",
        "status": status,
        "upgrade_status": upgrade_status,
        "project_path": str(root),
        "version_file": str(marker_path),
        "installed_version": installed_version,
        "target_version": target_package["version"],
        "package": target_package,
        "runtime": runtime,
        "manifest_status": manifest_status["status"],
        "manifest_file": str(manifest_status["path"]),
        "manifest_hash": manifest_status["hash"],
        "findings_count": len(findings),
        "findings": findings,
        "actions": actions,
    }


def read_version_marker(path: Path | str) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    marker_path = Path(path)
    try:
        payload = json.loads(marker_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        return None, [{"check": "version-marker", "detail": f"Invalid JSON: {exc.msg}"}]
    if not isinstance(payload, dict):
        return None, [{"check": "version-marker", "detail": "Version marker root must be an object"}]
    return payload, []


def inspect_manifest(project_root: Path | str, manifest_file: Path | str | None = None) -> dict[str, Any]:
    root = Path(project_root).resolve()
    path = Path(manifest_file) if manifest_file is not None else root / bundle_manifest.DEFAULT_OUTPUT
    if not path.is_absolute():
        path = root / path
    if not path.exists():
        return {
            "status": "missing",
            "path": path,
            "hash": None,
            "findings": [{"check": "bundle-manifest", "detail": f"Missing bundle manifest: {path}"}],
        }

    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        return {
            "status": "invalid",
            "path": path,
            "hash": None,
            "findings": [{"check": "bundle-manifest", "detail": f"Invalid JSON: {exc.msg}"}],
        }
    if not isinstance(payload, dict):
        return {
            "status": "invalid",
            "path": path,
            "hash": None,
            "findings": [{"check": "bundle-manifest", "detail": "Manifest root must be an object"}],
        }

    result = bundle_manifest.verify_manifest_payload(payload)
    if not result.ok:
        return {
            "status": "invalid",
            "path": path,
            "hash": payload.get("manifest_hash"),
            "findings": [{"check": "bundle-manifest", "detail": finding} for finding in result.findings],
        }

    return {
        "status": "valid",
        "path": path,
        "hash": payload.get("manifest_hash"),
        "findings": [],
    }


def compare_installed_to_target(installed_version: str, target_version: str) -> str:
    installed = _version_tuple(installed_version)
    target = _version_tuple(target_version)
    if installed is None or target is None:
        return "unknown-version"
    if installed == target:
        return "current"
    if installed < target:
        return "upgrade-available"
    return "ahead-of-package"


def current_package() -> dict[str, str]:
    return dict(bundle_manifest.create_manifest()["package"])


def render_report(report: dict[str, Any], *, title: str = "Relay-kit upgrade check") -> str:
    lines = [
        title,
        f"- project: {report['project_path']}",
        f"- status: {report['status']}",
        f"- upgrade status: {report['upgrade_status']}",
        f"- installed version: {report['installed_version'] or '-'}",
        f"- target version: {report['target_version']}",
        f"- manifest: {report['manifest_status']}",
        f"- findings: {report['findings_count']}",
    ]
    if report["actions"]:
        lines.append("- actions:")
        lines.extend(f"  - {action}" for action in report["actions"])
    if report["findings"]:
        lines.append("")
        lines.append("Findings:")
        for finding in report["findings"][:20]:
            lines.append(f"- {finding['check']}: {finding['detail']}")
    return "\n".join(lines)


def _actions_for(upgrade_status: str, manifest_status: str, root: Path) -> list[str]:
    actions: list[str] = []
    project = _shell_arg(root)
    if manifest_status != "valid":
        actions.append(f"relay-kit manifest write {project}")
    if upgrade_status in {"untracked", "invalid-marker", "unknown-version"}:
        actions.append(f"relay-kit upgrade mark-current {project} --bundle {DEFAULT_BUNDLE} --adapter codex")
    elif upgrade_status == "upgrade-available":
        actions.extend(
            [
                f"relay-kit init {project} --all --baseline",
                f"relay-kit manifest write {project}",
                f"relay-kit doctor {project}",
                f"relay-kit upgrade mark-current {project} --bundle {DEFAULT_BUNDLE} --adapter codex",
            ]
        )
    elif upgrade_status == "ahead-of-package":
        actions.append("Review package/runtime versions before downgrading or regenerating runtime files.")
    return _dedupe(actions)


def _normalize_adapters(adapters: list[str]) -> list[str]:
    normalized: list[str] = []
    for adapter in adapters:
        value = str(adapter).strip()
        if value and value not in normalized:
            normalized.append(value)
    return normalized or list(DEFAULT_ADAPTERS)


def _version_tuple(value: str) -> tuple[int, int, int] | None:
    match = re.match(r"^\s*(\d+)\.(\d+)\.(\d+)", value)
    if match is None:
        return None
    return tuple(int(part) for part in match.groups())


def _dedupe(values: list[str]) -> list[str]:
    deduped: list[str] = []
    for value in values:
        if value not in deduped:
            deduped.append(value)
    return deduped


def _shell_arg(path: Path) -> str:
    value = str(path)
    if any(char.isspace() for char in value):
        return f'"{value}"'
    return value


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
