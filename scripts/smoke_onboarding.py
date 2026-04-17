#!/usr/bin/env python3
"""Fast onboarding smoke for Relay-kit public runtime."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DIRS = [
    ".claude/skills",
    ".agent/skills",
    ".codex/skills",
    ".relay-kit/contracts",
    ".relay-kit/state",
    ".relay-kit/docs",
    ".relay-kit/references",
]

REQUIRED_FILES = [
    ".relay-kit/contracts/project-context.md",
    ".relay-kit/state/workflow-state.md",
    ".relay-kit/docs/folder-structure.md",
    ".relay-kit/references/project-architecture.md",
]


@dataclass(frozen=True)
class SmokeResult:
    project_path: str
    generated_count: int
    missing_dirs: List[str]
    missing_files: List[str]

    @property
    def ok(self) -> bool:
        return not self.missing_dirs and not self.missing_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a fast Relay-kit onboarding smoke for a new project.",
    )
    parser.add_argument(
        "project_path",
        nargs="?",
        help="Optional existing project path. If omitted, a temp project is created.",
    )
    parser.add_argument("--keep-temp", action="store_true", help="Keep temp project when no project_path is provided")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    return parser.parse_args()


def run_command(cmd: List[str]) -> str:
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "smoke generation failed\n"
            f"command: {' '.join(cmd)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result.stdout


def run_smoke(project: Path) -> SmokeResult:
    output = run_command(
        [
            sys.executable,
            str(REPO_ROOT / "relay_kit.py"),
            str(project),
            "--bundle",
            "baseline",
            "--ai",
            "all",
            "--emit-contracts",
            "--emit-docs",
            "--emit-reference-templates",
        ]
    )
    generated_count = sum(1 for line in output.splitlines() if line.strip().startswith("- "))

    missing_dirs = [
        rel for rel in REQUIRED_DIRS if not (project / rel).is_dir()
    ]
    missing_files = [
        rel for rel in REQUIRED_FILES if not (project / rel).is_file()
    ]

    return SmokeResult(
        project_path=str(project),
        generated_count=generated_count,
        missing_dirs=missing_dirs,
        missing_files=missing_files,
    )


def render_text(result: SmokeResult) -> str:
    lines = [
        "Relay-kit onboarding smoke",
        f"- project: {result.project_path}",
        f"- generated files: {result.generated_count}",
        f"- missing dirs: {len(result.missing_dirs)}",
        f"- missing files: {len(result.missing_files)}",
    ]
    if result.missing_dirs:
        lines.append("- missing dir list:")
        lines.extend([f"  - {item}" for item in result.missing_dirs])
    if result.missing_files:
        lines.append("- missing file list:")
        lines.extend([f"  - {item}" for item in result.missing_files])
    lines.append(f"- status: {'PASS' if result.ok else 'FAIL'}")
    return "\n".join(lines)


def render_json(result: SmokeResult) -> str:
    payload = {
        "project_path": result.project_path,
        "generated_count": result.generated_count,
        "missing_dirs": result.missing_dirs,
        "missing_files": result.missing_files,
        "status": "pass" if result.ok else "fail",
    }
    return json.dumps(payload, ensure_ascii=True, indent=2)


def main() -> int:
    args = parse_args()

    created_temp = False
    if args.project_path:
        project = Path(args.project_path).resolve()
        project.mkdir(parents=True, exist_ok=True)
    else:
        project = Path(tempfile.mkdtemp(prefix="relay-kit-smoke-"))
        created_temp = True

    try:
        result = run_smoke(project)
        print(render_json(result) if args.json else render_text(result))
        return 0 if result.ok else 2
    finally:
        if created_temp and not args.keep_temp:
            shutil.rmtree(project, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
