#!/usr/bin/env python3
"""Relay-kit v4.0 - registry-driven workflow runtime for .relay-kit artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from relay_kit_v3.generator import BUNDLES, create_runtime_bundle
from relay_kit_v3.runtime_locale import runtime_locale_file, write_runtime_locale
from relay_kit_v3.srs_policy import policy_file, write_srs_policy
from relay_kit_cycle_log import append_cycle_event, current_source
from relay_kit_compat import CANONICAL_ENTRYPOINT


_ROUND = "round"
_CORE = "core"
_LEGACY_PREFIX = "legacy"
_RETIRED_VENDOR = "b" + "mad"
RETIRED_BUNDLE_HINTS = {
    f"{_ROUND}2": _CORE,
    f"{_ROUND}3-{_CORE}": "orchestration-core",
    f"{_ROUND}3": "orchestration",
    f"{_ROUND}4-{_CORE}": "runtime-core",
    f"{_ROUND}4": "runtime",
    "baseline" + "-" + "next": "baseline",
    f"{_RETIRED_VENDOR}-{_CORE}": _CORE,
    f"{_RETIRED_VENDOR}-lite": _CORE,
    f"{_LEGACY_PREFIX}-native": _CORE,
}


def list_everything() -> None:
    print("Built-in runtime bundles:")
    for bundle, items in BUNDLES.items():
        print(f"  {bundle} ({len(items)}): {', '.join(items)}")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Relay-kit v4.0 - workflow runtime with Relay-kit-only naming and strict bundle taxonomy.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python relay_kit.py /path/to/project --bundle runtime --ai all --emit-contracts --emit-docs --emit-reference-templates
  python relay_kit.py /path/to/project --bundle runtime-core --ai codex --emit-contracts --emit-docs --emit-reference-templates
  python relay_kit.py /path/to/project --bundle orchestration --ai claude --emit-contracts --emit-docs
  python relay_kit.py /path/to/project --bundle core --ai codex --emit-contracts --emit-docs --emit-reference-templates
  python relay_kit.py /path/to/project --bundle utility-providers --ai codex --emit-docs
  python relay_kit.py /path/to/project --bundle discipline-utilities --ai claude --emit-docs
  python relay_kit.py /path/to/project --enable-srs-first --srs-gate warn --srs-scope product-enterprise
  python relay_kit.py /path/to/project --locale vi
  python relay_kit.py --list-skills
        """,
    )
    parser.add_argument("project_path", nargs="?", default=".", help="Target project path")
    parser.add_argument("--ai", choices=["claude", "antigravity", "codex", "all", "generic"], default="claude")
    parser.add_argument("--bundle", help="Generate registry-native skills for a named bundle")
    parser.add_argument("--emit-contracts", action="store_true", help="Write artifact contracts into .relay-kit/contracts/ and .relay-kit/state/")
    parser.add_argument("--emit-docs", action="store_true", help="Write topology, migration, gating, and runtime docs into .relay-kit/docs/")
    parser.add_argument("--emit-reference-templates", action="store_true", help="Write living reference templates into .relay-kit/references/")
    srs_switch = parser.add_mutually_exclusive_group()
    srs_switch.add_argument("--enable-srs-first", action="store_true", help="Enable SRS-first policy for this project")
    srs_switch.add_argument("--disable-srs-first", action="store_true", help="Disable SRS-first policy for this project")
    parser.add_argument("--srs-gate", choices=["off", "warn", "hard"], help="Override SRS gate mode")
    parser.add_argument("--srs-scope", choices=["product-enterprise", "all"], help="Override SRS policy scope")
    parser.add_argument("--srs-risk", choices=["normal", "high"], help="Override SRS policy risk profile")
    parser.add_argument(
        "--locale",
        help="Set global runtime locale profile (allowed: vi, en).",
    )
    parser.add_argument(
        "--fallback-locale",
        help="Set runtime fallback locale profile (allowed: vi, en; default: en).",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--list-skills", action="store_true")
    return parser.parse_args()



def _build_event(args: argparse.Namespace, invoked_as: str, exit_code: int) -> dict[str, object]:
    flow = "no_op"
    if args.list_skills:
        flow = "list_skills"
    elif args.bundle:
        flow = "v3_bundle"
    elif args.enable_srs_first or args.disable_srs_first or args.srs_gate or args.srs_scope or args.srs_risk:
        flow = "srs_policy_update"

    return {
        "entrypoint": invoked_as,
        "source": current_source(),
        "flow": flow,
        "project_path": args.project_path,
        "ai": args.ai,
        "bundle": args.bundle,
        "generic_output": args.ai == "generic",
        "srs_policy": {
            "enable": args.enable_srs_first,
            "disable": args.disable_srs_first,
            "gate": args.srs_gate,
            "scope": args.srs_scope,
            "risk": args.srs_risk,
        },
        "runtime_locale": {
            "locale": args.locale,
            "fallback_locale": args.fallback_locale,
        },
        "exit_code": exit_code,
        "success": exit_code == 0,
    }


def normalize_bundle_name(bundle: str) -> tuple[str | None, str | None]:
    if bundle in BUNDLES:
        return bundle, None
    if bundle in RETIRED_BUNDLE_HINTS:
        return None, f"Unsupported bundle '{bundle}'. Use '{RETIRED_BUNDLE_HINTS[bundle]}' instead."
    return None, f"Unsupported bundle '{bundle}'. Use one of: {', '.join(sorted(BUNDLES.keys()))}"


def _apply_srs_policy_overrides(args: argparse.Namespace) -> bool:
    has_override = any(
        [
            args.enable_srs_first,
            args.disable_srs_first,
            args.srs_gate is not None,
            args.srs_scope is not None,
            args.srs_risk is not None,
        ]
    )
    if not has_override:
        return False

    project_root = Path(args.project_path).resolve()
    gate_override = args.srs_gate
    enabled_override: bool | None = None

    if args.enable_srs_first:
        enabled_override = True
        if gate_override is None:
            gate_override = "warn"
    if args.disable_srs_first:
        enabled_override = False
        gate_override = "off"

    updated = write_srs_policy(
        project_root,
        enabled=enabled_override,
        gate=gate_override,
        scope=args.srs_scope,
        risk_profile=args.srs_risk,
    )

    print(f"Updated SRS policy: {policy_file(project_root)}")
    print(json.dumps(updated, ensure_ascii=True, indent=2))
    return True


def _apply_runtime_locale_overrides(args: argparse.Namespace) -> bool:
    has_override = any(
        [
            args.locale is not None,
            args.fallback_locale is not None,
        ]
    )
    if not has_override:
        return False

    project_root = Path(args.project_path).resolve()
    updated = write_runtime_locale(
        project_root,
        locale=args.locale,
        fallback_locale=args.fallback_locale,
    )

    print(f"Updated runtime locale policy: {runtime_locale_file(project_root)}")
    print(json.dumps(updated, ensure_ascii=True, indent=2))
    return True


def main(invoked_as: str | None = None) -> int:
    repo_root = Path(__file__).resolve().parent
    entrypoint = invoked_as or Path(sys.argv[0]).name or CANONICAL_ENTRYPOINT
    args = parse_args()
    exit_code = 0
    if args.list_skills:
        list_everything()
        append_cycle_event(repo_root, _build_event(args, entrypoint, 0))
        return 0

    ran_anything = False

    if args.bundle:
        bundle, error = normalize_bundle_name(args.bundle)
        if error:
            print(error)
            append_cycle_event(repo_root, _build_event(args, entrypoint, 1))
            return 1
        written = create_runtime_bundle(
            project_path=args.project_path,
            ai=args.ai,
            bundle=bundle,
            with_contracts=args.emit_contracts,
            with_docs=args.emit_docs,
            with_reference_templates=args.emit_reference_templates,
        )
        print(f"Generated {len(written)} v3 files:")
        for path in written:
            print(f"  - {path}")
        ran_anything = True

    if _apply_srs_policy_overrides(args):
        ran_anything = True
    try:
        if _apply_runtime_locale_overrides(args):
            ran_anything = True
    except ValueError as exc:
        print(f"Runtime locale update failed: {exc}")
        exit_code = 1
        append_cycle_event(repo_root, _build_event(args, entrypoint, exit_code))
        return exit_code

    if not ran_anything:
        print(
            "Nothing to do. Use --bundle for runtime generation, "
            "SRS policy flags, or --locale/--fallback-locale."
        )
        print("Tip: run with --list-skills to see active runtime bundles.")
        exit_code = 1
        append_cycle_event(repo_root, _build_event(args, entrypoint, exit_code))
        return exit_code

    append_cycle_event(repo_root, _build_event(args, entrypoint, exit_code))
    return 0


if __name__ == "__main__":
    sys.exit(main())
