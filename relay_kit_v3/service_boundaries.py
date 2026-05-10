from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


SCHEMA_VERSION = "relay-kit.service-boundaries.v1"

SERVICE_BOUNDARIES = [
    {
        "id": "public-cli",
        "label": "Public CLI",
        "owned_paths": ["relay_kit_public_cli.py"],
        "responsibility": "Parse public commands and delegate behavior to relay_kit_v3 services.",
    },
    {
        "id": "registry",
        "label": "Registry",
        "owned_paths": ["relay_kit_v3/registry"],
        "responsibility": "Define skills, topology, workflow templates, docs, and support references.",
    },
    {
        "id": "gates",
        "label": "Runtime gates",
        "owned_paths": ["relay_kit_v3/readiness.py", "scripts"],
        "responsibility": "Validate runtime, policy, migration, readiness, and workflow behavior.",
    },
    {
        "id": "support",
        "label": "Support operations",
        "owned_paths": ["relay_kit_v3/support_bundle.py", "relay_kit_v3/support_request.py", "relay_kit_v3/support_triage.py"],
        "responsibility": "Collect support diagnostics, intake requests, triage support handoffs, and run soak checks.",
    },
    {
        "id": "release",
        "label": "Release",
        "owned_paths": ["relay_kit_v3/release_lane.py"],
        "responsibility": "Check local release prerequisites and residual release risks.",
    },
    {
        "id": "publication",
        "label": "Publication",
        "owned_paths": ["relay_kit_v3/publication.py", "relay_kit_v3/commercial_dossier.py"],
        "responsibility": "Track package publication, package-index proof, and commercial dossier evidence.",
    },
    {
        "id": "telemetry-pulse",
        "label": "Telemetry and Pulse",
        "owned_paths": ["relay_kit_v3/pulse.py", "relay_kit_v3/signal_export.py", "relay_kit_v3/evidence_ledger.py"],
        "responsibility": "Build static quality reports, export local signals, and record gate events.",
    },
    {
        "id": "query",
        "label": "Query",
        "owned_paths": ["relay_kit_v3/query_search.py"],
        "responsibility": "Rank local Relay-kit state, contracts, docs, evidence, and registry hits.",
    },
]

ALLOWED_RUNTIME_SCRIPT_IMPORTERS = {
    "relay_kit_v3.pulse",
    "relay_kit_v3.support_bundle",
}


def build_service_boundary_report(root: Path | str) -> dict[str, Any]:
    project = Path(root).resolve()
    findings: list[dict[str, Any]] = []
    modules = _python_modules(project)
    for module in modules:
        imports = _imports_for(module.path)
        if module.name.startswith("relay_kit_v3.registry.") or module.name == "relay_kit_v3.registry":
            if any(import_name == "relay_kit_public_cli" or import_name.startswith("relay_kit_public_cli.") for import_name in imports):
                findings.append(
                    {
                        "id": "registry-imports-cli",
                        "status": "hold",
                        "module": module.name,
                        "path": _display_path(project, module.path),
                        "summary": f"registry module {module.name} imports the public CLI",
                    }
                )
        if module.name.startswith("relay_kit_v3.") and module.name not in ALLOWED_RUNTIME_SCRIPT_IMPORTERS:
            if any(import_name == "scripts" or import_name.startswith("scripts.") for import_name in imports):
                findings.append(
                    {
                        "id": "runtime-imports-scripts",
                        "status": "hold",
                        "module": module.name,
                        "path": _display_path(project, module.path),
                        "summary": f"runtime module {module.name} imports scripts instead of a package helper",
                    }
                )
        if module.name.startswith("relay_kit_v3."):
            if any(import_name == "relay_kit_public_cli" or import_name.startswith("relay_kit_public_cli.") for import_name in imports):
                findings.append(
                    {
                        "id": "runtime-imports-cli",
                        "status": "hold",
                        "module": module.name,
                        "path": _display_path(project, module.path),
                        "summary": f"runtime module {module.name} imports the public CLI",
                    }
                )

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "hold" if findings else "pass",
        "project_path": str(project),
        "summary": {
            "boundary_count": len(SERVICE_BOUNDARIES),
            "module_count": len(modules),
            "findings": len(findings),
        },
        "boundaries": SERVICE_BOUNDARIES,
        "findings": findings,
    }


def render_service_boundary_report(report: Mapping[str, Any]) -> str:
    summary = report.get("summary", {})
    lines = [
        "Relay-kit service boundaries",
        f"- status: {report.get('status')}",
        f"- boundaries: {summary.get('boundary_count', 0)}",
        f"- modules scanned: {summary.get('module_count', 0)}",
        f"- findings: {summary.get('findings', 0)}",
    ]
    for finding in report.get("findings", [])[:12]:
        lines.append(f"  - {finding.get('summary', finding.get('id', 'finding'))}")
    return "\n".join(lines)


def write_service_boundary_report(
    root: Path | str,
    report: Mapping[str, Any],
    output_file: Path | str | None = None,
) -> Path:
    project = Path(root).resolve()
    target = Path(output_file) if output_file else project / ".relay-kit" / "service-boundaries" / "service-boundaries.json"
    if not target.is_absolute():
        target = project / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return target


class ModuleInfo:
    def __init__(self, name: str, path: Path) -> None:
        self.name = name
        self.path = path


def _python_modules(project: Path) -> list[ModuleInfo]:
    modules: list[ModuleInfo] = []
    cli = project / "relay_kit_public_cli.py"
    if cli.exists():
        modules.append(ModuleInfo("relay_kit_public_cli", cli))
    package = project / "relay_kit_v3"
    if package.exists():
        for path in package.rglob("*.py"):
            modules.append(ModuleInfo(_module_name(project, path), path))
    return modules


def _module_name(project: Path, path: Path) -> str:
    relative = path.relative_to(project).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _imports_for(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError):
        return set()
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def _display_path(project: Path, path: Path) -> str:
    try:
        return path.relative_to(project).as_posix()
    except ValueError:
        return path.as_posix()
