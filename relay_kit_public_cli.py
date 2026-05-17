#!/usr/bin/env python3
"""Public Relay-kit installer CLI.

This wrapper exposes a friendlier command surface:
  relay-kit init <project_path> --codex|--claude|--antigravity
  relay-kit <project_path> --codex|--claude|--antigravity
  relay-kit doctor <project_path>
  relay-kit eval run <project_path>
  relay-kit upgrade check <project_path>
  relay-kit policy check <project_path>
  relay-kit support bundle <project_path>
  relay-kit support request <project_path>
  relay-kit support triage <project_path>
  relay-kit support soak <project_path>
  relay-kit readiness check <project_path>
  relay-kit release verify <project_path>
  relay-kit publish plan <project_path>
  relay-kit publish evidence <project_path>
  relay-kit publish trail <project_path>
  relay-kit publish status <project_path>
  relay-kit publish index-check <project_path>
  relay-kit commercial dossier <project_path>
  relay-kit pulse build <project_path>
  relay-kit signal export <project_path>
  relay-kit contract import <project_path> --contract-file <relay-contract.json>
  relay-kit context audit <project_path>
  relay-kit context index <project_path>
  relay-kit context search <project_path> --query "..."
  relay-kit context related <project_path> --path src/auth/login.ts
  relay-kit context budget <project_path>
  relay-kit context pack <project_path>
  relay-kit token audit <project_path>
  relay-kit shell compact <project_path> -- <command...>
  relay-kit eval real-world <project_path>
  relay-kit proof audit <project_path>
  relay-kit locale show <project_path>
  relay-kit locale set <project_path> --locale <code>
  relay-kit lane audit <project_path>
  relay-kit adapter diagnose <project_path>
  relay-kit command list <project_path>
  relay-kit command diagnose <project_path>
  relay-kit agent list <project_path>
  relay-kit agent diagnose <project_path>
  relay-kit query search <project_path> --query "..."
  relay-kit prompt enhance <project_path> --prompt "..."
  relay-kit service boundaries <project_path>
  relay-kit runtime doctor <project_path>
  relay-kit skill gauntlet <project_path>
  relay-kit impact radar <project_path>
  relay-kit accessibility review <project_path>
  relay-kit release readiness <project_path>
  relay-kit continuity checkpoint <project_path>
  relay-kit migration guard <project_path>

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
from relay_kit_v3.commercial_dossier import (
    build_commercial_dossier,
    render_commercial_dossier,
    write_commercial_dossier,
)
from relay_kit_v3.publication import (
    build_package_index_check,
    build_publication_evidence,
    build_publication_plan,
    build_publication_trail,
    build_publication_trail_status,
    render_package_index_check,
    render_publication_evidence,
    render_publication_plan,
    render_publication_trail,
    render_publication_trail_status,
    write_package_index_check,
    write_publication_evidence,
    write_publication_plan,
    write_publication_trail,
    write_publication_trail_markdown,
)
from relay_kit_v3.release_lane import build_release_lane_report, render_release_lane_report, write_release_lane_report
from relay_kit_v3.readiness import build_readiness_report, render_readiness_report
from relay_kit_v3.signal_export import build_signal_export, write_signal_export
from relay_kit_v3.token_economy import (
    DEFAULT_MAX_TOKENS,
    build_context_budget,
    build_context_pack,
    build_token_audit,
    render_context_budget,
    render_context_pack,
    render_token_audit,
    write_context_budget,
    write_context_pack,
    write_token_audit,
)
from relay_kit_v3.shell_compaction import ShellCompactionError, run_compacted_command
from relay_kit_v3.real_world_eval import (
    build_report as build_real_world_eval_report,
    render_report as render_real_world_eval_report,
    write_report as write_real_world_eval_report,
)
from relay_kit_v3.skill_proof import (
    build_report as build_skill_proof_report,
    render_report as render_skill_proof_report,
    write_report as write_skill_proof_report,
)
from relay_kit_v3.contract_export import write_contract_export
from relay_kit_v3.contract_import import import_contracts, render_contract_import_report
from relay_kit_v3.context_governance import build_context_audit, render_context_audit, write_context_audit
from relay_kit_v3.context_index import (
    build_context_index,
    build_context_related,
    build_context_search,
    render_context_index,
    render_context_related,
    render_context_search,
    write_context_index,
)
from relay_kit_v3.lane_audit import build_lane_audit, render_lane_audit, write_lane_audit
from relay_kit_v3.adapter_diagnostics import (
    build_adapter_diagnostics,
    render_adapter_diagnostics,
    write_adapter_diagnostics,
)
from relay_kit_v3.agent_profiles import (
    agent_profile_records,
    build_agent_diagnostics,
    render_agent_diagnostics,
    write_agent_diagnostics,
)
from relay_kit_v3.command_registry import (
    build_command_diagnostics,
    lifecycle_command_records,
    render_command_diagnostics,
    write_command_diagnostics,
)
from relay_kit_v3.intent_enhancer import (
    build_prompt_enhancement,
    render_prompt_enhancement,
    write_prompt_enhancement,
)
from relay_kit_v3.query_search import build_query_search, render_query_search, write_query_search
from relay_kit_v3.runtime_locale import (
    inspect_runtime_locale,
    load_runtime_locale,
    write_runtime_locale,
)
from relay_kit_v3.service_boundaries import (
    build_service_boundary_report,
    render_service_boundary_report,
    write_service_boundary_report,
)
from relay_kit_v3.support_bundle import build_support_bundle, write_support_bundle
from relay_kit_v3.support_request import build_support_request, render_support_request, write_support_request
from relay_kit_v3.support_triage import (
    build_support_soak_report,
    build_support_triage,
    render_support_soak_report,
    render_support_triage,
)
from relay_kit_v3.upgrade import build_upgrade_report, render_report, write_version_marker


REPO_ROOT = Path(__file__).resolve().parent


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit",
        description="Public Relay-kit installer for full runtime generation.",
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

    parser.add_argument("--bundle", default="enterprise", help="Bundle name (default: enterprise)")
    parser.add_argument(
        "--baseline",
        dest="bundle",
        action="store_const",
        const="baseline",
        help="Generate the smaller baseline bundle instead of the default enterprise bundle",
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
    parser.add_argument("--locale", help="Set runtime locale profile during init/install (allowed: vi, en)")
    parser.add_argument("--fallback-locale", help="Set runtime fallback locale during init/install (default: en)")

    parser.add_argument("--list-skills", action="store_true", help="List active runtime bundles")
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


def _parse_context_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit context",
        description="Audit Relay-kit context governance and build a local no-API context graph.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    audit = subparsers.add_parser("audit", help="Audit source freshness and authority")
    audit.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    audit.add_argument("--stale-days", type=int, default=30, help="Age threshold for stale sources")
    audit.add_argument("--output-file", default=None, help="Optional context audit JSON output path")
    audit.add_argument("--strict", action="store_true", help="Return non-zero unless context audit passes")
    audit.add_argument("--json", action="store_true", help="Emit machine-readable context audit")

    index = subparsers.add_parser("index", help="Build a local file, symbol, import, test, and docs index")
    index.add_argument("project_path", nargs="?", default=".", help="Project root to index")
    index.add_argument(
        "--output-file",
        default=None,
        help="Optional index JSON output path (default: <project>/.relay-kit/context/index.json)",
    )
    index.add_argument("--json", action="store_true", help="Emit machine-readable context index summary")

    search = subparsers.add_parser("search", help="Search the local context graph")
    search.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    search.add_argument("--query", required=True, help="Query text")
    search.add_argument("--limit", type=int, default=10, help="Maximum result count")
    search.add_argument("--index-file", default=None, help="Optional context index JSON path")
    search.add_argument("--json", action="store_true", help="Emit machine-readable search results")

    related = subparsers.add_parser("related", help="Find files related to a path in the local context graph")
    related.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    related.add_argument("--path", required=True, help="Source path to inspect")
    related.add_argument("--limit", type=int, default=10, help="Maximum related file count")
    related.add_argument("--index-file", default=None, help="Optional context index JSON path")
    related.add_argument("--json", action="store_true", help="Emit machine-readable related-file results")

    budget = subparsers.add_parser("budget", help="Estimate token budget and compression safety")
    budget.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    budget.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS, help="Token budget ceiling")
    budget.add_argument("--query", default=None, help="Optional query text to focus context budget sources")
    budget.add_argument(
        "--scope",
        action="append",
        choices=["state", "contracts", "docs", "evidence", "registry"],
        help="Limit source scopes; defaults to all scopes",
    )
    budget.add_argument("--stale-days", type=int, default=30, help="Age threshold for stale sources")
    budget.add_argument("--output-file", default=None, help="Optional context budget JSON output path")
    budget.add_argument("--strict", action="store_true", help="Return non-zero unless budget and retention pass")
    budget.add_argument("--json", action="store_true", help="Emit machine-readable context budget")

    pack = subparsers.add_parser("pack", help="Build task-scoped context pack within token budget")
    pack.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    pack.add_argument("--task", required=True, help="Task text used to rank relevant context sources")
    pack.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS, help="Token budget ceiling")
    pack.add_argument(
        "--scope",
        action="append",
        choices=["state", "contracts", "docs", "evidence", "registry"],
        help="Limit source scopes; defaults to all scopes",
    )
    pack.add_argument("--stale-days", type=int, default=30, help="Age threshold for stale sources")
    pack.add_argument("--output-file", default=None, help="Optional context pack JSON output path")
    pack.add_argument("--strict", action="store_true", help="Return non-zero unless budget and retention pass")
    pack.add_argument("--json", action="store_true", help="Emit machine-readable context pack")
    return parser.parse_args(argv)


def _parse_lane_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit lane",
        description="Audit Relay-kit multi-lane coordination state.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    audit = subparsers.add_parser("audit", help="Audit lane locks, dependencies, waves, and handoffs")
    audit.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    audit.add_argument("--output-file", default=None, help="Optional lane audit JSON output path")
    audit.add_argument("--strict", action="store_true", help="Return non-zero unless lane audit passes")
    audit.add_argument("--json", action="store_true", help="Emit machine-readable lane audit")
    return parser.parse_args(argv)


def _parse_locale_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit locale",
        description="Read or update Relay-kit global runtime locale policy.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)

    show = subparsers.add_parser("show", help="Show the current runtime locale policy")
    show.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    show.add_argument("--json", action="store_true", help="Emit machine-readable locale policy")

    set_cmd = subparsers.add_parser("set", help="Set runtime locale policy with one global switch")
    set_cmd.add_argument("project_path", nargs="?", default=".", help="Project root to update")
    set_cmd.add_argument("--locale", required=True, help="Primary locale profile (allowed: vi, en)")
    set_cmd.add_argument("--fallback-locale", default=None, help="Fallback locale profile (default unchanged)")
    set_cmd.add_argument(
        "--enforce-output-language",
        dest="enforce_output_language",
        action="store_true",
        help="Enforce output language according to locale profile (default on).",
    )
    set_cmd.add_argument(
        "--no-enforce-output-language",
        dest="enforce_output_language",
        action="store_false",
        help="Allow mixed-language output when explicitly needed.",
    )
    set_cmd.set_defaults(enforce_output_language=None)
    set_cmd.add_argument("--json", action="store_true", help="Emit machine-readable locale policy")
    return parser.parse_args(argv)


def _parse_token_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit token",
        description="Audit token-economy metrics for context budget and compression safety.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    audit = subparsers.add_parser("audit", help="Run token-economy audit")
    audit.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    audit.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS, help="Token budget ceiling")
    audit.add_argument(
        "--scope",
        action="append",
        choices=["state", "contracts", "docs", "evidence", "registry"],
        help="Limit source scopes; defaults to all scopes",
    )
    audit.add_argument("--stale-days", type=int, default=30, help="Age threshold for stale sources")
    audit.add_argument("--output-file", default=None, help="Optional token audit JSON output path")
    audit.add_argument("--strict", action="store_true", help="Return non-zero unless budget and retention pass")
    audit.add_argument("--json", action="store_true", help="Emit machine-readable token audit")
    return parser.parse_args(argv)


def _parse_shell_args(argv: list[str]) -> argparse.Namespace:
    command: list[str] = []
    parse_argv = list(argv)
    if "--" in parse_argv:
        separator = parse_argv.index("--")
        command = parse_argv[separator + 1 :]
        parse_argv = parse_argv[:separator]
    parser = argparse.ArgumentParser(
        prog="relay-kit shell",
        description="Run shell commands through Relay-kit raw-log preserving compaction.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    compact = subparsers.add_parser("compact", help="Run a command and compact its shell output")
    compact.add_argument("project_path", nargs="?", default=".", help="Project root used for raw evidence logs")
    compact.add_argument("--cwd", default=None, help="Working directory for the command; defaults to project root")
    compact.add_argument("--timeout", type=float, default=None, help="Optional command timeout in seconds")
    compact.add_argument("--strict", action="store_true", help="Fail if compaction drops required signal")
    compact.add_argument("--json", action="store_true", help="Emit machine-readable compact shell report")
    parsed = parser.parse_args(parse_argv)
    parsed.command = command
    return parsed


def _parse_adapter_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit adapter",
        description="Diagnose Relay-kit adapter skill surfaces.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    diagnose = subparsers.add_parser("diagnose", help="Check adapter skill parity and metadata drift")
    diagnose.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    diagnose.add_argument(
        "--adapter",
        choices=["codex", "claude", "agent", "antigravity", "all"],
        default="all",
        help="Adapter surface to inspect",
    )
    diagnose.add_argument("--output-file", default=None, help="Optional adapter diagnostics JSON output path")
    diagnose.add_argument("--strict", action="store_true", help="Return non-zero unless diagnostics pass")
    diagnose.add_argument("--json", action="store_true", help="Emit machine-readable diagnostics")
    return parser.parse_args(argv)


def _parse_command_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit command",
        description="List and diagnose Relay-kit lifecycle command surfaces.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    list_cmd = subparsers.add_parser("list", help="List lifecycle commands and route targets")
    list_cmd.add_argument("project_path", nargs="?", default=".", help="Project root (reserved for CLI symmetry)")
    list_cmd.add_argument("--json", action="store_true", help="Emit machine-readable lifecycle command list")

    diagnose = subparsers.add_parser("diagnose", help="Check adapter lifecycle command parity")
    diagnose.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    diagnose.add_argument(
        "--adapter",
        choices=["codex", "claude", "agent", "antigravity", "all"],
        default="all",
        help="Adapter surface to inspect",
    )
    diagnose.add_argument("--output-file", default=None, help="Optional command diagnostics JSON output path")
    diagnose.add_argument("--strict", action="store_true", help="Return non-zero unless command parity passes")
    diagnose.add_argument("--json", action="store_true", help="Emit machine-readable command diagnostics")
    return parser.parse_args(argv)


def _parse_agent_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit agent",
        description="List and diagnose Relay-kit role-based agent profiles.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    list_cmd = subparsers.add_parser("list", help="List Relay-kit agent profiles and route contracts")
    list_cmd.add_argument("project_path", nargs="?", default=".", help="Project root (reserved for CLI symmetry)")
    list_cmd.add_argument("--json", action="store_true", help="Emit machine-readable agent profile list")

    diagnose = subparsers.add_parser("diagnose", help="Check adapter agent profile parity and contract integrity")
    diagnose.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    diagnose.add_argument(
        "--adapter",
        choices=["codex", "claude", "agent", "antigravity", "all"],
        default="all",
        help="Adapter surface to inspect",
    )
    diagnose.add_argument("--output-file", default=None, help="Optional agent diagnostics JSON output path")
    diagnose.add_argument("--strict", action="store_true", help="Return non-zero unless agent diagnostics pass")
    diagnose.add_argument("--json", action="store_true", help="Emit machine-readable agent diagnostics")
    return parser.parse_args(argv)


def _parse_query_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit query",
        description="Search Relay-kit state, contracts, docs, evidence, and registry sources.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    search = subparsers.add_parser("search", help="Rank local Relay-kit sources for a query")
    search.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    search.add_argument("--query", required=True, help="Query text")
    search.add_argument(
        "--scope",
        action="append",
        choices=["state", "contracts", "docs", "evidence", "registry"],
        help="Limit search to one or more scopes; defaults to all scopes",
    )
    search.add_argument("--limit", type=int, default=10, help="Maximum result count")
    search.add_argument("--stale-days", type=int, default=30, help="Freshness threshold in days")
    search.add_argument("--output-file", default=None, help="Optional query search JSON output path")
    search.add_argument("--json", action="store_true", help="Emit machine-readable search results")
    return parser.parse_args(argv)


def _parse_prompt_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit prompt",
        description="Enhance short or ambiguous user prompts with Relay-kit skill context.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    enhance = subparsers.add_parser("enhance", help="Turn a short request into a skill-aware working prompt")
    enhance.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    enhance.add_argument("--prompt", required=True, help="User prompt to enhance")
    enhance.add_argument("--top-limit", type=int, default=5, help="Number of route candidates to include")
    enhance.add_argument("--output-file", default=None, help="Optional prompt enhancement JSON output path")
    enhance.add_argument("--json", action="store_true", help="Emit machine-readable prompt enhancement")
    return parser.parse_args(argv)


def _parse_service_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit service",
        description="Inspect Relay-kit service-boundary map and static dependency rules.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    boundaries = subparsers.add_parser("boundaries", help="Check service-boundary map and static import rules")
    boundaries.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    boundaries.add_argument("--output-file", default=None, help="Optional service-boundary JSON output path")
    boundaries.add_argument("--strict", action="store_true", help="Return non-zero when boundary findings exist")
    boundaries.add_argument("--json", action="store_true", help="Emit machine-readable boundary report")
    return parser.parse_args(argv)


def _parse_runtime_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit runtime",
        description="Run Relay-kit runtime diagnostics through portable public commands.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    doctor = subparsers.add_parser("doctor", help="Detect runtime drift in generated skill surfaces")
    doctor.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    doctor.add_argument("--state-mode", choices=["template", "live"], default="template")
    doctor.add_argument("--adapters", nargs="+", choices=["all", "claude", "agent", "codex"], default=["all"])
    doctor.add_argument("--strict", action="store_true", help="Return non-zero when findings exist")
    return parser.parse_args(argv)


def _parse_skill_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit skill",
        description="Run Relay-kit skill behavior gates through portable public commands.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    gauntlet = subparsers.add_parser("gauntlet", help="Run SKILL.md behavior regression checks")
    gauntlet.add_argument("project_path", nargs="?", default=".", help="Target project root")
    gauntlet.add_argument("--json", action="store_true", help="Emit JSON report")
    gauntlet.add_argument("--strict", action="store_true", help="Return non-zero when findings exist")
    gauntlet.add_argument("--semantic", action="store_true", help="Also check registry parity and routing scenarios")
    gauntlet.add_argument("--scenario-fixtures", default=None, help="Optional scenario fixture JSON path")
    return parser.parse_args(argv)


def _parse_impact_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit impact",
        description="Run Relay-kit blast-radius utilities through portable public commands.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    radar = subparsers.add_parser("radar", help="Generate a compact blast-radius report")
    radar.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    radar.add_argument("--base", default=None, help="Optional base ref for git diff")
    radar.add_argument("--head", default="HEAD", help="Head ref for git diff")
    radar.add_argument("--json", action="store_true", help="Emit JSON output")
    return parser.parse_args(argv)


def _parse_accessibility_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit accessibility",
        description="Run Relay-kit accessibility gates through portable public commands.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    review = subparsers.add_parser("review", help="Generate or evaluate an accessibility checklist")
    review.add_argument("project_path", nargs="?", default=".", help="Target project root")
    review.add_argument("--surface", default=None, help="Screen, flow, or surface under review")
    review.add_argument("--report-file", default=None, help="Optional checklist evidence file")
    review.add_argument("--output-file", default=None, help="Optional generated report output path")
    review.add_argument("--strict", action="store_true", help="Fail when evidence report is missing")
    review.add_argument("--json", action="store_true", help="Emit JSON output")
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

    real_world = subparsers.add_parser("real-world", help="Run production-shaped skill contract cases")
    real_world.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    real_world.add_argument("--cases-file", default=None, help="Optional real-world case fixture JSON")
    real_world.add_argument("--output-file", default=None, help="Optional JSON report output path")
    real_world.add_argument("--json", action="store_true", help="Emit JSON report")
    real_world.add_argument("--strict", action="store_true", help="Return non-zero unless all cases pass")
    return parser.parse_args(argv)


def _parse_proof_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit proof",
        description="Audit skill proof status across theoretical, validated, and field-tested levels.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    audit = subparsers.add_parser("audit", help="Classify canonical skills by proof level")
    audit.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    audit.add_argument("--workflow-fixture", default=None, help="Optional workflow scenario fixture JSON")
    audit.add_argument("--real-world-cases-file", default=None, help="Optional real-world skill case fixture JSON")
    audit.add_argument("--output-file", default=None, help="Optional JSON report output path")
    audit.add_argument("--strict", action="store_true", help="Return non-zero if any skill is theoretical")
    audit.add_argument("--json", action="store_true", help="Emit JSON report")
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
    mark.add_argument("--bundle", default="enterprise", help="Runtime bundle installed in the project (default: enterprise)")
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
    triage = subparsers.add_parser("triage", help="Inspect support request and bundle readiness for triage")
    triage.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    triage.add_argument(
        "--request-file",
        default=None,
        help="Support request JSON path (default: <project>/.relay-kit/support/support-request.json)",
    )
    triage.add_argument(
        "--bundle-file",
        default=None,
        help="Support bundle JSON path (default: <project>/.relay-kit/support/support-bundle.json)",
    )
    triage.add_argument("--strict", action="store_true", help="Return non-zero unless support triage is ready")
    triage.add_argument("--json", action="store_true", help="Emit machine-readable support triage")
    soak = subparsers.add_parser("soak", help="Run P0/P1/P2 support handoff soak fixtures")
    soak.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    soak.add_argument(
        "--bundle-file",
        default=None,
        help="Support bundle JSON path (default: <project>/.relay-kit/support/support-bundle.json)",
    )
    soak.add_argument("--strict", action="store_true", help="Return non-zero unless support soak passes")
    soak.add_argument("--json", action="store_true", help="Emit machine-readable support soak report")
    return parser.parse_args(argv)


def _parse_readiness_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit readiness",
        description="Run the local governance readiness gate suite.",
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
    readiness = subparsers.add_parser("readiness", help="Generate release readiness checklists and deploy signals")
    readiness.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    readiness.add_argument("--phase", choices=["pre", "post", "both"], default="both")
    readiness.add_argument("--signals-file", default=None, help="Optional JSON file with boolean release signals")
    readiness.add_argument("--output-file", default=None, help="Optional checklist report output path")
    readiness.add_argument("--strict", action="store_true", help="Fail when no machine-checkable signals file is supplied")
    readiness.add_argument("--json", action="store_true", help="Emit JSON result")
    return parser.parse_args(argv)


def _parse_continuity_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit continuity",
        description="Preserve and restore Relay-kit continuity across long chats and sessions.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    checkpoint = subparsers.add_parser("checkpoint", help="Capture continuity snapshot")
    checkpoint.add_argument("project_path", nargs="?", default=".", help="Target project root")
    checkpoint.add_argument("--json", action="store_true", help="Emit JSON output")
    checkpoint.add_argument("--objective", default=None, help="Current objective summary")
    checkpoint.add_argument("--lane", default=None, help="Active lane id")
    checkpoint.add_argument("--blocker", default=None, help="Current blocker")
    checkpoint.add_argument("--next-step", default=None, help="Exact next step")
    checkpoint.add_argument("--note", default=None, help="Optional checkpoint note")

    rehydrate = subparsers.add_parser("rehydrate", help="Rehydrate context from last checkpoint")
    rehydrate.add_argument("project_path", nargs="?", default=".", help="Target project root")
    rehydrate.add_argument("--json", action="store_true", help="Emit JSON output")

    handoff = subparsers.add_parser("handoff", help="Create handoff pack from latest manifest")
    handoff.add_argument("project_path", nargs="?", default=".", help="Target project root")
    handoff.add_argument("--json", action="store_true", help="Emit JSON output")
    handoff.add_argument("--reason", default=None, help="Reason for handoff file naming")
    handoff.add_argument("--receiver", default=None, help="Intended receiver")

    diff = subparsers.add_parser("diff-since-last", help="Diff tracked continuity files since last checkpoint")
    diff.add_argument("project_path", nargs="?", default=".", help="Target project root")
    diff.add_argument("--json", action="store_true", help="Emit JSON output")
    return parser.parse_args(argv)


def _parse_migration_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit migration",
        description="Run Relay-kit migration and naming guards through portable public commands.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    guard = subparsers.add_parser("guard", help="Detect retired naming tokens")
    guard.add_argument("project_path", nargs="?", default=".", help="Target project root")
    guard.add_argument("--strict", action="store_true", help="Return non-zero when findings exist")
    guard.add_argument("--json", action="store_true", help="Emit JSON report")
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

    index_check = subparsers.add_parser("index-check", help="Verify package-index metadata for the published version")
    index_check.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    index_check.add_argument("--channel", choices=["pypi", "testpypi", "internal"], default="pypi")
    index_check.add_argument("--target-version", default=None, help="Expected package-index version (default: project version)")
    index_check.add_argument("--package-url", default=None, help="Package index evidence URL")
    index_check.add_argument("--timeout", type=float, default=10.0, help="Package-index request timeout in seconds")
    index_check.add_argument(
        "--output-file",
        default=None,
        help="JSON report output path (default: <project>/.relay-kit/release/package-index-check.json)",
    )
    index_check.add_argument("--strict", action="store_true", help="Return non-zero unless package-index metadata is published")
    index_check.add_argument("--json", action="store_true", help="Emit machine-readable package-index check")

    status = subparsers.add_parser("status", help="Inspect local publication trail and execution evidence")
    status.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    status.add_argument(
        "--trail-file",
        default=None,
        help="Publication trail JSON path (default: <project>/.relay-kit/release/publication-trail.json)",
    )
    status.add_argument("--strict", action="store_true", help="Return non-zero unless the publication trail is complete")
    status.add_argument("--json", action="store_true", help="Emit machine-readable publication trail status")
    return parser.parse_args(argv)


def _parse_commercial_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit commercial",
        description="Assemble commercial proof dossiers from local gates and external evidence pointers.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    dossier = subparsers.add_parser("dossier", help="Write a commercial readiness proof dossier")
    dossier.add_argument("project_path", nargs="?", default=".", help="Project root to inspect")
    dossier.add_argument("--channel", choices=["pypi", "testpypi", "internal"], default="pypi")
    dossier.add_argument("--ci-url", default=None, help="Green remote CI evidence URL")
    dossier.add_argument("--release-url", default=None, help="Release page or release-note URL")
    dossier.add_argument("--package-url", default=None, help="Package-index or internal registry URL")
    dossier.add_argument("--sla-url", default=None, help="Approved SLA/support policy URL")
    dossier.add_argument("--support-url", default=None, help="Paid-support intake or escalation workflow URL")
    dossier.add_argument("--legal-owner", default=None, help="Owner who approved legal/SLA commitments")
    dossier.add_argument("--support-owner", default=None, help="Owner accountable for paid-support triage")
    dossier.add_argument("--readiness-profile", choices=["team", "enterprise"], default="enterprise")
    dossier.add_argument("--skip-readiness-tests", action="store_true", help="Skip pytest inside the readiness gate")
    dossier.add_argument(
        "--publication-trail-file",
        default=None,
        help="Publication trail JSON path (default: <project>/.relay-kit/release/publication-trail.json)",
    )
    dossier.add_argument(
        "--support-request-file",
        default=None,
        help="Support request JSON path (default: <project>/.relay-kit/support/support-request.json)",
    )
    dossier.add_argument(
        "--support-bundle-file",
        default=None,
        help="Support bundle JSON path (default: <project>/.relay-kit/support/support-bundle.json)",
    )
    dossier.add_argument(
        "--output-file",
        default=None,
        help="JSON dossier output path (default: <project>/.relay-kit/commercial/commercial-dossier.json)",
    )
    dossier.add_argument("--strict", action="store_true", help="Return non-zero unless the dossier is ready")
    dossier.add_argument("--json", action="store_true", help="Emit machine-readable commercial dossier")
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
    build.add_argument("--include-package-index", action="store_true", help="Read default package-index check artifact and include it")
    build.add_argument("--include-support-request", action="store_true", help="Read default support request intake artifact and include it")
    build.add_argument("--include-commercial-dossier", action="store_true", help="Read default commercial dossier artifact and include it")
    build.add_argument("--include-context-audit", action="store_true", help="Run context audit and include governance health")
    build.add_argument("--include-lane-audit", action="store_true", help="Run lane audit and include lane health")
    build.add_argument("--include-adapter-diagnostics", action="store_true", help="Run adapter diagnostics and include adapter health")
    build.add_argument("--include-token-audit", action="store_true", help="Run token audit and include token health")
    build.add_argument("--include-query-search", action="store_true", help="Run query search and include query health")
    build.add_argument("--include-service-boundaries", action="store_true", help="Run service-boundary checks and include service health")
    build.add_argument("--readiness-file", default=None, help="Existing readiness JSON report to include")
    build.add_argument("--publication-file", default=None, help="Existing publication plan JSON report to include")
    build.add_argument("--package-index-file", default=None, help="Existing package-index check JSON report to include")
    build.add_argument("--support-request-file", default=None, help="Existing support request JSON report to include")
    build.add_argument("--commercial-dossier-file", default=None, help="Existing commercial dossier JSON report to include")
    build.add_argument("--context-audit-file", default=None, help="Existing context audit JSON report to include")
    build.add_argument("--lane-audit-file", default=None, help="Existing lane audit JSON report to include")
    build.add_argument("--adapter-diagnostics-file", default=None, help="Existing adapter diagnostics JSON report to include")
    build.add_argument("--token-audit-file", default=None, help="Existing token audit JSON report to include")
    build.add_argument("--query-search-file", default=None, help="Existing query search JSON report to include")
    build.add_argument("--service-boundaries-file", default=None, help="Existing service-boundary JSON report to include")
    build.add_argument("--query-search-text", default="relay governance", help="Query text when --include-query-search builds a report")
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
    if args.locale:
        relay_argv.extend(["--locale", args.locale])
    if args.fallback_locale:
        relay_argv.extend(["--fallback-locale", args.fallback_locale])

    if args.verbose:
        relay_argv.append("--verbose")

    return relay_argv


def _doctor_commands(project_path: str, skip_tests: bool, policy_pack: str = DEFAULT_POLICY_PACK) -> list[tuple[str, list[str]]]:
    project = Path(project_path)
    adapter_args = _doctor_adapter_args(project)
    commands = []

    if _source_runtime_surfaces_available():
        commands.append(
            ("validate runtime", [sys.executable, str(REPO_ROOT / "scripts" / "validate_runtime.py")])
        )

    commands.extend(
        [
            (
                "runtime doctor template",
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "runtime_doctor.py"),
                    project_path,
                    "--strict",
                    *adapter_args,
                ],
            ),
            (
                "runtime doctor live",
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "runtime_doctor.py"),
                    project_path,
                    "--strict",
                    *adapter_args,
                    "--state-mode",
                    "live",
                ],
            ),
            (
                "naming guard",
                [sys.executable, str(REPO_ROOT / "scripts" / "naming_guard.py"), project_path, "--strict"],
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
    )

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


def _source_runtime_surfaces_available() -> bool:
    return all((REPO_ROOT / relative).exists() for relative in (".claude/skills", ".agent/skills", ".codex/skills"))


def _doctor_adapter_args(project: Path) -> list[str]:
    adapters = []
    for adapter, relative in (
        ("claude", ".claude/skills"),
        ("agent", ".agent/skills"),
        ("codex", ".codex/skills"),
    ):
        if (project / relative).exists():
            adapters.append(adapter)
    if not adapters or len(adapters) == 3:
        return []
    return ["--adapters", *adapters]


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


def run_context(args: argparse.Namespace) -> int:
    if args.action == "audit":
        report = build_context_audit(args.project_path, stale_days=args.stale_days)
        if args.output_file:
            write_context_audit(args.project_path, report, output_file=args.output_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_context_audit(report))
            if args.output_file:
                print(f"Wrote {args.output_file}")
        if args.strict and report["status"] != "pass":
            return 1
        return 0

    if args.action == "index":
        report = build_context_index(args.project_path)
        output_path = write_context_index(args.project_path, report, output_file=args.output_file)
        if args.json:
            payload = dict(report)
            payload["output_file"] = str(output_path)
            print(json.dumps(payload, ensure_ascii=True, indent=2))
        else:
            print(render_context_index(report))
            print(f"Wrote {output_path}")
        return 0

    if args.action == "search":
        report = build_context_search(
            args.project_path,
            query=args.query,
            limit=args.limit,
            index_file=args.index_file,
        )
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_context_search(report))
        return 0 if report["status"] in {"pass", "empty"} else 2

    if args.action == "related":
        report = build_context_related(
            args.project_path,
            path=args.path,
            limit=args.limit,
            index_file=args.index_file,
        )
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_context_related(report))
        return 0 if report["status"] in {"pass", "empty"} else 2

    if args.action == "budget":
        report = build_context_budget(
            args.project_path,
            max_tokens=args.max_tokens,
            query=args.query,
            scopes=args.scope,
            stale_days=args.stale_days,
        )
        output_path = write_context_budget(args.project_path, report, output_file=args.output_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_context_budget(report))
            print(f"Wrote {output_path}")
        if args.strict and report["status"] != "pass":
            return 1
        return 0

    if args.action == "pack":
        report = build_context_pack(
            args.project_path,
            task=args.task,
            max_tokens=args.max_tokens,
            scopes=args.scope,
            stale_days=args.stale_days,
        )
        output_path = write_context_pack(args.project_path, report, output_file=args.output_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_context_pack(report))
            print(f"Wrote {output_path}")
        if args.strict and report["status"] != "pass":
            return 1
        return 0

    return 2


def run_lane(args: argparse.Namespace) -> int:
    if args.action != "audit":
        return 2
    report = build_lane_audit(args.project_path)
    if args.output_file:
        write_lane_audit(args.project_path, report, output_file=args.output_file)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_lane_audit(report))
        if args.output_file:
            print(f"Wrote {args.output_file}")
    if args.strict and report["status"] != "pass":
        return 1
    return 0


def run_locale(args: argparse.Namespace) -> int:
    if args.action == "show":
        report = inspect_runtime_locale(args.project_path)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
            return 0 if report["status"] == "pass" else 2
        locale = load_runtime_locale(Path(args.project_path).resolve())
        print("Relay-kit runtime locale")
        print(f"- locale profile: {locale.get('locale_profile', 'en')}")
        print(f"- fallback locale: {locale.get('fallback_locale', 'en')}")
        print(f"- enforce output language: {locale.get('enforce_output_language', True)}")
        if report["status"] != "pass":
            for finding in report.get("findings", []):
                print(f"  - {finding.get('summary', finding.get('id', 'finding'))}")
            return 2
        return 0

    if args.action != "set":
        return 2

    try:
        updated = write_runtime_locale(
            Path(args.project_path).resolve(),
            locale=args.locale,
            fallback_locale=args.fallback_locale,
            enforce_output_language=args.enforce_output_language,
        )
    except ValueError as exc:
        print(f"Locale update failed: {exc}")
        return 2

    if args.json:
        print(json.dumps(updated, ensure_ascii=True, indent=2))
    else:
        print("Updated runtime locale policy")
        print(f"- locale profile: {updated.get('locale_profile')}")
        print(f"- fallback locale: {updated.get('fallback_locale')}")
        print(f"- enforce output language: {updated.get('enforce_output_language')}")
    return 0


def run_token(args: argparse.Namespace) -> int:
    if args.action != "audit":
        return 2
    report = build_token_audit(
        args.project_path,
        max_tokens=args.max_tokens,
        scopes=args.scope,
        stale_days=args.stale_days,
    )
    output_path = write_token_audit(args.project_path, report, output_file=args.output_file)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_token_audit(report))
        print(f"Wrote {output_path}")
    if args.strict and report["status"] != "pass":
        return 1
    return 0


def run_shell(args: argparse.Namespace) -> int:
    if args.action != "compact":
        return 2
    command = list(args.command or [])
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        print("Missing command. Use: relay-kit shell compact <project> -- <command...>", file=sys.stderr)
        return 2
    try:
        report = run_compacted_command(
            command,
            project_root=args.project_path,
            cwd=args.cwd or args.project_path,
            strict=args.strict,
            timeout=args.timeout,
        )
    except ShellCompactionError as exc:
        print(f"Shell compaction failed: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        executable = command[0] if command else "<missing>"
        print(f"Shell compaction failed: executable not found: {executable} ({exc})", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"Shell compaction failed: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(report["compact_output"], end="")
    return int(report.get("returncode", 0) or 0)


def run_adapter(args: argparse.Namespace) -> int:
    if args.action != "diagnose":
        return 2
    report = build_adapter_diagnostics(args.project_path, adapter=args.adapter)
    if args.output_file:
        write_adapter_diagnostics(args.project_path, report, output_file=args.output_file)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_adapter_diagnostics(report))
        if args.output_file:
            print(f"Wrote {args.output_file}")
    if args.strict and report["status"] != "pass":
        return 1
    return 0


def run_command_surface(args: argparse.Namespace) -> int:
    if args.action == "list":
        payload = {
            "schema_version": "relay-kit.command-registry.v1",
            "status": "pass",
            "project_path": str(Path(args.project_path).resolve()),
            "summary": {"command_count": len(lifecycle_command_records())},
            "commands": lifecycle_command_records(),
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=True, indent=2))
        else:
            print("Relay-kit lifecycle commands")
            print(f"- commands: {payload['summary']['command_count']}")
            for command in payload["commands"]:
                print(f"  - {command['slash']} -> {command['route_target']}")
        return 0

    if args.action != "diagnose":
        return 2

    report = build_command_diagnostics(args.project_path, adapter=args.adapter)
    if args.output_file:
        write_command_diagnostics(args.project_path, report, output_file=args.output_file)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_command_diagnostics(report))
        if args.output_file:
            print(f"Wrote {args.output_file}")
    if args.strict and report["status"] != "pass":
        return 1
    return 0


def run_agent_surface(args: argparse.Namespace) -> int:
    if args.action == "list":
        payload = {
            "schema_version": "relay-kit.agent-registry.v1",
            "status": "pass",
            "project_path": str(Path(args.project_path).resolve()),
            "summary": {"profile_count": len(agent_profile_records())},
            "profiles": agent_profile_records(),
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=True, indent=2))
        else:
            print("Relay-kit agent profiles")
            print(f"- profiles: {payload['summary']['profile_count']}")
            for profile in payload["profiles"]:
                route = " -> ".join(profile["route_contract"])
                print(f"  - {profile['id']}: {route}")
        return 0

    if args.action != "diagnose":
        return 2

    report = build_agent_diagnostics(args.project_path, adapter=args.adapter)
    if args.output_file:
        write_agent_diagnostics(args.project_path, report, output_file=args.output_file)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_agent_diagnostics(report))
        if args.output_file:
            print(f"Wrote {args.output_file}")
    if args.strict and report["status"] != "pass":
        return 1
    return 0


def run_query(args: argparse.Namespace) -> int:
    if args.action != "search":
        return 2
    report = build_query_search(
        args.project_path,
        query=args.query,
        scopes=args.scope,
        limit=args.limit,
        stale_days=args.stale_days,
    )
    if args.output_file:
        write_query_search(args.project_path, report, output_file=args.output_file)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_query_search(report))
        if args.output_file:
            print(f"Wrote {args.output_file}")
    return 0 if report["status"] in {"pass", "empty"} else 2


def run_prompt(args: argparse.Namespace) -> int:
    if args.action != "enhance":
        return 2
    report = build_prompt_enhancement(
        args.project_path,
        prompt=args.prompt,
        top_limit=args.top_limit,
    )
    output_path = None
    if args.output_file:
        output_path = write_prompt_enhancement(args.project_path, report, args.output_file)
    if args.json:
        payload = dict(report)
        if output_path is not None:
            payload["output_file"] = str(output_path)
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print(render_prompt_enhancement(report))
        if output_path is not None:
            print(f"Wrote {output_path}")
    return 0


def run_service(args: argparse.Namespace) -> int:
    if args.action != "boundaries":
        return 2
    report = build_service_boundary_report(args.project_path)
    if args.output_file:
        write_service_boundary_report(args.project_path, report, output_file=args.output_file)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_service_boundary_report(report))
        if args.output_file:
            print(f"Wrote {args.output_file}")
    if args.strict and report["status"] != "pass":
        return 1
    return 0


def _run_script_main(module: object, program: str, argv: list[str]) -> int:
    original_argv = sys.argv[:]
    try:
        sys.argv = [program, *argv]
        return int(module.main())  # type: ignore[attr-defined]
    finally:
        sys.argv = original_argv


def run_runtime(args: argparse.Namespace) -> int:
    if args.action != "doctor":
        return 2
    from scripts import runtime_doctor

    doctor_argv = [args.project_path, "--state-mode", args.state_mode, "--adapters", *args.adapters]
    if args.strict:
        doctor_argv.append("--strict")
    return _run_script_main(runtime_doctor, "runtime_doctor.py", doctor_argv)


def run_skill(args: argparse.Namespace) -> int:
    if args.action != "gauntlet":
        return 2
    from scripts import skill_gauntlet

    gauntlet_argv = [args.project_path]
    if args.json:
        gauntlet_argv.append("--json")
    if args.strict:
        gauntlet_argv.append("--strict")
    if args.semantic:
        gauntlet_argv.append("--semantic")
    if args.scenario_fixtures:
        gauntlet_argv.extend(["--scenario-fixtures", args.scenario_fixtures])
    return _run_script_main(skill_gauntlet, "skill_gauntlet.py", gauntlet_argv)


def run_impact(args: argparse.Namespace) -> int:
    if args.action != "radar":
        return 2
    from scripts import impact_radar

    radar_argv = [args.project_path, "--head", args.head]
    if args.base:
        radar_argv.extend(["--base", args.base])
    if args.json:
        radar_argv.append("--json")
    return _run_script_main(impact_radar, "impact_radar.py", radar_argv)


def run_accessibility(args: argparse.Namespace) -> int:
    if args.action != "review":
        return 2
    from scripts import accessibility_review

    review_argv = [args.project_path]
    for option_name in ("surface", "report_file", "output_file"):
        value = getattr(args, option_name)
        if value:
            review_argv.extend([f"--{option_name.replace('_', '-')}", value])
    if args.strict:
        review_argv.append("--strict")
    if args.json:
        review_argv.append("--json")
    return _run_script_main(accessibility_review, "accessibility_review.py", review_argv)


def run_continuity(args: argparse.Namespace) -> int:
    from scripts import context_continuity

    continuity_argv = [args.action, args.project_path]
    if getattr(args, "json", False):
        continuity_argv.append("--json")
    for option_name in ("objective", "lane", "blocker", "next_step", "note", "reason", "receiver"):
        value = getattr(args, option_name, None)
        if value:
            continuity_argv.extend([f"--{option_name.replace('_', '-')}", value])
    return _run_script_main(context_continuity, "context_continuity.py", continuity_argv)


def run_migration(args: argparse.Namespace) -> int:
    if args.action != "guard":
        return 2
    from scripts import naming_guard

    guard_argv = [args.project_path]
    if args.strict:
        guard_argv.append("--strict")
    if args.json:
        guard_argv.append("--json")
    return _run_script_main(naming_guard, "naming_guard.py", guard_argv)


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
    if args.action == "real-world":
        report = build_real_world_eval_report(
            args.project_path,
            cases_file=args.cases_file,
        )
        if args.output_file:
            write_real_world_eval_report(args.project_path, report, args.output_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_real_world_eval_report(report))
        if args.strict and report["status"] != "pass":
            return 2
        return 0

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


def run_proof(args: argparse.Namespace) -> int:
    if args.action != "audit":
        return 2
    report = build_skill_proof_report(
        args.project_path,
        workflow_fixture=args.workflow_fixture,
        real_world_cases_file=args.real_world_cases_file,
        strict=args.strict,
    )
    if args.output_file:
        write_skill_proof_report(args.project_path, report, args.output_file)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_skill_proof_report(report))
    if args.strict and report["status"] != "pass":
        return 2
    return 0


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
    if args.action == "triage":
        report = build_support_triage(args.project_path, request_file=args.request_file, bundle_file=args.bundle_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_support_triage(report))
        if args.strict and report["status"] != "ready":
            return 2
        return 0
    if args.action == "soak":
        report = build_support_soak_report(args.project_path, bundle_file=args.bundle_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_support_soak_report(report))
        if args.strict and report["status"] != "pass":
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
    if args.action == "readiness":
        from scripts import release_readiness

        readiness_argv = [args.project_path, "--phase", args.phase]
        if args.signals_file:
            readiness_argv.extend(["--signals-file", args.signals_file])
        if args.output_file:
            readiness_argv.extend(["--output-file", args.output_file])
        if args.strict:
            readiness_argv.append("--strict")
        if args.json:
            readiness_argv.append("--json")
        return _run_script_main(release_readiness, "release_readiness.py", readiness_argv)
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
    if args.action == "index-check":
        report = build_package_index_check(
            args.project_path,
            channel=args.channel,
            target_version=args.target_version,
            package_url=args.package_url,
            timeout_seconds=args.timeout,
        )
        output_path = write_package_index_check(args.project_path, report, output_file=args.output_file)
        if args.json:
            print(
                json.dumps(
                    {
                        "output_file": str(output_path),
                        "index_check": report,
                    },
                    ensure_ascii=True,
                    indent=2,
                )
            )
        else:
            print(render_package_index_check(report))
            print(f"Wrote {output_path}")
        if args.strict and report["status"] != "published":
            return 2
        return 0
    if args.action == "status":
        report = build_publication_trail_status(args.project_path, trail_file=args.trail_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_publication_trail_status(report))
        if args.strict and report["status"] != "complete":
            return 2
        return 0
    return 2


def run_commercial(args: argparse.Namespace) -> int:
    if args.action != "dossier":
        return 2
    report = build_commercial_dossier(
        args.project_path,
        channel=args.channel,
        ci_url=args.ci_url,
        release_url=args.release_url,
        package_url=args.package_url,
        sla_url=args.sla_url,
        support_url=args.support_url,
        legal_owner=args.legal_owner,
        support_owner=args.support_owner,
        readiness_profile=args.readiness_profile,
        skip_readiness_tests=args.skip_readiness_tests,
        publication_trail_file=args.publication_trail_file,
        support_request_file=args.support_request_file,
        support_bundle_file=args.support_bundle_file,
    )
    output_path = write_commercial_dossier(args.project_path, report, output_file=args.output_file)
    if args.json:
        print(
            json.dumps(
                {
                    "output_file": str(output_path),
                    "dossier": report,
                },
                ensure_ascii=True,
                indent=2,
            )
        )
    else:
        print(render_commercial_dossier(report))
        print(f"Wrote {output_path}")
    if args.strict and report["status"] != "ready":
        return 2
    return 0


def run_pulse(args: argparse.Namespace) -> int:
    if args.action != "build":
        return 2
    report = build_pulse_report(
        args.project_path,
        profile=args.profile,
        evidence_limit=args.evidence_limit,
        include_readiness=args.include_readiness,
        include_publication=args.include_publication,
        include_package_index=args.include_package_index,
        include_support_request=args.include_support_request,
        include_commercial_dossier=args.include_commercial_dossier,
        include_context_audit=args.include_context_audit,
        include_lane_audit=args.include_lane_audit,
        include_adapter_diagnostics=args.include_adapter_diagnostics,
        include_token_audit=args.include_token_audit,
        include_query_search=args.include_query_search,
        include_service_boundaries=args.include_service_boundaries,
        workflow_eval_file=args.workflow_eval_file,
        readiness_file=args.readiness_file,
        publication_file=args.publication_file,
        package_index_file=args.package_index_file,
        support_request_file=args.support_request_file,
        commercial_dossier_file=args.commercial_dossier_file,
        context_audit_file=args.context_audit_file,
        lane_audit_file=args.lane_audit_file,
        adapter_diagnostics_file=args.adapter_diagnostics_file,
        token_audit_file=args.token_audit_file,
        query_search_file=args.query_search_file,
        service_boundaries_file=args.service_boundaries_file,
        query_search_text=args.query_search_text,
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
    # Pulse build is a reporting command; it should emit artifacts even when status is hold.
    return 0


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
    if raw_argv and raw_argv[0] == "context":
        return run_context(_parse_context_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "lane":
        return run_lane(_parse_lane_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "locale":
        return run_locale(_parse_locale_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "token":
        return run_token(_parse_token_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "shell":
        return run_shell(_parse_shell_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "adapter":
        return run_adapter(_parse_adapter_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "command":
        return run_command_surface(_parse_command_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "agent":
        return run_agent_surface(_parse_agent_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "query":
        return run_query(_parse_query_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "prompt":
        return run_prompt(_parse_prompt_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "service":
        return run_service(_parse_service_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "runtime":
        return run_runtime(_parse_runtime_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "skill":
        return run_skill(_parse_skill_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "impact":
        return run_impact(_parse_impact_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "accessibility":
        return run_accessibility(_parse_accessibility_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "manifest":
        return run_manifest(_parse_manifest_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "eval":
        return run_eval(_parse_eval_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "proof":
        return run_proof(_parse_proof_args(raw_argv[1:]))
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
    if raw_argv and raw_argv[0] == "continuity":
        return run_continuity(_parse_continuity_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "migration":
        return run_migration(_parse_migration_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "publish":
        return run_publish(_parse_publish_args(raw_argv[1:]))
    if raw_argv and raw_argv[0] == "commercial":
        return run_commercial(_parse_commercial_args(raw_argv[1:]))
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
