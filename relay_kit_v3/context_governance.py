from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "relay-kit.context-audit.v1"


@dataclass(frozen=True)
class ContextSourceSpec:
    path: str
    source_type: str
    required: bool
    label: str


CONTEXT_SOURCES = [
    ContextSourceSpec(".relay-kit/state/workflow-state.md", "authoritative", True, "workflow state"),
    ContextSourceSpec(".relay-kit/contracts/project-context.md", "authoritative", True, "project context"),
    ContextSourceSpec(".relay-kit/contracts/qa-report.md", "recent", True, "QA report"),
    ContextSourceSpec(".relay-kit/state/team-board.md", "recent", True, "team board"),
    ContextSourceSpec(".relay-kit/state/lane-registry.md", "recent", True, "lane registry"),
    ContextSourceSpec(".relay-kit/state/handoff-log.md", "recent", True, "handoff log"),
    ContextSourceSpec(".relay-kit/state/context-manifest.json", "inferred", False, "continuity manifest"),
    ContextSourceSpec(".relay-kit/state/session-ledger.jsonl", "inferred", False, "session ledger"),
]


def age_days(path: Path, *, now: datetime | None = None) -> int:
    reference = now or datetime.now(timezone.utc)
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return max(0, (reference - modified).days)


def confidence_for(source_type: str, stale: bool) -> str:
    if source_type == "missing" or stale:
        return "low"
    if source_type == "authoritative":
        return "high"
    if source_type == "recent":
        return "medium"
    return "low"


def configured_source_type(relative_path: str) -> str:
    normalized = relative_path.replace("\\", "/")
    for spec in CONTEXT_SOURCES:
        if spec.path == normalized:
            return spec.source_type
    if normalized.startswith(".relay-kit/contracts/") or normalized.startswith(".relay-kit/state/workflow-state"):
        return "authoritative"
    if normalized.startswith(".relay-kit/state/"):
        return "recent"
    if normalized.startswith(".relay-kit/references/"):
        return "inferred"
    return "inferred"


def source_metadata(
    relative_path: str,
    path: Path,
    *,
    stale_days: int,
    required: bool = False,
    label: str | None = None,
) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": relative_path,
            "label": label or relative_path,
            "required": required,
            "exists": False,
            "source_type": "missing",
            "confidence": "low",
            "age_days": None,
            "modified_utc": None,
            "stale": False,
            "stale_warning": "",
        }

    source_age = age_days(path)
    stale = source_age > max(stale_days, 0)
    configured_type = configured_source_type(relative_path)
    source_type = "stale" if stale else configured_type
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).replace(microsecond=0)
    return {
        "path": relative_path,
        "label": label or relative_path,
        "required": required,
        "exists": True,
        "source_type": source_type,
        "confidence": confidence_for(configured_type, stale),
        "age_days": source_age,
        "modified_utc": modified.isoformat().replace("+00:00", "Z"),
        "stale": stale,
        "stale_warning": "stale source" if stale else "",
    }


def source_metadata_for_paths(root: Path, paths: Iterable[str], *, stale_days: int) -> list[dict[str, Any]]:
    return [source_metadata(rel_path, root / rel_path, stale_days=stale_days) for rel_path in paths]


def current_git_head(root: Path) -> str:
    top_result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if top_result.returncode != 0:
        return ""
    try:
        if Path(top_result.stdout.strip()).resolve() != root.resolve():
            return ""
    except OSError:
        return ""
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def current_git_branch(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def is_ancestor(root: Path, ancestor_sha: str, head_sha: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor_sha, head_sha],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def workflow_state_main_baseline(root: Path) -> str:
    path = root / ".relay-kit" / "state" / "workflow-state.md"
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if "Current main baseline" not in line or "`" not in line:
            continue
        parts = line.split("`")
        if len(parts) >= 2:
            return parts[1].strip()
    return ""


def build_context_audit(root: Path | str, *, stale_days: int = 30) -> dict[str, Any]:
    project = Path(root).resolve()
    sources = [
        source_metadata(spec.path, project / spec.path, stale_days=stale_days, required=spec.required, label=spec.label)
        for spec in CONTEXT_SOURCES
    ]
    findings: list[dict[str, Any]] = []
    for source in sources:
        if source["required"] and not source["exists"]:
            findings.append(
                {
                    "id": "missing-context-source",
                    "status": "hold",
                    "path": source["path"],
                    "summary": f"required context source is missing: {source['path']}",
                }
            )
        if source["required"] and source["stale"]:
            findings.append(
                {
                    "id": "stale-context-source",
                    "status": "attention",
                    "path": source["path"],
                    "summary": f"context source is older than {stale_days} days: {source['path']}",
                }
            )

    branch = current_git_branch(project)
    baseline = workflow_state_main_baseline(project)
    head = current_git_head(project)
    baseline_is_current = False
    if baseline and head:
        baseline_is_current = baseline == head or head.startswith(baseline) or is_ancestor(project, baseline, head)
    if branch == "main" and baseline and head and not baseline_is_current:
        findings.append(
            {
                "id": "stale-main-baseline",
                "status": "attention",
                "path": ".relay-kit/state/workflow-state.md",
                "summary": "workflow-state main baseline does not match current git HEAD",
                "details": {"workflow_state_baseline": baseline, "head_sha": head},
            }
        )

    status = "hold" if any(finding["status"] == "hold" for finding in findings) else ("attention" if findings else "pass")
    summary = {
        "total_sources": len(sources),
        "authoritative_sources": sum(1 for source in sources if source["source_type"] == "authoritative"),
        "recent_sources": sum(1 for source in sources if source["source_type"] == "recent"),
        "stale_sources": sum(1 for source in sources if source["stale"]),
        "missing_sources": sum(1 for source in sources if source["required"] and source["source_type"] == "missing"),
        "optional_missing_sources": sum(1 for source in sources if not source["required"] and source["source_type"] == "missing"),
        "inferred_sources": sum(1 for source in sources if source["source_type"] == "inferred"),
        "findings": len(findings),
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "project_path": str(project),
        "stale_days": stale_days,
        "summary": summary,
        "sources": sources,
        "findings": findings,
    }


def render_context_audit(report: dict[str, Any]) -> str:
    lines = [
        "Relay-kit context audit",
        f"- status: {report['status']}",
        f"- sources: {report['summary']['total_sources']}",
        f"- stale sources: {report['summary']['stale_sources']}",
        f"- missing sources: {report['summary']['missing_sources']}",
        f"- findings: {report['summary']['findings']}",
    ]
    for finding in report.get("findings", []):
        lines.append(f"  - {finding.get('summary', finding.get('id', 'finding'))}")
    return "\n".join(lines)


def write_context_audit(root: Path | str, report: dict[str, Any], output_file: Path | str | None = None) -> Path:
    project = Path(root).resolve()
    target = Path(output_file) if output_file else project / ".relay-kit" / "context" / "context-audit.json"
    if not target.is_absolute():
        target = project / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return target
