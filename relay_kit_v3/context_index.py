from __future__ import annotations

import json
import hashlib
import re
import sqlite3
import subprocess
import time
import unicodedata
from datetime import datetime, timezone
from importlib.util import find_spec
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


INDEX_SCHEMA_VERSION = "relay-kit.context-index.v1"
INDEX_ENGINE_VERSION = "hybrid-local-v3"
SEARCH_SCHEMA_VERSION = "relay-kit.context-search.v1"
RELATED_SCHEMA_VERSION = "relay-kit.context-related.v1"
EXPLAIN_SYMBOL_SCHEMA_VERSION = "relay-kit.context-explain-symbol.v1"
ACTIVE_CONTEXT_SCHEMA_VERSION = "relay-kit.context-active.v1"
MCP_SCHEMA_VERSION = "relay-kit.context-mcp.v1"

DEFAULT_INDEX_PATH = ".relay-kit/context/index.json"
DEFAULT_SQLITE_INDEX_PATH = ".relay-kit/context/index.sqlite"
DEFAULT_ACTIVE_CONTEXT_PATH = ".relay-kit/context/active.json"
MAX_TEXT_CHARS = 80_000

INDEX_EXTENSIONS = {
    ".css",
    ".csv",
    ".go",
    ".html",
    ".js",
    ".jsx",
    ".json",
    ".md",
    ".mdx",
    ".py",
    ".rs",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}

SKIP_DIRS = {
    ".agent",
    ".claude",
    ".codex",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".relay-kit/context",
    ".tmp",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "target",
}

CONFIG_NAMES = {
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "tsconfig.json",
    "vite.config.ts",
    "next.config.js",
    "next.config.mjs",
    "pytest.ini",
}


def build_context_index(root: Path | str) -> dict[str, Any]:
    project = Path(root).resolve()
    previous = load_context_index(project)
    previous_by_path = {
        str(item.get("path")): item
        for item in (previous or {}).get("files", [])
        if isinstance(item, Mapping) and item.get("path")
    }
    reused_count = 0
    files: list[dict[str, Any]] = []
    for path in _iter_indexable_files(project):
        item, reused = _index_file(project, path, previous_by_path=previous_by_path)
        if item is None:
            continue
        files.append(item)
        if reused:
            reused_count += 1
    files = [item for item in files if item is not None]
    files.sort(key=lambda item: item["path"])
    related_tests = _nearby_tests(files)
    git_history = _git_history_counts(project)
    symbol_index = _build_symbol_index(files)
    for item in files:
        item["nearby_tests"] = related_tests.get(item["path"], [])
        item["git_history"] = {
            "recent_change_count": git_history.get(item["path"], 0),
        }
        item["call_targets"] = _resolve_call_targets(item, symbol_index)
    return {
        "schema_version": INDEX_SCHEMA_VERSION,
        "engine_version": INDEX_ENGINE_VERSION,
        "status": "pass",
        "project_path": str(project),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "storage": {
            "json_path": str((project / DEFAULT_INDEX_PATH).resolve()),
            "sqlite_path": str((project / DEFAULT_SQLITE_INDEX_PATH).resolve()),
            "sqlite_fts": True,
        },
        "capabilities": {
            "path_name": True,
            "symbols": True,
            "imports": True,
            "nearby_tests": True,
            "docs_config": True,
            "local_chunks": True,
            "call_graph_hints": True,
            "git_history_hints": bool(git_history),
            "sqlite_fts": True,
            "incremental_index": True,
            "ast_parser": True,
            "active_context": True,
            "mcp_local": True,
            "optional_local_embeddings": find_spec("fastembed") is not None,
        },
        "ast": _ast_status(),
        "semantic": {
            "provider": "fastembed",
            "status": "available" if find_spec("fastembed") is not None else "unavailable",
            "used": False,
            "note": "Install relay-kit[context] to enable local embedding experiments; lexical and graph search work without it.",
        },
        "summary": {
            "file_count": len(files),
            "symbol_count": sum(len(item["symbols"]) for item in files),
            "import_count": sum(len(item["imports"]) for item in files),
            "chunk_count": sum(len(item.get("chunks", [])) for item in files),
            "call_hint_count": sum(len(item.get("call_hints", [])) for item in files),
            "test_file_count": sum(1 for item in files if item["kind"] == "test"),
            "doc_file_count": sum(1 for item in files if item["kind"] == "doc"),
            "config_file_count": sum(1 for item in files if item["kind"] == "config"),
            "reused_file_count": reused_count,
        },
        "files": files,
    }


def write_context_index(
    root: Path | str,
    report: Mapping[str, Any],
    output_file: Path | str | None = None,
) -> Path:
    project = Path(root).resolve()
    target = Path(output_file) if output_file else project / DEFAULT_INDEX_PATH
    if not target.is_absolute():
        target = project / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    write_sqlite_context_index(project, report)
    return target


def write_sqlite_context_index(root: Path | str, report: Mapping[str, Any], output_file: Path | str | None = None) -> Path:
    project = Path(root).resolve()
    target = Path(output_file) if output_file else project / DEFAULT_SQLITE_INDEX_PATH
    if not target.is_absolute():
        target = project / target
    target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target)
    try:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute(
            "CREATE TABLE IF NOT EXISTS files ("
            "path TEXT PRIMARY KEY, kind TEXT, name TEXT, extension TEXT, "
            "symbols TEXT, imports TEXT, call_hints TEXT, nearby_tests TEXT, "
            "content_hash TEXT, mtime_ns INTEGER, size INTEGER)"
        )
        connection.execute("CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(path, chunk_id, content)")
        connection.execute("DELETE FROM files")
        connection.execute("DELETE FROM chunks_fts")
        for item in report.get("files", []):
            if not isinstance(item, Mapping):
                continue
            connection.execute(
                "INSERT OR REPLACE INTO files VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    item.get("path"),
                    item.get("kind"),
                    item.get("name"),
                    item.get("extension"),
                    json.dumps(item.get("symbols", []), ensure_ascii=True),
                    json.dumps(item.get("imports", []), ensure_ascii=True),
                    json.dumps(item.get("call_hints", []), ensure_ascii=True),
                    json.dumps(item.get("nearby_tests", []), ensure_ascii=True),
                    item.get("content_hash"),
                    int(item.get("mtime_ns", 0)),
                    int(item.get("size", 0)),
                ),
            )
            for chunk in item.get("chunks", []):
                if not isinstance(chunk, Mapping):
                    continue
                terms = " ".join(str(term) for term in chunk.get("text_terms", []))
                symbols = " ".join(str(symbol) for symbol in chunk.get("symbols", []))
                content = f"{item.get('path')} {item.get('name')} {terms} {symbols}"
                connection.execute(
                    "INSERT INTO chunks_fts(path, chunk_id, content) VALUES (?, ?, ?)",
                    (item.get("path"), chunk.get("id"), content),
                )
        connection.commit()
    finally:
        connection.close()
    return target


def load_context_index(root: Path | str, index_file: Path | str | None = None) -> dict[str, Any] | None:
    project = Path(root).resolve()
    target = Path(index_file) if index_file else project / DEFAULT_INDEX_PATH
    if not target.is_absolute():
        target = project / target
    if not target.exists():
        return None
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if payload.get("schema_version") != INDEX_SCHEMA_VERSION:
        return None
    return payload


def build_context_search(
    root: Path | str,
    *,
    query: str,
    limit: int = 10,
    index_file: Path | str | None = None,
) -> dict[str, Any]:
    project = Path(root).resolve()
    index = load_context_index(project, index_file=index_file)
    terms = _query_terms(query)
    if index is None:
        return _empty_search(project, query, "missing-index")
    if not terms:
        return _empty_search(project, query, "empty-query", indexed=index)
    fts_matches = _sqlite_fts_matches(project, query)
    results = [_score_file(item, terms, query, fts_matches=fts_matches) for item in index.get("files", [])]
    results = [item for item in results if item["score"] > 0]
    results.sort(key=lambda item: (-item["score"], item["path"]))
    limited = results[: max(limit, 0)]
    return {
        "schema_version": SEARCH_SCHEMA_VERSION,
        "status": "pass" if limited else "empty",
        "project_path": str(project),
        "query": query,
        "index_status": "available",
        "storage": {
            "sqlite_fts": bool(fts_matches),
            "sqlite_path": str((project / DEFAULT_SQLITE_INDEX_PATH).resolve()),
        },
        "summary": {
            "indexed_file_count": index.get("summary", {}).get("file_count", 0),
            "hit_count": len(results),
            "returned": len(limited),
        },
        "results": limited,
    }


def build_context_related(
    root: Path | str,
    *,
    path: str,
    limit: int = 10,
    index_file: Path | str | None = None,
) -> dict[str, Any]:
    project = Path(root).resolve()
    index = load_context_index(project, index_file=index_file)
    display_path = _normalize_display_path(project, path)
    if index is None:
        return _empty_related(project, display_path, "missing-index")
    files = list(index.get("files", []))
    source = next((item for item in files if item.get("path") == display_path), None)
    if source is None:
        return _empty_related(project, display_path, "path-not-indexed", indexed=index)
    source_terms = set(source.get("path_terms", [])) | set(source.get("symbols", []))
    source_imports = set(source.get("imports", []))
    source_tests = set(source.get("nearby_tests", []))
    source_call_paths = {
        path
        for target in source.get("call_targets", [])
        for path in target.get("paths", [])
    }
    results: list[dict[str, Any]] = []
    for item in files:
        if item.get("path") == source.get("path"):
            continue
        path_value = str(item.get("path", ""))
        shared_terms = sorted(source_terms & (set(item.get("path_terms", [])) | set(item.get("symbols", []))))
        shared_imports = sorted(source_imports & set(item.get("imports", [])))
        shared_calls = sorted(source_call_paths & {path_value})
        reasons: list[str] = []
        score = 0
        if path_value in source_tests:
            score += 30
            reasons.append("nearby-test")
        if shared_calls:
            score += 24
            reasons.append("call-graph-hint")
        if shared_terms:
            score += min(len(shared_terms), 5) * 5
            reasons.append("shared-path-or-symbol")
        if shared_imports:
            score += min(len(shared_imports), 5) * 6
            reasons.append("shared-import")
        if _same_directory(source, item):
            score += 4
            reasons.append("same-directory")
        if score <= 0:
            continue
        results.append(
            _result_item(
                item,
                score=score,
                matched_terms=[*shared_terms[:8], *shared_calls[:2]],
                reasons=reasons,
            )
        )
    results.sort(key=lambda item: (-item["score"], item["path"]))
    limited = results[: max(limit, 0)]
    return {
        "schema_version": RELATED_SCHEMA_VERSION,
        "status": "pass" if limited else "empty",
        "project_path": str(project),
        "path": display_path,
        "index_status": "available",
        "source": {
            "path": source.get("path"),
            "kind": source.get("kind"),
            "symbols": source.get("symbols", [])[:20],
            "imports": source.get("imports", [])[:20],
            "nearby_tests": source.get("nearby_tests", []),
        },
        "summary": {
            "indexed_file_count": index.get("summary", {}).get("file_count", 0),
            "related_count": len(results),
            "returned": len(limited),
        },
        "results": limited,
    }


def build_context_explain_symbol(
    root: Path | str,
    *,
    symbol: str,
    limit: int = 10,
    index_file: Path | str | None = None,
) -> dict[str, Any]:
    project = Path(root).resolve()
    index = load_context_index(project, index_file=index_file)
    normalized = _normalize_term(symbol)
    if index is None:
        return {
            "schema_version": EXPLAIN_SYMBOL_SCHEMA_VERSION,
            "status": "empty",
            "project_path": str(project),
            "symbol": symbol,
            "index_status": "missing",
            "definitions": [],
            "references": [],
            "related_tests": [],
            "summary": {"reason": "missing-index", "definition_count": 0, "reference_count": 0},
        }
    definitions: list[dict[str, Any]] = []
    references: list[dict[str, Any]] = []
    related_tests: list[str] = []
    for item in index.get("files", []):
        if not isinstance(item, Mapping):
            continue
        item_symbols = {str(value): _normalize_term(str(value)) for value in item.get("symbols", [])}
        item_calls = {str(value): _normalize_term(str(value)) for value in item.get("call_hints", [])}
        if normalized in item_symbols.values():
            definitions.append(_result_item(item, score=100, matched_terms=[symbol], reasons=["symbol-definition"]))
            for test_path in item.get("nearby_tests", []):
                if test_path not in related_tests:
                    related_tests.append(str(test_path))
        if normalized in item_calls.values():
            references.append(_result_item(item, score=50, matched_terms=[symbol], reasons=["call-reference"]))
            for test_path in item.get("nearby_tests", []):
                if test_path not in related_tests:
                    related_tests.append(str(test_path))
    definitions.sort(key=lambda item: item["path"])
    references.sort(key=lambda item: item["path"])
    status = "pass" if definitions or references else "empty"
    return {
        "schema_version": EXPLAIN_SYMBOL_SCHEMA_VERSION,
        "status": status,
        "project_path": str(project),
        "symbol": symbol,
        "index_status": "available",
        "definitions": definitions[: max(limit, 0)],
        "references": references[: max(limit, 0)],
        "related_tests": related_tests[: max(limit, 0)],
        "summary": {
            "definition_count": len(definitions),
            "reference_count": len(references),
            "related_test_count": len(related_tests),
        },
    }


def write_active_context(
    root: Path | str,
    *,
    file_path: str,
    selection: str | None = None,
    output_file: Path | str | None = None,
) -> dict[str, Any]:
    project = Path(root).resolve()
    target = Path(output_file) if output_file else project / DEFAULT_ACTIVE_CONTEXT_PATH
    if not target.is_absolute():
        target = project / target
    display_path = _normalize_display_path(project, file_path)
    payload = {
        "schema_version": ACTIVE_CONTEXT_SCHEMA_VERSION,
        "status": "pass",
        "project_path": str(project),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "active_file": display_path,
        "selection": selection or "",
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return payload


def read_active_context(root: Path | str, *, active_file: Path | str | None = None) -> dict[str, Any]:
    project = Path(root).resolve()
    target = Path(active_file) if active_file else project / DEFAULT_ACTIVE_CONTEXT_PATH
    if not target.is_absolute():
        target = project / target
    if not target.exists():
        return {
            "schema_version": ACTIVE_CONTEXT_SCHEMA_VERSION,
            "status": "empty",
            "project_path": str(project),
            "active_file": None,
            "selection": "",
            "summary": {"reason": "missing-active-context"},
        }
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {
            "schema_version": ACTIVE_CONTEXT_SCHEMA_VERSION,
            "status": "empty",
            "project_path": str(project),
            "active_file": None,
            "selection": "",
            "summary": {"reason": "invalid-active-context"},
        }
    if payload.get("schema_version") != ACTIVE_CONTEXT_SCHEMA_VERSION:
        payload["schema_version"] = ACTIVE_CONTEXT_SCHEMA_VERSION
    payload.setdefault("status", "pass")
    payload.setdefault("project_path", str(project))
    return payload


def build_context_mcp_tool_result(root: Path | str, tool_name: str, arguments: Mapping[str, Any] | None = None) -> dict[str, Any]:
    args = dict(arguments or {})
    if tool_name == "context.search":
        return build_context_search(root, query=str(args.get("query", "")), limit=int(args.get("limit", 10)))
    if tool_name == "context.related":
        return build_context_related(root, path=str(args.get("path", "")), limit=int(args.get("limit", 10)))
    if tool_name == "context.explain_symbol":
        return build_context_explain_symbol(root, symbol=str(args.get("symbol", "")), limit=int(args.get("limit", 10)))
    if tool_name == "context.active":
        return read_active_context(root)
    return {
        "schema_version": MCP_SCHEMA_VERSION,
        "status": "error",
        "project_path": str(Path(root).resolve()),
        "error": f"unknown tool: {tool_name}",
    }


def context_mcp_manifest(root: Path | str) -> dict[str, Any]:
    return {
        "schema_version": MCP_SCHEMA_VERSION,
        "status": "pass",
        "project_path": str(Path(root).resolve()),
        "tools": [
            {"name": "context.search", "description": "Search the local Relay-kit context index."},
            {"name": "context.related", "description": "Find files related to a path."},
            {"name": "context.explain_symbol", "description": "Explain definitions, references, and tests for a symbol."},
            {"name": "context.active", "description": "Read the active file/selection context."},
        ],
    }


def context_hits_for_prompt(root: Path | str, prompt: str, *, limit: int = 5) -> tuple[str, list[dict[str, Any]]]:
    report = build_context_search(root, query=prompt, limit=limit)
    return str(report.get("index_status", "missing")), list(report.get("results", []))


def watch_context_index(
    root: Path | str,
    *,
    output_file: Path | str | None = None,
    once: bool = False,
    interval_seconds: float = 2.0,
    max_iterations: int | None = None,
) -> dict[str, Any]:
    project = Path(root).resolve()
    iterations = 0
    last_signature: tuple[int, int] | None = None
    last_output: Path | None = None
    while True:
        signature = _tree_signature(project)
        if signature != last_signature:
            report = build_context_index(project)
            last_output = write_context_index(project, report, output_file=output_file)
            last_signature = signature
        iterations += 1
        if once or (max_iterations is not None and iterations >= max_iterations):
            return {
                "schema_version": INDEX_SCHEMA_VERSION,
                "engine_version": INDEX_ENGINE_VERSION,
                "status": "pass",
                "project_path": str(project),
                "iterations": iterations,
                "output_file": str(last_output) if last_output else None,
                "signature": {
                    "file_count": signature[0],
                    "mtime_total": signature[1],
                },
            }
        time.sleep(max(interval_seconds, 0.1))


def render_context_index(report: Mapping[str, Any]) -> str:
    summary = report.get("summary", {})
    capabilities = report.get("capabilities", {})
    return "\n".join(
        [
            "Relay-kit context index",
            f"- status: {report.get('status')}",
            f"- engine: {report.get('engine_version', 'legacy')}",
            f"- files: {summary.get('file_count', 0)}",
            f"- symbols: {summary.get('symbol_count', 0)}",
            f"- imports: {summary.get('import_count', 0)}",
            f"- chunks: {summary.get('chunk_count', 0)}",
            f"- call hints: {summary.get('call_hint_count', 0)}",
            f"- tests: {summary.get('test_file_count', 0)}",
            f"- docs: {summary.get('doc_file_count', 0)}",
            f"- optional local embeddings: {capabilities.get('optional_local_embeddings', False)}",
        ]
    )


def render_context_search(report: Mapping[str, Any]) -> str:
    lines = [
        "Relay-kit context search",
        f"- status: {report.get('status')}",
        f"- index: {report.get('index_status')}",
        f"- query: {report.get('query')}",
        f"- hits: {report.get('summary', {}).get('hit_count', 0)}",
    ]
    for result in report.get("results", [])[:10]:
        lines.append(
            f"  - {result.get('path')} "
            f"[{result.get('kind')} score={result.get('score')}] {', '.join(result.get('reasons', []))}"
        )
    return "\n".join(lines)


def render_context_related(report: Mapping[str, Any]) -> str:
    lines = [
        "Relay-kit context related",
        f"- status: {report.get('status')}",
        f"- index: {report.get('index_status')}",
        f"- path: {report.get('path')}",
        f"- related: {report.get('summary', {}).get('related_count', 0)}",
    ]
    for result in report.get("results", [])[:10]:
        lines.append(
            f"  - {result.get('path')} "
            f"[{result.get('kind')} score={result.get('score')}] {', '.join(result.get('reasons', []))}"
        )
    return "\n".join(lines)


def render_context_watch(report: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "Relay-kit context watch",
            f"- status: {report.get('status')}",
            f"- engine: {report.get('engine_version', 'legacy')}",
            f"- iterations: {report.get('iterations', 0)}",
            f"- output: {report.get('output_file')}",
        ]
    )


def render_context_explain_symbol(report: Mapping[str, Any]) -> str:
    lines = [
        "Relay-kit context explain-symbol",
        f"- status: {report.get('status')}",
        f"- index: {report.get('index_status')}",
        f"- symbol: {report.get('symbol')}",
        f"- definitions: {report.get('summary', {}).get('definition_count', 0)}",
        f"- references: {report.get('summary', {}).get('reference_count', 0)}",
    ]
    for result in report.get("definitions", [])[:5]:
        lines.append(f"  - def {result.get('path')} [{result.get('kind')}]")
    for result in report.get("references", [])[:5]:
        lines.append(f"  - ref {result.get('path')} [{result.get('kind')}]")
    return "\n".join(lines)


def render_active_context(report: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "Relay-kit context active",
            f"- status: {report.get('status')}",
            f"- active file: {report.get('active_file')}",
            f"- selection: {'present' if report.get('selection') else 'empty'}",
        ]
    )


def render_context_mcp(report: Mapping[str, Any]) -> str:
    lines = [
        "Relay-kit context MCP",
        f"- status: {report.get('status')}",
        f"- project: {report.get('project_path')}",
    ]
    for tool in report.get("tools", []):
        lines.append(f"  - {tool.get('name')}: {tool.get('description')}")
    return "\n".join(lines)


def _iter_indexable_files(project: Path) -> Iterable[Path]:
    for path in project.rglob("*"):
        if not path.is_file():
            continue
        try:
            relative = path.relative_to(project).as_posix()
        except ValueError:
            continue
        if _is_skipped(relative):
            continue
        if path.suffix.lower() not in INDEX_EXTENSIONS:
            continue
        yield path


def _tree_signature(project: Path) -> tuple[int, int]:
    file_count = 0
    mtime_total = 0
    for path in _iter_indexable_files(project):
        try:
            stat = path.stat()
        except OSError:
            continue
        file_count += 1
        mtime_total += int(stat.st_mtime)
    return file_count, mtime_total


def _is_skipped(relative_path: str) -> bool:
    parts = relative_path.split("/")
    for index in range(len(parts)):
        candidate = "/".join(parts[: index + 1])
        if candidate in SKIP_DIRS or parts[index] in SKIP_DIRS:
            return True
    return False


def _index_file(
    project: Path,
    path: Path,
    *,
    previous_by_path: Mapping[str, Mapping[str, Any]] | None = None,
) -> tuple[dict[str, Any] | None, bool]:
    previous_by_path = previous_by_path or {}
    try:
        stat = path.stat()
    except OSError:
        return None, False
    relative = path.relative_to(project).as_posix()
    previous = previous_by_path.get(relative)
    if previous and previous.get("engine_version") == INDEX_ENGINE_VERSION:
        if int(previous.get("mtime_ns", -1)) == int(stat.st_mtime_ns) and int(previous.get("size", -1)) == int(stat.st_size):
            return dict(previous), True
    try:
        raw_text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None, False
    text = raw_text[:MAX_TEXT_CHARS]
    symbols = _extract_symbols(relative, text)
    imports = _extract_imports(relative, text)
    call_hints = _extract_call_hints(relative, text)
    text_terms = _terms_from_text(text, limit=80)
    path_terms = _path_terms(relative)
    return {
        "path": relative,
        "name": path.name,
        "extension": path.suffix.lower(),
        "engine_version": INDEX_ENGINE_VERSION,
        "kind": _file_kind(relative),
        "symbols": symbols,
        "imports": imports,
        "call_hints": call_hints,
        "call_targets": [],
        "path_terms": path_terms,
        "text_terms": text_terms,
        "chunks": _extract_chunks(relative, text, symbols),
        "nearby_tests": [],
        "git_history": {"recent_change_count": 0},
        "line_count": len(text.splitlines()),
        "content_hash": hashlib.sha256(raw_text.encode("utf-8", errors="replace")).hexdigest(),
        "mtime_ns": int(stat.st_mtime_ns),
        "size": int(stat.st_size),
    }, False


def _extract_symbols(relative: str, text: str) -> list[str]:
    suffix = Path(relative).suffix.lower()
    patterns: list[str] = []
    if suffix == ".py":
        patterns = [
            r"^\s*(?:async\s+def|def)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
            r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)\b",
        ]
    elif suffix in {".js", ".jsx", ".ts", ".tsx"}:
        patterns = [
            r"\b(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\(",
            r"\b(?:export\s+)?class\s+([A-Za-z_$][A-Za-z0-9_$]*)\b",
            r"\b(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=",
            r"\b(?:export\s+)?(?:interface|type)\s+([A-Za-z_$][A-Za-z0-9_$]*)\b",
        ]
    elif suffix == ".go":
        patterns = [r"\bfunc\s+(?:\([^)]+\)\s*)?([A-Za-z_][A-Za-z0-9_]*)\s*\(", r"\btype\s+([A-Za-z_][A-Za-z0-9_]*)\s+"]
    elif suffix == ".rs":
        patterns = [r"\bfn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", r"\b(?:struct|enum|trait)\s+([A-Za-z_][A-Za-z0-9_]*)\b"]
    elif suffix in {".md", ".mdx", ".txt", ".json", ".yaml", ".yml", ".csv"}:
        patterns = [
            r"^\s*#+\s+([A-Za-z_][A-Za-z0-9_-]*)\b",
            r"`([A-Za-z_][A-Za-z0-9_-]*)`",
            r"\b([A-Z][A-Za-z0-9_]{3,})\b",
        ]
    symbols: list[str] = []
    for pattern in patterns:
        for match in re.findall(pattern, text, flags=re.MULTILINE):
            if match not in symbols:
                symbols.append(match)
    return symbols[:80]


def _extract_imports(relative: str, text: str) -> list[str]:
    suffix = Path(relative).suffix.lower()
    imports: list[str] = []
    patterns: list[str] = []
    if suffix == ".py":
        patterns = [r"^\s*import\s+([A-Za-z0-9_.,\s]+)", r"^\s*from\s+([A-Za-z0-9_.]+)\s+import\s+"]
    elif suffix in {".js", ".jsx", ".ts", ".tsx"}:
        patterns = [r"\bfrom\s+['\"]([^'\"]+)['\"]", r"\brequire\(\s*['\"]([^'\"]+)['\"]\s*\)"]
    elif suffix == ".go":
        patterns = [r"^\s*\"([A-Za-z0-9_./-]+)\""]
    elif suffix == ".rs":
        patterns = [r"^\s*use\s+([^;]+);"]
    for pattern in patterns:
        for match in re.findall(pattern, text, flags=re.MULTILINE):
            for value in str(match).split(","):
                value = value.strip()
                if value and value not in imports:
                    imports.append(value)
    return imports[:80]


def _extract_call_hints(relative: str, text: str) -> list[str]:
    suffix = Path(relative).suffix.lower()
    if suffix not in {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs"}:
        return []
    ignored = {
        "if",
        "for",
        "while",
        "switch",
        "catch",
        "return",
        "function",
        "def",
        "class",
        "new",
        "await",
        "async",
        "test",
        "describe",
    }
    hints: list[str] = []
    for match in re.findall(r"\b([A-Za-z_][$A-Za-z0-9_]*)\s*\(", text[:MAX_TEXT_CHARS]):
        if match in ignored or match in hints:
            continue
        hints.append(match)
        if len(hints) >= 100:
            break
    return hints


def _extract_chunks(relative: str, text: str, symbols: Sequence[str]) -> list[dict[str, Any]]:
    lines = text.splitlines()
    chunks: list[dict[str, Any]] = []
    symbol_set = set(symbols)
    for index, line in enumerate(lines, start=1):
        if len(chunks) >= 16:
            break
        names = [symbol for symbol in symbol_set if re.search(rf"\b{re.escape(symbol)}\b", line)]
        if not names and index != 1 and index % 80 != 0:
            continue
        start = max(index - 4, 1)
        end = min(index + 12, len(lines))
        text_slice = "\n".join(lines[start - 1 : end])
        chunks.append(
            {
                "id": f"{relative}:{start}-{end}",
                "path": relative,
                "line_start": start,
                "line_end": end,
                "symbols": names[:8],
                "text_terms": _terms_from_text(text_slice, limit=40),
            }
        )
    if not chunks and lines:
        text_slice = "\n".join(lines[: min(40, len(lines))])
        chunks.append(
            {
                "id": f"{relative}:1-{min(40, len(lines))}",
                "path": relative,
                "line_start": 1,
                "line_end": min(40, len(lines)),
                "symbols": [],
                "text_terms": _terms_from_text(text_slice, limit=40),
            }
        )
    return chunks


def _build_symbol_index(files: Sequence[Mapping[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for item in files:
        path = str(item.get("path", ""))
        for symbol in item.get("symbols", []):
            key = _normalize_term(str(symbol))
            if not key:
                continue
            index.setdefault(key, [])
            if path not in index[key]:
                index[key].append(path)
    return index


def _resolve_call_targets(item: Mapping[str, Any], symbol_index: Mapping[str, Sequence[str]]) -> list[dict[str, Any]]:
    source_path = str(item.get("path", ""))
    targets: list[dict[str, Any]] = []
    for call in item.get("call_hints", []):
        key = _normalize_term(str(call))
        paths = [path for path in symbol_index.get(key, []) if path != source_path]
        if not paths:
            continue
        targets.append({"symbol": call, "paths": paths[:5]})
        if len(targets) >= 20:
            break
    return targets


def _git_history_counts(project: Path) -> dict[str, int]:
    if not (project / ".git").exists():
        return {}
    try:
        completed = subprocess.run(
            ["git", "log", "--name-only", "--max-count", "50", "--pretty=format:"],
            cwd=project,
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return {}
    if completed.returncode != 0:
        return {}
    counts: dict[str, int] = {}
    for raw in completed.stdout.splitlines():
        value = raw.strip().replace("\\", "/")
        if not value or _is_skipped(value):
            continue
        counts[value] = counts.get(value, 0) + 1
    return counts


def _nearby_tests(files: Sequence[Mapping[str, Any]]) -> dict[str, list[str]]:
    tests = [item for item in files if item.get("kind") == "test"]
    result: dict[str, list[str]] = {}
    for item in files:
        if item.get("kind") == "test":
            continue
        source_terms = set(item.get("path_terms", [])) | {_normalize_term(str(symbol)) for symbol in item.get("symbols", [])}
        matches: list[tuple[int, str]] = []
        for test in tests:
            test_terms = set(test.get("path_terms", [])) | {_normalize_term(str(symbol)) for symbol in test.get("symbols", [])}
            overlap = {term for term in source_terms & test_terms if len(term) >= 3}
            score = len(overlap) * 10
            if _same_directory(item, test):
                score += 4
            if score > 0:
                matches.append((score, str(test.get("path"))))
        matches.sort(key=lambda pair: (-pair[0], pair[1]))
        result[str(item.get("path"))] = [path for _, path in matches[:5]]
    return result


def _score_file(
    item: Mapping[str, Any],
    terms: Sequence[str],
    query: str,
    *,
    fts_matches: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    path_terms = set(item.get("path_terms", []))
    symbol_terms = {_normalize_term(str(symbol)) for symbol in item.get("symbols", [])}
    import_terms = {_normalize_term(str(value)) for value in item.get("imports", [])}
    text_terms = set(item.get("text_terms", []))
    chunk_terms = {
        str(term)
        for chunk in item.get("chunks", [])
        for term in chunk.get("text_terms", [])
    }
    call_terms = {_normalize_term(str(value)) for value in item.get("call_hints", [])}
    path_value = str(item.get("path", "")).casefold()
    phrase = normalize_text(query)
    score = 0
    matched: list[str] = []
    reasons: list[str] = []
    for term in terms:
        term_score = 0
        if term in path_terms or term in path_value:
            term_score += 25
            reasons.append("path")
        if term in symbol_terms:
            term_score += 20
            reasons.append("symbol")
        if term in import_terms:
            term_score += 12
            reasons.append("import")
        if term in call_terms:
            term_score += 10
            reasons.append("call-hint")
        if term in chunk_terms:
            term_score += 8
            reasons.append("chunk")
        if term in text_terms:
            term_score += 5
            reasons.append("text")
        if term_score:
            score += term_score
            matched.append(term)
    if phrase and phrase in path_value:
        score += 30
        reasons.append("path-phrase")
    if fts_matches and item.get("path") in fts_matches:
        score += int(fts_matches[str(item.get("path"))])
        reasons.append("sqlite-fts")
    if item.get("kind") == "test" and any(term in {"test", "spec", "ci", "login"} for term in terms):
        score += 6
        reasons.append("nearby-test")
    return _result_item(item, score=score, matched_terms=matched, reasons=reasons)


def _sqlite_fts_matches(project: Path, query: str) -> dict[str, int]:
    target = project / DEFAULT_SQLITE_INDEX_PATH
    if not target.exists() or not query.strip():
        return {}
    normalized_terms = _query_terms(query)
    if not normalized_terms:
        return {}
    fts_query = " OR ".join(term.replace('"', "") for term in normalized_terms[:8])
    matches: dict[str, int] = {}
    try:
        connection = sqlite3.connect(target)
        try:
            rows = connection.execute(
                "SELECT path, COUNT(*) FROM chunks_fts WHERE chunks_fts MATCH ? GROUP BY path",
                (fts_query,),
            ).fetchall()
        finally:
            connection.close()
    except sqlite3.Error:
        return {}
    for path, count in rows:
        matches[str(path)] = min(int(count), 5) * 6
    return matches


def _result_item(
    item: Mapping[str, Any],
    *,
    score: int,
    matched_terms: Sequence[str],
    reasons: Sequence[str],
) -> dict[str, Any]:
    return {
        "score": int(score),
        "path": item.get("path"),
        "kind": item.get("kind"),
        "matched_terms": sorted(set(matched_terms)),
        "reasons": sorted(set(reasons)),
        "symbols": list(item.get("symbols", []))[:10],
        "imports": list(item.get("imports", []))[:10],
        "call_hints": list(item.get("call_hints", []))[:10],
        "call_targets": list(item.get("call_targets", []))[:5],
        "nearby_tests": list(item.get("nearby_tests", []))[:5],
        "git_history": dict(item.get("git_history", {})),
    }


def _empty_search(
    project: Path,
    query: str,
    reason: str,
    *,
    indexed: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SEARCH_SCHEMA_VERSION,
        "status": "empty",
        "project_path": str(project),
        "query": query,
        "index_status": "available" if indexed is not None else "missing",
        "summary": {
            "indexed_file_count": indexed.get("summary", {}).get("file_count", 0) if indexed else 0,
            "hit_count": 0,
            "returned": 0,
            "reason": reason,
        },
        "results": [],
    }


def _empty_related(
    project: Path,
    path: str,
    reason: str,
    *,
    indexed: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": RELATED_SCHEMA_VERSION,
        "status": "empty",
        "project_path": str(project),
        "path": path,
        "index_status": "available" if indexed is not None else "missing",
        "source": None,
        "summary": {
            "indexed_file_count": indexed.get("summary", {}).get("file_count", 0) if indexed else 0,
            "related_count": 0,
            "returned": 0,
            "reason": reason,
        },
        "results": [],
    }


def _query_terms(query: str) -> list[str]:
    terms = []
    for raw in re.findall(r"[A-Za-z0-9_.-]+", normalize_text(query)):
        term = _normalize_term(raw)
        if len(term) >= 2 and term not in terms:
            terms.append(term)
    return terms


def _terms_from_text(text: str, *, limit: int) -> list[str]:
    terms: list[str] = []
    for raw in re.findall(r"[A-Za-z0-9_.-]+", normalize_text(text[:MAX_TEXT_CHARS])):
        term = _normalize_term(raw)
        if len(term) < 3 or term in terms:
            continue
        terms.append(term)
        if len(terms) >= limit:
            break
    return terms


def _path_terms(relative: str) -> list[str]:
    parts = re.split(r"[/\\_.\-\s]+", relative)
    terms: list[str] = []
    for part in parts:
        for raw in _split_identifier(part):
            term = _normalize_term(raw)
            if len(term) >= 2 and term not in terms:
                terms.append(term)
    return terms


def _split_identifier(value: str) -> list[str]:
    pieces = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value).split()
    return pieces or [value]


def _normalize_term(value: str) -> str:
    return normalize_text(value).strip("._-")


def normalize_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    ascii_text = decomposed.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_text.casefold()).strip()


def _file_kind(relative: str) -> str:
    path = Path(relative)
    lowered = relative.casefold()
    name = path.name.casefold()
    if name in CONFIG_NAMES or lowered.startswith(".github/") or lowered.startswith(".relay-kit/contracts/"):
        return "config"
    if path.suffix.lower() in {".md", ".mdx", ".txt"} or lowered.startswith("docs/"):
        return "doc"
    if re.search(r"(^|[/_.-])(test|spec)([/_.-]|$)", lowered) or lowered.endswith((".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx", "_test.go")):
        return "test"
    return "source"


def _same_directory(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return str(Path(str(left.get("path", ""))).parent) == str(Path(str(right.get("path", ""))).parent)


def _normalize_display_path(project: Path, path: str) -> str:
    candidate = Path(path)
    if candidate.is_absolute():
        try:
            return candidate.resolve().relative_to(project).as_posix()
        except ValueError:
            return candidate.as_posix()
    return candidate.as_posix().replace("\\", "/")


def _ast_status() -> dict[str, Any]:
    tree_sitter_available = find_spec("tree_sitter") is not None
    language_pack_available = find_spec("tree_sitter_language_pack") is not None
    return {
        "provider": "tree-sitter",
        "status": "available" if tree_sitter_available and language_pack_available else "fallback-regex",
        "tree_sitter_available": tree_sitter_available,
        "language_pack_available": language_pack_available,
        "fallback": not (tree_sitter_available and language_pack_available),
        "note": "tree-sitter is optional; Relay-kit keeps regex AST fallback when the extra is not installed.",
    }
