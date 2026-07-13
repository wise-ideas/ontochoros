"""Stable UID helpers for graph-native migration templates."""

from __future__ import annotations

import hashlib
from collections.abc import Sequence

MIGRATION_UID_DIGEST_HEX_LENGTH = 32
MIGRATION_UID_SCALAR_NAMESPACE = "ontopoiesis:migration:scalar:v1"
MIGRATION_UID_AXIOM_NAMESPACE = "ontopoiesis:migration:axiom:v1"


def scalar_uid(kind: str, value: str) -> str:
    """Return a stable UID for a named scalar construct in a migration."""
    return _migration_uid(MIGRATION_UID_SCALAR_NAMESPACE, kind, value)


def axiom_uid(kind: str, edge_specs: Sequence[tuple[str, str]]) -> str:
    """Return a stable UID for an axiom or anonymous expression by edge shape."""
    edge_key = "|".join(f"{index}:{role}={uid}" for index, (role, uid) in enumerate(edge_specs))
    return _migration_uid(MIGRATION_UID_AXIOM_NAMESPACE, kind, edge_key)


def _migration_uid(namespace: str, kind: str, key: str) -> str:
    payload = "\x1f".join((namespace, kind, key))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"0x{digest[:MIGRATION_UID_DIGEST_HEX_LENGTH]}"
