from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    vault_root: Path
    db_path: Path
    documents_dir: Path
    logs_dir: Path


def resolve_vault_root(explicit: Path | None = None) -> Path:
    """
    Resolve vault root path priority:
    1) explicit argument
    2) PERDOCMAN_VAULT_ROOT environment variable
    3) default ./vault (relative to current working directory)
    """
    if explicit is not None:
        return Path(explicit)

    env = os.getenv("PERDOCMAN_VAULT_ROOT")
    if env:
        return Path(env)

    return Path("vault")


def build_paths(vault_root: Path | None = None) -> AppPaths:
    vr = resolve_vault_root(vault_root).resolve()
    return AppPaths(
        vault_root=vr,
        db_path=vr / "perdocman.db",
        documents_dir=vr / "documents",
        logs_dir=vr / "logs",
    )
