#!/usr/bin/env python3
"""Public Relay-kit installer CLI.

This wrapper exposes a friendlier command surface:
  relay-kit init <project_path> --codex|--claude|--antigravity --baseline
  relay-kit <project_path> --codex|--claude|--antigravity
  relay-kit doctor <project_path>
  relay-kit eval run <project_path>
  relay-kit upgrade check <project_path>

It maps to the existing canonical runtime entrypoint (`relay_kit.py`)
without changing the underlying generation flow.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import relay_kit as relay_core
from relay_kit_v3.evidence_ledger import append_event, ledger_path, new_run_id, parse_findings_count, summarize_events
from relay_kit_v3.bundle_manifest import verify_manifest_file, write_manifest
from relay_kit_v3.spec_export import write_spec
from relay_kit_v3.upgrade import build_upgrade_report, render_report, write_version_marker


REPO_ROOT = Path(__file__).resolve().parent


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit",
        description="Public Relay-kit installer for baseline runtime generation.",
    )
    parser.add_argument("project_path", nargs="?", default=".", help="Target project path")

    adapter = parser.add_mutually_exclusive_group()
    adapter.add_argument("--codex", action="store_true", help="Install Codex runtime skills")
    adapter.add_argument("--claude", action="store_true", help="Install Claude runtime skills")
    adapter.add_argument(
        "--antigravity",
        action="store_true",
        help="Install Antigravity runtime skills (mapped to .agent)",
    )
    adapter.add_argument("--all", action="store_true", help="Install all active runtime adapters")
    adapter.add_argument("--generic", action="store_true", help="Generate generic prompts output")

    parser.add_argument("--bundle", default="baseline", help="Bundle name (default: baseline)")
    parser.add_argument(
        "--baseline",
        dest="bundle",
        action="store_const",
        const="baseline",
        help="Generate the baseline bundle (default)",
    )
    parser.add_argument("--no-bundle", action="store_true", help="Skip v3 bundle generation")

    parser.add_argument(
        "--emit-contracts",
        dest="emit_contracts",
        action="store_true",
        default=True,
        help="Emit contracts/state artifacts (default: on)",
    )
    parser.add_argument(
        "--no-emit-contracts",
        dest="emit_contracts",
        action="store_false",
        help="Disable contracts/state emit",
    )
    parser.add_argument(
        "--emit-docs",
        dest="emit_docs",
        action="store_true",
        default=True,
        help="Emit docs artifacts (default: on)",
    )
    parser.add_argument(
        "--no-emit-docs",
        dest="emit_docs",
        action="store_false",
        help="Disable docs emit",
    )
    parser.add_argument(
        "--emit-reference-templates",
        dest="emit_reference_templates",
        action="store_true",
        default=True,
        help="Emit reference templates (default: on)",
    )
    parser.add_argument(
        "--no-emit-reference-templates",
        dest="emit_reference_templates",
        action="store_false",
        help="Disable reference templates emit",
    )

    srs_switch = parser.add_mutually_exclusive_group()
    srs_switch.add_argument("--enable-srs-first", action="store_true", help="Enable SRS-first policy for this project")
    srs_switch.add_argument("--disable-srs-first", action="store_true", help="Disable SRS-first policy for this project")
    parser.add_argument("--srs-gate", choices=["off", "warn", "hard"], help="SRS policy gate mode")
    parser.add_argument("--srs-scope", choices=["product-enterprise", "all"], help="SRS policy scope")
    parser.add_argument("--srs-risk", choices=["normal", "high"], help="SRS policy risk profile")

    parser.add_argument("--legacy-kit", help="Optional preserved legacy kit")
    parser.add_argument("--skills", nargs="+", metavar="SKILL", help="Optional legacy skills")
    parser.add_argument("--list-skills", action="store_true", help="List bundles and legacy kits")
    parser.add_argument("--show-legacy", action="store_true", help="Show preserved legacy kits in --list-skills output")
    parser.add_argument("-v", "--verbose", action="store_true")

    return parser.parse_args(argv)


def _parse_doctor_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit doctor",
        description="Run Relay-kit runtime verification gates.",
    )
    parser.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    parser.add_argument("--skip-tests", action="store_true", help="Skip the local pytest suite")
    parser.add_argument("--verbose", action="store_true", help="Print stdout and stderr for passing gates")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable doctor results")
    return parser.parse_args(argv)


def _parse_evidence_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit evidence",
        description="Inspect Relay-kit evidence ledger events.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    summary = subparsers.add_parser("summary", help="Summarize recent evidence events")
    summary.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    summary.add_argument("--limit", type=int, default=20, help="Recent event count to show")
    summary.add_argument("--json", action="store_true", help="Emit JSON summary")
    return parser.parse_args(argv)


def _parse_spec_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit spec",
        description="Export Relay-kit planning and QA contracts as machine-readable specs.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    export = subparsers.add_parser("export", help="Export Relay-kit contracts to JSON")
    export.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    export.add_argument(
        "--output-file",
        default=None,
        help="Output path (default: <project>/.relay-kit/specs/relay-spec.json)",
    )
    return parser.parse_args(argv)


def _parse_manifest_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit manifest",
        description="Write or verify checksummed Relay-kit bundle manifests.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    write = subparsers.add_parser("write", help="Write a checksummed bundle manifest")
    write.add_argument("project_path", nargs="?", default=".", help="Project root for default output")
    write.add_argument(
        "--output-file",
        default=None,
        help="Output path (default: <project>/.relay-kit/manifest/bundles.json)",
    )
    verify = subparsers.add_parser("verify", help="Verify a checksummed bundle manifest")
    verify.add_argument("project_path", nargs="?", default=".", help="Project root for default manifest lookup")
    verify.add_argument(
        "--manifest-file",
        default=None,
        help="Manifest path (default: <project>/.relay-kit/manifest/bundles.json)",
    )
    return parser.parse_args(argv)


def _parse_eval_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit eval",
        description="Run Relay-kit workflow scenario evaluations.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    run = subparsers.add_parser("run", help="Run workflow routing scenario evals")
    run.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    run.add_argument(
        "--scenario-fixtures",
        default=None,
        help="JSON scenario fixture file (default: bundled Relay-kit fixtures)",
    )
    run.add_argument("--output-file", default=None, help="Optional JSON report output path")
    run.add_argument("--json", action="store_true", help="Emit JSON report")
    run.add_argument("--strict", action="store_true", help="Return non-zero when any scenario fails")
    return parser.parse_args(argv)


def _parse_upgrade_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit upgrade",
        description="Check and mark versioned Relay-kit runtime upgrades.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)

    check = subparsers.add_parser("check", help="Check whether a project runtime is current")
    check.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    check.add_argument("--manifest-file", default=None, help="Optional bundle manifest path")
    check.add_argument("--json", action="store_true", help="Emit JSON report")
    check.add_argument("--strict", action="store_true", help="Return non-zero when action is required")

    plan = subparsers.add_parser("plan", help="Print an upgrade plan for this project")
    plan.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    plan.add_argument("--manifest-file", default=None, help="Optional bundle manifest path")
    plan.add_argument("--json", action="store_true", help="Emit JSON report")
    plan.add_argument("--strict", action="store_true", help="Return non-zero when action is required")

    mark = subparsers.add_parser("mark-current", help="Write the current Relay-kit runtime version marker")
    mark.add_argument("project_path", nargs="?", default=".", help="Project root to update")
    mark.add_argument("--bundle", default="baseline", help="Runtime bundle installed in the project")
    mark.add_argument(
        "--adapter",
        action="append",
        choices=["codex", "claude", "antigravity", "generic", "all"],
        help="Installed adapter. Repeat for multiple adapters.",
    )
    mark.add_argument("--manifest-file", default=None, help="Optional bundle manifest path")
    return parser.parse_args(argv)


def _resolve_ai(args: argparse.Namespace) -> str:
    if args.codex:
        return "codex"
    if args.claude:
        return "claude"
    if args.antigravity:
        return "antigravity"
    if args.all:
        return "all"
    if args.generic:
        return "generic"
    return "codex"


def _build_relay_argv(args: argparse.Namespace) -> list[str]:
    relay_argv: list[str] = ["relay-kit-core"]

    if args.list_skills:
        relay_argv.append("--list-skills")
        if args.show_legacy:
            relay_argv.append("--show-legacy")
        return relay_argv

    relay_argv.append(args.project_path)
    relay_argv.extend(["--ai", _resolve_ai(args)])

    if not args.no_bundle:
        relay_argv.extend(["--bundle", args.bundle])

    if args.emit_contracts:
        relay_argv.append("--emit-contracts")
    if args.emit_docs:
        relay_argv.append("--emit-docs")
    if args.emit_reference_templates:
        relay_argv.append("--emit-reference-templates")

    if args.enable_srs_first:
        relay_argv.append("--enable-srs-first")
    if args.disable_srs_first:
        relay_argv.append("--disable-srs-first")
    if args.srs_gate:
        relay_argv.extend(["--srs-gate", args.srs_gate])
    if args.srs_scope:
        relay_argv.extend(["--srs-scope", args.srs_scope])
    if args.srs_risk:
        relay_argv.extend(["--srs-risk", args.srs_risk])

    if args.legacy_kit:
        relay_argv.extend(["--legacy-kit", args.legacy_kit])
    if args.skills:
        relay_argv.append("--skills")
        relay_argv.extend(args.skills)
    if args.verbose:
        relay_argv.append("--verbose")

    return relay_argv


def _doctor_commands(project_path: str, skip_tests: bool) -> list[tuple[str, list[str]]]:
    commands = [
        ("validate runtime", [sys.executable, str(REPO_ROOT / "scripts" / "validate_runtime.py")]),
        (
            "runtime doctor template",
            [sys.executable, str(REPO_ROOT / "scripts" / "runtime_doctor.py"), project_path, "--strict"],
        ),
        (
            "runtime doctor live",
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "runtime_doctor.py"),
                project_path,
                "--strict",
                "--state-mode",
                "live",
            ],
        ),
        (
            "migration guard",
            [sys.executable, str(REPO_ROOT / "scripts" / "migration_guard.py"), project_path, "--strict"],
        ),
        (
            "policy guard",
            [sys.executable, str(REPO_ROOT / "scripts" / "policy_guard.py"), project_path, "--strict"],
        ),
        (
            "srs guard",
            [sys.executable, str(REPO_ROOT / "scripts" / "srs_guard.py"), project_path, "--strict"],
        ),
        (
            "skill gauntlet",
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "skill_gauntlet.py"),
                project_path,
                "--strict",
                "--semantic",
            ],
        ),
        (
            "workflow eval",
            [sys.executable, str(REPO_ROOT / "scripts" / "eval_workflows.py"), project_path, "--strict"],
        ),
    ]

    if not skip_tests and (REPO_ROOT / "tests").exists():
        commands.append(("pytest", [sys.executable, "-m", "pytest", "tests", "-q"]))

    return commands


def _print_doctor_output(label: str, result: subprocess.CompletedProcess[str], verbose: bool) -> None:
    status = "pass" if result.returncode == 0 else "fail"
    print(f"- {label}: {status}")
    if verbose or result.returncode != 0:
        if result.stdout:
            print(result.stdout.rstrip())
        if result.stderr:
            print(result.stderr.rstrip())


def run_doctor(args: argparse.Namespace) -> int:
    project_path = str(Path(args.project_path).resolve())
    run_id = new_run_id()
    if not args.json:
        print("Relay-kit doctor")
        print(f"- project: {project_path}")

    exit_code = 0
    gate_results: list[dict[str, object]] = []
    for label, command in _doctor_commands(project_path, args.skip_tests):
        started = time.perf_counter()
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        status = "pass" if result.returncode == 0 else "fail"
        gate_event = {
            "run_id": run_id,
            "command": "doctor",
            "gate": label,
            "adapter": None,
            "selected_skill": None,
            "status": status,
            "exit_code": result.returncode,
            "findings_count": parse_findings_count(result.stdout, result.stderr),
            "evidence_files": [],
            "elapsed_ms": elapsed_ms,
        }
        append_event(project_path, gate_event)
        gate_results.append(gate_event)
        if not args.json:
            _print_doctor_output(label, result, args.verbose)
        if result.returncode != 0:
            exit_code = 1

    if args.json:
        payload = {
            "run_id": run_id,
            "project": project_path,
            "status": "pass" if exit_code == 0 else "fail",
            "ledger_path": str(ledger_path(project_path)),
            "results": gate_results,
        }
        print(json.dumps(payload, ensure_ascii=True, indent=2))

    return exit_code


def run_evidence(args: argparse.Namespace) -> int:
    if args.action != "summary":
        return 2

    summary = summarize_events(args.project_path, limit=args.limit)
    if args.json:
        payload = {
            "ledger_path": str(summary.ledger_path),
            "total_events": summary.total_events,
            "status_counts": summary.status_counts,
            "gate_counts": summary.gate_counts,
            "recent_events": summary.recent_events,
        }
        print(json.dumps(payload, ensure_ascii=True, indent=2))
        return 0

    print("Relay-kit evidence summary")
    print(f"- ledger: {summary.ledger_path}")
    print(f"- total events: {summary.total_events}")
    if summary.status_counts:
        statuses = ", ".join(f"{key}={value}" for key, value in summary.status_counts.items())
        print(f"- statuses: {statuses}")
    if summary.recent_events:
        print("- recent:")
        for event in summary.recent_events:
            gate = event.get("gate", event.get("command", "unknown"))
            status = event.get("status", "unknown")
            timestamp = event.get("timestamp", "-")
            print(f"  - {timestamp} {gate}: {status}")
    return 0


def run_spec(args: argparse.Namespace) -> int:
    if args.action != "export":
        return 2
    output_path = write_spec(args.project_path, args.output_file)
    print(f"Wrote {output_path}")
    return 0


def run_manifest(args: argparse.Namespace) -> int:
    if args.action == "write":
        output_path = write_manifest(args.project_path, args.output_file)
        print(f"Wrote {output_path}")
        return 0
    if args.action == "verify":
        manifest_path = Path(args.manifest_file) if args.manifest_file else Path(args.project_path) / ".relay-kit" / "manifest" / "bundles.json"
        result = verify_manifest_file(manifest_path)
        if result.ok:
            print("Manifest verification passed.")
            return 0
        print("Manifest verification failed.")
        for finding in result.findings:
            print(f"- {finding}")
        return 2
    return 2


def run_eval(args: argparse.Namespace) -> int:
    if args.action != "run":
        return 2
    from scripts import eval_workflows

    eval_argv = [args.project_path]
    if args.scenario_fixtures:
        eval_argv.extend(["--scenario-fixtures", args.scenario_fixtures])
    if args.output_file:
        eval_argv.extend(["--output-file", args.output_file])
    if args.json:
        eval_argv.append("--json")
    if args.strict:
        eval_argv.append("--strict")
    return eval_workflows.main(eval_argv)


def run_upgrade(args: argparse.Namespace) -> int:
    if args.action in {"check", "plan"}:
        report = build_upgrade_report(args.project_path, manifest_file=args.manifest_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            title = "Relay-kit upgrade plan" if args.action == "plan" else "Relay-kit upgrade check"
            print(render_report(report, title=title))
        if args.strict and report["status"] != "pass":
            return 2
        return 0
    if args.action == "mark-current":
        output_path = write_version_marker(
            args.project_path,
            bundle=args.bundle,
            adapters=args.adapter,
            manifest_file=args.manifest_file,
        )
        print(f"Wrote {output_path}")
        return 0
    return 2


def main(argv: list[str] | None = None) -> int:
    raw_argv = sys.argv[1:] if argv is None else argv
    if raw_argv and raw_argv[0] == "doctor":
        return run_doctor(_parse_doctor_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "evidence":
        return run_evidence(_parse_evidence_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "spec":
        return run_spec(_parse_spec_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "manifest":
        return run_manifest(_parse_manifest_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "eval":
        return run_eval(_parse_eval_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "upgrade":
        return run_upgrade(_parse_upgrade_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "init":
        raw_argv = raw_argv[1:]

    args = _parse_args(raw_argv)
    relay_argv = _build_relay_argv(args)

    original_argv = sys.argv[:]
    try:
        sys.argv = relay_argv
        return relay_core.main(invoked_as="relay-kit")
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    raise SystemExit(main())
