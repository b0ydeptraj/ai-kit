#!/usr/bin/env python3
"""Read-only search utility for Relay-kit state and contract artifacts."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class Match:
    path: str
    line: int
    text: str
    before: List[str]
    after: List[str]
    section: str
    modified_utc: str
    stale: bool
    score: float


INTENT_HINTS = {
    "decision": {
        "path": ("workflow-state", "prd", "architecture", "decision", "tech-spec"),
        "line": ("decision", "decided", "agreed", "locked", "rationale"),
    },
    "handoff": {
        "path": ("handoff", "handoff-log", "team-board", "workflow-state"),
        "line": ("handoff", "owner", "receiver", "next step", "blocked"),
    },
    "debug": {
        "path": ("investigation", "qa-report", "debug", "incident"),
        "line": ("root cause", "repro", "error", "failure", "regression", "fix"),
    },
    "review": {
        "path": ("review", "qa-report", "checklist", "ready"),
        "line": ("risk", "regression", "verify", "evidence", "hold", "pass"),
    },
    "migration": {
        "path": ("migration", "compat", "timeline", "changelog"),
        "line": ("compatibility", "rename", "alias", "cycle", "phase"),
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search .relay-kit artifacts for previous decisions, handoffs, and debug context.",
    )
    parser.add_argument("project_path", nargs="?", default=".", help="Target project root")
    parser.add_argument("--query", required=True, help="Case-insensitive query string")
    parser.add_argument(
        "--scope",
        choices=["state", "contracts", "references", "all"],
        default="all",
        help="Artifact scope to search",
    )
    parser.add_argument(
        "--intent",
        choices=["any", "decision", "handoff", "debug", "review", "migration"],
        default="any",
        help="Optional intent hint for relevance ranking (default: any)",
    )
    parser.add_argument(
        "--path-contains",
        action="append",
        default=[],
        help="Filter candidate files by path substring (repeatable)",
    )
    parser.add_argument(
        "--sort",
        choices=["relevance", "recent", "path"],
        default="relevance",
        help="Result ordering (default: relevance)",
    )
    parser.add_argument(
        "--stale-days",
        type=int,
        default=30,
        help="Mark results older than this many days as stale (default: 30)",
    )
    parser.add_argument(
        "--context",
        type=int,
        default=1,
        help="Context lines before and after each hit (default: 1)",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=30,
        help="Maximum number of results to return (default: 30)",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    return parser.parse_args()


def candidate_files(base: Path, scope: str, path_contains: List[str]) -> Iterable[Path]:
    ai_root = base / ".relay-kit"
    groups = []
    if scope in {"state", "all"}:
        groups.append(ai_root / "state")
    if scope in {"contracts", "all"}:
        groups.append(ai_root / "contracts")
    if scope in {"references", "all"}:
        groups.append(ai_root / "references")
    filters = [entry.casefold() for entry in path_contains if entry.strip()]
    for folder in groups:
        if not folder.exists():
            continue
        for path in sorted(folder.glob("**/*.md")):
            if not path.is_file():
                continue
            if filters:
                normalized = path.as_posix().casefold()
                if not any(token in normalized for token in filters):
                    continue
            yield path


def nearest_section(lines: List[str], index: int) -> str:
    for candidate in range(index, -1, -1):
        line = lines[candidate].strip()
        if line.startswith("#"):
            return line.lstrip("#").strip() or "(root)"
    return "(root)"


def compute_score(path: str, line: str, section: str, query_tokens: List[str], intent: str) -> float:
    line_cf = line.casefold()
    section_cf = section.casefold()
    path_cf = path.casefold()
    score = 0.0
    for token in query_tokens:
        score += line_cf.count(token) * 3.0
        score += section_cf.count(token) * 1.5
        score += path_cf.count(token) * 1.0
    if intent != "any":
        hints = INTENT_HINTS[intent]
        for token in hints["path"]:
            if token in path_cf:
                score += 1.0
        for token in hints["line"]:
            if token in line_cf:
                score += 1.0
    return score


def sort_matches(matches: List[Match], mode: str) -> List[Match]:
    if mode == "recent":
        return sorted(matches, key=lambda item: (item.modified_utc, item.path, item.line), reverse=True)
    if mode == "path":
        return sorted(matches, key=lambda item: (item.path, item.line))
    return sorted(matches, key=lambda item: (item.score, item.modified_utc, item.path, -item.line), reverse=True)


def find_matches(
    paths: Iterable[Path],
    query: str,
    context: int,
    max_results: int,
    base: Path,
    intent: str,
    sort_mode: str,
    stale_days: int,
) -> List[Match]:
    needle = query.casefold()
    query_tokens = [token for token in needle.split() if token]
    now = datetime.now(timezone.utc)
    matches: List[Match] = []
    for path in paths:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        age_days = (now - modified).days
        modified_utc = modified.replace(microsecond=0).isoformat().replace("+00:00", "Z")
        relative_path = path.relative_to(base).as_posix()
        for index, line in enumerate(lines):
            if needle not in line.casefold():
                continue
            start = max(0, index - context)
            end = min(len(lines), index + context + 1)
            section = nearest_section(lines, index)
            score = compute_score(relative_path, line, section, query_tokens, intent)
            matches.append(
                Match(
                    path=relative_path,
                    line=index + 1,
                    text=line.rstrip(),
                    before=[entry.rstrip() for entry in lines[start:index]],
                    after=[entry.rstrip() for entry in lines[index + 1 : end]],
                    section=section,
                    modified_utc=modified_utc,
                    stale=age_days > max(stale_days, 0),
                    score=score,
                )
            )
    ordered = sort_matches(matches, sort_mode)
    return ordered[:max_results]


def render_markdown(matches: List[Match], query: str) -> str:
    if not matches:
        return f"No matches found for query: {query!r}"
    lines: List[str] = [f"Found {len(matches)} match(es) for {query!r}:"]
    for match in matches:
        stale_label = "stale" if match.stale else "fresh"
        lines.append(
            f"- {match.path}:{match.line} [{stale_label}] "
            f"(section: {match.section}, updated: {match.modified_utc}, score: {match.score:.2f})"
        )
        if match.before:
            for before in match.before:
                lines.append(f"    {before}")
        lines.append(f"  > {match.text}")
        if match.after:
            for after in match.after:
                lines.append(f"    {after}")
    return "\n".join(lines)


def render_json(matches: List[Match], query: str) -> str:
    payload = {
        "query": query,
        "matches": [
            {
                "path": match.path,
                "line": match.line,
                "text": match.text,
                "before": match.before,
                "after": match.after,
                "section": match.section,
                "modified_utc": match.modified_utc,
                "stale": match.stale,
                "score": round(match.score, 3),
            }
            for match in matches
        ],
    }
    return json.dumps(payload, ensure_ascii=True, indent=2)


def main() -> int:
    args = parse_args()
    base = Path(args.project_path).resolve()
    paths = list(candidate_files(base, args.scope, args.path_contains))
    matches = find_matches(
        paths=paths,
        query=args.query,
        context=max(0, args.context),
        max_results=max(1, args.max_results),
        base=base,
        intent=args.intent,
        sort_mode=args.sort,
        stale_days=args.stale_days,
    )
    if args.json:
        print(render_json(matches, args.query))
    else:
        print(render_markdown(matches, args.query))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

