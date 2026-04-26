#!/usr/bin/env python3
"""Build and install Relay-kit in an isolated virtualenv, then smoke the CLI."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path
from typing import Any


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Relay-kit package install smoke checks.")
    parser.add_argument("project_path", nargs="?", default=".", help="Project root to package")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable report")
    return parser.parse_args(argv)


def run_command(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def build_report(project_root: Path | str) -> dict[str, Any]:
    root = Path(project_root).resolve()
    with tempfile.TemporaryDirectory(prefix="relay-package-smoke-") as temp_dir:
        work = Path(temp_dir)
        wheelhouse = work / "wheelhouse"
        venv_dir = work / "venv"
        wheelhouse.mkdir(parents=True, exist_ok=True)

        build = run_command(
            [sys.executable, "-m", "pip", "wheel", str(root), "--no-deps", "-w", str(wheelhouse)],
            cwd=root,
        )
        wheel_files = sorted(wheelhouse.glob("relay_kit-*.whl"))
        if build.returncode != 0 or not wheel_files:
            return report("fail", root, build=build, wheel_files=wheel_files, install=None, smoke=None)

        venv.EnvBuilder(with_pip=True, clear=True).create(venv_dir)
        venv_python = venv_dir / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")
        relay_bin = venv_dir / ("Scripts" if os.name == "nt" else "bin") / ("relay-kit.exe" if os.name == "nt" else "relay-kit")

        install = run_command(
            [
                str(venv_python),
                "-m",
                "pip",
                "install",
                "--no-index",
                "--find-links",
                str(wheelhouse),
                "relay-kit",
            ],
            cwd=root,
        )
        if install.returncode != 0:
            return report("fail", root, build=build, wheel_files=wheel_files, install=install, smoke=None)

        smoke_command = [str(relay_bin), "--list-skills"] if relay_bin.exists() else [str(venv_python), "-m", "relay_kit_public_cli", "--list-skills"]
        smoke = run_command(smoke_command, cwd=root)
        status = "pass" if smoke.returncode == 0 and "baseline" in smoke.stdout else "fail"
        return report(status, root, build=build, wheel_files=wheel_files, install=install, smoke=smoke)


def report(
    status: str,
    root: Path,
    *,
    build: subprocess.CompletedProcess[str],
    wheel_files: list[Path],
    install: subprocess.CompletedProcess[str] | None,
    smoke: subprocess.CompletedProcess[str] | None,
) -> dict[str, Any]:
    return {
        "schema_version": "relay-kit.package-smoke.v1",
        "status": status,
        "project_path": str(root),
        "wheel_files": [path.name for path in wheel_files],
        "steps": {
            "build_wheel": step_payload(build),
            "install_wheel": step_payload(install),
            "cli_smoke": step_payload(smoke),
        },
    }


def step_payload(result: subprocess.CompletedProcess[str] | None) -> dict[str, Any]:
    if result is None:
        return {"status": "skipped", "exit_code": None, "summary": ""}
    return {
        "status": "pass" if result.returncode == 0 else "fail",
        "exit_code": result.returncode,
        "summary": summarize_output(result.stdout, result.stderr),
    }


def summarize_output(stdout: str, stderr: str) -> str:
    combined = "\n".join(part.strip() for part in [stdout, stderr] if part and part.strip())
    if not combined:
        return ""
    return "\n".join(combined.splitlines()[:12])


def render_text(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Relay-kit package smoke",
            f"- project: {payload['project_path']}",
            f"- status: {payload['status']}",
            f"- wheels: {', '.join(payload['wheel_files']) if payload['wheel_files'] else '-'}",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_report(args.project_path)
    if args.json:
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print(render_text(payload))
    return 0 if payload["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
