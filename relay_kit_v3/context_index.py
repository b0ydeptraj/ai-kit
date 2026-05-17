from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


INDEX_SCHEMA_VERSION = "relay-kit.context-index.v1"
SEARCH_SCHEMA_VERSION = "relay-kit.context-search.v1"
RELATED_SCHEMA_VERSION = "relay-kit.context-related.v1"

DEFAULT_INDEX_PATH = ".relay-kit/context/index.json"
MAX_TEXT_CHARS = 80_000

INDEX_EXTENSIONS = {
    ".css",
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
    files = [_index_file(project, path) for path in _iter_indexable_files(project)]
    files = [item for item in files if item is not None]
    files.sort(key=lambda item: item["path"])
    related_tests = _nearby_tests(files)
    for item in files:
        item["nearby_tests"] = related_tests.get(item["path"], [])
    return {
        "schema_version": INDEX_SCHEMA_VERSION,
        "status": "pass",
        "project_path": str(project),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "file_count": len(files),
            "symbol_count": sum(len(item["symbols"]) for item in files),
            "import_count": sum(len(item["imports"]) for item in files),
            "test_file_count": sum(1 for item in files if item["kind"] == "test"),
            "doc_file_count": sum(1 for item in files if item["kind"] == "doc"),
            "config_file_count": sum(1 for item in files if item["kind"] == "config"),
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
    results = [_score_file(item, terms, query) for item in index.get("files", [])]
    results = [item for item in results if item["score"] > 0]
    results.sort(key=lambda item: (-item["score"], item["path"]))
    limited = results[: max(limit, 0)]
    return {
        "schema_version": SEARCH_SCHEMA_VERSION,
        "status": "pass" if limited else "empty",
        "project_path": str(project),
        "query": query,
        "index_status": "available",
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
    results: list[dict[str, Any]] = []
    for item in files:
        if item.get("path") == source.get("path"):
            continue
        path_value = str(item.get("path", ""))
        shared_terms = sorted(source_terms & (set(item.get("path_terms", [])) | set(item.get("symbols", []))))
        shared_imports = sorted(source_imports & set(item.get("imports", [])))
        reasons: list[str] = []
        score = 0
        if path_value in source_tests:
            score += 30
            reasons.append("nearby-test")
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
                matched_terms=shared_terms[:8],
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


def context_hits_for_prompt(root: Path | str, prompt: str, *, limit: int = 5) -> tuple[str, list[dict[str, Any]]]:
    report = build_context_search(root, query=prompt, limit=limit)
    return str(report.get("index_status", "missing")), list(report.get("results", []))


def render_context_index(report: Mapping[str, Any]) -> str:
    summary = report.get("summary", {})
    return "\n".join(
        [
            "Relay-kit context index",
            f"- status: {report.get('status')}",
            f"- files: {summary.get('file_count', 0)}",
            f"- symbols: {summary.get('symbol_count', 0)}",
            f"- imports: {summary.get('import_count', 0)}",
            f"- tests: {summary.get('test_file_count', 0)}",
            f"- docs: {summary.get('doc_file_count', 0)}",
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


def _is_skipped(relative_path: str) -> bool:
    parts = relative_path.split("/")
    for index in range(len(parts)):
        candidate = "/".join(parts[: index + 1])
        if candidate in SKIP_DIRS or parts[index] in SKIP_DIRS:
            return True
    return False


def _index_file(project: Path, path: Path) -> dict[str, Any] | None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")[:MAX_TEXT_CHARS]
    except OSError:
        return None
    relative = path.relative_to(project).as_posix()
    symbols = _extract_symbols(relative, text)
    imports = _extract_imports(relative, text)
    text_terms = _terms_from_text(text, limit=80)
    path_terms = _path_terms(relative)
    return {
        "path": relative,
        "name": path.name,
        "extension": path.suffix.lower(),
        "kind": _file_kind(relative),
        "symbols": symbols,
        "imports": imports,
        "path_terms": path_terms,
        "text_terms": text_terms,
        "nearby_tests": [],
        "line_count": len(text.splitlines()),
    }


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


def _score_file(item: Mapping[str, Any], terms: Sequence[str], query: str) -> dict[str, Any]:
    path_terms = set(item.get("path_terms", []))
    symbol_terms = {_normalize_term(str(symbol)) for symbol in item.get("symbols", [])}
    import_terms = {_normalize_term(str(value)) for value in item.get("imports", [])}
    text_terms = set(item.get("text_terms", []))
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
        if term in text_terms:
            term_score += 5
            reasons.append("text")
        if term_score:
            score += term_score
            matched.append(term)
    if phrase and phrase in path_value:
        score += 30
        reasons.append("path-phrase")
    if item.get("kind") == "test" and any(term in {"test", "spec", "ci", "login"} for term in terms):
        score += 6
        reasons.append("nearby-test")
    return _result_item(item, score=score, matched_terms=matched, reasons=reasons)


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
        "nearby_tests": list(item.get("nearby_tests", []))[:5],
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
