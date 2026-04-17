from __future__ import annotations

import hashlib
from pathlib import Path

from relay_kit_v3.generator import BUNDLES, bundle_skill_names, generate_relay_bundle


def _hash_map(base: Path, paths: list[Path]) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in paths:
        relative = path.relative_to(base).as_posix()
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def test_bundle_skill_names_deduplicates_without_reordering() -> None:
    for bundle_name, raw_names in BUNDLES.items():
        assert bundle_skill_names(bundle_name) == list(dict.fromkeys(raw_names))


def test_generate_relay_bundle_is_idempotent_and_sorted(tmp_path: Path) -> None:
    project = tmp_path / "idempotent-project"
    project.mkdir()

    kwargs = {
        "ai": "all",
        "bundle": "baseline",
        "with_contracts": True,
        "with_docs": True,
        "with_reference_templates": True,
    }

    first = generate_relay_bundle(str(project), **kwargs)
    second = generate_relay_bundle(str(project), **kwargs)

    first_rel = [path.relative_to(project).as_posix() for path in first]
    second_rel = [path.relative_to(project).as_posix() for path in second]

    assert first_rel == sorted(set(first_rel))
    assert second_rel == first_rel
    assert _hash_map(project, first) == _hash_map(project, second)
