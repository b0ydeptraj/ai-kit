from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from relay_kit_v3.registry.skills import ALL_V3_SKILLS


PROFILE_SCHEMA_VERSION = "relay-kit.skill-competency.v1"
CATALOG_SCHEMA_VERSION = "relay-kit.competency-catalog.v1"
RESOURCE_ROOT = Path(__file__).resolve().parent / "skill_resources"
MIN_CORE_COMPETENCIES = 5
MIN_FAILURE_TRAPS = 2


@dataclass(frozen=True)
class CompetencyTemplate:
    category: str
    competencies: tuple[tuple[str, str, tuple[str, ...], tuple[str, ...]], ...]
    traps: tuple[tuple[str, str], ...]


TEMPLATES: dict[str, CompetencyTemplate] = {
    "routing-orchestration": CompetencyTemplate(
        "routing-orchestration",
        (
            ("intent-routing", "Choose the right next skill from a compact or ambiguous request.", ("route", "intent", "skill"), ("orchestrator", "unknown-domain")),
            ("ask-act-scout", "Decide whether to act, ask one question, or scout first.", ("ask", "act", "scout"), ("orchestrator", "repo-analysis")),
            ("state-handoff", "Use workflow state and handoff evidence before changing direction.", ("state", "handoff", "evidence"), ("long-running-lane",)),
            ("coordination-boundary", "Keep lane ownership and parallel work boundaries explicit.", ("ownership", "parallel", "boundary"), ("multi-agent",)),
            ("claim-discipline", "Separate proven facts from residual risk and missing evidence.", ("verified", "residual risk", "missing evidence"), ("all",)),
        ),
        (
            ("route-from-name-only", "Routes from skill name or popularity instead of request evidence."),
            ("multi-step-overclaim", "Claims a lane is ready without state, tests, or handoff proof."),
        ),
    ),
    "implementation": CompetencyTemplate(
        "implementation",
        (
            ("scope-control", "Keep edits bounded to the accepted story or fix.", ("scope", "changed files", "blast radius"), ("codebase",)),
            ("context-before-edit", "Read relevant files, tests, and contracts before editing.", ("read first", "source files", "tests"), ("codebase",)),
            ("test-evidence", "Tie completion to focused and risk-scaled verification.", ("test", "verification", "regression"), ("codebase",)),
            ("rollback-note", "Name rollback or recovery path for risky changes.", ("rollback", "recovery", "residual risk"), ("release",)),
            ("handoff-quality", "Produce a clear handoff with changed files and remaining risk.", ("handoff", "changed files", "risk"), ("multi-agent",)),
        ),
        (
            ("edit-before-context", "Edits before reading the relevant source and tests."),
            ("completion-without-proof", "Says done without a command, artifact, or observed proof."),
        ),
    ),
    "debugging": CompetencyTemplate(
        "debugging",
        (
            ("fresh-reproduction", "Start from a failing command, log, or observed mismatch.", ("reproduction", "failure", "log"), ("bugfix",)),
            ("hypothesis-pruning", "Test one hypothesis at a time and reject alternatives with evidence.", ("hypothesis", "root cause", "evidence"), ("bugfix",)),
            ("affected-surface", "Map affected files, tests, and downstream behavior.", ("affected files", "tests", "blast radius"), ("codebase",)),
            ("fix-verification", "Verify the fix with the original failure mode and regressions.", ("passing", "regression", "verification"), ("bugfix",)),
            ("residual-risk", "Name what remains unverified after the local fix.", ("residual risk", "unverified", "next check"), ("all",)),
        ),
        (
            ("fix-from-symptom", "Patches the symptom without proving the cause."),
            ("broad-debug-checklist", "Returns a generic checklist instead of file-specific evidence."),
        ),
    ),
    "api-integration": CompetencyTemplate(
        "api-integration",
        (
            ("client-endpoint-contract", "Map client, endpoint, and request/response contracts.", ("client", "endpoint", "request", "response"), ("backend-api", "api-client")),
            ("auth-scope", "Check auth, token, permission, and secret handling.", ("auth", "token", "scope"), ("api-client", "security-policy")),
            ("retry-rate-limit", "Handle retry, backoff, timeout, and rate-limit behavior.", ("retry", "backoff", "rate limit"), ("api-client", "automation-worker")),
            ("idempotency", "Protect writes, webhooks, and replayed requests with idempotency.", ("idempotency", "webhook", "replay"), ("backend-api", "commerce-api")),
            ("contract-test-anchor", "Find or require contract, integration, or fixture evidence.", ("contract test", "integration test", "fixture"), ("backend-api",)),
        ),
        (
            ("checklist-without-contract", "Mentions API advice without naming the contract surface."),
            ("retry-without-idempotency", "Adds retry language without replay or idempotency evidence."),
        ),
    ),
    "data-persistence": CompetencyTemplate(
        "data-persistence",
        (
            ("schema-model", "Map schema, model, repository, and storage ownership.", ("schema", "model", "repository"), ("database-heavy",)),
            ("transaction-boundary", "Identify transaction, isolation, rollback, and consistency boundaries.", ("transaction", "rollback", "consistency"), ("database-heavy",)),
            ("migration-safety", "Check migration path, reversibility, and data backfill risk.", ("migration", "backfill", "reversible"), ("database-heavy",)),
            ("cache-index-query", "Inspect cache invalidation, indexes, and query behavior.", ("cache", "index", "query"), ("database-heavy", "backend-api")),
            ("persistence-test-anchor", "Find tests or fixtures proving persistence behavior.", ("test", "fixture", "database"), ("database-heavy",)),
        ),
        (
            ("schema-only-review", "Reviews schema shape without transaction or migration evidence."),
            ("query-claim-without-test", "Claims data behavior without test, fixture, or query proof."),
        ),
    ),
    "dependency-management": CompetencyTemplate(
        "dependency-management",
        (
            ("dependency-drift", "Detect version drift across declared packages, lockfiles, and installed or runtime evidence.", ("dependency drift", "lockfile", "declared package"), ("library-core", "backend-api", "frontend-app")),
            ("source-of-truth", "Choose package manifests and lockfiles as the dependency source of truth before advice.", ("source of truth", "package manifest", "lockfile"), ("library-core", "backend-api", "frontend-app")),
            ("upgrade-risk", "Assess upgrade, downgrade, transitive dependency, and compatibility risk.", ("upgrade risk", "transitive", "compatibility"), ("library-core", "backend-api", "frontend-app")),
            ("supply-chain-boundary", "Check supply-chain, script, registry, and checksum boundaries without running install hooks.", ("supply-chain", "install script", "registry"), ("security-policy", "library-core")),
            ("rollback-pin-strategy", "Name rollback, pin, lockfile restore, or staged rollout evidence before completion.", ("rollback", "pin", "staged rollout"), ("release", "library-core")),
        ),
        (
            ("latest-version-chasing", "Recommends latest versions without lockfile or source-of-truth evidence."),
            ("install-hook-blindness", "Runs or trusts install scripts without supply-chain review."),
        ),
    ),
    "go-service-engineering": CompetencyTemplate(
        "go-service-engineering",
        (
            ("handler-service-boundary", "Map handler, service, repository, and request lifecycle ownership.", ("handler boundary", "service boundary", "request lifecycle"), ("backend-api",)),
            ("context-cancellation", "Preserve context cancellation, deadlines, and timeout behavior across service calls.", ("context cancellation", "deadline", "timeout"), ("backend-api", "automation-worker")),
            ("middleware-job-ownership", "Separate middleware, background jobs, and worker ownership from request handlers.", ("middleware", "job ownership", "worker"), ("backend-api", "automation-worker")),
            ("transaction-cache-boundary", "Name transaction, repository, and cache boundaries before changing service behavior.", ("transaction boundary", "cache boundary", "repository"), ("backend-api", "database-heavy")),
            ("httptest-integration-evidence", "Tie service changes to httptest, integration tests, or fixture evidence.", ("httptest", "integration test", "test fixture"), ("backend-api", "test-runner")),
        ),
        (
            ("handler-only-review", "Reviews only handlers while missing service, repository, transaction, or cache boundaries."),
            ("context-ignored", "Ignores cancellation, deadlines, or timeout propagation in Go service paths."),
        ),
    ),
    "testing-patterns": CompetencyTemplate(
        "testing-patterns",
        (
            ("fixture-factory-strategy", "Choose fixture, factory, and test data strategy based on the failure mode.", ("fixture", "factory", "test data"), ("test-runner",)),
            ("mock-integration-boundary", "Separate mock, integration, contract, and end-to-end boundaries.", ("mock", "integration boundary", "contract"), ("test-runner", "backend-api", "frontend-app")),
            ("regression-anchor", "Anchor tests to the regression, bug, or risk being proven.", ("regression", "failure mode", "test anchor"), ("test-runner",)),
            ("flake-control", "Control flakes with deterministic setup, isolation, and stable assertions.", ("flake", "deterministic", "isolation"), ("test-runner", "ci-devops")),
            ("risk-coverage-map", "Map coverage decisions to risk, edge cases, and blast radius.", ("coverage", "risk", "edge case"), ("test-runner", "release")),
        ),
        (
            ("coverage-count-over-risk", "Treats coverage percentage as proof without mapping it to risk."),
            ("mock-everything", "Mocks away the behavior that should be proven by integration or contract evidence."),
        ),
    ),
    "repo-map": CompetencyTemplate(
        "repo-map",
        (
            ("entrypoint-map", "Map entrypoints, main routes, commands, and runtime roots before deeper analysis.", ("entrypoint", "main", "route"), ("repo-analysis", "backend-api", "frontend-app", "cli-tool")),
            ("ownership-boundary", "Identify module ownership, boundaries, and handoff candidates.", ("ownership", "boundary", "module"), ("repo-analysis",)),
            ("dependency-direction", "Trace import, call graph, and dependency direction instead of dumping the tree.", ("dependency direction", "import", "call graph"), ("repo-analysis", "large-context")),
            ("test-doc-adjacency", "Connect source files to nearby tests, docs, config, and contracts.", ("nearby test", "docs", "config"), ("repo-analysis", "test-runner")),
            ("scout-handoff", "Hand off unknown or risky areas to the next skill with evidence and gaps.", ("handoff", "next skill", "unknown"), ("repo-analysis", "unknown-domain")),
        ),
        (
            ("tree-dump-without-meaning", "Lists files without explaining ownership, entrypoints, or dependency direction."),
            ("ownership-guess", "Guesses ownership from filenames without import, docs, or test adjacency evidence."),
        ),
    ),
    "frontend-product": CompetencyTemplate(
        "frontend-product",
        (
            ("route-component-boundary", "Map route, component, server/client, and data boundaries.", ("route", "component", "boundary"), ("frontend-app",)),
            ("state-error-loading", "Handle state, error, loading, and empty states.", ("state", "error", "loading"), ("frontend-app",)),
            ("visual-accessibility", "Check visual quality, accessibility, and responsive behavior.", ("visual", "accessibility", "responsive"), ("frontend-app",)),
            ("frontend-test-anchor", "Find component, smoke, or end-to-end test evidence.", ("component test", "smoke", "e2e"), ("frontend-app",)),
            ("ux-flow-evidence", "Tie UI choices to the user workflow and information hierarchy.", ("workflow", "hierarchy", "user"), ("frontend-app", "docs-product")),
        ),
        (
            ("pretty-without-flow", "Optimizes visual surface without proving the workflow works."),
            ("responsive-claim-without-check", "Claims responsive/accessibility quality without evidence."),
        ),
    ),
    "browser-inspector": CompetencyTemplate(
        "browser-inspector",
        (
            ("console-network-evidence", "Capture console, network, request, and response evidence for the runtime issue.", ("console", "network", "request"), ("frontend-app", "browser-runtime")),
            ("dom-state-trace", "Tie UI observations to DOM, selector, state, and interaction sequence.", ("dom", "selector", "state"), ("frontend-app", "browser-runtime")),
            ("screenshot-video-artifact", "Attach screenshot, video, or visual artifact evidence when runtime UI matters.", ("screenshot", "video", "artifact"), ("frontend-app", "browser-runtime")),
            ("browser-state-isolation", "Control browser state, cookies, storage, viewport, and session isolation.", ("browser state", "cookies", "local storage"), ("frontend-app", "browser-runtime")),
            ("runtime-handoff", "Produce a reproduction trace and frontend handoff instead of screenshot-only feedback.", ("reproduction trace", "frontend handoff", "runtime evidence"), ("frontend-app", "browser-runtime")),
        ),
        (
            ("screenshot-only", "Shows a screenshot without console, network, DOM, or reproduction trace evidence."),
            ("network-log-without-repro", "Mentions network logs without tying them to user action and page state."),
        ),
    ),
    "automation-ops": CompetencyTemplate(
        "automation-ops",
        (
            ("scheduler-queue", "Map scheduler, queue, worker, and trigger ownership.", ("scheduler", "queue", "worker"), ("automation-worker", "ci-devops")),
            ("dry-run-rollback", "Require dry-run and rollback evidence before enabling automation.", ("dry-run", "rollback", "enable"), ("automation-worker",)),
            ("idempotent-retry", "Design idempotency, dedupe, retry, and backoff behavior.", ("idempotency", "dedupe", "retry"), ("automation-worker",)),
            ("execution-history", "Record execution logs, run ids, and operator-visible status.", ("execution history", "run id", "status"), ("automation-worker",)),
            ("operator-runbook", "Produce runbook, ownership, and failure handling.", ("runbook", "owner", "failure"), ("automation-worker", "ci-devops")),
        ),
        (
            ("automation-without-dry-run", "Enables automation without dry-run or rollback evidence."),
            ("queue-without-idempotency", "Designs queues without dedupe or replay safety."),
        ),
    ),
    "policy-security": CompetencyTemplate(
        "policy-security",
        (
            ("policy-rule-map", "Map policy, rule, allowlist, and blocked operation surfaces.", ("policy", "rule", "allowlist"), ("security-policy",)),
            ("secret-scope", "Detect secret, token, and permission-scope risk.", ("secret", "token", "permission"), ("security-policy", "api-client")),
            ("fail-closed", "Fail closed on high-risk shell, path, prompt, or release actions.", ("fail closed", "blocked", "risk"), ("security-policy",)),
            ("audit-evidence", "Tie findings to static check, audit, or trusted manifest evidence.", ("audit", "manifest", "static check"), ("security-policy",)),
            ("exception-review", "Escalate intentional exceptions with owner and residual risk.", ("exception", "owner", "residual risk"), ("security-policy",)),
        ),
        (
            ("policy-warning-only", "Reports policy risk without blocking or escalation path."),
            ("secret-blind-review", "Ignores token, secret, or permission scope evidence."),
        ),
    ),
    "research-product": CompetencyTemplate(
        "research-product",
        (
            ("source-triangulation", "Use multiple sources or artifacts before making a claim.", ("source", "artifact", "evidence"), ("docs-product", "unknown-domain")),
            ("audience-fit", "Adapt output to the user, buyer, operator, or maintainer audience.", ("audience", "user", "operator"), ("docs-product",)),
            ("decision-criteria", "State decision criteria, tradeoffs, and confidence.", ("criteria", "tradeoff", "confidence"), ("planning",)),
            ("claim-boundary", "Label unknowns, stale facts, and unverified assumptions.", ("unknown", "unverified", "assumption"), ("all",)),
            ("actionable-output", "Produce next actions, artifacts, or acceptance criteria.", ("next action", "artifact", "acceptance"), ("planning",)),
        ),
        (
            ("unsupported-market-claim", "Makes a market/product claim without evidence."),
            ("generic-persona-output", "Produces persona or plan text without decision criteria."),
        ),
    ),
    "context-continuity": CompetencyTemplate(
        "context-continuity",
        (
            ("state-retrieval", "Find current state, prior decisions, and handoff breadcrumbs.", ("state", "memory", "handoff"), ("long-running-lane",)),
            ("freshness-check", "Separate current evidence from stale or historical context.", ("freshness", "stale", "current"), ("long-running-lane",)),
            ("context-pack", "Pack only task-relevant files, evidence, and constraints.", ("context pack", "relevant", "constraints"), ("large-context",)),
            ("token-budget", "Preserve raw-required evidence while compressing low-signal context.", ("token", "raw-required", "compress"), ("large-context",)),
            ("resume-safety", "Resume without losing the newest user request or active lane.", ("resume", "newest request", "active lane"), ("long-running-lane",)),
        ),
        (
            ("stale-state-resume", "Continues from stale state while ignoring newer user input."),
            ("context-dump", "Dumps too much context instead of selecting task-relevant evidence."),
        ),
    ),
    "mmo-safe-ops": CompetencyTemplate(
        "mmo-safe-ops",
        (
            ("profile-inventory", "Maintain profile, account, device, and session inventory.", ("profile", "account", "session"), ("mmo-safe-ops",)),
            ("quota-dedupe", "Use quotas, dedupe keys, and pacing controls.", ("quota", "dedupe", "pacing"), ("mmo-safe-ops",)),
            ("policy-safe-api", "Prefer official APIs and policy-safe execution boundaries.", ("official api", "policy", "scope"), ("mmo-safe-ops",)),
            ("operator-ledger", "Record redacted logs, run queues, and operator decisions.", ("ledger", "queue", "redacted"), ("mmo-safe-ops",)),
            ("manual-review-gate", "Escalate risky or ambiguous actions to manual review.", ("manual review", "risk", "approval"), ("mmo-safe-ops",)),
        ),
        (
            ("platform-risk-blindness", "Ignores platform policy, consent, or quota boundaries."),
            ("bulk-action-without-ledger", "Designs bulk operations without audit or rollback evidence."),
        ),
    ),
}


SKILL_CATEGORY_OVERRIDES: dict[str, str] = {
    "api-integration": "api-integration",
    "data-persistence": "data-persistence",
    "automation-ops": "automation-ops",
    "policy-guard": "policy-security",
    "architect": "implementation",
    "bootstrap": "context-continuity",
    "brainstorm": "research-product",
    "brainstorm-hub": "research-product",
    "browser-inspector": "browser-inspector",
    "dependency-management": "dependency-management",
    "project-architecture": "implementation",
    "developer": "implementation",
    "execution-loop": "implementation",
    "fix-hub": "implementation",
    "go-service-engineering": "go-service-engineering",
    "impact-radar": "implementation",
    "repo-map": "repo-map",
    "scout-hub": "implementation",
    "test-first-development": "implementation",
    "debug-hub": "debugging",
    "root-cause-debugging": "debugging",
    "review-hub": "debugging",
    "test-hub": "debugging",
    "testing-patterns": "testing-patterns",
    "next-product-frontend": "frontend-product",
    "frontend-design": "frontend-product",
    "accessibility-review": "frontend-product",
    "ux-structure": "frontend-product",
    "ui-styling": "frontend-product",
    "context-continuity": "context-continuity",
    "cook": "context-continuity",
    "memory-search": "context-continuity",
    "handoff-context": "context-continuity",
    "token-economy": "context-continuity",
    "analyst": "research-product",
    "growth-marketing": "research-product",
    "market-research": "research-product",
    "plan-hub": "research-product",
    "pm": "research-product",
    "scrum-master": "research-product",
    "vietnamese-product-localization": "research-product",
    "workflow-router": "routing-orchestration",
    "team": "routing-orchestration",
}


def category_for_skill(skill_name: str) -> str:
    if skill_name in SKILL_CATEGORY_OVERRIDES:
        return SKILL_CATEGORY_OVERRIDES[skill_name]
    spec = ALL_V3_SKILLS[skill_name]
    haystack = " ".join(
        str(value).casefold()
        for value in [skill_name, getattr(spec, "role", ""), getattr(spec, "description", "")]
    )
    if skill_name.startswith("mmo-"):
        return "mmo-safe-ops"
    if any(term in haystack for term in ("api", "webhook", "endpoint", "network")):
        return "api-integration"
    if any(term in haystack for term in ("schema", "database", "persistence", "cache", "transaction")):
        return "data-persistence"
    if any(term in haystack for term in ("automation", "workflow", "queue", "scheduler", "runbook")):
        return "automation-ops"
    if any(term in haystack for term in ("policy", "security", "guard", "secret", "risk")):
        return "policy-security"
    if any(term in haystack for term in ("debug", "failure", "regression", "root-cause")):
        return "debugging"
    if any(term in haystack for term in ("frontend", "ui", "accessibility", "visual", "browser")):
        return "frontend-product"
    if any(term in haystack for term in ("context", "memory", "handoff", "token", "continuity")):
        return "context-continuity"
    if any(term in haystack for term in ("research", "market", "product", "localization", "analyst", "pm")):
        return "research-product"
    if any(term in haystack for term in ("developer", "test", "release", "qa", "architecture")):
        return "implementation"
    return "routing-orchestration"


def build_competency_profile(skill_name: str) -> dict[str, Any]:
    if skill_name not in ALL_V3_SKILLS:
        raise ValueError(f"Unknown skill: {skill_name}")
    spec = ALL_V3_SKILLS[skill_name]
    category = category_for_skill(skill_name)
    template = TEMPLATES[category]
    competencies = [
        {
            "id": f"{category}.{slug}",
            "label": label,
            "evidence_terms": list(terms),
            "archetypes": list(archetypes),
        }
        for slug, label, terms, archetypes in template.competencies
    ]
    traps = [{"id": f"{category}.{slug}", "description": description} for slug, description in template.traps]
    return {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "skill": skill_name,
        "role": getattr(spec, "role", ""),
        "category": category,
        "core_competencies": competencies,
        "failure_traps": traps,
        "unknown_domain_policy": "scout_first_without_expert_claim",
        "claim_policy": "competency-covered only when every core competency is present and battle evidence passes.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def competency_profile_path(skill_name: str, resource_root: Path | None = None) -> Path:
    root = resource_root or RESOURCE_ROOT
    return root / skill_name / "competencies" / f"{skill_name}-competencies.json"


def load_competency_profile(skill_name: str, resource_root: Path | None = None) -> dict[str, Any]:
    path = competency_profile_path(skill_name, resource_root)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    profile = build_competency_profile(skill_name)
    profile["source"] = "generated-fallback"
    return profile


def validate_competency_profile(profile: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []
    if profile.get("schema_version") != PROFILE_SCHEMA_VERSION:
        findings.append("invalid-schema-version")
    if profile.get("source") == "generated-fallback":
        findings.append("missing-competency-resource")
    competencies = profile.get("core_competencies", [])
    traps = profile.get("failure_traps", [])
    if len(competencies) < MIN_CORE_COMPETENCIES:
        findings.append("too-few-core-competencies")
    if len(traps) < MIN_FAILURE_TRAPS:
        findings.append("too-few-failure-traps")
    ids = [str(item.get("id", "")) for item in competencies if isinstance(item, Mapping)]
    if len(set(ids)) != len(ids):
        findings.append("duplicate-competency-id")
    for item in competencies:
        if not isinstance(item, Mapping):
            findings.append("invalid-competency-shape")
            continue
        if not item.get("evidence_terms"):
            findings.append(f"missing-evidence-terms:{item.get('id')}")
    return findings


def competency_coverage_for_skill(skill_name: str, resource_root: Path | None = None) -> dict[str, Any]:
    profile = load_competency_profile(skill_name, resource_root)
    findings = validate_competency_profile(profile)
    competencies = [str(item.get("id")) for item in profile.get("core_competencies", []) if isinstance(item, Mapping)]
    covered = competencies if not findings else []
    missing = [] if not findings else competencies
    return {
        "skill": skill_name,
        "category": profile.get("category"),
        "covered_competencies": covered,
        "missing_competencies": missing,
        "coverage_score": round(len(covered) / max(len(competencies), 1), 3),
        "unknown_domain_mode": False,
        "findings": findings,
    }


def build_competency_catalog(resource_root: Path | None = None) -> dict[str, Any]:
    profiles = [load_competency_profile(skill_name, resource_root) for skill_name in sorted(ALL_V3_SKILLS)]
    findings = [
        {"skill": str(profile.get("skill")), "finding": finding}
        for profile in profiles
        for finding in validate_competency_profile(profile)
    ]
    return {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "status": "pass" if not findings else "fail",
        "skill_count": len(profiles),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "profiles": profiles,
        "findings": findings,
    }


def write_competency_profiles(resource_root: Path | None = None) -> list[Path]:
    root = resource_root or RESOURCE_ROOT
    written: list[Path] = []
    for skill_name in sorted(ALL_V3_SKILLS):
        profile = build_competency_profile(skill_name)
        path = competency_profile_path(skill_name, root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(profile, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
        written.append(path)
    return written


def normalize_competency_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
