from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from relay_kit_v3.context_index import build_context_index, build_context_search, write_context_index
from relay_kit_v3.intent_enhancer import build_prompt_enhancement
from relay_kit_v3.repo_profile import build_repo_profile_from_index


SCHEMA_VERSION = "relay-kit.battle-benchmark.v1"
TEMP_ROOT = ".tmp/relay-kit-battle-benchmark"
MAX_FILE_BYTES = 2_000_000
MAX_REPO_FILES = 8_000

EXECUTABLE_SUFFIXES = {
    ".com",
    ".dll",
    ".dylib",
    ".exe",
    ".jar",
    ".msi",
    ".scr",
    ".so",
}
SCRIPT_SUFFIXES = {".bat", ".cmd", ".ps1", ".sh"}

DANGEROUS_PACKAGE_SCRIPT = re.compile(
    r"\b(postinstall|preinstall|prepare|install)\b.*\b(curl|wget|powershell|cmd\.exe|bash|sh|python\s+-c|node\s+-e)\b",
    flags=re.IGNORECASE,
)
DANGEROUS_SCRIPT_CONTENT = re.compile(
    r"\b(curl|wget|Invoke-WebRequest|iwr|irm|Invoke-Expression|iex|rm\s+-rf|del\s+/s|format\s+[A-Z]:|powershell\s+-enc)\b",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class BenchmarkCase:
    id: str
    domain: str
    archetype: str
    competencies: tuple[str, ...]
    repo_url: str
    repo_name: str
    task: str
    query: str
    expected_skill: str
    expected_files: tuple[str, ...]
    expected_symbols: tuple[str, ...]
    expected_tests: tuple[str, ...]
    expected_evidence_terms: tuple[str, ...]


CURATED_SUITE: tuple[BenchmarkCase, ...] = (
    BenchmarkCase(
        id="flask-backend-routing-architecture",
        domain="backend-api",
        archetype="backend-api",
        competencies=("api-integration.client-endpoint-contract", "implementation.context-before-edit"),
        repo_url="https://github.com/pallets/flask.git",
        repo_name="pallets-flask",
        task="read repo and map Flask routing/request architecture without running code",
        query="flask route request app context test",
        expected_skill="scout-hub",
        expected_files=("src/flask/app.py", "src/flask/sansio/app.py"),
        expected_symbols=("Flask",),
        expected_tests=("tests/test_request.py",),
        expected_evidence_terms=("flask", "route", "request", "context"),
    ),
    BenchmarkCase(
        id="p-limit-concurrency-review",
        domain="automation-concurrency",
        archetype="library-core",
        competencies=("automation-ops.idempotent-retry", "implementation.test-evidence"),
        repo_url="https://github.com/sindresorhus/p-limit.git",
        repo_name="sindresorhus-p-limit",
        task="find concurrency queue behavior and related tests without installing packages",
        query="concurrency queue activeCount pendingCount",
        expected_skill="scout-hub",
        expected_files=("index.js", "test.js"),
        expected_symbols=("pLimit",),
        expected_tests=("test.js",),
        expected_evidence_terms=("concurrency", "queue", "activeCount", "pendingCount"),
    ),
    BenchmarkCase(
        id="click-command-routing",
        domain="cli-tooling",
        archetype="cli-tool",
        competencies=("routing-orchestration.intent-routing", "implementation.test-evidence"),
        repo_url="https://github.com/pallets/click.git",
        repo_name="pallets-click",
        task="map command parsing architecture and test anchors without running code",
        query="command group context option parser",
        expected_skill="scout-hub",
        expected_files=("src/click/core.py", "tests/test_basic.py"),
        expected_symbols=("Command", "Group"),
        expected_tests=("tests/test_basic.py",),
        expected_evidence_terms=("command", "context", "option", "parser"),
    ),
)

DEEP_SUITE: tuple[BenchmarkCase, ...] = (
    *CURATED_SUITE,
    BenchmarkCase(
        id="httpx-client-transport-review",
        domain="api-client",
        archetype="backend-api",
        competencies=("api-integration.client-endpoint-contract", "api-integration.contract-test-anchor"),
        repo_url="https://github.com/encode/httpx.git",
        repo_name="encode-httpx",
        task="map HTTP client transport and request/response test anchors without running code",
        query="client transport request response timeout tests",
        expected_skill="api-integration",
        expected_files=("httpx/_client.py", "tests/client/test_client.py"),
        expected_symbols=("Client", "AsyncClient"),
        expected_tests=("tests/client/test_client.py",),
        expected_evidence_terms=("client", "transport", "request", "response"),
    ),
    BenchmarkCase(
        id="attrs-data-model-generation",
        domain="data-modeling",
        archetype="library-core",
        competencies=("implementation.context-before-edit", "implementation.test-evidence"),
        repo_url="https://github.com/python-attrs/attrs.git",
        repo_name="python-attrs-attrs",
        task="map attrs class generation, validators, and tests without running code",
        query="attrs define field validator make tests",
        expected_skill="project-architecture",
        expected_files=("src/attr/_make.py", "tests/test_make.py"),
        expected_symbols=("attrs", "Factory"),
        expected_tests=("tests/test_make.py",),
        expected_evidence_terms=("attrs", "define", "field", "validator"),
    ),
    BenchmarkCase(
        id="pytest-collection-devtools",
        domain="test-runner",
        archetype="test-runner",
        competencies=("debugging.fresh-reproduction", "implementation.test-evidence"),
        repo_url="https://github.com/pytest-dev/pytest.git",
        repo_name="pytest-dev-pytest",
        task="map pytest collection/session entrypoints and related tests without running code",
        query="pytest collection session main hooks tests",
        expected_skill="scout-hub",
        expected_files=("src/_pytest/main.py", "testing/test_collection.py"),
        expected_symbols=("Session", "pytest_cmdline_main"),
        expected_tests=("testing/test_collection.py",),
        expected_evidence_terms=("pytest", "collection", "session", "hook"),
    ),
    BenchmarkCase(
        id="sqlalchemy-engine-transaction-flow",
        domain="database",
        archetype="database-heavy",
        competencies=("data-persistence.transaction-boundary", "data-persistence.persistence-test-anchor"),
        repo_url="https://github.com/sqlalchemy/sqlalchemy.git",
        repo_name="sqlalchemy-sqlalchemy",
        task="map engine connection and transaction execution surfaces without running tests",
        query="engine connection execute transaction tests",
        expected_skill="data-persistence",
        expected_files=("lib/sqlalchemy/engine/base.py", "test/engine/test_execute.py"),
        expected_symbols=("Connection", "Engine"),
        expected_tests=("test/engine/test_execute.py",),
        expected_evidence_terms=("engine", "connection", "execute", "transaction"),
    ),
    BenchmarkCase(
        id="gitleaks-security-detection-rules",
        domain="security-policy",
        archetype="security-policy",
        competencies=("policy-security.policy-rule-map", "policy-security.audit-evidence"),
        repo_url="https://github.com/gitleaks/gitleaks.git",
        repo_name="gitleaks-gitleaks",
        task="map secret detection rules, config, and tests without running code",
        query="detect config rule secret test",
        expected_skill="policy-guard",
        expected_files=("config/rule.go", "detect/detect_test.go", "config/config_test.go"),
        expected_symbols=("Detector", "Config"),
        expected_tests=("detect/detect_test.go", "config/config_test.go"),
        expected_evidence_terms=("detect", "config", "rule", "secret"),
    ),
    BenchmarkCase(
        id="github-actions-ci-workflow-catalog",
        domain="ci-devops",
        archetype="automation-worker",
        competencies=("automation-ops.scheduler-queue", "automation-ops.operator-runbook"),
        repo_url="https://github.com/actions/starter-workflows.git",
        repo_name="actions-starter-workflows",
        task="map CI workflow templates and package jobs without running anything",
        query="node python workflow ci package readme",
        expected_skill="automation-ops",
        expected_files=("ci/node.js.yml", "ci/python-package.yml"),
        expected_symbols=(),
        expected_tests=("ci/node.js.yml", "ci/python-package.yml"),
        expected_evidence_terms=("workflow", "ci", "node", "python"),
    ),
    BenchmarkCase(
        id="mkdocs-plugin-config-docs",
        domain="docs-product",
        archetype="docs-product",
        competencies=("research-product.source-triangulation", "research-product.audience-fit"),
        repo_url="https://github.com/mkdocs/mkdocs.git",
        repo_name="mkdocs-mkdocs",
        task="map MkDocs config/plugin documentation and config tests without running code",
        query="config option validation plugin tests",
        expected_skill="scout-hub",
        expected_files=("mkdocs/config/base.py", "mkdocs/tests/config/base_tests.py"),
        expected_symbols=("Config", "BaseConfigOption"),
        expected_tests=("mkdocs/tests/config/base_tests.py",),
        expected_evidence_terms=("config", "option", "validation", "plugin"),
    ),
    BenchmarkCase(
        id="fastapi-routing-dependency-frontend-api",
        domain="frontend-api-boundary",
        archetype="backend-api",
        competencies=("api-integration.client-endpoint-contract", "api-integration.contract-test-anchor"),
        repo_url="https://github.com/fastapi/fastapi.git",
        repo_name="fastapi-fastapi",
        task="map FastAPI application routing and dependency tests without running code",
        query="fastapi route dependency application tests",
        expected_skill="api-integration",
        expected_files=("fastapi/applications.py", "tests/test_dependency_duplicates.py"),
        expected_symbols=("FastAPI", "APIRoute"),
        expected_tests=("tests/test_dependency_duplicates.py",),
        expected_evidence_terms=("fastapi", "route", "dependency", "application"),
    ),
    BenchmarkCase(
        id="vite-plugin-config-routing",
        domain="frontend-next-build-tooling",
        archetype="frontend-app",
        competencies=("frontend-product.route-component-boundary", "frontend-product.frontend-test-anchor"),
        repo_url="https://github.com/vitejs/vite.git",
        repo_name="vitejs-vite",
        task="find config/plugin resolution surfaces and tests without installing packages",
        query="config plugin resolve server test",
        expected_skill="scout-hub",
        expected_files=("packages/vite/src/node/config.ts", "packages/vite/src/node/server/__tests__/pluginContainer.spec.ts"),
        expected_symbols=("resolveConfig",),
        expected_tests=("packages/vite/src/node/server/__tests__/pluginContainer.spec.ts",),
        expected_evidence_terms=("config", "plugin", "resolve", "server"),
    ),
)


CloneFn = Callable[[BenchmarkCase, Path], tuple[bool, str]]


def build_battle_benchmark(
    project_root: Path | str,
    *,
    suite: str = "curated",
    cleanup: bool = False,
    repo_limit: int | None = None,
    cases: Sequence[BenchmarkCase] | None = None,
    clone_fn: CloneFn | None = None,
) -> dict[str, Any]:
    project = Path(project_root).resolve()
    selected_cases = list(cases or _suite_cases(suite))
    if repo_limit is not None:
        selected_cases = selected_cases[: max(repo_limit, 0)]
    temp_root = project / TEMP_ROOT
    temp_root.mkdir(parents=True, exist_ok=True)
    clone = clone_fn or _safe_clone
    case_reports: list[dict[str, Any]] = []
    try:
        for case in selected_cases:
            case_reports.append(_run_case(project, temp_root, case, clone))
    finally:
        if cleanup:
            _cleanup_temp_root(project, temp_root)
    passed = sum(1 for item in case_reports if item.get("status") == "pass")
    skipped = sum(1 for item in case_reports if item.get("status") == "skip")
    failed = sum(1 for item in case_reports if item.get("status") == "fail")
    scored = [
        item
        for item in case_reports
        if item.get("status") != "skip" and isinstance(item.get("score"), (int, float))
    ]
    weakest = min(scored, key=lambda item: float(item.get("score", 0)), default=None)
    maxed = sum(1 for item in case_reports if item.get("status") == "pass" and float(item.get("score", 0)) >= 10)
    partial = sum(1 for item in case_reports if item.get("status") == "pass" and float(item.get("score", 0)) < 10)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass" if failed == 0 and passed > 0 else "fail",
        "project_path": str(project),
        "suite": suite,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "safety_policy": {
            "runs_foreign_code": False,
            "installs_dependencies": False,
            "builds_or_tests_foreign_repo": False,
            "clone_mode": "shallow-no-submodules",
            "temp_root": str(temp_root),
            "cleanup_requested": cleanup,
        },
        "summary": {
            "case_count": len(case_reports),
            "passed": passed,
            "skipped": skipped,
            "failed": failed,
            "battle_max_cases": maxed,
            "partial_cases": partial,
            "weakest_case": weakest.get("id") if weakest else None,
            "weakest_score": weakest.get("score") if weakest else None,
        },
        "cases": case_reports,
    }


def write_battle_benchmark(project_root: Path | str, report: Mapping[str, Any], output_file: Path | str) -> Path:
    project = Path(project_root).resolve()
    target = Path(output_file)
    if not target.is_absolute():
        target = project / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return target


def render_battle_benchmark(report: Mapping[str, Any]) -> str:
    summary = report.get("summary", {})
    lines = [
        "Relay-kit battle benchmark",
        f"- status: {report.get('status')}",
        f"- suite: {report.get('suite')}",
        f"- passed: {summary.get('passed', 0)}",
        f"- skipped: {summary.get('skipped', 0)}",
        f"- failed: {summary.get('failed', 0)}",
    ]
    for item in report.get("cases", []):
        lines.append(
            f"  - {item.get('id')}: {item.get('status')} "
            f"files={item.get('matched_files', [])} skill={item.get('prompt_enhance', {}).get('recommended_skill')}"
        )
    return "\n".join(lines)


def _suite_cases(suite: str) -> tuple[BenchmarkCase, ...]:
    if suite == "curated":
        return CURATED_SUITE
    if suite == "deep":
        return DEEP_SUITE
    raise ValueError(f"Unknown benchmark suite: {suite}")


def _run_case(project: Path, temp_root: Path, case: BenchmarkCase, clone: CloneFn) -> dict[str, Any]:
    if not _pre_clone_allowed(case.repo_url):
        return _skip_case(case, "pre-clone URL policy rejected the repo")
    target = temp_root / case.repo_name
    if target.exists():
        _cleanup_temp_root(project, target)
    cloned, clone_message = clone(case, target)
    if not cloned:
        return _skip_case(case, clone_message)
    safety = static_safety_scan(target)
    if safety["status"] != "pass":
        return _skip_case(case, f"post-clone static safety scan rejected repo: {safety['reason']}", safety=safety)
    index = build_context_index(target)
    write_context_index(target, index)
    repo_profile = build_repo_profile_from_index(target, index)
    search = build_context_search(target, query=case.query, limit=20)
    prompt = build_prompt_enhancement(target, prompt=case.task)
    result_paths = [str(item.get("path")) for item in search.get("results", [])]
    matched_files = [expected for expected in case.expected_files if any(expected in path for path in result_paths)]
    matched_tests = [expected for expected in case.expected_tests if any(expected in path for path in result_paths)]
    indexed_symbols = {
        str(symbol)
        for item in index.get("files", [])
        for symbol in item.get("symbols", [])
    }
    matched_symbols = [symbol for symbol in case.expected_symbols if symbol in indexed_symbols]
    evidence_text = " ".join(
        [
            " ".join(result_paths),
            " ".join(str(term) for item in search.get("results", []) for term in item.get("matched_terms", [])),
            " ".join(prompt.get("evidence_required", [])),
            " ".join(prompt.get("read_first", [])),
        ]
    ).casefold()
    matched_evidence = [term for term in case.expected_evidence_terms if term.casefold() in evidence_text]
    matched_archetypes = [
        item.get("archetype")
        for item in repo_profile.get("archetypes", [])
        if item.get("archetype") == case.archetype
    ]
    matched_competencies = sorted(set(case.competencies) & set(repo_profile.get("suggested_competencies", [])))
    score_breakdown = {
        "file_evidence": _ratio_score(len(matched_files), len(case.expected_files), 3),
        "symbol_evidence": _ratio_score(len(matched_symbols), len(case.expected_symbols), 2),
        "test_evidence": _ratio_score(len(matched_tests), len(case.expected_tests), 2),
        "evidence_terms": _ratio_score(len(matched_evidence), len(case.expected_evidence_terms), 2),
        "routing": 1 if prompt.get("recommended_skill") == case.expected_skill or case.expected_skill in [item.get("skill") for item in prompt.get("top_candidates", []) if isinstance(item, Mapping)] else 0,
    }
    score = round(sum(score_breakdown.values()), 2)
    passed = len(matched_files) == len(case.expected_files) and len(matched_tests) == len(case.expected_tests) and len(matched_evidence) == len(case.expected_evidence_terms)
    if case.expected_symbols:
        passed = passed and len(matched_symbols) == len(case.expected_symbols)
    return {
        "id": case.id,
        "domain": case.domain,
        "archetype": case.archetype,
        "competencies": list(case.competencies),
        "repo_profile": {
            "dominant_archetype": repo_profile.get("dominant_archetype"),
            "domain_coverage": repo_profile.get("domain_coverage"),
            "unknown_domain_mode": repo_profile.get("unknown_domain_mode"),
            "suggested_competencies": repo_profile.get("suggested_competencies", []),
        },
        "repo_url": case.repo_url,
        "status": "pass" if passed else "fail",
        "task": case.task,
        "query": case.query,
        "expected_skill": case.expected_skill,
        "prompt_enhance": {
            "recommended_skill": prompt.get("recommended_skill"),
            "ask_or_act": prompt.get("ask_or_act"),
            "context_index_status": prompt.get("context_index_status"),
        },
        "matched_files": matched_files,
        "matched_symbols": matched_symbols,
        "matched_tests": matched_tests,
        "matched_archetypes": matched_archetypes,
        "matched_competencies": matched_competencies,
        "matched_evidence_terms": matched_evidence,
        "score": score,
        "score_breakdown": score_breakdown,
        "claim_status": _claim_status(passed, score),
        "suggested_fix": _suggest_case_fix(case, matched_files, matched_symbols, matched_tests, matched_evidence, prompt),
        "search_results": search.get("results", [])[:8],
        "safety": safety,
        "clone_message": clone_message,
    }


def static_safety_scan(root: Path | str) -> dict[str, Any]:
    repo = Path(root).resolve()
    file_count = 0
    for path in repo.rglob("*"):
        if not path.is_file():
            continue
        try:
            relative = path.relative_to(repo).as_posix()
            stat = path.stat()
        except OSError:
            continue
        if relative.startswith(".git/"):
            continue
        file_count += 1
        if file_count > MAX_REPO_FILES:
            return {"status": "skip", "reason": "too-many-files", "file": relative}
        if stat.st_size > MAX_FILE_BYTES:
            return {"status": "skip", "reason": "file-too-large", "file": relative}
        if path.suffix.casefold() in EXECUTABLE_SUFFIXES:
            return {"status": "skip", "reason": "executable-or-script-file", "file": relative}
        if path.suffix.casefold() in SCRIPT_SUFFIXES:
            text = path.read_text(encoding="utf-8", errors="replace")
            if DANGEROUS_SCRIPT_CONTENT.search(text):
                return {"status": "skip", "reason": "dangerous-script-content", "file": relative}
        if path.name == "package.json":
            text = path.read_text(encoding="utf-8", errors="replace")
            if DANGEROUS_PACKAGE_SCRIPT.search(text):
                return {"status": "skip", "reason": "dangerous-package-script", "file": relative}
    return {"status": "pass", "reason": "static-scan-clean", "file_count": file_count}


def _pre_clone_allowed(repo_url: str) -> bool:
    return repo_url.startswith("https://github.com/") and repo_url.endswith(".git") and not re.search(r"[\s;&|`]", repo_url)


def _safe_clone(case: BenchmarkCase, target: Path) -> tuple[bool, str]:
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    command = [
        "git",
        "-c",
        "filter.lfs.smudge=",
        "-c",
        "filter.lfs.required=false",
        "clone",
        "--depth",
        "1",
        "--no-tags",
        "--recurse-submodules=no",
        case.repo_url,
        str(target),
    ]
    try:
        completed = subprocess.run(command, text=True, capture_output=True, timeout=90, check=False, env=env)
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"clone failed before benchmark: {exc}"
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip().splitlines()
        return False, detail[-1] if detail else "clone failed"
    return True, "cloned shallow without submodules"


def _skip_case(case: BenchmarkCase, reason: str, *, safety: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {
        "id": case.id,
        "domain": case.domain,
        "archetype": case.archetype,
        "competencies": list(case.competencies),
        "repo_url": case.repo_url,
        "status": "skip",
        "reason": reason,
        "safety": dict(safety or {}),
        "matched_files": [],
        "matched_symbols": [],
        "matched_tests": [],
        "matched_archetypes": [],
        "matched_competencies": [],
        "matched_evidence_terms": [],
        "score": 0,
        "claim_status": "not-tested",
    }


def _ratio_score(matched: int, expected: int, weight: float) -> float:
    if expected <= 0:
        return weight
    return round(weight * min(matched / expected, 1.0), 2)


def _suggest_case_fix(
    case: BenchmarkCase,
    matched_files: Sequence[str],
    matched_symbols: Sequence[str],
    matched_tests: Sequence[str],
    matched_evidence: Sequence[str],
    prompt: Mapping[str, Any] | None = None,
) -> str:
    if len(matched_files) < len(case.expected_files):
        return "Improve context search and expected file anchors for this repo family."
    if len(matched_symbols) < len(case.expected_symbols):
        return "Improve AST/symbol extraction for this language or adjust expected symbols."
    if len(matched_tests) < len(case.expected_tests):
        return "Improve test graph detection and benchmark expected test anchors."
    if len(matched_evidence) < len(case.expected_evidence_terms):
        return "Add stronger evidence terms to prompt enhancement and skill resources."
    if prompt and prompt.get("recommended_skill") != case.expected_skill:
        return "Improve prompt routing for this task family or adjust the benchmark expected skill."
    return "No fix required for this benchmark case."


def _claim_status(passed: bool, score: float) -> str:
    if not passed:
        return "needs-hardening"
    if score >= 10:
        return "public-repo-benchmark-tested"
    return "public-repo-benchmark-partial"


def _cleanup_temp_root(project: Path, target: Path) -> None:
    resolved_project = project.resolve()
    resolved_target = target.resolve()
    allowed_root = (resolved_project / TEMP_ROOT).resolve()
    if resolved_target != allowed_root and allowed_root not in resolved_target.parents:
        raise ValueError(f"Refusing to remove path outside benchmark temp root: {resolved_target}")
    if resolved_target.exists():
        shutil.rmtree(resolved_target, onexc=_chmod_and_retry_remove)


def _chmod_and_retry_remove(function, path, excinfo) -> None:
    try:
        os.chmod(path, stat.S_IWRITE)
        function(path)
    except OSError:
        raise excinfo[1]
