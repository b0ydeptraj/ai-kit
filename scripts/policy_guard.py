#!/usr/bin/env python3
"""Deterministic policy guard for high-risk Relay-kit runtime surfaces."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


DEFAULT_FILE_SUFFIXES = {
    ".md",
    ".txt",
    ".py",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".ps1",
    ".sh",
}

DEFAULT_EXCLUDED_SEGMENTS = {
    ".git",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "relay_kit.egg-info",
    ".relay-kit-cycle",
    "tests",
}

SECRET_PATTERNS: Sequence[tuple[str, re.Pattern[str]]] = (
    ("secret-token", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("secret-token", re.compile(r"\bghp_[A-Za-z0-9]{20,}\b")),
    ("secret-token", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private-key", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----")),
)

PATH_TRAVERSAL_PATTERN = re.compile(r"(?:\.\./|\.\.\\){2,}")

DESTRUCTIVE_SHELL_PATTERNS: Sequence[re.Pattern[str]] = (
    re.compile(r"\brm\s+-[A-Za-z]*r[A-Za-z]*f[A-Za-z]*\s+/(?:\s|['\"]|$)"),
    re.compile(r"\bRemove-Item\b.*\b-Recurse\b.*\b-Force\b", re.IGNORECASE),
    re.compile(r"\bgit\s+reset\s+--hard\b"),
    re.compile(r"\bdel\s+/s\s+/q\b", re.IGNORECASE),
    re.compile(r"\brmdir\s+/s\s+/q\b", re.IGNORECASE),
)

PROMPT_INJECTION_PATTERNS: Sequence[re.Pattern[str]] = (
    re.compile(r"\bignore (?:all )?(?:previous|prior) instructions\b", re.IGNORECASE),
    re.compile(r"\bdisregard (?:all )?(?:previous|prior) instructions\b", re.IGNORECASE),
    re.compile(r"\breveal (?:the )?(?:system prompt|developer message|hidden instructions|secrets)\b", re.IGNORECASE),
)

BROAD_ALLOWLIST_GLOBS = {"*", "**", "**/*", "*/*", "*/**"}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    check: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect high-risk runtime policy violations.")
    parser.add_argument("project_path", nargs="?", default=".", help="Target project root")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when findings exist")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    return parser.parse_args()


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


def is_skill_or_rule_file(rel_path: str) -> bool:
    normalized = rel_path.replace("\\", "/")
    return (
        normalized.endswith("/SKILL.md")
        or normalized.startswith(".codex/")
        or normalized.startswith(".claude/")
        or normalized.startswith(".agent/")
        or normalized.startswith("templates/skills/")
    )


def collect_line_findings(rel_path: str, line_no: int, line: str) -> list[Finding]:
    findings: list[Finding] = []

    for check, pattern in SECRET_PATTERNS:
        if pattern.search(line):
            findings.append(Finding(rel_path, line_no, check, "Potential hard-coded secret or private key marker"))

    if Path(rel_path).suffix.lower() in {".py", ".toml", ".yaml", ".yml", ".json", ".ps1", ".sh"} and PATH_TRAVERSAL_PATTERN.search(line):
        findings.append(Finding(rel_path, line_no, "path-traversal", "Potential path traversal sequence"))

    for pattern in DESTRUCTIVE_SHELL_PATTERNS:
        if pattern.search(line):
            findings.append(Finding(rel_path, line_no, "destructive-shell", "Potential broad destructive shell operation"))
            break

    if is_skill_or_rule_file(rel_path):
        for pattern in PROMPT_INJECTION_PATTERNS:
            if pattern.search(line):
                findings.append(
                    Finding(rel_path, line_no, "prompt-injection-phrase", "Prompt-injection phrase in skill/rule surface")
                )
                break

    return findings


def collect_allowlist_findings(path: Path, base: Path) -> list[Finding]:
    rel_path = path.relative_to(base).as_posix()
    if rel_path != "scripts/migration_guard_allowlist.txt":
        return []

    findings: list[Finding] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#") or "|" not in line:
            continue
        path_glob, token = [part.strip() for part in line.split("|", 1)]
        if path_glob in BROAD_ALLOWLIST_GLOBS and token == "*":
            findings.append(
                Finding(rel_path, line_no, "broad-migration-allowlist", "Broad path glob with wildcard token")
            )
    return findings


def collect_findings(base: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in candidate_files(base):
        rel_path = path.relative_to(base).as_posix()
        findings.extend(collect_allowlist_findings(path, base))
        for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            findings.extend(collect_line_findings(rel_path, line_no, line))
    return findings


def render_text(findings: Sequence[Finding]) -> str:
    lines = [
        "Policy guard report",
        f"- findings: {len(findings)}",
    ]
    if findings:
        lines.append("")
        lines.append("Top findings:")
        for item in findings[:50]:
            lines.append(f"- {item.path}:{item.line} [{item.check}] {item.detail}")
        if len(findings) > 50:
            lines.append(f"- ... and {len(findings) - 50} more")
    return "\n".join(lines)


def render_json(findings: Sequence[Finding]) -> str:
    payload = {
        "findings_count": len(findings),
        "findings": [
            {"path": item.path, "line": item.line, "check": item.check, "detail": item.detail}
            for item in findings
        ],
    }
    return json.dumps(payload, ensure_ascii=True, indent=2)


def main() -> int:
    args = parse_args()
    findings = collect_findings(Path(args.project_path).resolve())

    if args.json:
        print(render_json(findings))
    else:
        print(render_text(findings))

    if args.strict and findings:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
