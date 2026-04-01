#!/usr/bin/env python3
"""Behavior regression checks for Relay-kit runtime skills."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ai_kit_v3.registry.skills import ALL_V3_SKILLS


RUNTIME_ROOTS = [".claude/skills", ".agent/skills", ".codex/skills"]
REQUIRED_HEADERS = [
    "# Mission",
    "## Role",
    "## Layer",
    "## Inputs",
    "## Outputs",
    "## Reference skills and rules",
    "## Likely next step",
]


@dataclass(frozen=True)
class Finding:
    path: str
    check: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run SKILL.md behavior regression checks across runtime surfaces.",
    )
    parser.add_argument("project_path", nargs="?", default=".", help="Target project root")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero exit code when any finding is detected",
    )
    return parser.parse_args()


def check_skill_file(path: Path, base: Path) -> List[Finding]:
    findings: List[Finding] = []
    content = path.read_text(encoding="utf-8")
    rel_path = path.relative_to(base).as_posix()
    frontmatter = parse_frontmatter(content)
    if frontmatter is None:
        findings.append(Finding(rel_path, "frontmatter", "Missing or malformed frontmatter"))
        return findings

    name = frontmatter.get("name", "").strip()
    description = frontmatter.get("description", "").strip()
    if not name:
        findings.append(Finding(rel_path, "frontmatter-name", "Missing name in frontmatter"))
    if not description:
        findings.append(Finding(rel_path, "frontmatter-description", "Missing description in frontmatter"))
    expected_name = path.parent.name
    if name != expected_name:
        findings.append(
            Finding(
                rel_path,
                "name-match",
                f"Frontmatter name {name!r} does not match folder name {expected_name!r}",
            )
        )
    if not description.startswith("Use when "):
        findings.append(
            Finding(
                rel_path,
                "trigger-description",
                "Description must start with 'Use when '",
            )
        )

    for header in REQUIRED_HEADERS:
        if header not in content:
            findings.append(Finding(rel_path, "required-section", f"Missing section: {header}"))

    if "- TBD" in content or "TBD" in content:
        findings.append(Finding(rel_path, "placeholder", "Contains unresolved placeholder text"))

    return findings


def parse_frontmatter(content: str) -> Dict[str, str] | None:
    lines = content.splitlines()
    if not lines:
        return None
    first = lines[0].lstrip("\ufeff").strip()
    if first != "---":
        return None
    end_index = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_index = idx
            break
    if end_index is None:
        return None

    frontmatter_lines = lines[1:end_index]
    data: Dict[str, str] = {}
    i = 0
    while i < len(frontmatter_lines):
        raw = frontmatter_lines[i]
        if ":" not in raw:
            i += 1
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value in {">", ">-", "|", "|-"}:
            i += 1
            block: List[str] = []
            while i < len(frontmatter_lines):
                next_line = frontmatter_lines[i]
                if not next_line.startswith((" ", "\t")):
                    break
                block.append(next_line.strip())
                i += 1
            data[key] = " ".join(block).strip()
            continue
        data[key] = value
        i += 1
    return data


def collect_skills(base: Path) -> List[Path]:
    paths: List[Path] = []
    required_names = sorted(ALL_V3_SKILLS.keys())
    for root in RUNTIME_ROOTS:
        skill_root = base / root
        if not skill_root.exists():
            continue
        for name in required_names:
            path = skill_root / name / "SKILL.md"
            if path.exists():
                paths.append(path)
            else:
                missing_path = skill_root / name / "SKILL.md"
                paths.append(missing_path)
    return paths


def report_payload(findings: List[Finding], checked_files: int) -> Dict[str, object]:
    return {
        "checked_files": checked_files,
        "findings_count": len(findings),
        "findings": [
            {
                "path": item.path,
                "check": item.check,
                "detail": item.detail,
            }
            for item in findings
        ],
    }


def render_text(findings: List[Finding], checked_files: int) -> str:
    lines = [
        f"Checked {checked_files} SKILL.md files.",
        f"Findings: {len(findings)}",
    ]
    if findings:
        lines.append("")
        lines.append("Top findings:")
        for item in findings[:20]:
            lines.append(f"- {item.path} [{item.check}] {item.detail}")
        if len(findings) > 20:
            lines.append(f"- ... and {len(findings) - 20} more")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    base = Path(args.project_path).resolve()
    skill_files = collect_skills(base)
    findings: List[Finding] = []
    for path in skill_files:
        if not path.exists():
            findings.append(
                Finding(
                    path.relative_to(base).as_posix(),
                    "missing-skill",
                    "Expected runtime skill file is missing",
                )
            )
            continue
        findings.extend(check_skill_file(path, base))

    payload = report_payload(findings, checked_files=len(skill_files))
    if args.json:
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print(render_text(findings, checked_files=len(skill_files)))

    if args.strict and findings:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
