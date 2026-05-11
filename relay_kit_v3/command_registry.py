from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


SCHEMA_VERSION = "relay-kit.command-diagnostics.v1"

ADAPTER_COMMAND_ROOTS: dict[str, dict[str, str]] = {
    "codex": {"path": ".codex/commands", "display": "Codex"},
    "claude": {"path": ".claude/commands", "display": "Claude"},
    "agent": {"path": ".agent/commands", "display": "Agent/Antigravity"},
}

GENERATION_TARGETS = {
    "codex": ["codex"],
    "claude": ["claude"],
    "antigravity": ["agent"],
    "all": ["codex", "claude", "agent"],
}


@dataclass(frozen=True)
class LifecycleCommandSpec:
    command_id: str
    slash: str
    intent: str
    route_target: str
    expected_evidence: str


LIFECYCLE_COMMANDS: tuple[LifecycleCommandSpec, ...] = (
    LifecycleCommandSpec(
        command_id="relay-start",
        slash="/relay-start",
        intent="Start a request with explicit routing and lane mode.",
        route_target="workflow-router",
        expected_evidence="workflow-state updated with selected track, hub, and next skill.",
    ),
    LifecycleCommandSpec(
        command_id="relay-brief",
        slash="/relay-brief",
        intent="Turn a rough ask into a brief before planning depth increases.",
        route_target="brainstorm-hub",
        expected_evidence="problem framing, initial constraints, and candidate direction.",
    ),
    LifecycleCommandSpec(
        command_id="relay-plan",
        slash="/relay-plan",
        intent="Build implementation-ready plan artifacts and slice sequence.",
        route_target="plan-hub",
        expected_evidence="updated plan artifacts with acceptance and delivery order.",
    ),
    LifecycleCommandSpec(
        command_id="relay-architect",
        slash="/relay-architect",
        intent="Resolve architecture-level decisions for the selected slice.",
        route_target="architect",
        expected_evidence="architecture notes with boundaries, tradeoffs, and risk calls.",
    ),
    LifecycleCommandSpec(
        command_id="relay-build",
        slash="/relay-build",
        intent="Execute implementation changes in the active lane.",
        route_target="developer",
        expected_evidence="scoped code edits plus matching verification output.",
    ),
    LifecycleCommandSpec(
        command_id="relay-test",
        slash="/relay-test",
        intent="Run verification and route-quality checks for the active change.",
        route_target="test-hub",
        expected_evidence="test and gate output mapped to acceptance criteria.",
    ),
    LifecycleCommandSpec(
        command_id="relay-review",
        slash="/relay-review",
        intent="Run coherence and readiness review before completion claims.",
        route_target="review-hub",
        expected_evidence="review findings or explicit pass with residual risks.",
    ),
    LifecycleCommandSpec(
        command_id="relay-ship",
        slash="/relay-ship",
        intent="Prepare release-readiness and deployment safety checks.",
        route_target="release-readiness",
        expected_evidence="release readiness checklist with smoke and rollback status.",
    ),
    LifecycleCommandSpec(
        command_id="relay-support",
        slash="/relay-support",
        intent="Prepare support-ready triage and completion confidence signals.",
        route_target="qa-governor",
        expected_evidence="qa/support posture with blocker severity and next actions.",
    ),
    LifecycleCommandSpec(
        command_id="relay-research",
        slash="/relay-research",
        intent="Collect focused evidence for product or technical uncertainty.",
        route_target="research",
        expected_evidence="ranked source findings and decision-impact summary.",
    ),
    LifecycleCommandSpec(
        command_id="relay-grow",
        slash="/relay-grow",
        intent="Drive growth and launch execution for product adoption work.",
        route_target="growth-marketing",
        expected_evidence="positioning, funnel metrics, and campaign QA notes.",
    ),
    LifecycleCommandSpec(
        command_id="relay-automate",
        slash="/relay-automate",
        intent="Design safe workflow automation and operations runbooks.",
        route_target="automation-ops",
        expected_evidence="dry-run, rollback, and owner-aware automation plan.",
    ),
    LifecycleCommandSpec(
        command_id="relay-token-audit",
        slash="/relay-token-audit",
        intent="Audit token budget, compression safety, and signal retention before execution.",
        route_target="token-economy",
        expected_evidence="token audit report with budget violations, raw pointers, and retention metrics.",
    ),
)


def lifecycle_commands() -> list[LifecycleCommandSpec]:
    return list(LIFECYCLE_COMMANDS)


def lifecycle_command_records() -> list[dict[str, str]]:
    return [
        {
            "id": command.command_id,
            "slash": command.slash,
            "intent": command.intent,
            "route_target": command.route_target,
            "expected_evidence": command.expected_evidence,
        }
        for command in LIFECYCLE_COMMANDS
    ]


def command_ids() -> list[str]:
    return [command.command_id for command in LIFECYCLE_COMMANDS]


def render_command_surface(command: LifecycleCommandSpec, *, adapter: str) -> str:
    return (
        f"# {command.slash}\n\n"
        f"- command-id: `{command.command_id}`\n"
        f"- adapter: `{adapter}`\n"
        f"- route-target: `{command.route_target}`\n\n"
        "## Intent\n\n"
        f"{command.intent}\n\n"
        "## Expected Evidence\n\n"
        f"{command.expected_evidence}\n\n"
        "## Routing Contract\n\n"
        f"- Entry command: `{command.slash}`\n"
        f"- Delegate to: `{command.route_target}`\n"
        "- Keep skills and hubs as authoritative workflow units.\n"
    )


def emit_command_surfaces(project_path: Path | str, ai: str) -> list[Path]:
    project = Path(project_path).resolve()
    if ai not in GENERATION_TARGETS:
        return []
    written: list[Path] = []
    for adapter in GENERATION_TARGETS[ai]:
        adapter_root = project / ADAPTER_COMMAND_ROOTS[adapter]["path"]
        adapter_root.mkdir(parents=True, exist_ok=True)
        for command in LIFECYCLE_COMMANDS:
            output = adapter_root / f"{command.command_id}.md"
            output.write_text(render_command_surface(command, adapter=adapter), encoding="utf-8")
            written.append(output)
    return written


def build_command_diagnostics(root: Path | str, *, adapter: str = "all") -> dict[str, Any]:
    project = Path(root).resolve()
    selected = _selected_adapters(adapter)
    expected = command_ids()
    expected_set = set(expected)
    findings: list[dict[str, Any]] = []
    adapter_reports: list[dict[str, Any]] = []

    for adapter_name in selected:
        config = ADAPTER_COMMAND_ROOTS[adapter_name]
        relative_root = config["path"]
        command_root = project / relative_root
        existing = _command_files(command_root)
        missing = sorted(expected_set - existing)
        unexpected = sorted(existing - expected_set)

        for command_id in missing:
            findings.append(
                {
                    "id": "missing-command",
                    "status": "hold",
                    "adapter": adapter_name,
                    "path": f"{relative_root}/{command_id}.md",
                    "command_id": command_id,
                    "summary": f"{adapter_name} is missing generated command {command_id}",
                }
            )
        for command_id in unexpected:
            findings.append(
                {
                    "id": "unexpected-command",
                    "status": "hold",
                    "adapter": adapter_name,
                    "path": f"{relative_root}/{command_id}.md",
                    "command_id": command_id,
                    "summary": f"{adapter_name} has unexpected command surface {command_id}",
                }
            )

        adapter_reports.append(
            {
                "adapter": adapter_name,
                "display": config["display"],
                "path": relative_root,
                "expected_command_count": len(expected),
                "generated_command_count": len(existing & expected_set),
                "missing_command_count": len(missing),
                "unexpected_command_count": len(unexpected),
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "hold" if findings else "pass",
        "project_path": str(project),
        "adapter": adapter,
        "summary": {
            "adapter_count": len(adapter_reports),
            "expected_command_count": len(expected),
            "missing_commands": sum(item["missing_command_count"] for item in adapter_reports),
            "unexpected_commands": sum(item["unexpected_command_count"] for item in adapter_reports),
            "findings": len(findings),
        },
        "adapters": adapter_reports,
        "findings": findings,
        "commands": lifecycle_command_records(),
    }


def render_command_diagnostics(report: Mapping[str, Any]) -> str:
    summary = report.get("summary", {})
    lines = [
        "Relay-kit command diagnostics",
        f"- status: {report.get('status')}",
        f"- adapters: {summary.get('adapter_count', 0)}",
        f"- expected commands: {summary.get('expected_command_count', 0)}",
        f"- missing commands: {summary.get('missing_commands', 0)}",
        f"- unexpected commands: {summary.get('unexpected_commands', 0)}",
    ]
    for adapter in report.get("adapters", []):
        lines.append(
            f"  - {adapter.get('adapter')}: generated={adapter.get('generated_command_count')} "
            f"missing={adapter.get('missing_command_count')} "
            f"unexpected={adapter.get('unexpected_command_count')}"
        )
    for finding in report.get("findings", [])[:12]:
        lines.append(f"  - {finding.get('summary', finding.get('id', 'finding'))}")
    return "\n".join(lines)


def write_command_diagnostics(
    root: Path | str,
    report: Mapping[str, Any],
    output_file: Path | str | None = None,
) -> Path:
    project = Path(root).resolve()
    target = Path(output_file) if output_file else project / ".relay-kit" / "commands" / "command-diagnostics.json"
    if not target.is_absolute():
        target = project / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return target


def _selected_adapters(adapter: str) -> list[str]:
    value = str(adapter).strip().lower()
    if value == "antigravity":
        value = "agent"
    if value == "all":
        return ["codex", "claude", "agent"]
    if value not in ADAPTER_COMMAND_ROOTS:
        raise ValueError(f"Unknown adapter: {adapter!r}")
    return [value]


def _command_files(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {
        entry.stem
        for entry in path.iterdir()
        if entry.is_file() and entry.suffix.lower() == ".md"
    }
