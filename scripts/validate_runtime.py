#!/usr/bin/env python3
"""Validate Relay-kit runtime integrity for the post-cutover model."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from relay_kit_v3.localized_metadata import expected_trigger_prefixes, resolve_metadata_locale
from relay_kit_v3.adapters import ADAPTER_TARGETS
from relay_kit_v3.generator import BUNDLES
from relay_kit_v3.public_entrypoints import PUBLIC_ENTRYPOINT_SHIMS
from relay_kit_v3.registry.skills import ALL_V3_SKILLS
from relay_kit_v3.runtime_locale import load_runtime_locale
from relay_kit_v3.temp_paths import stable_temp_dir
from relay_kit_compat import (
    CANONICAL_ARTIFACT_ROOT,
    CANONICAL_ENTRYPOINT,
    GENERIC_CANONICAL_DIR,
)

ALL_TARGETS = [".claude/skills", ".agent/skills", ".codex/skills"]
EXPECTED_RUNTIME_SKILLS = set(ALL_V3_SKILLS.keys())
EXPECTED_CHECKED_IN_SKILLS = EXPECTED_RUNTIME_SKILLS | set(PUBLIC_ENTRYPOINT_SHIMS)
RETIRED_BUNDLE_LABELS = {
    "round" + "2",
    "round" + "3-core",
    "round" + "3",
    "round" + "4-core",
    "round" + "4",
    "baseline" + "-" + "next",
    "b" + "mad-core",
    "b" + "mad-lite",
    "legacy" + "-native",
}
REQUIRED_GITIGNORE_PATTERNS = {
    ".kilo/",
    ".kiro/",
    "build/",
    "dist/",
    "*.egg-info/",
    ".eggs/",
}
REJECTED_TRACKED_PATH_PREFIXES = (
    ".kilo/",
    ".kiro/",
    "build/",
    "dist/",
    ".eggs/",
)
RUNTIME_DISCIPLINE_SKILLS = {
    "root-cause-debugging",
    "evidence-before-completion",
    "test-first-development",
}
BASELINE_APPROVED = {
    "root-cause-debugging",
    "evidence-before-completion",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def run_command(command: list[str], label: str, *, cwd: Path = REPO_ROOT) -> str:
    env = dict(os.environ)
    env["RELAY_KIT_CYCLE_SOURCE"] = "validate_runtime"
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    if result.returncode != 0:
        fail(
            f"{label} failed:\n"
            f"command: {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result.stdout


def run_cli(script_name: str, *args: str) -> str:
    return run_command([sys.executable, str(REPO_ROOT / script_name), *args], script_name)


def run_public_cli(*args: str) -> str:
    return run_command(
        [sys.executable, str(REPO_ROOT / "relay_kit_public_cli.py"), *args],
        "relay_kit_public_cli.py",
    )


def run_helper_script(script_relative_path: str, *args: str) -> str:
    return run_command(
        [sys.executable, str(REPO_ROOT / script_relative_path), *args],
        script_relative_path,
    )


def skill_dirs(base: Path, relative_dir: str) -> set[str]:
    target = base / Path(relative_dir)
    if not target.exists():
        fail(f"Missing runtime folder: {target}")
    return {entry.name for entry in target.iterdir() if entry.is_dir()}


def assert_set(name: str, actual: set[str], expected: set[str]) -> None:
    if actual == expected:
        return
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    fail(f"{name} mismatch. Missing: {missing or '-'} Extra: {extra or '-'}")


def assert_contains(path: Path, required_tokens: list[str]) -> None:
    content = path.read_text(encoding="utf-8")
    missing = [token for token in required_tokens if token not in content]
    if missing:
        fail(f"{path} is missing expected tokens: {missing}")


def assert_skill_descriptions_trigger_first() -> None:
    locale_policy = load_runtime_locale(REPO_ROOT)
    locale_profile = resolve_metadata_locale(locale_policy)
    fallback_locale = str(locale_policy.get("fallback_locale", "en"))
    trigger_prefixes = expected_trigger_prefixes(locale_profile, fallback_locale)
    skill_roots = [
        REPO_ROOT / ".claude" / "skills",
        REPO_ROOT / ".agent" / "skills",
        REPO_ROOT / ".codex" / "skills",
    ]
    bad_descriptions: list[str] = []
    for root in skill_roots:
        for skill_file in root.rglob("SKILL.md"):
            content = skill_file.read_text(encoding="utf-8")
            match = re.search(r"^description:\s*(.+)$", content, re.MULTILINE)
            if match is None:
                bad_descriptions.append(f"{skill_file}: missing description")
                continue
            description = match.group(1).strip()
            if not any(description.startswith(prefix) for prefix in trigger_prefixes):
                bad_descriptions.append(f"{skill_file}: {description}")
    if bad_descriptions:
        preview = "\n".join(bad_descriptions[:10])
        prefixes_text = ", ".join(repr(prefix) for prefix in trigger_prefixes)
        fail(
            "Skill descriptions must use trigger-first wording that starts with "
            f"one of {prefixes_text}.\n"
            f"Examples of drift:\n{preview}"
        )


def validate_skill_gauntlet() -> None:
    run_command(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "skill_gauntlet.py"),
            str(REPO_ROOT),
            "--strict",
        ],
        "skill_gauntlet",
    )


def validate_naming_guard() -> None:
    run_command(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "naming_guard.py"),
            str(REPO_ROOT),
            "--strict",
        ],
        "naming_guard",
    )


def validate_context_continuity_utility() -> None:
    temp_dir = stable_temp_dir(REPO_ROOT, "continuity")
    try:
        run_helper_script(
            "scripts/context_continuity.py",
            "checkpoint",
            str(temp_dir),
            "--objective",
            "runtime validation",
            "--lane",
            "primary",
            "--next-step",
            "run qa gate",
        )
        run_helper_script("scripts/context_continuity.py", "rehydrate", str(temp_dir))
        run_helper_script("scripts/context_continuity.py", "diff-since-last", str(temp_dir))
        run_helper_script(
            "scripts/context_continuity.py",
            "handoff",
            str(temp_dir),
            "--reason",
            "validate-runtime",
            "--receiver",
            "qa",
        )
        manifest = temp_dir / CANONICAL_ARTIFACT_ROOT / "state" / "context-manifest.json"
        ledger = temp_dir / CANONICAL_ARTIFACT_ROOT / "state" / "session-ledger.jsonl"
        handoff_dir = temp_dir / CANONICAL_ARTIFACT_ROOT / "handoffs"
        if not manifest.exists():
            fail("context_continuity checkpoint did not create context-manifest.json")
        if not ledger.exists():
            fail("context_continuity checkpoint did not create session-ledger.jsonl")
        handoffs = list(handoff_dir.glob("*.md"))
        if not handoffs:
            fail("context_continuity handoff did not create a handoff markdown file")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def prompt_files(base: Path, relative_dir: str) -> dict[str, str]:
    target = base / relative_dir
    if not target.exists():
        fail(f"Missing prompt folder: {target}")
    return {
        entry.name: entry.read_text(encoding="utf-8")
        for entry in target.iterdir()
        if entry.is_file() and entry.suffix == ".md"
    }


def validate_checked_in_runtime() -> None:
    adapter_sets = {target: skill_dirs(REPO_ROOT, target) for target in ALL_TARGETS}
    reference_target, reference_set = next(iter(adapter_sets.items()))
    for target, current_set in adapter_sets.items():
        assert_set(
            f"checked-in generated runtime for {target}",
            current_set,
            EXPECTED_CHECKED_IN_SKILLS,
        )
        assert_set(
            f"checked-in runtime parity vs {reference_target} for {target}",
            current_set,
            reference_set,
        )


def validate_bundle_integrity() -> None:
    retired = sorted(RETIRED_BUNDLE_LABELS & set(BUNDLES))
    if retired:
        fail(f"Retired bundle labels are still active: {retired}")

    empty = sorted(bundle for bundle, skill_names in BUNDLES.items() if not skill_names)
    if empty:
        fail(f"Bundles must not be empty: {empty}")

    for bundle, skill_names in BUNDLES.items():
        duplicated = sorted({name for name in skill_names if skill_names.count(name) > 1})
        unknown = sorted(set(skill_names) - EXPECTED_RUNTIME_SKILLS)
        if duplicated:
            fail(f"{bundle} bundle has duplicate skills: {duplicated}")
        if unknown:
            fail(f"{bundle} bundle references unknown skills: {unknown}")


def validate_skill_graph_integrity() -> None:
    inbound: dict[str, set[str]] = {name: set() for name in EXPECTED_RUNTIME_SKILLS}
    broken: list[str] = []
    for skill_name, spec in ALL_V3_SKILLS.items():
        for next_step in spec.next_steps:
            if next_step not in ALL_V3_SKILLS:
                broken.append(f"{skill_name} -> {next_step}")
                continue
            inbound[next_step].add(skill_name)

    if broken:
        fail(f"Broken next_steps references: {broken}")

    orphans = sorted(name for name, sources in inbound.items() if not sources)
    if orphans:
        fail(f"Unintentional canonical skill orphans: {orphans}")


def validate_repo_hygiene() -> None:
    gitignore = REPO_ROOT / ".gitignore"
    if not gitignore.exists():
        fail(".gitignore is missing")
    patterns = {
        line.strip()
        for line in gitignore.read_text(encoding="utf-8", errors="ignore").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    missing_patterns = sorted(REQUIRED_GITIGNORE_PATTERNS - patterns)
    if missing_patterns:
        fail(f".gitignore is missing artifact patterns: {missing_patterns}")

    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        fail(f"git ls-files failed:\n{result.stderr}")
    tracked = result.stdout.splitlines()
    bad = [
        path
        for path in tracked
        if path.endswith(".egg-info")
        or ".egg-info/" in path
        or path.endswith(".pyc")
        or any(path.startswith(prefix) for prefix in REJECTED_TRACKED_PATH_PREFIXES)
    ]
    if bad:
        fail(f"Generated or bulky artifacts are tracked: {bad[:50]}")


def validate_adapter_targets() -> None:
    if ADAPTER_TARGETS["all"] != ALL_TARGETS:
        fail(f"ADAPTER_TARGETS['all'] drifted: {ADAPTER_TARGETS['all']}")
    if ADAPTER_TARGETS["antigravity"] != [".agent/skills"]:
        fail(f"ADAPTER_TARGETS['antigravity'] drifted: {ADAPTER_TARGETS['antigravity']}")
    if ADAPTER_TARGETS["generic"] != [GENERIC_CANONICAL_DIR]:
        fail(f"ADAPTER_TARGETS['generic'] drifted: {ADAPTER_TARGETS['generic']}")


def validate_list_output() -> None:
    output = run_cli(CANONICAL_ENTRYPOINT, "--list-skills")
    for bundle in ("core", "orchestration", "runtime", "discipline-utilities", "baseline", "enterprise"):
        if bundle not in output:
            fail(f"{CANONICAL_ENTRYPOINT} --list-skills output is missing bundle: {bundle}")


def validate_checked_in_docs() -> None:
    assert_contains(
        REPO_ROOT / "README.md",
        [
            "`--ai all`",
            "`--antigravity`",
            ".claude/skills",
            ".agent/skills",
            ".codex/skills",
            "baseline",
            "relay_kit.py",
            ".relay-kit-prompts",
            ".relay-kit/",
        ],
    )
    assert_contains(
        REPO_ROOT / "skills.manifest.yaml",
        [
            ".claude/skills",
            ".agent/skills",
            ".codex/skills",
            "core",
            "orchestration",
            "runtime",
            "baseline",
            "enterprise",
            ".relay-kit/state/workflow-state.md",
        ],
    )
    assert_contains(
        REPO_ROOT / ".relay-kit" / "docs" / "bundle-gating.md",
        ["core", "orchestration", "runtime", "baseline", "enterprise"],
    )


def validate_generated_bundle(bundle: str) -> None:
    expected_skills = set(BUNDLES[bundle])
    temp_dir = stable_temp_dir(REPO_ROOT, f"bundle-{bundle}")
    try:
        run_cli(
            CANONICAL_ENTRYPOINT,
            str(temp_dir),
            "--bundle",
            bundle,
            "--ai",
            "all",
            "--emit-contracts",
            "--emit-docs",
            "--emit-reference-templates",
        )

        generated_sets = {target: skill_dirs(temp_dir, target) for target in ALL_TARGETS}
        for target, current_set in generated_sets.items():
            assert_set(f"{bundle} generated skills for {target}", current_set, expected_skills)

        if bundle == "runtime":
            leaked = generated_sets[ALL_TARGETS[0]] & RUNTIME_DISCIPLINE_SKILLS
            if leaked:
                fail(f"runtime leaked discipline skills: {sorted(leaked)}")

        if bundle == "baseline":
            current = generated_sets[ALL_TARGETS[0]]
            missing = BASELINE_APPROVED - current
            unexpected = current & {"test-first-development"}
            if missing or unexpected:
                fail(
                    f"{bundle} discipline mismatch. "
                    f"Missing approved: {sorted(missing) or '-'} "
                    f"Unexpected: {sorted(unexpected) or '-'}"
                )

        if bundle == "discipline-utilities":
            current = generated_sets[ALL_TARGETS[0]]
            assert_set(
                "discipline-utilities bundle",
                current,
                {
                    "root-cause-debugging",
                    "test-first-development",
                    "evidence-before-completion",
                    "skill-evolution",
                },
            )

        if bundle == "enterprise":
            current = generated_sets[ALL_TARGETS[0]]
            missing = {"test-first-development", "policy-guard", "release-readiness"} - current
            if missing:
                fail(f"enterprise bundle missing expected governance skills: {sorted(missing)}")

        bundle_gating_doc = temp_dir / CANONICAL_ARTIFACT_ROOT / "docs" / "bundle-gating.md"
        if bundle_gating_doc.exists():
            assert_contains(bundle_gating_doc, ["core", "orchestration", "runtime", "baseline", "enterprise"])
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def validate_generated_generic_bundle(bundle: str) -> None:
    expected_files = {f"{name}.md" for name in BUNDLES[bundle]}
    temp_dir = stable_temp_dir(REPO_ROOT, f"generic-{bundle}")
    try:
        run_cli(
            CANONICAL_ENTRYPOINT,
            str(temp_dir),
            "--bundle",
            bundle,
            "--ai",
            "generic",
        )
        canonical = prompt_files(temp_dir, GENERIC_CANONICAL_DIR)
        if set(canonical) != expected_files:
            missing = sorted(expected_files - set(canonical))
            extra = sorted(set(canonical) - expected_files)
            fail(f"{bundle} generic prompt set mismatch. Missing: {missing or '-'} Extra: {extra or '-'}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def validate_public_wrapper_surface() -> None:
    run_public_cli("--list-skills")
    for adapter, target in (
        ("codex", ".codex/skills"),
        ("claude", ".claude/skills"),
        ("antigravity", ".agent/skills"),
    ):
        temp_dir = stable_temp_dir(REPO_ROOT, f"public-{adapter}")
        try:
            run_public_cli(str(temp_dir), f"--{adapter}")
            if not (temp_dir / target).exists():
                fail(f"Public wrapper failed to generate adapter target {target} for --{adapter}")
            if not (temp_dir / CANONICAL_ARTIFACT_ROOT).exists():
                fail(f"Public wrapper failed to emit {CANONICAL_ARTIFACT_ROOT} artifacts for --{adapter}")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def main() -> int:
    validate_adapter_targets()
    validate_repo_hygiene()
    validate_bundle_integrity()
    validate_skill_graph_integrity()
    validate_list_output()
    validate_checked_in_runtime()
    assert_skill_descriptions_trigger_first()
    validate_skill_gauntlet()
    validate_context_continuity_utility()
    validate_naming_guard()
    validate_checked_in_docs()
    for bundle in (
        "core",
        "orchestration-core",
        "orchestration",
        "runtime-core",
        "runtime",
        "utility-providers",
        "discipline-utilities",
        "baseline",
        "enterprise",
    ):
        validate_generated_bundle(bundle)
        validate_generated_generic_bundle(bundle)
    validate_public_wrapper_surface()
    print("Runtime validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
