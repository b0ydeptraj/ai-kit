from __future__ import annotations

import json
import sys
from pathlib import Path
from textwrap import shorten


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from relay_kit_v3.registry.skills import ALL_V3_SKILLS

RESOURCE_ROOT = ROOT / "relay_kit_v3" / "skill_resources"
SITE_ROOT = ROOT / "docs" / "site"


FAMILY_CASES = {
    "frontend": {
        "repo_profile": "public Next.js product repo with app router, login UI, and Playwright smoke tests",
        "files": ["src/app/login/page.tsx", "src/components/LoginForm.tsx", "tests/login.spec.ts"],
        "symbols": ["LoginForm", "submitLogin", "LoginPage"],
        "terms": ["login flow", "component boundary", "accessibility state", "visual regression"],
        "task": "review a login UI change, name files first, and identify the test evidence before editing",
    },
    "backend": {
        "repo_profile": "public Python service repo with serializer, retry, cache, and session tests",
        "files": ["src/service/session.py", "src/service/retry.py", "tests/test_session.py"],
        "symbols": ["SessionManager", "retry_request", "serialize_session"],
        "terms": ["session", "retry", "cache", "transaction boundary"],
        "task": "trace a backend behavior bug from source file to test anchor without guessing from filenames only",
    },
    "dependency-drift": {
        "repo_profile": "public package repo with package manifest, lockfile, dependency policy, and upgrade notes",
        "files": ["package.json", "pnpm-lock.yaml", "docs/dependency-policy.md", "tests/dependency-lock.test.ts"],
        "symbols": ["resolveDependencyPlan", "LockfileGuard", "DependencyRisk"],
        "terms": ["dependency drift", "lockfile", "transitive dependency", "rollback pin"],
        "traps": ["latest-only advice", "lockfile skipped", "install hook trusted"],
        "task": "review a dependency drift report, compare manifest to lockfile, and name rollback or pin evidence before recommending an upgrade",
    },
    "service-boundary": {
        "repo_profile": "public Go API service with handler, service, repository, middleware, and httptest coverage",
        "files": ["cmd/api/main.go", "internal/http/user_handler.go", "internal/service/user_service.go", "internal/service/user_service_test.go"],
        "symbols": ["UserHandler", "UserService", "TestUserService"],
        "terms": ["handler boundary", "context cancellation", "transaction boundary", "httptest"],
        "traps": ["handler-only review", "context ignored", "transaction skipped"],
        "task": "trace a Go request from handler to service and repo, then identify context cancellation and httptest evidence before changing behavior",
    },
    "test-strategy": {
        "repo_profile": "public test-heavy repo with fixtures, factories, unit tests, integration tests, and a flaky e2e lane",
        "files": ["tests/fixtures/user_factory.py", "tests/integration/test_checkout.py", "tests/unit/test_price_rules.py", "tests/e2e/test_checkout_flow.py"],
        "symbols": ["user_factory", "TestCheckoutFlow", "PriceRuleTest"],
        "terms": ["fixture", "factory", "integration boundary", "flake"],
        "traps": ["coverage percent only", "mock everything", "flake ignored"],
        "task": "design the test strategy for a checkout regression, choosing fixture/factory, mock versus integration, and flake controls by risk",
    },
    "repo-discovery": {
        "repo_profile": "public mixed frontend/backend repo where the task is to map entrypoints, ownership, tests, docs, and dependency direction",
        "files": ["src/main.ts", "src/auth/session.ts", "tests/session.test.ts", "docs/architecture.md"],
        "symbols": ["main", "SessionService", "sessionFlow"],
        "terms": ["entrypoint", "ownership", "dependency direction", "nearby test"],
        "traps": ["tree dump", "ownership guessed", "no handoff"],
        "task": "map the repo area for a session bug, naming entrypoints, ownership boundary, dependency direction, and nearby tests/docs",
    },
    "browser-runtime": {
        "repo_profile": "public frontend repo with login page, Playwright flow, console log artifact, network HAR, and screenshot evidence",
        "files": ["src/app/login/page.tsx", "tests/e2e/login.spec.ts", "artifacts/login-console.json", "artifacts/login-network.har", "artifacts/login-screenshot.md"],
        "symbols": ["LoginPage", "loginSpec", "ConsoleError"],
        "terms": ["console", "network", "dom", "screenshot"],
        "traps": ["screenshot only", "network log without repro", "browser state leaked"],
        "task": "inspect a browser login runtime issue with console, network, DOM state, screenshot, and reproduction trace evidence",
    },
    "relay": {
        "repo_profile": "Relay-kit public repo with generated adapters, readiness gates, docs, and runtime tests",
        "files": ["relay_kit_public_cli.py", "relay_kit_v3/registry/skills.py", "tests/test_skill_resources.py"],
        "symbols": ["main", "SkillSpec", "emit_core_skills"],
        "terms": ["adapter surface", "readiness gate", "generated skill", "strict evidence"],
        "task": "audit a Relay-kit runtime change and prove the generated surfaces are still synchronized",
    },
    "ops": {
        "repo_profile": "public automation repo with GitHub Actions, scheduled jobs, rollback docs, and dry-run mode",
        "files": [".github/workflows/validate-runtime.yml", "scripts/runtime_doctor.py", "docs/site/readiness.md"],
        "symbols": ["main", "build_report", "validate_runtime"],
        "terms": ["dry run", "rollback", "workflow log", "idempotency"],
        "task": "plan an operational automation change with rollback and dry-run evidence before enabling it",
    },
    "research": {
        "repo_profile": "public product repo with README, pricing notes, competitor docs, and changelog",
        "files": ["README.md", "docs/site/skill-catalog.md", "CHANGELOG.md"],
        "symbols": ["pricing", "positioning", "adoption"],
        "terms": ["source freshness", "competitor claim", "unknown", "decision impact"],
        "task": "separate verified market evidence from inference before recommending product direction",
    },
    "mmo": {
        "repo_profile": "operator-owned automation repo with account inventory, worker queue, run logs, and policy guardrails",
        "files": ["ops/accounts.csv", "workers/session_runner.ts", "logs/run-2026-05-17.json"],
        "symbols": ["SessionRunner", "AccountHealth", "enqueueRun"],
        "terms": ["operator queue", "quota", "dedupe", "recovery runbook"],
        "task": "review an operator-owned MMO automation lane for safety, repeatability, and evidence logging",
    },
    "mmo-account-health": {
        "repo_profile": "operator-owned account operations repo with account inventory, health scoring, cooldown windows, and quarantine ledger",
        "files": ["ops/accounts.csv", "ops/account_health.ts", "logs/account-health.json", "docs/account-runbook.md"],
        "symbols": ["AccountHealth", "quarantineAccount", "cooldownWindow"],
        "terms": ["account health", "quarantine", "cooldown", "operator ledger"],
        "traps": ["bulk action without health score", "proxy binding ignored", "manual review skipped"],
        "task": "review account health automation with profile table, proxy binding, cooldown, quarantine, and operator ledger evidence",
    },
    "mmo-browser-session-lease": {
        "repo_profile": "operator-owned browser fleet repo with profile inventory, proxy affinity, session lease, screenshot, and console logs",
        "files": ["ops/browser_profiles.json", "workers/browser_session.ts", "tests/browser_session.test.ts", "logs/browser-session.json", "artifacts/session-screenshot.md"],
        "symbols": ["SessionLease", "BrowserSessionRunner", "releaseLease"],
        "terms": ["session lease", "profile-to-proxy affinity", "console logs", "operator ledger"],
        "traps": ["session reuse without lease", "proxy affinity ignored", "screenshot-only proof"],
        "task": "review browser fleet automation for profile-to-proxy affinity, session lease, live debug, screenshot, and console log evidence",
    },
    "mmo-api-request-ledger": {
        "repo_profile": "operator-owned HTTP automation repo with endpoint catalog, request ledger, retry budget, redacted logs, and idempotency keys",
        "files": ["ops/endpoints.yaml", "workers/api_client.ts", "logs/request-ledger.json", "tests/request-ledger.test.ts"],
        "symbols": ["EndpointCatalog", "RequestLedger", "idempotencyKey"],
        "terms": ["request ledger", "idempotency key", "retry count", "redacted"],
        "traps": ["raw token in logs", "retry without idempotency", "status code ignored"],
        "task": "review HTTP API automation with endpoint catalog, request ledger, status code, retry count, and idempotency key evidence",
    },
    "mmo-cloud-worker-queue": {
        "repo_profile": "operator-owned cloud worker repo with queue dashboard, worker pool, dead-letter queue, cost ceiling, and pause control",
        "files": ["ops/queues.yaml", "workers/cloud_worker.ts", "logs/dead-letter.json", "docs/cloud-worker-runbook.md"],
        "symbols": ["CloudWorker", "DeadLetterQueue", "pauseQueue"],
        "terms": ["worker queue", "queue depth", "dead-letter", "pause"],
        "traps": ["scale without cost ceiling", "dead-letter ignored", "pause missing"],
        "task": "review cloud automation with worker pool, queue depth, stalled jobs, dead-letter handling, pause control, and operator ledger evidence",
    },
    "mmo-mobile-device-lease": {
        "repo_profile": "operator-owned mobile automation repo with device inventory, hub/provider mapping, device lease, logcat, and app-state recovery",
        "files": ["ops/devices.json", "workers/mobile_runner.ts", "logs/device-lease.json", "docs/mobile-recovery-runbook.md"],
        "symbols": ["DeviceLease", "MobileRunner", "recoverAppState"],
        "terms": ["device lease", "logcat", "app-state", "operator ledger"],
        "traps": ["device reused without lease", "logcat missing", "hub/provider guessed"],
        "task": "review mobile automation with device inventory, hub, provider, lease owner, logcat, and app-state recovery evidence",
    },
    "mmo-lowcode-execution-history": {
        "repo_profile": "operator-owned low-code orchestration repo with node graph, execution history, redacted execution logs, and rollback notes",
        "files": ["ops/flow.json", "workers/lowcode_runner.ts", "logs/execution-history.json", "docs/lowcode-rollback.md"],
        "symbols": ["NodeGraph", "ExecutionHistory", "rollbackExecution"],
        "terms": ["node graph", "execution history", "redacted execution", "operator ledger"],
        "traps": ["manual and production execution mixed", "history missing", "rollback skipped"],
        "task": "review low-code automation with node graph, execution history, manual versus production execution, redacted logs, and rollback evidence",
    },
    "mmo-social-campaign-approval": {
        "repo_profile": "operator-owned social campaign repo with content calendar, approval lane, quota meter, reject reason, and campaign ledger",
        "files": ["ops/campaign_calendar.md", "workers/social_scheduler.ts", "logs/approval-ledger.json", "docs/social-approval-runbook.md"],
        "symbols": ["CampaignApproval", "QuotaMeter", "rejectReason"],
        "terms": ["approval lane", "quota meter", "reject reason", "operator ledger"],
        "traps": ["posting without approval", "quota meter ignored", "reject reason missing"],
        "task": "review social marketing automation with campaign workspace, content calendar, approval lane, quota meter, reject reason, and operator ledger evidence",
    },
    "mmo-reup-source-inventory": {
        "repo_profile": "operator-owned reup repo with source inventory, publish queue, dedupe controls, reject drawer, and evidence timeline",
        "files": ["ops/source_inventory.csv", "workers/reup_queue.ts", "logs/reup-ledger.json", "docs/reup-source-policy.md"],
        "symbols": ["SourceInventory", "PublishQueue", "dedupeSource"],
        "terms": ["source inventory", "publish queue", "dedupe", "evidence timeline"],
        "traps": ["bulk action without inventory", "dedupe skipped", "evidence timeline missing"],
        "task": "review reup workflow with source inventory, publish queue, dedupe, reject drawer, and evidence timeline before automation changes",
    },
    "docs": {
        "repo_profile": "public docs repo with README, localized docs, static GitHub catalog, and encoding tests",
        "files": ["README.md", "README.vi.md", "docs/site/index.md", "tests/test_readme_encoding.py"],
        "symbols": ["test_readme_files_are_utf8_without_mojibake", "render_battle_audit"],
        "terms": ["utf-8", "public copy", "overclaim", "evidence label"],
        "task": "review public docs for overclaim, broken localization, and missing evidence labels",
    },
}


def family_for(skill_name: str) -> str:
    mmo_families = {
        "mmo-account-operations": "mmo-account-health",
        "mmo-browser-fleet-automation": "mmo-browser-session-lease",
        "mmo-cloud-operations-automation": "mmo-cloud-worker-queue",
        "mmo-http-api-automation": "mmo-api-request-ledger",
        "mmo-lowcode-automation": "mmo-lowcode-execution-history",
        "mmo-mobile-app-automation": "mmo-mobile-device-lease",
        "mmo-reup-automation": "mmo-reup-source-inventory",
        "mmo-social-marketing-automation": "mmo-social-campaign-approval",
    }
    if skill_name in mmo_families:
        return mmo_families[skill_name]
    if skill_name.startswith("mmo-"):
        return "mmo"
    dedicated_families = {
        "dependency-management": "dependency-drift",
        "go-service-engineering": "service-boundary",
        "testing-patterns": "test-strategy",
        "repo-map": "repo-discovery",
        "browser-inspector": "browser-runtime",
    }
    if skill_name in dedicated_families:
        return dedicated_families[skill_name]
    if skill_name in {"next-product-frontend", "frontend-design", "ui-styling", "ux-structure", "accessibility-review"}:
        return "frontend"
    if skill_name in {"market-research", "growth-marketing", "research", "analyst", "brainstorm-hub"}:
        return "research"
    if skill_name in {"automation-ops", "release-readiness", "runtime-doctor", "policy-guard", "migration-guard", "impact-radar"}:
        return "ops"
    if skill_name in {"api-integration", "data-persistence", "go-service-engineering", "dependency-management"}:
        return "backend"
    if skill_name in {"vietnamese-product-localization", "doc-pointers", "media-tooling"}:
        return "docs"
    return "relay"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def refresh_resources() -> None:
    for skill_name, spec in sorted(ALL_V3_SKILLS.items()):
        family = family_for(skill_name)
        case = FAMILY_CASES[family]
        skill_root = RESOURCE_ROOT / skill_name
        write_text(
            skill_root / "references" / f"{skill_name}-operator-contract.md",
            render_reference(skill_name, spec, family, case),
        )
        write_text(
            skill_root / "examples" / f"{skill_name}-good-output.md",
            render_good_example(skill_name, spec, family, case),
        )
        write_text(
            skill_root / "examples" / f"{skill_name}-bad-output.md",
            render_bad_example(skill_name, spec, family, case),
        )
        write_text(
            skill_root / "evals" / f"{skill_name}-cases.json",
            json.dumps(render_eval_cases(skill_name, spec, family, case), ensure_ascii=True, indent=2),
        )


def render_reference(skill_name: str, spec, family: str, case: dict[str, list[str] | str]) -> str:
    return f"""# {skill_name} Battle Contract

Primary role: {spec.role}
Layer: {spec.layer}
Battle family: {family}

Use this skill only after the request is anchored to a real artifact, repo area, or explicit missing-context question. The goal is not to sound like an expert; the goal is to reduce ambiguity by tying the answer to files, symbols, commands, docs, logs, or state.

## Concrete Battle Profile

- Repo profile: {case['repo_profile']}
- First files to inspect: {', '.join(case['files'])}
- Symbols or named surfaces to confirm: {', '.join(case['symbols'])}
- Evidence terms that should appear in a strong answer: {', '.join(case['terms'])}

## Working Loop

1. Restate the user task as a verifiable repo action.
2. Name the candidate files before giving advice.
3. Check at least one source file and one proof surface when the task touches code, docs, release, routing, or automation.
4. Separate verified facts, inferred risk, and unknowns.
5. End with the next executable check or handoff, not broad process advice.

## Failure Modes To Block

- Guessing from the skill name without opening files.
- Treating a checklist as proof.
- Saying a change is ready when tests, generated adapters, docs, or safety scans were not checked.
- Hiding that a public repo benchmark is read-only and not user adoption proof.

## Evidence Checklist

- File evidence: cite exact paths or say which anchor is missing.
- Behavior evidence: cite test, static scan, route score, benchmark hit, screenshot, or command output.
- Risk evidence: name residual risk and the smallest next verification.
- Handoff evidence: name the receiving skill or CLI gate when another lane should continue.
"""


def render_good_example(skill_name: str, spec, family: str, case: dict[str, list[str] | str]) -> str:
    task = case["task"]
    files = case["files"]
    symbols = case["symbols"]
    terms = case["terms"]
    return f"""# {skill_name} Battle-Calibrated Output

Request: {task}

Recommended skill: `{skill_name}` because the request matches `{spec.role}` work and has concrete repo anchors.

Read first:

- `{files[0]}`
- `{files[1]}`
- `{files[-1]}`

Evidence gathered:

- Confirmed `{symbols[0]}` or nearby ownership before recommending changes.
- Checked `{terms[0]}` and `{terms[1]}` against the relevant source path.
- Identified `{terms[2]}` as a required proof term before completion.

Answer:

The safe next move is to inspect the named file path, compare it with the expected test or docs surface, and only then choose implementation, review, or planning. If the anchor is missing, ask one question that names the missing file, PR, log, screen, or workflow.

Residual risk:

- `{terms[-1]}` remains unverified until the focused gate or benchmark hit is captured.
"""


def render_bad_example(skill_name: str, spec, family: str, case: dict[str, list[str] | str]) -> str:
    return f"""# {skill_name} Weak Output Anti-Example

Request: {case['task']}

Weak answer:

This looks like `{skill_name}`, so follow the usual checklist and it should be fine.

Why this fails:

- No file path from `{case['repo_profile']}` was inspected.
- No symbol such as `{case['symbols'][0]}` was confirmed.
- No proof surface was named for `{case['terms'][0]}`.
- It blurs verified evidence and inference, which is exactly how overclaim slips back into Relay-kit.

Correction:

Name the concrete path, inspect or search it, state what is verified, and leave unverified claims labeled until a gate proves them.
"""


def render_eval_cases(skill_name: str, spec, family: str, case: dict[str, list[str] | str]) -> list[dict[str, object]]:
    files = list(case["files"])
    symbols = list(case["symbols"])
    terms = list(case["terms"])
    traps = list(case.get("traps", [])) if isinstance(case.get("traps", []), list) else []
    test_files = [path for path in files if "test" in path.casefold() or "spec" in path.casefold()] or [files[-1]]
    return [
        {
            "id": f"{skill_name}-battle-read-first",
            "skill": skill_name,
            "repo_profile": case["repo_profile"],
            "task": f"{case['task']} Use `{skill_name}` and cite the first files before advice.",
            "expected_files": files[:3],
            "expected_symbols": symbols[:2],
            "expected_tests": test_files,
            "expected_evidence_terms": [terms[0], terms[1], "verified", "residual risk"],
            "bad_answer_traps": traps[:2] + ["usual checklist", "guess from the name", "should be fine"],
        },
        {
            "id": f"{skill_name}-public-repo-benchmark-anchor",
            "skill": skill_name,
            "repo_profile": "safe public repo benchmark clone; shallow, read-only, no install, no build, no tests",
            "task": f"Run a read-only battle benchmark style review for `{skill_name}` and explain what evidence is still missing.",
            "expected_files": [files[0], files[-1]],
            "expected_symbols": [symbols[0]],
            "expected_tests": test_files,
            "expected_evidence_terms": [terms[2], terms[3], "read-only", "unverified"],
            "bad_answer_traps": traps[1:3] + ["checklist only", "expert guarantee", "field-tested"],
        },
        {
            "id": f"{skill_name}-deep-weakness-trap",
            "skill": skill_name,
            "repo_profile": f"deep {family} suite fixture with source, test, docs, and an explicit overclaim trap",
            "task": f"Score `{skill_name}` against a deep battle case, identify weak evidence, and avoid claiming maximum strength until files, symbols, tests, and residual risk are proven.",
            "expected_files": files[:2] + [files[-1]],
            "expected_symbols": symbols[:2],
            "expected_tests": test_files,
            "expected_evidence_terms": [terms[0], terms[-1], "weak evidence", "claim status", "residual risk"],
            "bad_answer_traps": traps[:3] + ["looks like", "usual checklist", "battle-max-on-suite without proof"],
        },
    ]


CORE_SHOWCASE_SKILLS = {
    "workflow-router",
    "repo-map",
    "context-continuity",
    "debug-hub",
    "root-cause-debugging",
    "fix-hub",
    "developer",
    "execution-loop",
    "test-first-development",
    "review-hub",
    "qa-governor",
    "api-integration",
    "data-persistence",
    "dependency-management",
    "testing-patterns",
    "go-service-engineering",
    "next-product-frontend",
    "browser-inspector",
    "policy-guard",
    "runtime-doctor",
    "skill-gauntlet",
    "release-readiness",
    "evidence-before-completion",
}

SPECIALIST_PACK_SKILLS = {
    "automation-ops",
    "growth-marketing",
    "market-research",
    "vietnamese-product-localization",
}


def catalog_surface_tier(skill_name: str, spec) -> str:
    if skill_name in CORE_SHOWCASE_SKILLS:
        return "core-showcase"
    if skill_name.startswith("mmo-"):
        return "specialized-extension"
    if skill_name in SPECIALIST_PACK_SKILLS:
        return "specialist-pack"
    if spec.layer == "layer-3-utility-providers":
        return "runtime-utility"
    if spec.layer == "layer-1-orchestrators":
        return "core-orchestrator"
    if spec.layer == "layer-2-workflow-hubs":
        return "workflow-hub"
    return "specialist-pack"


def refresh_catalog() -> None:
    lines = [
        "# Relay-kit Skill Catalog",
        "",
        "This catalog is a GitHub-rendered static view of the canonical Relay-kit skills. The front-door product story is the core runtime; specialized extension packs are listed for traceability, not as the main public pitch.",
        "",
        "Core showcase: `workflow-router`, `repo-map`, local context commands, debug/review hubs, engineering specialists, and proof gates.",
        "",
        "| Skill | Role | Layer | Surface tier | Resource status | Competency status | Archetype status | Audit status | Battle status | Pack status | Best use case |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for skill_name, spec in sorted(ALL_V3_SKILLS.items()):
        description = shorten(" ".join(spec.description.split()), width=150, placeholder="...")
        surface_tier = catalog_surface_tier(skill_name, spec)
        pack_status = "extension-pack" if surface_tier == "specialized-extension" else "core-or-utility"
        lines.append(
            f"| `{skill_name}` | {spec.role} | {spec.layer} | {surface_tier} | resource-complete | "
            f"competency-covered | archetype-tested | battle-audited | battle-max-on-suite | {pack_status} | {description} |"
        )
    lines.extend(
        [
            "",
            "Status meanings:",
            "",
            "- `core-showcase`: front-door Relay-kit capability; use these in README, demos, and first impressions.",
            "- `specialized-extension`: available runtime extension, but not the main public pitch.",
            "- `runtime-utility`, `workflow-hub`, `core-orchestrator`, and `specialist-pack`: supporting surfaces used by the routing system.",
            "- `resource-complete`: references, good/bad examples, eval cases, and competency profiles exist for the skill.",
            "- `competency-covered`: the skill has core competencies and failure traps in `competencies/<skill>-competencies.json`.",
            "- `archetype-tested`: battle benchmark cases map public repos to repo archetypes and competency patterns.",
            "- `battle-audited`: `relay-kit eval battle-audit` checks the skill pack for generic skeletons and weak evals.",
            "- `battle-tested-on-suite`: the skill is covered by the local deep battle suite. Use `battle-max-on-suite` only after a 10/10 skill-battle report.",
            "- `extension-pack`: extension capability; no row claims domain-pack-tested until that pack is run for the target repo.",
            "- These labels are local evidence labels; external adoption labels require separate release evidence.",
        ]
    )
    write_text(SITE_ROOT / "skill-catalog.md", "\n".join(lines))


def refresh_battle_docs() -> None:
    write_text(
        SITE_ROOT / "battle-benchmark.md",
        """# Battle Benchmark

Relay-kit battle benchmark is a read-only public-repo benchmark lane for checking whether the runtime can find useful files, symbols, tests, and evidence terms on real repositories.

It provides public-repo benchmark evidence, not proof of external commercial adoption and not field-tested/user proof.

## Safety Model

- Shallow clone only.
- No submodules.
- No package install.
- No build.
- No test execution.
- No project scripts or hooks are run.
- Static safety scan rejects suspicious binaries, package install payloads, very large files, and oversized repos.
- `--cleanup` removes the temporary clone folder after the benchmark.

## CLI

```bash
relay-kit eval battle-audit . --json
relay-kit eval battle-benchmark . --suite curated --cleanup --json
relay-kit eval competency-battle . --skill all --suite core --json
relay-kit eval repo-profile . --json
relay-kit eval domain-pack list . --json
```

## What It Measures

- Can context index find expected files?
- Can local symbol extraction see relevant symbols?
- Does prompt enhancement include file-aware evidence?
- Does the repo profile map the repo to an archetype instead of pretending every industry is known?
- Does the expected public repo case map to competencies?
- Does the answer stay clear that this is read-only benchmark evidence?

This is not a semantic codebase engine, not an Augment clone, and not a guarantee that every repo task will route perfectly.
""",
    )


def main() -> None:
    refresh_resources()
    refresh_catalog()
    refresh_battle_docs()


if __name__ == "__main__":
    main()
