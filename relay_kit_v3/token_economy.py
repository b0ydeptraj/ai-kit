from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from relay_kit_v3.query_search import DEFAULT_SCOPES, SCOPE_CONFIG, build_query_search


CONTEXT_BUDGET_SCHEMA_VERSION = "relay-kit.context-budget.v1"
CONTEXT_PACK_SCHEMA_VERSION = "relay-kit.context-pack.v1"
TOKEN_AUDIT_SCHEMA_VERSION = "relay-kit.token-audit.v1"

DEFAULT_MAX_TOKENS = 8000
DEFAULT_STALE_DAYS = 30
DEFAULT_QUERY_LIMIT = 160
MAX_FILE_BYTES = 256 * 1024

CRITICAL_MARKERS = ("fail", "error", "traceback", "exception", "assert", "exit code")
STRICT_FAILURE_MARKERS = (
    "traceback (most recent call last)",
    "assertionerror",
    "runtimeerror",
    "valueerror",
    "typeerror",
)
EXIT_CODE_PATTERN = re.compile(r"\bexit\s+code\s+[1-9]\d*\b", re.IGNORECASE)
PATH_SIGNAL_PATTERN = re.compile(r"[A-Za-z0-9_./\\-]+\.[A-Za-z0-9_]{1,8}")
LINE_SIGNAL_PATTERN = re.compile(r"line\s+\d+", re.IGNORECASE)
COMMAND_SIGNAL_PATTERN = re.compile(r"`([^`\n]{3,})`")


def estimate_tokens(text: str) -> int:
    return int(math.ceil(len(text) / 4)) if text else 0


def build_context_budget(
    project_root: Path | str,
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    query: str | None = None,
    scopes: Iterable[str] | None = None,
    stale_days: int = DEFAULT_STALE_DAYS,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    selected_scopes = _normalize_scopes(scopes)
    sources = _collect_sources(
        root,
        scopes=selected_scopes,
        query=query,
        stale_days=stale_days,
    )
    analyzed = _analyze_sources(sources)
    selected, dropped, selected_tokens = _select_with_budget(analyzed, max_tokens=max_tokens)
    metrics = _metrics(analyzed, selected_tokens=selected_tokens, max_tokens=max_tokens)
    findings = _budget_findings(selected, dropped, metrics=metrics, max_tokens=max_tokens)
    status = _report_status(findings)
    return {
        "schema_version": CONTEXT_BUDGET_SCHEMA_VERSION,
        "status": status,
        "project_path": str(root),
        "query": query or "",
        "scopes": list(selected_scopes),
        "max_tokens": max_tokens,
        "summary": {
            "source_count": len(analyzed),
            "selected_source_count": len(selected),
            "dropped_source_count": len(dropped),
            "selected_tokens": selected_tokens,
            **metrics,
            "findings": len(findings),
        },
        "selected_sources": selected,
        "dropped_sources": dropped,
        "findings": findings,
    }


def build_context_pack(
    project_root: Path | str,
    *,
    task: str,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    scopes: Iterable[str] | None = None,
    stale_days: int = DEFAULT_STALE_DAYS,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    selected_scopes = _normalize_scopes(scopes)
    task_query = task.strip()
    sources = _collect_sources(
        root,
        scopes=selected_scopes,
        query=task_query,
        stale_days=stale_days,
    )
    analyzed = _analyze_sources(sources)
    selected, dropped, selected_tokens = _select_with_budget(analyzed, max_tokens=max_tokens)
    metrics = _metrics(analyzed, selected_tokens=selected_tokens, max_tokens=max_tokens)
    findings = _budget_findings(selected, dropped, metrics=metrics, max_tokens=max_tokens)
    status = _report_status(findings)
    return {
        "schema_version": CONTEXT_PACK_SCHEMA_VERSION,
        "status": status,
        "project_path": str(root),
        "task": task_query,
        "scopes": list(selected_scopes),
        "max_tokens": max_tokens,
        "summary": {
            "source_count": len(analyzed),
            "selected_source_count": len(selected),
            "dropped_source_count": len(dropped),
            "selected_tokens": selected_tokens,
            **metrics,
            "findings": len(findings),
        },
        "selected_sources": selected,
        "dropped_sources": dropped,
        "findings": findings,
    }


def build_token_audit(
    project_root: Path | str,
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    scopes: Iterable[str] | None = None,
    stale_days: int = DEFAULT_STALE_DAYS,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    selected_scopes = _normalize_scopes(scopes)
    sources = _collect_sources(
        root,
        scopes=selected_scopes,
        query=None,
        stale_days=stale_days,
    )
    analyzed = _analyze_sources(sources)
    selected, dropped, selected_tokens = _select_with_budget(analyzed, max_tokens=max_tokens)
    metrics = _metrics(analyzed, selected_tokens=selected_tokens, max_tokens=max_tokens)
    findings = _budget_findings(selected, dropped, metrics=metrics, max_tokens=max_tokens)
    status = _report_status(findings)
    return {
        "schema_version": TOKEN_AUDIT_SCHEMA_VERSION,
        "status": status,
        "project_path": str(root),
        "scopes": list(selected_scopes),
        "max_tokens": max_tokens,
        "metrics": metrics,
        "summary": {
            "source_count": len(analyzed),
            "selected_source_count": len(selected),
            "dropped_source_count": len(dropped),
            "selected_tokens": selected_tokens,
            "findings": len(findings),
        },
        "selected_sources": selected,
        "dropped_sources": dropped,
        "findings": findings,
    }


def render_context_budget(report: Mapping[str, Any]) -> str:
    summary = _mapping(report.get("summary"))
    lines = [
        "Relay-kit context budget",
        f"- status: {report.get('status')}",
        f"- sources: {summary.get('source_count', 0)}",
        f"- selected tokens: {summary.get('selected_tokens', 0)}",
        f"- max tokens: {report.get('max_tokens', 0)}",
        f"- budget violations: {summary.get('budget_violations', 0)}",
        f"- signal retention: {summary.get('signal_retention', 1.0)}",
    ]
    for finding in _list(report.get("findings"))[:10]:
        if isinstance(finding, Mapping):
            lines.append(f"  - {finding.get('summary', finding.get('id', 'finding'))}")
    return "\n".join(lines)


def render_context_pack(report: Mapping[str, Any]) -> str:
    summary = _mapping(report.get("summary"))
    lines = [
        "Relay-kit context pack",
        f"- status: {report.get('status')}",
        f"- task: {report.get('task', '')}",
        f"- selected sources: {summary.get('selected_source_count', 0)}",
        f"- selected tokens: {summary.get('selected_tokens', 0)}",
        f"- max tokens: {report.get('max_tokens', 0)}",
        f"- budget violations: {summary.get('budget_violations', 0)}",
    ]
    for source in _list(report.get("selected_sources"))[:8]:
        if isinstance(source, Mapping):
            lines.append(
                "  - "
                f"{source.get('path', '-')}"
                f" [{source.get('classification', '-')}]"
                f" tokens={source.get('packed_tokens', 0)}"
            )
    return "\n".join(lines)


def render_token_audit(report: Mapping[str, Any]) -> str:
    metrics = _mapping(report.get("metrics"))
    lines = [
        "Relay-kit token audit",
        f"- status: {report.get('status')}",
        f"- estimated tokens: {metrics.get('estimated_tokens', 0)}",
        f"- compressed tokens: {metrics.get('compressed_tokens', 0)}",
        f"- signal retention: {metrics.get('signal_retention', 1.0)}",
        f"- raw-required blocks: {metrics.get('raw_required_blocks', 0)}",
        f"- budget violations: {metrics.get('budget_violations', 0)}",
    ]
    for finding in _list(report.get("findings"))[:10]:
        if isinstance(finding, Mapping):
            lines.append(f"  - {finding.get('summary', finding.get('id', 'finding'))}")
    return "\n".join(lines)


def write_context_budget(
    root: Path | str,
    report: Mapping[str, Any],
    *,
    output_file: Path | str | None = None,
) -> Path:
    return _write_json(root, report, output_file=output_file, default_path=Path(".relay-kit/context/context-budget.json"))


def write_context_pack(
    root: Path | str,
    report: Mapping[str, Any],
    *,
    output_file: Path | str | None = None,
) -> Path:
    return _write_json(root, report, output_file=output_file, default_path=Path(".relay-kit/context/context-pack.json"))


def write_token_audit(
    root: Path | str,
    report: Mapping[str, Any],
    *,
    output_file: Path | str | None = None,
) -> Path:
    return _write_json(root, report, output_file=output_file, default_path=Path(".relay-kit/token/token-audit.json"))


def _write_json(
    root: Path | str,
    report: Mapping[str, Any],
    *,
    output_file: Path | str | None,
    default_path: Path,
) -> Path:
    project = Path(root).resolve()
    target = Path(output_file) if output_file else project / default_path
    if not target.is_absolute():
        target = project / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return target


def _collect_sources(
    root: Path,
    *,
    scopes: tuple[str, ...],
    query: str | None,
    stale_days: int,
) -> list[dict[str, Any]]:
    if query:
        return _collect_query_sources(root, query=query, scopes=scopes, stale_days=stale_days)
    return _collect_scope_sources(root, scopes=scopes, stale_days=stale_days)


def _collect_query_sources(
    root: Path,
    *,
    query: str,
    scopes: tuple[str, ...],
    stale_days: int,
) -> list[dict[str, Any]]:
    report = build_query_search(
        root,
        query=query,
        scopes=scopes,
        limit=DEFAULT_QUERY_LIMIT,
        stale_days=stale_days,
    )
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for result in _list(report.get("results")):
        if not isinstance(result, Mapping):
            continue
        path = str(result.get("path", "")).strip()
        line = int(result.get("line", 0) or 0)
        text = str(result.get("text", "")).strip()
        if not path:
            continue
        record_id = f"{path}:{line}"
        if record_id in seen:
            continue
        seen.add(record_id)
        records.append(
            {
                "id": record_id,
                "path": path,
                "source_type": str(result.get("source_type", "query")),
                "authority": float(result.get("authority", 0.0) or 0.0),
                "freshness": str(result.get("freshness", "unknown")),
                "raw_text": text,
            }
        )
    return records


def _collect_scope_sources(
    root: Path,
    *,
    scopes: tuple[str, ...],
    stale_days: int,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for source_type in scopes:
        config = SCOPE_CONFIG.get(source_type)
        if not config:
            continue
        authority = float(config.get("authority", 0.0) or 0.0)
        roots = config.get("roots", [])
        patterns = config.get("patterns", [])
        for file_path in _iter_scope_files(root, roots, patterns):
            raw_text = _read_file(file_path)
            rel_path = _display_path(root, file_path)
            freshness = _freshness(file_path, stale_days=stale_days)
            records.append(
                {
                    "id": rel_path,
                    "path": rel_path,
                    "source_type": source_type,
                    "authority": authority,
                    "freshness": freshness,
                    "raw_text": raw_text,
                }
            )
    records.sort(key=lambda item: str(item.get("id", "")))
    return records[:DEFAULT_QUERY_LIMIT]


def _iter_scope_files(root: Path, roots: Iterable[str], patterns: Iterable[str]) -> Iterable[Path]:
    for relative_root in roots:
        scope_root = root / relative_root
        if not scope_root.exists():
            continue
        for pattern in patterns:
            for path in scope_root.rglob(pattern):
                if path.is_file():
                    yield path


def _read_file(path: Path) -> str:
    try:
        raw = path.read_bytes()
    except OSError:
        return ""
    payload = raw[:MAX_FILE_BYTES]
    return payload.decode("utf-8", errors="replace")


def _freshness(path: Path, *, stale_days: int) -> str:
    try:
        modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    except OSError:
        return "unknown"
    age = (datetime.now(timezone.utc) - modified).days
    return "stale" if age > max(stale_days, 0) else "recent"


def _analyze_sources(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    analyzed: list[dict[str, Any]] = []
    seen_fingerprints: set[str] = set()
    for source in sources:
        path = str(source.get("path", ""))
        raw_text = str(source.get("raw_text", ""))
        lowered = raw_text.lower()
        fingerprint = lowered[:512]
        critical = _is_raw_required_text(lowered)
        signals = _extract_signals(raw_text)
        raw_signal_count = len(signals)
        duplicate = bool(fingerprint and fingerprint in seen_fingerprints)
        if fingerprint:
            seen_fingerprints.add(fingerprint)

        classification = "raw-required"
        if critical:
            classification = "raw-required"
        elif raw_signal_count == 0 and duplicate:
            classification = "summary-only"
        elif raw_signal_count == 0 and estimate_tokens(raw_text) <= 40:
            classification = "summary-only"
        else:
            classification = "compressible"

        packed_text = raw_text
        if classification == "summary-only":
            packed_text = f"{path} ({source.get('source_type', 'unknown')}, {len(raw_text.splitlines())} lines)"
        elif classification == "compressible":
            packed_text = _compress_text(raw_text)
            if not packed_text:
                classification = "raw-required"
                packed_text = raw_text

        packed_signals = _extract_signals(packed_text)
        required_signals = _required_signals(signals, classification=classification)
        signal_count = len(required_signals)
        retained_signal_count = signal_count if classification == "raw-required" else len(required_signals & packed_signals)
        signal_retention = (
            round(retained_signal_count / signal_count, 4)
            if signal_count > 0
            else 1.0
        )
        analyzed.append(
            {
                "id": source.get("id", path),
                "path": path,
                "source_type": str(source.get("source_type", "unknown")),
                "authority": float(source.get("authority", 0.0) or 0.0),
                "freshness": str(source.get("freshness", "unknown")),
                "classification": classification,
                "raw_path": path if classification == "raw-required" else "",
                "raw_tokens": estimate_tokens(raw_text),
                "packed_tokens": estimate_tokens(packed_text),
                "signal_count": signal_count,
                "retained_signal_count": retained_signal_count,
                "signal_retention": signal_retention,
                "snippet": packed_text[:320],
                "packed_text": packed_text,
                "raw_text": raw_text,
            }
        )
    return analyzed


def _select_with_budget(
    analyzed: list[dict[str, Any]],
    *,
    max_tokens: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    ordered = sorted(
        analyzed,
        key=lambda item: (
            0 if item.get("classification") == "raw-required" else 1,
            -float(item.get("authority", 0.0) or 0.0),
            0 if item.get("freshness") == "recent" else 1,
            -int(item.get("packed_tokens", 0) or 0),
            str(item.get("path", "")),
        ),
    )
    selected: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    selected_tokens = 0

    for item in ordered:
        tokens = int(item.get("packed_tokens", 0) or 0)
        must_keep = item.get("classification") == "raw-required"
        candidate = _public_source_record(item)
        if must_keep:
            selected_tokens += tokens
            candidate["budget_decision"] = "forced-keep"
            selected.append(candidate)
            continue
        if selected_tokens + tokens <= max_tokens:
            selected_tokens += tokens
            candidate["budget_decision"] = "keep"
            selected.append(candidate)
            continue
        candidate["budget_decision"] = "drop"
        dropped.append(candidate)
    return selected, dropped, selected_tokens


def _public_source_record(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": str(item.get("id", "")),
        "path": str(item.get("path", "")),
        "source_type": str(item.get("source_type", "unknown")),
        "authority": float(item.get("authority", 0.0) or 0.0),
        "freshness": str(item.get("freshness", "unknown")),
        "classification": str(item.get("classification", "raw-required")),
        "raw_path": str(item.get("raw_path", "")),
        "raw_tokens": int(item.get("raw_tokens", 0) or 0),
        "packed_tokens": int(item.get("packed_tokens", 0) or 0),
        "signal_count": int(item.get("signal_count", 0) or 0),
        "retained_signal_count": int(item.get("retained_signal_count", 0) or 0),
        "signal_retention": float(item.get("signal_retention", 1.0) or 1.0),
        "snippet": str(item.get("snippet", "")),
    }


def _metrics(
    analyzed: list[dict[str, Any]],
    *,
    selected_tokens: int,
    max_tokens: int,
) -> dict[str, Any]:
    estimated_tokens = sum(int(item.get("raw_tokens", 0) or 0) for item in analyzed)
    compressed_tokens = sum(int(item.get("packed_tokens", 0) or 0) for item in analyzed)
    total_signals = sum(int(item.get("signal_count", 0) or 0) for item in analyzed)
    retained_signals = sum(int(item.get("retained_signal_count", 0) or 0) for item in analyzed)
    signal_retention = round(retained_signals / total_signals, 4) if total_signals else 1.0
    return {
        "estimated_tokens": estimated_tokens,
        "compressed_tokens": compressed_tokens,
        "signal_retention": signal_retention,
        "raw_required_blocks": sum(1 for item in analyzed if item.get("classification") == "raw-required"),
        "budget_violations": 1 if selected_tokens > max_tokens or signal_retention < 1.0 else 0,
    }


def _budget_findings(
    selected: list[dict[str, Any]],
    dropped: list[dict[str, Any]],
    *,
    metrics: Mapping[str, Any],
    max_tokens: int,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    selected_tokens = sum(int(item.get("packed_tokens", 0) or 0) for item in selected)
    if selected_tokens > max_tokens:
        findings.append(
            {
                "id": "token-budget-exceeded",
                "status": "hold",
                "summary": f"selected context tokens {selected_tokens} exceed max_tokens {max_tokens}",
            }
        )
    if float(metrics.get("signal_retention", 1.0) or 1.0) < 1.0:
        findings.append(
            {
                "id": "signal-retention-loss",
                "status": "hold",
                "summary": (
                    "token compression dropped required signal; fail-open requires raw-required classification"
                ),
            }
        )
    for item in dropped[:12]:
        findings.append(
            {
                "id": "over-budget-source",
                "status": "attention",
                "path": item.get("path", ""),
                "summary": (
                    f"source dropped to satisfy budget: {item.get('path', '')} "
                    f"({item.get('packed_tokens', 0)} tokens)"
                ),
            }
        )
    return findings


def _compress_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ""
    selected: list[str] = [lines[0]]
    for line in lines[1:]:
        lowered = line.lower()
        if (
            any(marker in lowered for marker in CRITICAL_MARKERS)
            or "line " in lowered
            or ".py" in line
            or ".md" in line
            or "/" in line
            or "\\" in line
        ):
            selected.append(line)
        if len(selected) >= 8:
            break
    if len(selected) < 3:
        for line in lines[1:]:
            if line not in selected:
                selected.append(line)
            if len(selected) >= 3:
                break
    return "\n".join(selected)[:1200]


def _extract_signals(text: str) -> set[str]:
    lowered = text.lower()
    signals: set[str] = set()
    for marker in CRITICAL_MARKERS:
        if marker in lowered:
            signals.add(f"kw:{marker}")
    for match in PATH_SIGNAL_PATTERN.findall(text):
        signals.add(f"path:{match.lower()}")
    for match in LINE_SIGNAL_PATTERN.findall(text):
        signals.add(f"line:{match.lower()}")
    for match in COMMAND_SIGNAL_PATTERN.findall(text):
        signals.add(f"cmd:{match.strip().lower()}")
    return signals


def _required_signals(signals: set[str], *, classification: str) -> set[str]:
    if classification == "raw-required":
        return set(signals)
    return set()


def _is_raw_required_text(lowered_text: str) -> bool:
    if any(marker in lowered_text for marker in STRICT_FAILURE_MARKERS):
        return True
    if "error collecting" in lowered_text or "\ne   " in lowered_text:
        return True
    if EXIT_CODE_PATTERN.search(lowered_text) and any(
        hint in lowered_text for hint in ("command failed", "pytest", "stderr:", "stdout:", "returncode")
    ):
        return True
    if ("stderr:" in lowered_text or "stdout:" in lowered_text) and any(token in lowered_text for token in ("error", "failed", "failure")):
        return True
    return False


def _report_status(findings: list[dict[str, Any]]) -> str:
    return "hold" if any(str(item.get("status", "")).lower() == "hold" for item in findings) else "pass"


def _normalize_scopes(scopes: Iterable[str] | None) -> tuple[str, ...]:
    if scopes is None:
        return tuple(DEFAULT_SCOPES)
    normalized: list[str] = []
    for scope in scopes:
        key = str(scope).strip()
        if key in SCOPE_CONFIG and key not in normalized:
            normalized.append(key)
    return tuple(normalized or DEFAULT_SCOPES)


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
