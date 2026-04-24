"""Compatibility shim for the previous runtime package name."""

from __future__ import annotations

import importlib
import sys


_PRIMARY_PACKAGE = "relay_kit_v3"
_SUBMODULES = [
    "adapters",
    "generator",
    "registry",
    "registry.artifacts",
    "registry.gating",
    "registry.skills",
    "registry.support_refs",
    "registry.topology",
    "registry.workflows",
]


def _install_aliases() -> None:
    primary = importlib.import_module(_PRIMARY_PACKAGE)
    globals().update({name: getattr(primary, name) for name in getattr(primary, "__all__", []) if hasattr(primary, name)})

    for submodule in _SUBMODULES:
        alias = f"{__name__}.{submodule}"
        target = importlib.import_module(f"{_PRIMARY_PACKAGE}.{submodule}")
        sys.modules[alias] = target

    globals()["adapters"] = sys.modules[f"{__name__}.adapters"]
    globals()["generator"] = sys.modules[f"{__name__}.generator"]
    globals()["registry"] = sys.modules[f"{__name__}.registry"]


_install_aliases()

__all__ = ["adapters", "generator", "registry"]
