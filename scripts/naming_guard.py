#!/usr/bin/env python3
"""Relay-kit naming guard.

Fail-closed guard that blocks retired compatibility labels and tokens.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


_ROUND = "round"
_OLD_RUNTIME_LABELS = (
    "ai_" + "kit_v3",
    ".ai" + "-kit",
    ".python" + "-kit-prompts",
    "python" + "_kit.py",
    "python" + "_kit_legacy.py",
)
_OLD_BUNDLE_LABELS = (
    f"{_ROUND}2",
    f"{_ROUND}3",
    f"{_ROUND}4",
    "baseline" + "-" + "next",
    "bmad" + "-" + "core",
    "bmad" + "-" + "lite",
    "legacy" + "-" + "native",
)
DEFAULT_TOKENS: Sequence[str] = _OLD_RUNTIME_LABELS + _OLD_BUNDLE_LABELS

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

DEFAULT_EXCLUDED_PREFIXES = (
    ".relay-kit/context/",
    ".relay-kit/token/",
    ".relay-kit/pulse/",
    ".relay-kit/signals/",
    "templates/skills/docx/ooxml/schemas/",
    "templates/skills/pptx/ooxml/schemas/",
)

DEFAULT_EXCLUDED_FILES = {
    "scripts/naming_guard.py",
}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    token: str
    text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect retired naming tokens in Relay-kit sources.",
    )
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
        rel_obj = path.relative_to(base)
        if is_excluded(rel_obj):
            continue
        rel_path = rel_obj.as_posix()
        if rel_path in DEFAULT_EXCLUDED_FILES:
            continue
        if rel_path.startswith(DEFAULT_EXCLUDED_PREFIXES):
            continue
        if path.suffix.lower() not in DEFAULT_FILE_SUFFIXES:
            continue
        yield path


def _token_pattern(token: str) -> re.Pattern[str]:
    return re.compile(rf"(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])")


def collect_findings(base: Path, tokens: Sequence[str]) -> list[Finding]:
    findings: list[Finding] = []
    compiled = {token: _token_pattern(token) for token in tokens}
    for path in candidate_files(base):
        rel_path = path.relative_to(base).as_posix()
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        for idx, line in enumerate(lines, start=1):
            for token, pattern in compiled.items():
                if pattern.search(line):
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
    lines = ["Naming guard report", f"- findings: {len(findings)}"]
    if findings:
        lines.extend(["", "Top findings:"])
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
    findings = collect_findings(base, DEFAULT_TOKENS)
    if args.json:
        print(render_json(findings))
    else:
        print(render_text(findings))
    if args.strict and findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
