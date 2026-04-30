#!/usr/bin/env python3
"""Public Relay-kit installer CLI.

This wrapper exposes a friendlier command surface:
  relay-kit init <project_path> --codex|--claude|--antigravity --baseline
  relay-kit <project_path> --codex|--claude|--antigravity
  relay-kit doctor <project_path>
  relay-kit eval run <project_path>
  relay-kit upgrade check <project_path>
  relay-kit policy check <project_path>
  relay-kit support bundle <project_path>
  relay-kit support request <project_path>
  relay-kit readiness check <project_path>
  relay-kit release verify <project_path>
  relay-kit publish plan <project_path>
  relay-kit publish evidence <project_path>
  relay-kit publish trail <project_path>
  relay-kit pulse build <project_path>
  relay-kit signal export <project_path>
  relay-kit contract import <project_path> --contract-file <relay-contract.json>

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
from relay_kit_v3.bundle_manifest import verify_manifest_file, verify_trusted_manifest_file, write_manifest, write_trust_stamp
from relay_kit_v3.policy_packs import DEFAULT_POLICY_PACK, POLICY_PACKS
from relay_kit_v3.pulse import build_pulse_report, write_pulse_report
from relay_kit_v3.publication import (
    build_publication_evidence,
    build_publication_plan,
    build_publication_trail,
    render_publication_evidence,
    render_publication_plan,
    render_publication_trail,
    write_publication_evidence,
    write_publication_plan,
    write_publication_trail,
    write_publication_trail_markdown,
)
from relay_kit_v3.release_lane import build_release_lane_report, render_release_lane_report, write_release_lane_report
from relay_kit_v3.readiness import build_readiness_report, render_readiness_report
from relay_kit_v3.signal_export import build_signal_export, write_signal_export
from relay_kit_v3.contract_export import write_contract_export
from relay_kit_v3.contract_import import import_contracts, render_contract_import_report
from relay_kit_v3.support_bundle import build_support_bundle, write_support_bundle
from relay_kit_v3.support_request import build_support_request, render_support_request, write_support_request
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
    parser.add_argument(
        "--policy-pack",
        choices=sorted(POLICY_PACKS),
        default=DEFAULT_POLICY_PACK,
        help="Policy pack passed to policy guard",
    )
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


def _parse_contract_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit contract",
        description="Export and import Relay-kit planning and QA contracts as machine-readable contract JSON.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    export = subparsers.add_parser("export", help="Export Relay-kit contracts to JSON")
    export.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    export.add_argument(
        "--output-file",
        default=None,
        help="Output path (default: <project>/.relay-kit/contract-sync/relay-contract.json)",
    )
    import_cmd = subparsers.add_parser("import", help="Plan or apply Relay contract JSON into contracts")
    import_cmd.add_argument("project_path", nargs="?", default=".", help="Project root to update")
    import_cmd.add_argument(
        "--contract-file",
        default=None,
        help="Input contract JSON path (default: <project>/.relay-kit/contract-sync/relay-contract.json)",
    )
    import_cmd.add_argument("--apply", action="store_true", help="Write contract updates instead of dry-running")
    import_cmd.add_argument("--force", action="store_true", help="Overwrite concrete existing contract sections")
    import_cmd.add_argument("--strict", action="store_true", help="Return non-zero on invalid contract JSON or skipped conflicts")
    import_cmd.add_argument("--json", action="store_true", help="Emit machine-readable import report")
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
    stamp = subparsers.add_parser("stamp", help="Write deterministic trust metadata for a manifest")
    stamp.add_argument("project_path", nargs="?", default=".", help="Project root for default manifest/trust paths")
    stamp.add_argument(
        "--manifest-file",
        default=None,
        help="Manifest path (default: <project>/.relay-kit/manifest/bundles.json)",
    )
    stamp.add_argument(
        "--trust-file",
        default=None,
        help="Trust metadata path (default: <project>/.relay-kit/manifest/trust.json)",
    )
    stamp.add_argument("--issuer", default="local", help="Trust stamp issuer label")
    stamp.add_argument("--channel", default="local", help="Release channel label")
    verify = subparsers.add_parser("verify", help="Verify a checksummed bundle manifest")
    verify.add_argument("project_path", nargs="?", default=".", help="Project root for default manifest lookup")
    verify.add_argument(
        "--manifest-file",
        default=None,
        help="Manifest path (default: <project>/.relay-kit/manifest/bundles.json)",
    )
    verify.add_argument(
        "--trust-file",
        default=None,
        help="Trust metadata path (default: beside manifest as trust.json)",
    )
    verify.add_argument("--trusted", action="store_true", help="Require deterministic trust metadata")
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
    run.add_argument("--baseline-file", default=None, help="Optional prior workflow eval JSON used for regression checks")
    run.add_argument("--min-pass-rate", type=float, default=None, help="Minimum accepted scenario pass rate")
    run.add_argument("--min-route-margin", type=int, default=None, help="Minimum top-route score margin")
    run.add_argument("--min-evidence-coverage", type=float, default=None, help="Minimum expected-term coverage")
    run.add_argument("--min-scenarios", type=int, default=None, help="Minimum scenario count")
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


def _parse_policy_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit policy",
        description="Inspect and run Relay-kit policy guard packs.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    subparsers.add_parser("list", help="List available policy packs")

    check = subparsers.add_parser("check", help="Run policy guard with a named pack")
    check.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    check.add_argument("--pack", choices=sorted(POLICY_PACKS), default=DEFAULT_POLICY_PACK)
    check.add_argument("--strict", action="store_true", help="Return non-zero when findings exist")
    check.add_argument("--json", action="store_true", help="Emit JSON report")
    return parser.parse_args(argv)


def _parse_support_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit support",
        description="Prepare Relay-kit support diagnostics.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    bundle = subparsers.add_parser("bundle", help="Write a support diagnostic JSON bundle")
    bundle.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    bundle.add_argument(
        "--policy-pack",
        choices=sorted(POLICY_PACKS),
        default=DEFAULT_POLICY_PACK,
        help="Policy pack used for support diagnostics",
    )
    bundle.add_argument("--output-file", default=None, help="Output path (default: <project>/.relay-kit/support/support-bundle.json)")
    bundle.add_argument("--evidence-limit", type=int, default=20, help="Recent evidence ledger events to include")
    bundle.add_argument("--json", action="store_true", help="Emit bundle payload and output path as JSON")
    request = subparsers.add_parser("request", help="Write and validate a support request intake JSON")
    request.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    request.add_argument("--severity", choices=["P0", "P1", "P2", "P3"], default=None)
    request.add_argument("--summary", default=None, help="One sentence describing the blocked workflow")
    request.add_argument("--package-version", default=None, help="Relay-kit package version")
    request.add_argument("--os", dest="operating_system", default=None, help="Operating system")
    request.add_argument("--shell", default=None, help="Shell used for failing commands")
    request.add_argument("--bundle", dest="installed_bundle", default=None, help="Installed Relay-kit bundle")
    request.add_argument("--adapter", dest="adapter_target", default=None, help="Adapter target such as codex or claude")
    request.add_argument("--policy-pack", default=None, help="Policy pack used for diagnostics")
    request.add_argument("--expected", dest="expected_behavior", default=None, help="Expected behavior")
    request.add_argument("--actual", dest="actual_behavior", default=None, help="Actual behavior")
    request.add_argument("--recent-changes", default=None, help="Recent Relay-kit or runtime changes")
    request.add_argument("--workaround", default=None, help="Current workaround, if any")
    request.add_argument(
        "--diagnostic-file",
        action="append",
        default=None,
        help="Diagnostic file to attach. Repeat for multiple files.",
    )
    request.add_argument(
        "--output-file",
        default=None,
        help="Output path (default: <project>/.relay-kit/support/support-request.json)",
    )
    request.add_argument("--strict", action="store_true", help="Return non-zero unless the support request is ready")
    request.add_argument("--json", action="store_true", help="Emit machine-readable support request")
    return parser.parse_args(argv)


def _parse_readiness_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit readiness",
        description="Run the commercial readiness gate suite.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    check = subparsers.add_parser("check", help="Check whether Relay-kit is ready for paid/team use")
    check.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    check.add_argument("--profile", choices=["team", "enterprise"], default="enterprise")
    check.add_argument("--skip-tests", action="store_true", help="Skip pytest inside the readiness suite")
    check.add_argument("--json", action="store_true", help="Emit machine-readable readiness report")
    return parser.parse_args(argv)


def _parse_release_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit release",
        description="Verify local release-lane prerequisites for Relay-kit.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    verify = subparsers.add_parser("verify", help="Verify local release-lane prerequisites")
    verify.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    verify.add_argument("--require-clean", action="store_true", help="Fail when the git worktree is dirty")
    verify.add_argument("--output-file", default=None, help="Optional JSON report output path")
    verify.add_argument("--json", action="store_true", help="Emit machine-readable release-lane report")
    return parser.parse_args(argv)


def _parse_publish_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit publish",
        description="Plan and record package publication evidence without uploading artifacts.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    plan = subparsers.add_parser("plan", help="Check package publication prerequisites")
    plan.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    plan.add_argument("--channel", choices=["pypi", "testpypi", "internal"], default="pypi")
    plan.add_argument("--target-version", default=None, help="Expected package version")
    plan.add_argument("--dist-dir", default=None, help="Distribution artifact directory (default: <project>/dist)")
    plan.add_argument("--ci-url", default=None, help="Remote CI evidence URL")
    plan.add_argument("--release-url", default=None, help="GitHub release or release-note URL")
    plan.add_argument("--package-url", default=None, help="Package index evidence URL")
    plan.add_argument("--allow-dev", action="store_true", help="Allow dev/local versions on the selected channel")
    plan.add_argument("--output-file", default=None, help="Optional JSON report output path")
    plan.add_argument("--strict", action="store_true", help="Return non-zero unless the publication plan is ready")
    plan.add_argument("--json", action="store_true", help="Emit machine-readable publication plan")

    evidence = subparsers.add_parser("evidence", help="Record package publication execution evidence")
    evidence.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    evidence.add_argument("--channel", choices=["pypi", "testpypi", "internal"], default="pypi")
    evidence.add_argument("--dist-dir", default=None, help="Distribution artifact directory (default: <project>/dist)")
    evidence.add_argument("--ci-url", default=None, help="Remote CI evidence URL")
    evidence.add_argument("--release-url", default=None, help="GitHub release or release-note URL")
    evidence.add_argument("--package-url", default=None, help="Package index evidence URL")
    evidence.add_argument("--twine-check-file", default=None, help="Captured output from python -m twine check dist/*")
    evidence.add_argument("--upload-log-file", default=None, help="Captured package upload log or package-index confirmation")
    evidence.add_argument("--publication-plan-file", default=None, help="Optional publication-plan JSON to bind to this evidence")
    evidence.add_argument("--allow-dev", action="store_true", help="Allow dev/local versions on the selected channel")
    evidence.add_argument(
        "--output-file",
        default=None,
        help="JSON report output path (default: <project>/.relay-kit/release/publication-evidence.json)",
    )
    evidence.add_argument("--strict", action="store_true", help="Return non-zero unless publication evidence is complete")
    evidence.add_argument("--json", action="store_true", help="Emit machine-readable publication evidence")

    trail = subparsers.add_parser("trail", help="Write a publication execution trail with capture commands")
    trail.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    trail.add_argument("--channel", choices=["pypi", "testpypi", "internal"], default="pypi")
    trail.add_argument("--target-version", default=None, help="Expected package version")
    trail.add_argument("--dist-dir", default=None, help="Distribution artifact directory (default: <project>/dist)")
    trail.add_argument(
        "--evidence-dir",
        default=None,
        help="Directory for captured twine/upload logs (default: <project>/.tmp/relay-publication/<version>)",
    )
    trail.add_argument("--ci-url", default=None, help="Remote CI evidence URL")
    trail.add_argument("--release-url", default=None, help="GitHub release or release-note URL")
    trail.add_argument("--package-url", default=None, help="Package index evidence URL")
    trail.add_argument("--shell", choices=["powershell", "bash"], default="powershell")
    trail.add_argument("--allow-dev", action="store_true", help="Allow dev/local versions on the selected channel")
    trail.add_argument(
        "--output-file",
        default=None,
        help="JSON trail output path (default: <project>/.relay-kit/release/publication-trail.json)",
    )
    trail.add_argument(
        "--markdown-file",
        default=None,
        help="Markdown trail output path (default: <project>/.relay-kit/release/publication-trail.md)",
    )
    trail.add_argument("--strict", action="store_true", help="Return non-zero unless the publication trail is ready")
    trail.add_argument("--json", action="store_true", help="Emit machine-readable publication trail")
    return parser.parse_args(argv)


def _parse_pulse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit pulse",
        description="Build a static Relay-kit Pulse report from quality, readiness, and evidence signals.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    build = subparsers.add_parser("build", help="Write Pulse JSON and HTML reports")
    build.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    build.add_argument("--output-dir", default=None, help="Output directory (default: <project>/.relay-kit/pulse)")
    build.add_argument("--profile", choices=["team", "enterprise"], default="enterprise")
    build.add_argument("--include-readiness", action="store_true", help="Run readiness check with --skip-tests")
    build.add_argument("--include-publication", action="store_true", help="Run no-upload publication plan and include it")
    build.add_argument("--readiness-file", default=None, help="Existing readiness JSON report to include")
    build.add_argument("--publication-file", default=None, help="Existing publication plan JSON report to include")
    build.add_argument("--workflow-eval-file", default=None, help="Existing workflow eval JSON report to include")
    build.add_argument("--evidence-limit", type=int, default=20, help="Recent evidence events to include")
    build.add_argument("--history-limit", type=int, default=20, help="Historical Pulse snapshots to include")
    build.add_argument("--no-history", action="store_true", help="Do not append this run to Pulse history")
    build.add_argument("--json", action="store_true", help="Emit machine-readable output paths and report")
    return parser.parse_args(argv)


def _parse_signal_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit signal",
        description="Export Relay-kit Pulse and evidence signals as local telemetry artifacts.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    export = subparsers.add_parser("export", help="Write Relay signal JSON, JSONL, and optional OTLP JSON")
    export.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    export.add_argument("--pulse-file", default=None, help="Pulse report JSON file")
    export.add_argument("--output-dir", default=None, help="Output directory (default: <project>/.relay-kit/signals)")
    export.add_argument("--event-limit", type=int, default=50, help="Recent evidence events to export")
    export.add_argument("--otlp", action="store_true", help="Also write Relay OTLP-compatible JSON")
    export.add_argument("--json", action="store_true", help="Emit machine-readable output paths and export payload")
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


def _doctor_commands(project_path: str, skip_tests: bool, policy_pack: str = DEFAULT_POLICY_PACK) -> list[tuple[str, list[str]]]:
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
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "policy_guard.py"),
                project_path,
                "--strict",
                "--pack",
                policy_pack,
            ],
        ),
    ]

    if policy_pack == "enterprise":
        commands.append(
            (
                "trusted manifest",
                [
                    sys.executable,
                    str(REPO_ROOT / "relay_kit_public_cli.py"),
                    "manifest",
                    "verify",
                    project_path,
                    "--trusted",
                ],
            )
        )

    commands.extend(
        [
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
    )

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
    for label, command in _doctor_commands(project_path, args.skip_tests, args.policy_pack):
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


def run_contract(args: argparse.Namespace) -> int:
    if args.action == "export":
        output_path = write_contract_export(args.project_path, args.output_file)
        print(f"Wrote {output_path}")
        return 0
    if args.action == "import":
        report = import_contracts(
            args.project_path,
            contract_file=args.contract_file,
            apply=args.apply,
            force=args.force,
        )
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_contract_import_report(report))
        if args.strict and report["status"] != "pass":
            return 2
        return 2 if report["status"] == "fail" else 0
    return 2


def run_manifest(args: argparse.Namespace) -> int:
    if args.action == "write":
        output_path = write_manifest(args.project_path, args.output_file)
        print(f"Wrote {output_path}")
        return 0
    if args.action == "stamp":
        try:
            output_path = write_trust_stamp(
                args.project_path,
                manifest_file=args.manifest_file,
                trust_file=args.trust_file,
                issuer=args.issuer,
                channel=args.channel,
            )
        except ValueError as exc:
            print(f"Manifest trust stamp failed: {exc}")
            return 2
        print(f"Wrote {output_path}")
        return 0
    if args.action == "verify":
        manifest_path = Path(args.manifest_file) if args.manifest_file else Path(args.project_path) / ".relay-kit" / "manifest" / "bundles.json"
        result = (
            verify_trusted_manifest_file(manifest_path, args.trust_file)
            if args.trusted
            else verify_manifest_file(manifest_path)
        )
        if result.ok:
            print("Trust verification passed." if args.trusted else "Manifest verification passed.")
            return 0
        print("Trust verification failed." if args.trusted else "Manifest verification failed.")
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
    if args.baseline_file:
        eval_argv.extend(["--baseline-file", args.baseline_file])
    if args.min_pass_rate is not None:
        eval_argv.extend(["--min-pass-rate", str(args.min_pass_rate)])
    if args.min_route_margin is not None:
        eval_argv.extend(["--min-route-margin", str(args.min_route_margin)])
    if args.min_evidence_coverage is not None:
        eval_argv.extend(["--min-evidence-coverage", str(args.min_evidence_coverage)])
    if args.min_scenarios is not None:
        eval_argv.extend(["--min-scenarios", str(args.min_scenarios)])
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


def run_policy(args: argparse.Namespace) -> int:
    if args.action == "list":
        print("Relay-kit policy packs")
        for name, pack in sorted(POLICY_PACKS.items()):
            print(f"- {name}: {pack.description}")
        return 0
    if args.action == "check":
        from scripts import policy_guard

        policy_argv = [args.project_path, "--pack", args.pack]
        if args.strict:
            policy_argv.append("--strict")
        if args.json:
            policy_argv.append("--json")
        return policy_guard.main(policy_argv)
    return 2


def run_support(args: argparse.Namespace) -> int:
    if args.action == "bundle":
        output_path = write_support_bundle(
            args.project_path,
            policy_pack=args.policy_pack,
            output_file=args.output_file,
            evidence_limit=args.evidence_limit,
        )
        if args.json:
            payload = {
                "output_file": str(output_path),
                "bundle": build_support_bundle(
                    args.project_path,
                    policy_pack=args.policy_pack,
                    evidence_limit=args.evidence_limit,
                ),
            }
            print(json.dumps(payload, ensure_ascii=True, indent=2))
            return 0
        print(f"Wrote {output_path}")
        return 0
    if args.action == "request":
        report = build_support_request(
            args.project_path,
            severity=args.severity,
            summary=args.summary,
            package_version=args.package_version,
            operating_system=args.operating_system,
            shell=args.shell,
            installed_bundle=args.installed_bundle,
            adapter_target=args.adapter_target,
            policy_pack=args.policy_pack,
            expected_behavior=args.expected_behavior,
            actual_behavior=args.actual_behavior,
            recent_changes=args.recent_changes,
            workaround=args.workaround,
            diagnostic_files=args.diagnostic_file,
        )
        output_path = write_support_request(args.project_path, report, output_file=args.output_file)
        if args.json:
            print(
                json.dumps(
                    {
                        "output_file": str(output_path),
                        "request": report,
                    },
                    ensure_ascii=True,
                    indent=2,
                )
            )
        else:
            print(render_support_request(report))
            print(f"Wrote {output_path}")
        if args.strict and report["status"] != "ready":
            return 2
        return 0
    return 2


def run_readiness(args: argparse.Namespace) -> int:
    if args.action != "check":
        return 2
    report = build_readiness_report(args.project_path, profile=args.profile, skip_tests=args.skip_tests)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_readiness_report(report))
    return 0 if report["status"] == "pass" else 2


def run_release(args: argparse.Namespace) -> int:
    if args.action != "verify":
        return 2
    report = build_release_lane_report(args.project_path, require_clean=args.require_clean)
    if args.output_file:
        write_release_lane_report(args.project_path, report, output_file=args.output_file)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_release_lane_report(report))
    return 0 if report["status"] == "pass" else 2


def run_publish(args: argparse.Namespace) -> int:
    if args.action == "plan":
        report = build_publication_plan(
            args.project_path,
            channel=args.channel,
            target_version=args.target_version,
            dist_dir=args.dist_dir,
            ci_url=args.ci_url,
            release_url=args.release_url,
            package_url=args.package_url,
            allow_dev=args.allow_dev,
        )
        if args.output_file:
            write_publication_plan(args.project_path, report, output_file=args.output_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_publication_plan(report))
        if args.strict and report["status"] != "ready":
            return 2
        return 0
    if args.action == "evidence":
        report = build_publication_evidence(
            args.project_path,
            channel=args.channel,
            dist_dir=args.dist_dir,
            ci_url=args.ci_url,
            release_url=args.release_url,
            package_url=args.package_url,
            twine_check_file=args.twine_check_file,
            upload_log_file=args.upload_log_file,
            publication_plan_file=args.publication_plan_file,
            allow_dev=args.allow_dev,
        )
        output_path = write_publication_evidence(args.project_path, report, output_file=args.output_file)
        if args.json:
            print(
                json.dumps(
                    {
                        "output_file": str(output_path),
                        "evidence": report,
                    },
                    ensure_ascii=True,
                    indent=2,
                )
            )
        else:
            print(render_publication_evidence(report))
            print(f"Wrote {output_path}")
        if args.strict and report["status"] != "published":
            return 2
        return 0
    if args.action == "trail":
        report = build_publication_trail(
            args.project_path,
            channel=args.channel,
            target_version=args.target_version,
            dist_dir=args.dist_dir,
            evidence_dir=args.evidence_dir,
            ci_url=args.ci_url,
            release_url=args.release_url,
            package_url=args.package_url,
            shell=args.shell,
            allow_dev=args.allow_dev,
        )
        output_path = write_publication_trail(args.project_path, report, output_file=args.output_file)
        markdown_path = write_publication_trail_markdown(args.project_path, report, output_file=args.markdown_file)
        if args.json:
            print(
                json.dumps(
                    {
                        "output_file": str(output_path),
                        "markdown_file": str(markdown_path),
                        "trail": report,
                    },
                    ensure_ascii=True,
                    indent=2,
                )
            )
        else:
            print(render_publication_trail(report))
            print(f"Wrote {output_path}")
            print(f"Wrote {markdown_path}")
        if args.strict and report["status"] != "ready":
            return 2
        return 0
    return 2


def run_pulse(args: argparse.Namespace) -> int:
    if args.action != "build":
        return 2
    report = build_pulse_report(
        args.project_path,
        profile=args.profile,
        evidence_limit=args.evidence_limit,
        include_readiness=args.include_readiness,
        include_publication=args.include_publication,
        workflow_eval_file=args.workflow_eval_file,
        readiness_file=args.readiness_file,
        publication_file=args.publication_file,
        output_dir=args.output_dir,
        history_limit=args.history_limit,
    )
    outputs = write_pulse_report(
        args.project_path,
        report,
        output_dir=args.output_dir,
        record_history=not args.no_history,
    )
    if args.json:
        payload = {
            "outputs": {name: str(path) for name, path in outputs.items()},
            "report": report,
        }
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print(f"Wrote {outputs['json']}")
        print(f"Wrote {outputs['html']}")
        print(f"Pulse status: {report['status']}")
        print(f"Pulse score: {report['pulse_score']}")
    return 0 if report["status"] in {"pass", "attention"} else 2


def run_signal(args: argparse.Namespace) -> int:
    if args.action != "export":
        return 2
    payload = build_signal_export(
        args.project_path,
        pulse_file=args.pulse_file,
        event_limit=args.event_limit,
    )
    outputs = write_signal_export(args.project_path, payload, output_dir=args.output_dir, include_otlp=args.otlp)
    if args.json:
        print(
            json.dumps(
                {
                    "outputs": {name: str(path) for name, path in outputs.items()},
                    "export": payload,
                },
                ensure_ascii=True,
                indent=2,
            )
        )
    else:
        print(f"Wrote {outputs['json']}")
        print(f"Wrote {outputs['jsonl']}")
        if "otlp" in outputs:
            print(f"Wrote {outputs['otlp']}")
        print(f"Signals: {payload['summary']['signal_count']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    raw_argv = sys.argv[1:] if argv is None else argv
    if raw_argv and raw_argv[0] == "doctor":
        return run_doctor(_parse_doctor_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "evidence":
        return run_evidence(_parse_evidence_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "contract":
        return run_contract(_parse_contract_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "manifest":
        return run_manifest(_parse_manifest_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "eval":
        return run_eval(_parse_eval_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "upgrade":
        return run_upgrade(_parse_upgrade_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "policy":
        return run_policy(_parse_policy_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "support":
        return run_support(_parse_support_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "readiness":
        return run_readiness(_parse_readiness_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "release":
        return run_release(_parse_release_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "publish":
        return run_publish(_parse_publish_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "pulse":
        return run_pulse(_parse_pulse_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "signal":
        return run_signal(_parse_signal_args(raw_argv[1:]))
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
