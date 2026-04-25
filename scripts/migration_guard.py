#!/usr/bin/env python3
"""Migration guard for Relay-kit Phase 3 cutover.

This gate blocks stale compatibility tokens outside explicit allowlist paths.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
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
    ".pytest_cache",
    ".tmp",
    "__pycache__",
    "build",
    "relay_kit.egg-info",
    ".relay-kit-cycle",
}

DEFAULT_EXCLUDED_FILES = {
    "scripts/migration_guard.py",
    "scripts/migration_guard_allowlist.txt",
}

ALLOWLIST_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class AllowRule:
    path_glob: str
    token: str
    owner: str = ""
    date: str = ""
    reason: str = ""


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    token: str
    text: str
    check: str = "blocked-token"


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


def _parse_allow_rule(line: str) -> AllowRule:
    parts = [part.strip() for part in line.split("|", 4)]
    if len(parts) == 5:
        return AllowRule(
            path_glob=parts[0],
            token=parts[1],
            owner=parts[2],
            date=parts[3],
            reason=parts[4],
        )
    if len(parts) == 2:
        return AllowRule(path_glob=parts[0], token=parts[1])
    return AllowRule(path_glob=parts[0] if parts else "", token="*")


def allow_rule_policy_issues(rule: AllowRule) -> List[str]:
    issues: List[str] = []
    if not rule.path_glob:
        issues.append("missing path")
    if any(marker in rule.path_glob for marker in ("*", "?", "[")):
        issues.append("path must be an exact file path")
    if rule.token == "*" or not rule.token:
        issues.append("token must be explicit")
    if not rule.owner:
        issues.append("missing owner")
    if not rule.date or ALLOWLIST_DATE_PATTERN.match(rule.date) is None:
        issues.append("missing ISO date")
    if not rule.reason:
        issues.append("missing reason")
    return issues


def load_allow_rules(path: Path) -> List[AllowRule]:
    if not path.exists():
        return []
    rules: List[AllowRule] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        rule = _parse_allow_rule(line)
        if allow_rule_policy_issues(rule):
            continue
        rules.append(rule)
    return rules


def collect_allowlist_findings(base: Path, path: Path) -> List[Finding]:
    if not path.exists():
        return []
    findings: List[Finding] = []
    rel_path = path.relative_to(base).as_posix() if path.is_relative_to(base) else path.as_posix()
    for idx, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        rule = _parse_allow_rule(line)
        issues = allow_rule_policy_issues(rule)
        if not issues:
            continue
        findings.append(
            Finding(
                path=rel_path,
                line=idx,
                token="allowlist-policy",
                text=f"{'; '.join(issues)}: {line}",
                check="allowlist-policy",
            )
        )
    return findings


def is_excluded(path: Path) -> bool:
    return any(part in DEFAULT_EXCLUDED_SEGMENTS for part in path.parts)


def candidate_files(base: Path) -> Iterable[Path]:
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        rel_path_obj = path.relative_to(base)
        if is_excluded(rel_path_obj):
            continue
        rel_path = rel_path_obj.as_posix()
        if rel_path in DEFAULT_EXCLUDED_FILES:
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
                "check": item.check,
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

    allowlist_findings = collect_allowlist_findings(base, allowlist_path)
    rules = load_allow_rules(allowlist_path)
    findings = allowlist_findings + collect_findings(base, DEFAULT_TOKENS, rules)

    if args.json:
        print(render_json(findings))
    else:
        print(render_text(findings))

    if args.strict and findings:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
