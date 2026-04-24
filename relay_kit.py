#!/usr/bin/env python3
"""Relay-kit v3.3 - registry-driven workflow runtime for .relay-kit artifacts.

How to adopt:
1. Use `relay_kit.py` as the runtime entrypoint.
2. Keep using legacy kits for project-specific analysis/template generation via `relay_kit_legacy.py`.
3. Use bundles to generate orchestrators, workflow hubs, utility providers,
   discipline overlays, artifact contracts, topology docs, and cleaned runtime skills.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from relay_kit_v3.generator import BUNDLES, create_bmad_upgrade, create_legacy_skills, load_legacy_module
from relay_kit_v3.srs_policy import policy_file, write_srs_policy
from relay_kit_cycle_log import append_cycle_event, current_source
from relay_kit_compat import (
    CANONICAL_ENTRYPOINT,
    CANONICAL_LEGACY_ENTRYPOINT,
)



def legacy_kits(repo_root: Path):
    module = load_legacy_module(repo_root)
    if module is None:
        return None, []
    return module, list(module.SKILL_SETS.keys())



def normalize_legacy_kit_name(repo_root: Path, kit: str | None) -> str | None:
    if not kit:
        return kit
    module, _ = legacy_kits(repo_root)
    if module is None or not hasattr(module, "normalize_legacy_kit"):
        return kit
    return module.normalize_legacy_kit(kit)


def list_everything(repo_root: Path) -> None:
    module, legacy = legacy_kits(repo_root)
    print("Built-in v3 bundles:")
    for bundle, items in BUNDLES.items():
        print(f"  {bundle} ({len(items)}): {', '.join(items)}")
    print()
    if module is None:
        print(f"Legacy kits: unavailable (expected {CANONICAL_LEGACY_ENTRYPOINT})")
    else:
        print("Legacy kits:")
        for set_name, skill_list in module.SKILL_SETS.items():
            print(f"  {set_name} ({len(skill_list)}):")
            for skill in skill_list:
                print(f"    - {skill}")



def parse_args(repo_root: Path) -> argparse.Namespace:
    _, legacy = legacy_kits(repo_root)
    parser = argparse.ArgumentParser(
        description="Relay-kit v3.3 - workflow runtime with orchestrators, workflow hubs, utility providers, discipline overlays, baseline bundle gating, and legacy generation via relay_kit_legacy.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python relay_kit.py /path/to/project --bundle round4 --ai all --emit-contracts --emit-docs --emit-reference-templates
  python relay_kit.py /path/to/project --bundle utility-providers --ai codex --emit-docs
  python relay_kit.py /path/to/project --bundle discipline-utilities --ai claude --emit-docs
  python relay_kit.py /path/to/project --bundle baseline --ai antigravity --emit-contracts --emit-docs --emit-reference-templates
  python relay_kit.py /path/to/project --bundle baseline --ai codex --emit-contracts --emit-docs --emit-reference-templates
  python relay_kit.py /path/to/project --enable-srs-first --srs-gate warn --srs-scope product-enterprise
  python relay_kit.py /path/to/project --bundle round3 --ai claude --emit-contracts --emit-docs
  python relay_kit.py /path/to/project --legacy-kit python --ai claude
  python relay_kit.py --list-skills
        """,
    )
    parser.add_argument("project_path", nargs="?", default=".", help="Target project path")
    parser.add_argument("--ai", choices=["claude", "antigravity", "codex", "all", "generic"], default="claude")
    parser.add_argument("--bundle", choices=sorted(BUNDLES.keys()), help="Generate new registry-native skills")
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
        "--legacy-kit",
        help=(
            f"Run a preserved legacy suite through {CANONICAL_LEGACY_ENTRYPOINT}. "
            f"Visible suites: {', '.join(legacy) if legacy else 'unavailable'}"
        ),
    )
    parser.add_argument(
        "--skills",
        nargs="+",
        metavar="SKILL",
        help=f"Pass specific legacy skills through {CANONICAL_LEGACY_ENTRYPOINT}",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--list-skills", action="store_true")
    return parser.parse_args()



def _build_event(args: argparse.Namespace, invoked_as: str, exit_code: int) -> dict[str, object]:
    repo_root = Path(__file__).resolve().parent
    flow = "no_op"
    if args.list_skills:
        flow = "list_skills"
    elif args.bundle and (args.legacy_kit or args.skills):
        flow = "bundle_plus_legacy"
    elif args.bundle:
        flow = "v3_bundle"
    elif args.legacy_kit or args.skills:
        flow = "legacy_bridge"
    elif args.enable_srs_first or args.disable_srs_first or args.srs_gate or args.srs_scope or args.srs_risk:
        flow = "srs_policy_update"

    return {
        "entrypoint": invoked_as,
        "source": current_source(),
        "flow": flow,
        "project_path": args.project_path,
        "ai": args.ai,
        "bundle": args.bundle,
        "legacy_kit": normalize_legacy_kit_name(repo_root, args.legacy_kit or ("python" if args.skills else None)),
        "skills": list(args.skills or []),
        "generic_output": args.ai == "generic",
        "srs_policy": {
            "enable": args.enable_srs_first,
            "disable": args.disable_srs_first,
            "gate": args.srs_gate,
            "scope": args.srs_scope,
            "risk": args.srs_risk,
        },
        "exit_code": exit_code,
        "success": exit_code == 0,
    }


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


def main(invoked_as: str | None = None) -> int:
    repo_root = Path(__file__).resolve().parent
    entrypoint = invoked_as or Path(sys.argv[0]).name or CANONICAL_ENTRYPOINT
    args = parse_args(repo_root)
    exit_code = 0
    if args.list_skills:
        list_everything(repo_root)
        append_cycle_event(repo_root, _build_event(args, entrypoint, 0))
        return 0

    ran_anything = False

    if args.bundle:
        written = create_bmad_upgrade(
            project_path=args.project_path,
            ai=args.ai,
            bundle=args.bundle,
            with_contracts=args.emit_contracts,
            with_docs=args.emit_docs,
            with_reference_templates=args.emit_reference_templates,
        )
        print(f"Generated {len(written)} v3 files:")
        for path in written:
            print(f"  - {path}")
        ran_anything = True

    if args.legacy_kit or args.skills:
        if load_legacy_module(repo_root) is None:
            print(
                f"Cannot run legacy generation because {CANONICAL_LEGACY_ENTRYPOINT} is not available."
            )
            exit_code = 1
            append_cycle_event(repo_root, _build_event(args, entrypoint, exit_code))
            return exit_code
        legacy_kit = args.legacy_kit or "python"
        exit_code = create_legacy_skills(
            project_path=args.project_path,
            ai=args.ai,
            verbose=args.verbose,
            skills=args.skills,
            kit=legacy_kit,
            repo_root=repo_root,
        )
        if exit_code != 0:
            append_cycle_event(repo_root, _build_event(args, entrypoint, exit_code))
            return exit_code
        ran_anything = True

    if _apply_srs_policy_overrides(args):
        ran_anything = True

    if not ran_anything:
        print("Nothing to do. Use --bundle for v3 generation, --legacy-kit/--skills for legacy generation, or SRS policy flags.")
        print("Tip: run with --list-skills to see both v3 bundles and legacy kits.")
        exit_code = 1
        append_cycle_event(repo_root, _build_event(args, entrypoint, exit_code))
        return exit_code

    append_cycle_event(repo_root, _build_event(args, entrypoint, exit_code))
    return 0


if __name__ == "__main__":
    sys.exit(main())
