#!/usr/bin/env python3
"""Python Kit v3.2 - registry-driven BMAD-lite hardening for ai-kit.

How to adopt with minimal breakage:
1. Keep the old generator as `python_kit_legacy.py`.
2. Use this file plus the `ai_kit_v3/` package as the active entrypoint.
3. Keep using legacy kits for project-specific analysis/template generation.
4. Use the new bundles to generate orchestrators, workflow hubs, utility providers,
   discipline overlays, next-baseline candidates, artifact contracts, topology docs, and cleaned runtime skills.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ai_kit_v3.generator import BUNDLES, create_bmad_upgrade, create_legacy_skills, load_legacy_module



def legacy_kits(repo_root: Path):
    module = load_legacy_module(repo_root)
    if module is None:
        return None, []
    return module, list(module.SKILL_SETS.keys())



def list_everything(repo_root: Path) -> None:
    module, legacy = legacy_kits(repo_root)
    print("Built-in v3 bundles:")
    for bundle, items in BUNDLES.items():
        print(f"  {bundle} ({len(items)}): {', '.join(items)}")
    print()
    if module is None:
        print("Legacy kits: unavailable (rename old script to python_kit_legacy.py to enable)")
    else:
        print("Legacy kits:")
        for set_name, skill_list in module.SKILL_SETS.items():
            print(f"  {set_name} ({len(skill_list)}):")
            for skill in skill_list:
                print(f"    - {skill}")



def parse_args(repo_root: Path) -> argparse.Namespace:
    _, legacy = legacy_kits(repo_root)
    parser = argparse.ArgumentParser(
        description="Python Kit v3.2 - BMAD-lite hardening with orchestrators, workflow hubs, utility providers, discipline overlays, baseline-next candidates, bundle gating, and legacy compatibility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python python_kit.py /path/to/project --bundle round4 --ai all --emit-contracts --emit-docs --emit-reference-templates
  python python_kit.py /path/to/project --bundle utility-providers --ai codex --emit-docs
  python python_kit.py /path/to/project --bundle discipline-utilities --ai claude --emit-docs
  python python_kit.py /path/to/project --bundle baseline-next --ai codex --emit-contracts --emit-docs --emit-reference-templates
  python python_kit.py /path/to/project --bundle round3 --ai claude --emit-contracts --emit-docs
  python python_kit.py /path/to/project --legacy-kit python --ai claude
  python python_kit.py --list-skills
        """,
    )
    parser.add_argument("project_path", nargs="?", default=".", help="Target project path")
    parser.add_argument("--ai", choices=["claude", "gemini", "codex", "all", "generic"], default="claude")
    parser.add_argument("--bundle", choices=sorted(BUNDLES.keys()), help="Generate new registry-native skills")
    parser.add_argument("--emit-contracts", action="store_true", help="Write artifact contracts into .ai-kit/contracts/ and .ai-kit/state/")
    parser.add_argument("--emit-docs", action="store_true", help="Write topology, migration, gating, and runtime docs into .ai-kit/docs/")
    parser.add_argument("--emit-reference-templates", action="store_true", help="Write living reference templates into .ai-kit/references/")
    parser.add_argument("--legacy-kit", choices=legacy or None, help="Run an old skill set through python_kit_legacy.py")
    parser.add_argument("--skills", nargs="+", metavar="SKILL", help="Pass specific legacy skills through python_kit_legacy.py")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--list-skills", action="store_true")
    return parser.parse_args()



def main() -> int:
    repo_root = Path(__file__).resolve().parent
    args = parse_args(repo_root)
    if args.list_skills:
        list_everything(repo_root)
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
        if not repo_root.joinpath("python_kit_legacy.py").exists():
            print("Cannot run legacy generation because python_kit_legacy.py is missing.")
            print("Rename the old python_kit.py to python_kit_legacy.py and run again.")
            return 1
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
            return exit_code
        ran_anything = True

    if not ran_anything:
        print("Nothing to do. Use --bundle for v3 generation or --legacy-kit/--skills for legacy generation.")
        print("Tip: run with --list-skills to see both v3 bundles and legacy kits.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
