#!/usr/bin/env python3
"""Read-only search utility for Relay-kit state and contract artifacts."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class Match:
    path: str
    line: int
    text: str
    before: List[str]
    after: List[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search .ai-kit artifacts for previous decisions, handoffs, and debug context.",
    )
    parser.add_argument("project_path", nargs="?", default=".", help="Target project root")
    parser.add_argument("--query", required=True, help="Case-insensitive query string")
    parser.add_argument(
        "--scope",
        choices=["state", "contracts", "all"],
        default="all",
        help="Artifact scope to search",
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


def candidate_files(base: Path, scope: str) -> Iterable[Path]:
    ai_root = base / ".ai-kit"
    groups = []
    if scope in {"state", "all"}:
        groups.append(ai_root / "state")
    if scope in {"contracts", "all"}:
        groups.append(ai_root / "contracts")
    for folder in groups:
        if not folder.exists():
            continue
        for path in sorted(folder.glob("**/*.md")):
            if path.is_file():
                yield path


def find_matches(paths: Iterable[Path], query: str, context: int, max_results: int, base: Path) -> List[Match]:
    needle = query.casefold()
    matches: List[Match] = []
    for path in paths:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for index, line in enumerate(lines):
            if needle not in line.casefold():
                continue
            start = max(0, index - context)
            end = min(len(lines), index + context + 1)
            matches.append(
                Match(
                    path=path.relative_to(base).as_posix(),
                    line=index + 1,
                    text=line.rstrip(),
                    before=[entry.rstrip() for entry in lines[start:index]],
                    after=[entry.rstrip() for entry in lines[index + 1 : end]],
                )
            )
            if len(matches) >= max_results:
                return matches
    return matches


def render_markdown(matches: List[Match], query: str) -> str:
    if not matches:
        return f"No matches found for query: {query!r}"
    lines: List[str] = [f"Found {len(matches)} match(es) for {query!r}:"]
    for match in matches:
        lines.append(f"- {match.path}:{match.line}")
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
            }
            for match in matches
        ],
    }
    return json.dumps(payload, ensure_ascii=True, indent=2)


def main() -> int:
    args = parse_args()
    base = Path(args.project_path).resolve()
    paths = list(candidate_files(base, args.scope))
    matches = find_matches(
        paths=paths,
        query=args.query,
        context=max(0, args.context),
        max_results=max(1, args.max_results),
        base=base,
    )
    if args.json:
        print(render_json(matches, args.query))
    else:
        print(render_markdown(matches, args.query))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
