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
    repo_url: str
    repo_name: str
    task: str
    query: str
    expected_skill: str
    expected_files: tuple[str, ...]
    expected_symbols: tuple[str, ...]
    expected_evidence_terms: tuple[str, ...]


CURATED_SUITE: tuple[BenchmarkCase, ...] = (
    BenchmarkCase(
        id="itsdangerous-serializer-architecture",
        repo_url="https://github.com/pallets/itsdangerous.git",
        repo_name="pallets-itsdangerous",
        task="read repo and explain serializer signing architecture without running tests",
        query="serializer signer timestamp token expiry",
        expected_skill="scout-hub",
        expected_files=("src/itsdangerous/serializer.py", "src/itsdangerous/timed.py"),
        expected_symbols=("Serializer", "TimedSerializer"),
        expected_evidence_terms=("serializer", "signer", "timestamp", "salt"),
    ),
    BenchmarkCase(
        id="p-limit-concurrency-review",
        repo_url="https://github.com/sindresorhus/p-limit.git",
        repo_name="sindresorhus-p-limit",
        task="find concurrency queue behavior and related tests without installing packages",
        query="concurrency queue activeCount pendingCount",
        expected_skill="review-hub",
        expected_files=("index.js", "test.js"),
        expected_symbols=("pLimit",),
        expected_evidence_terms=("concurrency", "queue", "activeCount", "pendingCount"),
    ),
    BenchmarkCase(
        id="click-command-routing",
        repo_url="https://github.com/pallets/click.git",
        repo_name="pallets-click",
        task="map command parsing architecture and test anchors without running code",
        query="command group context option parser",
        expected_skill="scout-hub",
        expected_files=("src/click/core.py", "tests/test_basic.py"),
        expected_symbols=("Command", "Group"),
        expected_evidence_terms=("command", "context", "option", "parser"),
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
    if suite != "curated":
        raise ValueError(f"Unknown benchmark suite: {suite}")
    return CURATED_SUITE


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
    search = build_context_search(target, query=case.query, limit=12)
    prompt = build_prompt_enhancement(target, prompt=case.task)
    result_paths = [str(item.get("path")) for item in search.get("results", [])]
    matched_files = [expected for expected in case.expected_files if any(expected in path for path in result_paths)]
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
    passed = bool(matched_files) and bool(matched_evidence)
    if case.expected_symbols:
        passed = passed and bool(matched_symbols)
    return {
        "id": case.id,
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
        "matched_evidence_terms": matched_evidence,
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
        "repo_url": case.repo_url,
        "status": "skip",
        "reason": reason,
        "safety": dict(safety or {}),
        "matched_files": [],
        "matched_symbols": [],
        "matched_evidence_terms": [],
    }


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
