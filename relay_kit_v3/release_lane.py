"""Local release-lane verification for Relay-kit commercial releases."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Mapping

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    tomllib = None  # type: ignore[assignment]


SCHEMA_VERSION = "relay-kit.release-lane.v1"
REQUIRED_RELEASE_DOCS = [
    "README.md",
    "docs/relay-kit-readiness-check.md",
    "docs/relay-kit-support-sla.md",
    "docs/relay-kit-contract-sync.md",
    "docs/relay-kit-pulse-report.md",
    "docs/relay-kit-signal-export.md",
    "docs/relay-kit-release-readiness.md",
    "docs/relay-kit-release-lane.md",
    "docs/relay-kit-publication-plan.md",
]
REQUIRED_CI_PATTERNS = [
    "python scripts/validate_runtime.py",
    "python scripts/runtime_doctor.py . --strict",
    "python scripts/runtime_doctor.py . --strict --state-mode live",
    "python scripts/migration_guard.py . --strict",
    "python scripts/policy_guard.py . --strict",
    "python scripts/skill_gauntlet.py . --strict --semantic",
    "python scripts/eval_workflows.py . --strict",
    "python relay_kit_public_cli.py doctor . --skip-tests --policy-pack enterprise",
    "python -m pip wheel . --no-deps -w .tmp/wheelhouse",
    "python scripts/package_smoke.py .",
    "python -m pytest tests -q",
]


def build_release_lane_report(
    project_root: Path | str,
    *,
    require_clean: bool = False,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    checks = [
        package_metadata_check(root),
        ci_runtime_gates_check(root),
        commercial_docs_check(root),
        release_artifacts_check(root),
        artifact_ignore_policy_check(root),
        git_metadata_check(root, require_clean=require_clean),
    ]
    findings = [
        {"gate": check["id"], "status": check["status"], "summary": check.get("summary", "")}
        for check in checks
        if check["required"] and check["status"] != "pass"
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass" if not findings else "fail",
        "project_path": str(root),
        "checks": checks,
        "findings": findings,
        "residual_risks": [
            "Remote CI status is not verified by this local command.",
            "Package upload, marketplace publication, and paid support operations require external release evidence.",
        ],
    }


def package_metadata_check(root: Path) -> dict[str, Any]:
    path = root / "pyproject.toml"
    if not path.exists():
        return required_check("package-metadata", "fail", "missing pyproject.toml")
    if tomllib is None:
        return required_check("package-metadata", "fail", "tomllib is unavailable")
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return required_check("package-metadata", "fail", f"invalid pyproject.toml: {exc}")

    project = _mapping(payload.get("project"))
    scripts = _mapping(project.get("scripts"))
    tool = _mapping(payload.get("tool"))
    setuptools = _mapping(tool.get("setuptools"))
    packages = _mapping(_mapping(setuptools.get("packages")).get("find"))
    includes = [str(item) for item in packages.get("include", []) if str(item)]
    missing: list[str] = []
    if project.get("name") != "relay-kit":
        missing.append("project.name=relay-kit")
    if not project.get("version"):
        missing.append("project.version")
    if scripts.get("relay-kit") != "relay_kit_public_cli:main":
        missing.append("project.scripts.relay-kit")
    for include in ["relay_kit_v3*", "scripts*"]:
        if include not in includes:
            missing.append(f"package include {include}")
    return required_check(
        "package-metadata",
        "fail" if missing else "pass",
        "missing: " + ", ".join(missing) if missing else "package metadata ready",
        details={"missing": missing, "version": str(project.get("version", ""))},
    )


def ci_runtime_gates_check(root: Path) -> dict[str, Any]:
    path = root / ".github" / "workflows" / "validate-runtime.yml"
    if not path.exists():
        return required_check("ci-runtime-gates", "fail", "missing validate-runtime workflow")
    text = path.read_text(encoding="utf-8")
    missing = [pattern for pattern in REQUIRED_CI_PATTERNS if pattern not in text]
    return required_check(
        "ci-runtime-gates",
        "fail" if missing else "pass",
        "missing CI commands: " + ", ".join(missing) if missing else "CI runtime gates present",
        details={"missing": missing, "workflow": str(path)},
    )


def commercial_docs_check(root: Path) -> dict[str, Any]:
    missing = [rel for rel in REQUIRED_RELEASE_DOCS if not (root / rel).exists()]
    return required_check(
        "commercial-docs",
        "fail" if missing else "pass",
        "missing docs: " + ", ".join(missing) if missing else "release docs present",
        details={"missing": missing},
    )


def release_artifacts_check(root: Path) -> dict[str, Any]:
    required = [
        ".relay-kit/manifest/bundles.json",
        ".relay-kit/manifest/trust.json",
        ".relay-kit/version.json",
    ]
    missing = [rel for rel in required if not (root / rel).exists()]
    return required_check(
        "release-artifacts",
        "fail" if missing else "pass",
        "missing artifacts: " + ", ".join(missing) if missing else "release artifacts present",
        details={"missing": missing},
    )


def artifact_ignore_policy_check(root: Path) -> dict[str, Any]:
    required_entries = {
        ".relay-kit/support/.gitignore": ["support-bundle.json"],
        ".relay-kit/signals/.gitignore": ["relay-signals.json", "relay-signals.jsonl", "relay-signals-otlp.json"],
        ".relay-kit/release/.gitignore": ["publication-evidence.json"],
    }
    missing: list[str] = []
    for rel, entries in required_entries.items():
        path = root / rel
        if not path.exists():
            missing.append(rel)
            continue
        text = path.read_text(encoding="utf-8")
        for entry in entries:
            if entry not in text:
                missing.append(f"{rel}:{entry}")
    return required_check(
        "artifact-ignore-policy",
        "fail" if missing else "pass",
        "missing ignore entries: " + ", ".join(missing) if missing else "generated release artifacts are ignored",
        details={"missing": missing},
    )


def git_metadata_check(root: Path, *, require_clean: bool) -> dict[str, Any]:
    if not (root / ".git").exists():
        return {
            "id": "git-metadata",
            "label": "git metadata",
            "status": "skipped",
            "required": bool(require_clean),
            "summary": "no .git directory found",
            "details": {},
        }
    branch = _git(root, "rev-parse", "--abbrev-ref", "HEAD")
    commit = _git(root, "rev-parse", "HEAD")
    status = _git(root, "status", "--porcelain")
    dirty = bool(status["stdout"].strip()) or status["returncode"] != 0
    check_status = "fail" if require_clean and dirty else "pass"
    return {
        "id": "git-metadata",
        "label": "git metadata",
        "status": check_status,
        "required": bool(require_clean),
        "summary": "git worktree dirty" if dirty else "git metadata captured",
        "details": {
            "branch": branch["stdout"].strip(),
            "commit": commit["stdout"].strip(),
            "dirty": dirty,
        },
    }


def write_release_lane_report(
    project_root: Path | str,
    report: Mapping[str, Any],
    *,
    output_file: Path | str | None = None,
) -> Path:
    root = Path(project_root).resolve()
    path = Path(output_file) if output_file is not None else root / ".relay-kit" / "release" / "release-lane.json"
    if not path.is_absolute():
        path = root / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return path


def render_release_lane_report(report: Mapping[str, Any]) -> str:
    lines = [
        "Relay-kit release lane",
        f"- project: {report.get('project_path')}",
        f"- status: {report.get('status')}",
        f"- checks: {len(report.get('checks', []))}",
        f"- findings: {len(report.get('findings', []))}",
    ]
    for check in report.get("checks", []):
        if isinstance(check, Mapping):
            required = "required" if check.get("required") else "advisory"
            lines.append(f"  - {check.get('label', check.get('id'))}: {check.get('status')} ({required})")
    return "\n".join(lines)


def required_check(
    check_id: str,
    status: str,
    summary: str,
    *,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": check_id,
        "label": check_id.replace("-", " "),
        "status": status,
        "required": True,
        "summary": summary,
        "details": dict(details or {}),
    }


def _git(root: Path, *args: str) -> dict[str, Any]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
