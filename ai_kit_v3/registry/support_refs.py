from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class SupportReference:
    name: str
    path: str
    purpose: str
    sections: List[str]
    used_by: List[str]


SUPPORT_REFERENCES: Dict[str, SupportReference] = {
    "project-architecture": SupportReference(
        name="project-architecture",
        path=".relay-kit/references/project-architecture.md",
        purpose="Capture the actual layer structure, entrypoints, module boundaries, dependency direction, and architecture drift observed in the current codebase.",
        sections=[
            "Entry points and execution flow",
            "Layer or package structure",
            "Module responsibilities",
            "Dependency direction and boundaries",
            "Architecture drift and hotspots",
            "Files to mirror when adding new work",
        ],
        used_by=["architect", "developer", "code-review"],
    ),
    "dependency-management": SupportReference(
        name="dependency-management",
        path=".relay-kit/references/dependency-management.md",
        purpose="Record the package manager, lockfiles, environment rules, dependency pinning policy, upgrade conventions, and how new dependencies should be added safely.",
        sections=[
            "Package manager and lockfiles",
            "Environment and toolchain setup",
            "Version pinning and upgrade policy",
            "Dev vs prod dependencies",
            "How to add a new dependency",
            "Known dependency risks",
        ],
        used_by=["architect", "developer", "qa-governor"],
    ),
    "api-integration": SupportReference(
        name="api-integration",
        path=".relay-kit/references/api-integration.md",
        purpose="Document HTTP or RPC clients, authentication, retry and timeout behavior, request or response shapes, error mapping, and test doubles for external integrations.",
        sections=[
            "Clients, transports, and endpoints",
            "Authentication and secret handling",
            "Retry, timeout, and idempotency rules",
            "Request and response patterns",
            "Error mapping and recovery",
            "Testing and mocking approach",
        ],
        used_by=["architect", "developer", "qa-governor"],
    ),
    "data-persistence": SupportReference(
        name="data-persistence",
        path=".relay-kit/references/data-persistence.md",
        purpose="Describe storage engines, schema or model locations, repository patterns, migrations, caching, transactions, and data consistency expectations.",
        sections=[
            "Stores and connection points",
            "Schemas, models, and repositories",
            "Migrations and schema evolution",
            "Transactions and consistency",
            "Caching and invalidation",
            "Data risks and rollback notes",
        ],
        used_by=["architect", "developer", "qa-governor"],
    ),
    "testing-patterns": SupportReference(
        name="testing-patterns",
        path=".relay-kit/references/testing-patterns.md",
        purpose="Capture the project test framework, folder rules, fixtures, mocking conventions, async testing patterns, and the command matrix for collecting evidence.",
        sections=[
            "Frameworks and folder rules",
            "Fixture and factory patterns",
            "Mocking and dependency isolation",
            "Async or integration testing rules",
            "Commands for local evidence",
            "Coverage gaps and brittle areas",
        ],
        used_by=["developer", "qa-governor", "code-review"],
    ),
    "security-patterns": SupportReference(
        name="security-patterns",
        path=".relay-kit/references/security-patterns.md",
        purpose="Capture repo-specific authentication boundaries, authorization checks, secret handling rules, input validation expectations, sensitive logging constraints, and the highest-risk security failure modes.",
        sections=[
            "Auth and trust boundaries",
            "Secrets and configuration hygiene",
            "Input validation and output encoding",
            "Sensitive data handling and logging rules",
            "Dependency and supply-chain watchpoints",
            "Security review hotspots",
        ],
        used_by=["architect", "developer", "qa-governor", "review-hub"],
    ),
    "logging-observability": SupportReference(
        name="logging-observability",
        path=".relay-kit/references/logging-observability.md",
        purpose="Document how this codebase emits logs, metrics, traces, health signals, alerts, and other runtime evidence so debugging and review work can rely on concrete signals instead of guesswork.",
        sections=[
            "Logs, metrics, traces, and health signals",
            "Where to inspect runtime evidence",
            "Structured logging and correlation rules",
            "Alerting, dashboards, and noisy signals",
            "Common blind spots during debugging",
            "Observability follow-ups when behavior changes",
        ],
        used_by=["developer", "debug-hub", "review-hub", "qa-governor", "test-hub"],
    ),
    "performance-optimization": SupportReference(
        name="performance-optimization",
        path=".relay-kit/references/performance-optimization.md",
        purpose="Record the codebase-specific performance budget, hot paths, profiling tools, query or rendering bottlenecks, and the rules for proving a performance claim with evidence.",
        sections=[
            "Performance-sensitive paths",
            "Budgets, SLOs, and user-facing thresholds",
            "Profiling and measurement commands",
            "Known bottlenecks and regression traps",
            "Caching, batching, and concurrency rules",
            "Evidence required before claiming an optimization",
        ],
        used_by=["architect", "developer", "debug-hub", "review-hub", "qa-governor"],
    ),
}


def render_support_reference(doc: SupportReference) -> str:
    lines = [
        f"# {doc.name}",
        "",
        f"> Path: `{doc.path}`",
        f"> Purpose: {doc.purpose}",
        f"> Used by: {', '.join(doc.used_by)}",
        "",
    ]
    for section in doc.sections:
        lines.append(f"## {section}")
        lines.append("Record only codebase-specific facts, current conventions, or open risks. Include file paths when possible.")
        lines.append("")
        lines.append("TBD")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"

