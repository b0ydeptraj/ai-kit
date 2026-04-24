#!/usr/bin/env python3
"""Migration guard for Relay-kit Phase 3 cutover.

This gate blocks stale compatibility tokens outside explicit allowlist paths.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

DEFAULT_TOKENS: Sequence[str] = (
    "ai_kit_v3",
    ".ai-kit",
    ".python-kit-prompts",
    "python_kit.py",
    "python_kit_legacy.py",
)

DEFAULT_FILE_SUFFIXES = {
    ".md",
    ".txt",
    ".py",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
}

DEFAULT_EXCLUDED_SEGMENTS = {
    ".git",
    "__pycache__",
    "build",
    "relay_kit.egg-info",
    ".relay-kit-cycle",
}


@dataclass(frozen=True)
class AllowRule:
    path_glob: str
    token: str


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    token: str
    text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect cutover drift by blocking stale compatibility tokens outside allowlist paths.",
    )
    parser.add_argument("project_path", nargs="?", default=".", help="Target project root")
    parser.add_argument(
        "--allowlist",
        default="scripts/migration_guard_allowlist.txt",
        help="Allowlist file (default: scripts/migration_guard_allowlist.txt)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when findings exist",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON report",
    )
    return parser.parse_args()


def load_allow_rules(path: Path) -> List[AllowRule]:
    if not path.exists():
        return []
    rules: List[AllowRule] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "|" in line:
            path_glob, token = line.split("|", 1)
            rules.append(AllowRule(path_glob.strip(), token.strip() or "*"))
        else:
            rules.append(AllowRule(line, "*"))
    return rules


def is_excluded(path: Path) -> bool:
    return any(part in DEFAULT_EXCLUDED_SEGMENTS for part in path.parts)


def candidate_files(base: Path) -> Iterable[Path]:
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        if is_excluded(path):
            continue
        if path.suffix.lower() not in DEFAULT_FILE_SUFFIXES:
            continue
        yield path


def allowed(rel_path: str, token: str, rules: Sequence[AllowRule]) -> bool:
    for rule in rules:
        if fnmatch.fnmatch(rel_path, rule.path_glob):
            if rule.token in {"*", token}:
                return True
    return False


def collect_findings(base: Path, tokens: Sequence[str], rules: Sequence[AllowRule]) -> List[Finding]:
    findings: List[Finding] = []
    for path in candidate_files(base):
        rel_path = path.relative_to(base).as_posix()
        content = path.read_text(encoding="utf-8", errors="ignore")
        lines = content.splitlines()
        for idx, line in enumerate(lines, start=1):
            for token in tokens:
                if token not in line:
                    continue
                if allowed(rel_path, token, rules):
                    continue
                findings.append(
                    Finding(
                        path=rel_path,
                        line=idx,
                        token=token,
                        text=line.strip(),
                    )
                )
    return findings


def render_text(findings: Sequence[Finding]) -> str:
    lines = [
        "Migration guard report",
        f"- findings: {len(findings)}",
    ]
    if findings:
        lines.append("")
        lines.append("Top findings:")
        for item in findings[:50]:
            lines.append(f"- {item.path}:{item.line} [{item.token}] {item.text}")
        if len(findings) > 50:
            lines.append(f"- ... and {len(findings) - 50} more")
    return "\n".join(lines)


def render_json(findings: Sequence[Finding]) -> str:
    payload = {
        "findings_count": len(findings),
        "findings": [
            {
                "path": item.path,
                "line": item.line,
                "token": item.token,
                "text": item.text,
            }
            for item in findings
        ],
    }
    return json.dumps(payload, ensure_ascii=True, indent=2)


def main() -> int:
    args = parse_args()
    base = Path(args.project_path).resolve()
    allowlist_path = Path(args.allowlist)
    if not allowlist_path.is_absolute():
        allowlist_path = base / allowlist_path

    rules = load_allow_rules(allowlist_path)
    findings = collect_findings(base, DEFAULT_TOKENS, rules)

    if args.json:
        print(render_json(findings))
    else:
        print(render_text(findings))

    if args.strict and findings:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
