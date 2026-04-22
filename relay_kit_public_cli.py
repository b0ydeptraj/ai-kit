#!/usr/bin/env python3
"""Public Relay-kit installer CLI.

This wrapper exposes a friendlier command surface:
  relay-kit <project_path> --codex|--claude|--antigravity

It maps to the existing canonical runtime entrypoint (`relay_kit.py`)
without changing the underlying generation flow.
"""

from __future__ import annotations

import argparse
import sys

import relay_kit as relay_core


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

    fidelity_switch = parser.add_mutually_exclusive_group()
    fidelity_switch.add_argument("--enable-intent-fidelity", action="store_true", help="Enable intent-fidelity policy for this project")
    fidelity_switch.add_argument("--disable-intent-fidelity", action="store_true", help="Disable intent-fidelity policy for this project")
    parser.add_argument("--fidelity-gate", choices=["off", "warn", "hard"], help="Intent-fidelity policy gate mode")
    parser.add_argument("--fidelity-scope", choices=["all-edits", "media-ui", "media-only"], help="Intent-fidelity policy scope")

    parser.add_argument("--legacy-kit", help="Optional preserved legacy kit")
    parser.add_argument("--skills", nargs="+", metavar="SKILL", help="Optional legacy skills")
    parser.add_argument("--list-skills", action="store_true", help="List bundles and legacy kits")
    parser.add_argument("-v", "--verbose", action="store_true")

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
    if args.enable_intent_fidelity:
        relay_argv.append("--enable-intent-fidelity")
    if args.disable_intent_fidelity:
        relay_argv.append("--disable-intent-fidelity")
    if args.fidelity_gate:
        relay_argv.extend(["--fidelity-gate", args.fidelity_gate])
    if args.fidelity_scope:
        relay_argv.extend(["--fidelity-scope", args.fidelity_scope])

    if args.legacy_kit:
        relay_argv.extend(["--legacy-kit", args.legacy_kit])
    if args.skills:
        relay_argv.append("--skills")
        relay_argv.extend(args.skills)
    if args.verbose:
        relay_argv.append("--verbose")

    return relay_argv


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    relay_argv = _build_relay_argv(args)

    original_argv = sys.argv[:]
    try:
        sys.argv = relay_argv
        return relay_core.main(invoked_as="relay-kit")
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    raise SystemExit(main())
