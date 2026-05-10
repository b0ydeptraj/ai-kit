from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


SCHEMA_VERSION = "relay-kit.query-search.v1"

DEFAULT_SCOPES = ("state", "contracts", "docs", "evidence", "registry")
SCOPE_CONFIG = {
    "state": {
        "roots": [".relay-kit/state"],
        "patterns": ["*.md", "*.json", "*.jsonl"],
        "authority": 0.9,
    },
    "contracts": {
        "roots": [".relay-kit/contracts"],
        "patterns": ["*.md", "*.json"],
        "authority": 1.0,
    },
    "docs": {
        "roots": ["docs", ".relay-kit/docs"],
        "patterns": ["*.md", "*.txt"],
        "authority": 0.7,
    },
    "evidence": {
        "roots": [".relay-kit/evidence"],
        "patterns": ["*.json", "*.jsonl", "*.md"],
        "authority": 0.6,
    },
    "registry": {
        "roots": ["relay_kit_v3/registry"],
        "patterns": ["*.py", "*.json"],
        "authority": 0.85,
    },
}


def build_query_search(
    root: Path | str,
    *,
    query: str,
    scopes: Iterable[str] | None = None,
    limit: int = 10,
    stale_days: int = 30,
) -> dict[str, Any]:
    project = Path(root).resolve()
    selected_scopes = tuple(scopes or DEFAULT_SCOPES)
    terms = _query_terms(query)
    results: list[dict[str, Any]] = []
    if not terms:
        return _empty_report(project, query, selected_scopes, "empty-query")

    for source_type in selected_scopes:
        config = SCOPE_CONFIG.get(source_type)
        if not config:
            continue
        for path in _iter_scope_files(project, config["roots"], config["patterns"]):
            results.extend(
                _search_file(
                    project,
                    path,
                    source_type=source_type,
                    authority=float(config["authority"]),
                    query=query,
                    terms=terms,
                    stale_days=stale_days,
                )
            )

    results.sort(key=lambda item: (-item["score"], -item["authority"], item["path"], item["line"]))
    limited = results[: max(limit, 0)]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass" if limited else "empty",
        "project_path": str(project),
        "query": query,
        "scopes": list(selected_scopes),
        "summary": {
            "hit_count": len(results),
            "returned": len(limited),
            "scope_count": len(selected_scopes),
        },
        "results": limited,
    }


def render_query_search(report: Mapping[str, Any]) -> str:
    lines = [
        "Relay-kit query search",
        f"- status: {report.get('status')}",
        f"- query: {report.get('query')}",
        f"- hits: {report.get('summary', {}).get('hit_count', 0)}",
    ]
    for result in report.get("results", [])[:10]:
        lines.append(
            f"  - {result.get('path')}:{result.get('line')} "
            f"[{result.get('source_type')} score={result.get('score')}] {result.get('text')}"
        )
    return "\n".join(lines)


def write_query_search(
    root: Path | str,
    report: Mapping[str, Any],
    output_file: Path | str | None = None,
) -> Path:
    project = Path(root).resolve()
    target = Path(output_file) if output_file else project / ".relay-kit" / "query" / "query-search.json"
    if not target.is_absolute():
        target = project / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return target


def _empty_report(project: Path, query: str, scopes: Iterable[str], reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "empty",
        "project_path": str(project),
        "query": query,
        "scopes": list(scopes),
        "summary": {"hit_count": 0, "returned": 0, "scope_count": len(tuple(scopes)), "reason": reason},
        "results": [],
    }


def _query_terms(query: str) -> list[str]:
    return [term.casefold() for term in re.findall(r"[A-Za-z0-9_.-]+", query) if len(term) >= 2]


def _iter_scope_files(project: Path, roots: Iterable[str], patterns: Iterable[str]) -> Iterable[Path]:
    for root_name in roots:
        root = project / root_name
        if not root.exists():
            continue
        for pattern in patterns:
            yield from (path for path in root.rglob(pattern) if path.is_file())


def _search_file(
    project: Path,
    path: Path,
    *,
    source_type: str,
    authority: float,
    query: str,
    terms: list[str],
    stale_days: int,
) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    freshness = _freshness(path, stale_days=stale_days)
    hits: list[dict[str, Any]] = []
    phrase = query.casefold().strip()
    for index, line in enumerate(lines, start=1):
        haystack = line.casefold()
        matched = [term for term in terms if term in haystack]
        if not matched:
            continue
        term_score = len(matched) * 10
        phrase_score = 15 if phrase and phrase in haystack else 0
        score = round(term_score + phrase_score + authority * 10, 3)
        hits.append(
            {
                "score": score,
                "authority": authority,
                "freshness": freshness["status"],
                "source_type": source_type,
                "path": _display_path(project, path),
                "line": index,
                "matched_terms": matched,
                "text": line.strip()[:240],
                "modified_at": freshness["modified_at"],
            }
        )
    return hits


def _freshness(path: Path, *, stale_days: int) -> dict[str, str]:
    try:
        modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    except OSError:
        return {"status": "unknown", "modified_at": ""}
    age_days = (datetime.now(timezone.utc) - modified).days
    return {
        "status": "stale" if age_days > stale_days else "recent",
        "modified_at": modified.isoformat(),
    }


def _display_path(project: Path, path: Path) -> str:
    try:
        return path.relative_to(project).as_posix()
    except ValueError:
        return path.as_posix()
