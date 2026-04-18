#!/usr/bin/env python3
"""Run one deep Relay-kit checkpoint with 30 high-signal cases.

The script is designed for Windows and defaults heavy temp/log output to D:.
It returns non-zero when any strict case fails.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from relay_kit_v3.generator import REFERENCE_NAMES_FOR_BUNDLE, contract_names_for_bundle
from relay_kit_v3.registry.artifacts import ARTIFACT_CONTRACTS
from relay_kit_v3.registry.support_refs import SUPPORT_REFERENCES


DEFAULT_OUTPUT_ROOT = Path(r"D:\relay-kit-checkpoint")
DEFAULT_TEMP_ROOT = Path(r"D:\relay-kit-temp")
DEFAULT_REAL_PROJECTS = [
    Path(r"C:\Users\b0ydeptrai\OneDrive\Documents\prompt-genius"),
    Path(r"C:\Users\b0ydeptrai\OneDrive\Documents\fakeinfo-fix"),
    Path(r"C:\Users\b0ydeptrai\OneDrive\Documents\donut"),
    Path(r"D:\Download\VIN-Pair-Tool"),
]
RUNTIME_BY_AI = {
    "codex": [".codex/skills"],
    "claude": [".claude/skills"],
    "antigravity": [".agent/skills"],
    "all": [".codex/skills", ".claude/skills", ".agent/skills"],
    "generic": [".relay-kit-prompts"],
}


@dataclass
class RunResult:
    name: str
    ok: bool
    returncode: int
    duration_sec: float
    stdout: str
    stderr: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one deep Relay-kit checkpoint (30 cases).")
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Root folder for logs/projects/runs. Default: D:\\relay-kit-checkpoint",
    )
    parser.add_argument(
        "--temp-root",
        default=str(DEFAULT_TEMP_ROOT),
        help="Temp folder for subprocesses. Default: D:\\relay-kit-temp",
    )
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Relay-kit repo root.",
    )
    parser.add_argument(
        "--allow-no-real-projects",
        action="store_true",
        help="Do not fail when no real projects are found; use synthetic projects only.",
    )
    return parser.parse_args()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def ensure_synthetic_projects(projects_root: Path) -> dict[str, Path]:
    ensure_dir(projects_root)
    base = {
        "syn_1": projects_root / "synthetic-proj-1",
        "syn_2": projects_root / "synthetic-proj-2",
        "syn_3": projects_root / "synthetic-proj-3",
        "space": projects_root / "space project",
    }
    deep = projects_root / "very-long-path"
    for idx in range(1, 11):
        deep = deep / f"nested-level-{idx}"
    base["long"] = deep / "target-project"

    for path in base.values():
        ensure_dir(path)
        readme = path / "README.md"
        if not readme.exists():
            readme.write_text("# deep-checkpoint project\n", encoding="utf-8")
    return base


def discover_real_projects() -> list[Path]:
    return [project for project in DEFAULT_REAL_PROJECTS if project.exists()]


def run_cmd(
    *,
    name: str,
    cmd: list[str],
    cwd: Path,
    temp_root: Path,
    expect: int = 0,
    env_patch: dict[str, str] | None = None,
    timeout: int = 240,
) -> RunResult:
    env = dict(os.environ)
    env["TEMP"] = str(temp_root)
    env["TMP"] = str(temp_root)
    env["RELAY_KIT_CYCLE_SOURCE"] = name
    if env_patch:
        env.update(env_patch)

    started = time.perf_counter()
    process = subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        env=env,
        timeout=timeout,
        check=False,
    )
    elapsed = round(time.perf_counter() - started, 3)
    return RunResult(
        name=name,
        ok=process.returncode == expect,
        returncode=process.returncode,
        duration_sec=elapsed,
        stdout=process.stdout,
        stderr=process.stderr,
    )


def expected_contract_paths(bundle: str) -> list[str]:
    names = contract_names_for_bundle(bundle)
    expected = [ARTIFACT_CONTRACTS[name].path for name in names]
    expected.append(".relay-kit/state/srs-policy.json")
    return sorted(set(expected))


def expected_reference_paths(bundle: str) -> list[str]:
    return sorted(
        set(
            SUPPORT_REFERENCES[name].path
            for name in REFERENCE_NAMES_FOR_BUNDLE.get(bundle, [])
        )
    )


def list_files_relative(root: Path) -> list[str]:
    if not root.exists():
        return []
    return sorted(
        path.relative_to(root.parent.parent).as_posix()
        for path in root.rglob("*")
        if path.is_file()
    )


def validate_generated(target_dir: Path, bundle: str, ai: str) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    unexpected: list[str] = []

    for rel in RUNTIME_BY_AI[ai]:
        if not (target_dir / rel).exists():
            missing.append(rel)

    contracts_expected = expected_contract_paths(bundle)
    refs_expected = expected_reference_paths(bundle)

    for rel in contracts_expected:
        if not (target_dir / rel).exists():
            missing.append(rel)
    for rel in refs_expected:
        if not (target_dir / rel).exists():
            missing.append(rel)

    contracts_root = target_dir / ".relay-kit" / "contracts"
    contract_files = list_files_relative(contracts_root)
    expected_contract_files = sorted(
        rel for rel in contracts_expected if rel.startswith(".relay-kit/contracts/")
    )
    unexpected.extend(path for path in contract_files if path not in expected_contract_files)

    refs_root = target_dir / ".relay-kit" / "references"
    ref_files = list_files_relative(refs_root)
    unexpected.extend(path for path in ref_files if path not in refs_expected)

    return missing, unexpected


def append_case(
    cases: list[dict[str, object]],
    *,
    category: str,
    result: RunResult,
    notes: Iterable[str] | None = None,
    warnings: Iterable[str] | None = None,
) -> None:
    cases.append(
        {
            "id": len(cases) + 1,
            "category": category,
            "name": result.name,
            "ok": result.ok,
            "duration_sec": result.duration_sec,
            "returncode": result.returncode,
            "notes": list(notes or []),
            "warnings": list(warnings or []),
            "stdout_tail": result.stdout[-1200:],
            "stderr_tail": result.stderr[-1200:],
        }
    )


def run_gate_suite(
    *,
    profile_name: str,
    env_patch: dict[str, str],
    repo_root: Path,
    temp_root: Path,
) -> RunResult:
    suite_steps = [
        ("validate_runtime", [sys.executable, "scripts/validate_runtime.py"]),
        ("skill_gauntlet", [sys.executable, "scripts/skill_gauntlet.py", "--strict"]),
        ("migration_guard", [sys.executable, "scripts/migration_guard.py", ".", "--strict"]),
        ("srs_guard", [sys.executable, "scripts/srs_guard.py", ".", "--strict"]),
        ("pytest", [sys.executable, "-m", "pytest", "-q", "tests"]),
    ]

    step_notes: list[str] = []
    suite_ok = True
    total_duration = 0.0
    for step_name, cmd in suite_steps:
        result = run_cmd(
            name=f"{profile_name}-{step_name}",
            cmd=cmd,
            cwd=repo_root,
            temp_root=temp_root,
            env_patch=env_patch,
            timeout=420,
        )
        suite_ok = suite_ok and result.ok
        total_duration += result.duration_sec
        step_notes.append(f"{step_name}: rc={result.returncode}")

    return RunResult(
        name=profile_name,
        ok=suite_ok,
        returncode=0 if suite_ok else 1,
        duration_sec=round(total_duration, 3),
        stdout="\n".join(step_notes),
        stderr="",
    )


def summarize_markdown(summary: dict[str, object], report_path: Path) -> str:
    results: list[dict[str, object]] = summary["results"]  # type: ignore[assignment]
    failed = [item for item in results if not bool(item["ok"])]
    lines = [
        f"# Deep checkpoint 30 ({summary['timestamp']})",
        "",
        f"- Total: {summary['total_cases']}",
        f"- Pass: {summary['pass_cases']}",
        f"- Fail: {summary['fail_cases']}",
        f"- Pass rate: {summary['pass_rate']}",
        f"- Avg duration/case (s): {summary['avg_case_duration_sec']}",
        f"- Max duration/case (s): {summary['max_case_duration_sec']}",
        f"- JSON report: `{report_path}`",
        "",
        "## Failed cases",
    ]
    if not failed:
        lines.append("- None")
    else:
        for item in failed:
            lines.append(f"- [{item['id']}] {item['name']} ({item['category']})")
            warnings = item.get("warnings") or []
            if warnings:
                lines.append(f"  - warnings: {' | '.join(warnings)}")

    lines.append("")
    lines.append("## Runtime-doctor live")
    for item in results:
        if item["name"] != "runtime-doctor-live":
            continue
        for warning in item.get("warnings") or []:
            lines.append(f"- {warning}")
        for line in str(item.get("stdout_tail", "")).strip().splitlines()[:10]:
            lines.append(f"- {line}")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    output_root = Path(args.output_root).resolve()
    temp_root = Path(args.temp_root).resolve()
    ensure_dir(output_root)
    ensure_dir(temp_root)

    logs_dir = output_root / "logs"
    runs_dir = output_root / "runs"
    projects_dir = output_root / "projects"
    ensure_dir(logs_dir)
    ensure_dir(runs_dir)
    synthetic = ensure_synthetic_projects(projects_dir)
    real_projects = discover_real_projects()

    if len(real_projects) < 2 and not args.allow_no_real_projects:
        print(
            "Deep checkpoint needs at least 2 real projects. "
            "Use --allow-no-real-projects to run with synthetic-only mode."
        )
        return 2

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_root = runs_dir / f"deep-checkpoint-30-{timestamp}"
    ensure_dir(run_root)

    cases: list[dict[str, object]] = []

    profiles = [
        ("gate-suite-profile-1", {}),
        ("gate-suite-profile-2", {"PYTHONUTF8": "1"}),
        ("gate-suite-profile-3", {"PYTHONIOENCODING": "utf-8"}),
    ]
    for profile_name, env_patch in profiles:
        result = run_gate_suite(
            profile_name=profile_name,
            env_patch=env_patch,
            repo_root=repo_root,
            temp_root=temp_root,
        )
        append_case(cases, category="gate-suite", result=result, notes=result.stdout.splitlines())

    diverse_targets = [
        *real_projects,
        synthetic["space"],
        synthetic["long"],
        synthetic["syn_1"],
        synthetic["syn_2"],
        synthetic["syn_3"],
    ]
    diverse_targets = list(dict.fromkeys(diverse_targets))
    diverse_cmd = [sys.executable, "scripts/soak_beta.py", *[str(path) for path in diverse_targets], "--json"]
    diverse_result = run_cmd(
        name="soak-diverse",
        cmd=diverse_cmd,
        cwd=repo_root,
        temp_root=temp_root,
        timeout=480,
    )
    diverse_warnings: list[str] = []
    if diverse_result.ok:
        payload = json.loads(diverse_result.stdout)
        bad = [item for item in payload["results"] if item["status"] != "pass"]
        if bad:
            diverse_result.ok = False
            diverse_result.returncode = 1
            diverse_warnings.append(f"soak failures: {len(bad)}")
        else:
            diverse_warnings.append(f"all pass: {len(payload['results'])} projects")
    append_case(cases, category="soak", result=diverse_result, warnings=diverse_warnings)

    real_targets = real_projects[:4] if real_projects else [synthetic["syn_1"], synthetic["syn_2"]]
    real_result = run_cmd(
        name="soak-real",
        cmd=[sys.executable, "scripts/soak_beta.py", *[str(path) for path in real_targets], "--json"],
        cwd=repo_root,
        temp_root=temp_root,
        timeout=420,
    )
    append_case(cases, category="soak", result=real_result)

    smoke_ok = True
    smoke_durations: list[float] = []
    for idx in range(20):
        smoke_result = run_cmd(
            name=f"smoke-{idx + 1}",
            cmd=[sys.executable, "scripts/smoke_onboarding.py", "--json"],
            cwd=repo_root,
            temp_root=temp_root,
            timeout=240,
        )
        smoke_ok = smoke_ok and smoke_result.ok
        smoke_durations.append(smoke_result.duration_sec)
        if smoke_result.ok:
            payload = json.loads(smoke_result.stdout)
            smoke_ok = smoke_ok and str(payload.get("status", "")).lower() == "pass"
    append_case(
        cases,
        category="smoke",
        result=RunResult(
            name="smoke-onboarding-x20",
            ok=smoke_ok,
            returncode=0 if smoke_ok else 1,
            duration_sec=round(sum(smoke_durations), 3),
            stdout="",
            stderr="",
        ),
        warnings=[
            f"avg={round(statistics.mean(smoke_durations), 3)}s",
            f"max={max(smoke_durations)}s",
        ],
    )

    for bundle in ["round4", "discipline-utilities", "srs-first", "baseline"]:
        for ai in ["codex", "claude", "antigravity", "generic", "all"]:
            target = run_root / "matrix" / f"{bundle}-{ai}"
            if target.exists():
                shutil.rmtree(target, ignore_errors=True)
            ensure_dir(target)
            matrix_result = run_cmd(
                name=f"matrix-{bundle}-{ai}",
                cmd=[
                    sys.executable,
                    "relay_kit.py",
                    str(target),
                    "--bundle",
                    bundle,
                    "--ai",
                    ai,
                    "--emit-contracts",
                    "--emit-docs",
                    "--emit-reference-templates",
                ],
                cwd=repo_root,
                temp_root=temp_root,
                timeout=300,
            )
            notes: list[str] = []
            warnings: list[str] = []
            if matrix_result.ok:
                missing, unexpected = validate_generated(target, bundle, ai)
                if missing or unexpected:
                    matrix_result.ok = False
                    matrix_result.returncode = 1
                    if missing:
                        warnings.append("missing: " + ", ".join(missing))
                    if unexpected:
                        warnings.append("unexpected: " + ", ".join(unexpected[:10]))
                else:
                    notes.append("bundle-gating match")
            append_case(cases, category="matrix", result=matrix_result, notes=notes, warnings=warnings)

    public_ok = True
    public_notes: list[str] = []
    for adapter, rel in [("--codex", ".codex/skills"), ("--claude", ".claude/skills"), ("--antigravity", ".agent/skills")]:
        target = run_root / "public" / adapter.replace("--", "")
        if target.exists():
            shutil.rmtree(target, ignore_errors=True)
        ensure_dir(target)
        public_result = run_cmd(
            name=f"public-{adapter}",
            cmd=[sys.executable, "relay_kit_public_cli.py", str(target), adapter],
            cwd=repo_root,
            temp_root=temp_root,
            timeout=300,
        )
        current_ok = public_result.ok and (target / rel).exists() and (target / ".relay-kit").exists()
        public_ok = public_ok and current_ok
        public_notes.append(f"{adapter}:{'ok' if current_ok else 'fail'}")
    append_case(
        cases,
        category="public-cli",
        result=RunResult(
            name="public-cli-adapters",
            ok=public_ok,
            returncode=0 if public_ok else 1,
            duration_sec=0.0,
            stdout="\n".join(public_notes),
            stderr="",
        ),
        notes=public_notes,
    )

    continuity_project = synthetic["syn_1"]
    steps = [
        run_cmd(
            name="ctx-checkpoint",
            cmd=[
                sys.executable,
                "scripts/context_continuity.py",
                "checkpoint",
                str(continuity_project),
                "--objective",
                "deep-day-checkpoint",
                "--lane",
                "primary",
                "--next-step",
                "triage",
            ],
            cwd=repo_root,
            temp_root=temp_root,
        ),
        run_cmd(
            name="ctx-rehydrate",
            cmd=[sys.executable, "scripts/context_continuity.py", "rehydrate", str(continuity_project)],
            cwd=repo_root,
            temp_root=temp_root,
        ),
        run_cmd(
            name="ctx-diff",
            cmd=[sys.executable, "scripts/context_continuity.py", "diff-since-last", str(continuity_project)],
            cwd=repo_root,
            temp_root=temp_root,
        ),
        run_cmd(
            name="ctx-handoff",
            cmd=[
                sys.executable,
                "scripts/context_continuity.py",
                "handoff",
                str(continuity_project),
                "--reason",
                "deep-checkpoint",
                "--receiver",
                "qa",
            ],
            cwd=repo_root,
            temp_root=temp_root,
        ),
    ]
    handoff_files = list((continuity_project / ".relay-kit" / "handoffs").glob("*.md"))
    continuity_ok = (
        all(step.ok for step in steps)
        and (continuity_project / ".relay-kit" / "state" / "context-manifest.json").exists()
        and (continuity_project / ".relay-kit" / "state" / "session-ledger.jsonl").exists()
        and bool(handoff_files)
    )
    append_case(
        cases,
        category="context-continuity",
        result=RunResult(
            name="context-continuity-flow",
            ok=continuity_ok,
            returncode=0 if continuity_ok else 1,
            duration_sec=round(sum(step.duration_sec for step in steps), 3),
            stdout="",
            stderr="",
        ),
        notes=[f"handoff_files={len(handoff_files)}"],
    )

    doctor_template = run_cmd(
        name="runtime-doctor-template",
        cmd=[sys.executable, "scripts/runtime_doctor.py", ".", "--state-mode", "template", "--strict"],
        cwd=repo_root,
        temp_root=temp_root,
    )
    append_case(cases, category="runtime-doctor", result=doctor_template)

    doctor_live = run_cmd(
        name="runtime-doctor-live",
        cmd=[sys.executable, "scripts/runtime_doctor.py", str(continuity_project), "--state-mode", "live"],
        cwd=repo_root,
        temp_root=temp_root,
    )
    doctor_live_warnings = [
        line.strip()
        for line in doctor_live.stdout.splitlines()
        if line.strip().startswith("- findings:")
    ]
    append_case(
        cases,
        category="runtime-doctor",
        result=doctor_live,
        warnings=doctor_live_warnings,
    )

    pass_cases = sum(1 for item in cases if bool(item["ok"]))
    fail_cases = len(cases) - pass_cases
    durations = [float(item["duration_sec"]) for item in cases]
    summary = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "repo_root": str(repo_root),
        "output_root": str(output_root),
        "temp_root": str(temp_root),
        "real_projects_found": [str(path) for path in real_projects],
        "total_cases": len(cases),
        "pass_cases": pass_cases,
        "fail_cases": fail_cases,
        "pass_rate": round(pass_cases / len(cases), 4) if cases else 0.0,
        "avg_case_duration_sec": round(statistics.mean(durations), 3) if durations else 0.0,
        "max_case_duration_sec": max(durations) if durations else 0.0,
        "results": cases,
    }

    json_path = logs_dir / f"deep-checkpoint-30-{timestamp}.json"
    md_path = logs_dir / f"deep-checkpoint-30-{timestamp}.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(summarize_markdown(summary, json_path), encoding="utf-8")

    print(
        json.dumps(
            {
                "timestamp": summary["timestamp"],
                "total_cases": summary["total_cases"],
                "pass_cases": summary["pass_cases"],
                "fail_cases": summary["fail_cases"],
                "pass_rate": summary["pass_rate"],
                "avg_case_duration_sec": summary["avg_case_duration_sec"],
                "max_case_duration_sec": summary["max_case_duration_sec"],
                "json_report": str(json_path),
                "md_report": str(md_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    return 0 if fail_cases == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
