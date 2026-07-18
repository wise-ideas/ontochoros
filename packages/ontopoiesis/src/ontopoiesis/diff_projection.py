"""Structural diffing of two projections by local subtree fingerprints.

Node uids are not stable across builds, so the diff compares multisets of
per-construct fingerprints: one fingerprint per top-level construct (each
child of an Ontology node — axioms, prefixes, imports). A construct edited
in place therefore reports as one removal plus one addition.
"""

from __future__ import annotations

import hashlib
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from ontoplexis import Edge, Graph, Projection

_log = logging.getLogger(__name__)

_FINGERPRINT_DISPLAY_LENGTH = 12
_CYCLE_MARKER = "\x00cycle"


@dataclass(frozen=True)
class DiffRow:
    status: str
    kind: str
    iri: str
    count: int
    fingerprint: str
    ontology_iri: str | None = None


@dataclass(frozen=True)
class _DiffEntry:
    kind: str
    iri: str | None
    fingerprint: str
    ontology_iri: str | None


def diff_projections(before_path: Path, after_path: Path) -> list[DiffRow]:
    """Return added or removed construct fingerprints between two projections."""
    _log.info("Diffing projections: %s vs %s", before_path, after_path)
    before_entries = _load_projection_entries(before_path)
    after_entries = _load_projection_entries(after_path)
    rows = _diff_rows(before_entries, after_entries)
    _log.info(
        "Diff complete: %d changed entries (%d before, %d after)",
        len(rows),
        len(before_entries),
        len(after_entries),
    )
    return rows


def _load_projection_entries(path: Path) -> list[_DiffEntry]:
    with Projection.open(path) as projection:
        graph = projection.graph()
    return _fingerprint_graph_constructs(graph)


def _fingerprint_graph_constructs(graph: Graph) -> list[_DiffEntry]:
    """Fingerprint every top-level construct (child of an Ontology node)."""
    nodes_by_uid = {node.uid: node for node in graph.nodes}
    children: dict[str, list[Edge]] = defaultdict(list)
    for edge in graph.edges:
        children[edge.source].append(edge)
    for edges in children.values():
        edges.sort(key=lambda edge: edge.position)

    fingerprints: dict[str, str] = {}

    def fingerprint(uid: str) -> str:
        memoized = fingerprints.get(uid)
        if memoized is not None:
            return memoized
        fingerprints[uid] = _CYCLE_MARKER
        node = nodes_by_uid.get(uid)
        if node is None:
            digest = _digest(["missing", uid])
        else:
            parts = [node.kind]
            parts.extend(f"{name}={value}" for name, value in sorted(node.properties.items()))
            for edge in children.get(uid, ()):
                child_fingerprint = fingerprint(edge.target)
                if child_fingerprint == _CYCLE_MARKER:
                    child_fingerprint = _digest(["cycle", edge.target])
                parts.append(f"{edge.role or ''}>{child_fingerprint}")
            digest = _digest(parts)
        fingerprints[uid] = digest
        return digest

    def first_iri(uid: str, seen: set[str]) -> str | None:
        if uid in seen:
            return None
        seen.add(uid)
        node = nodes_by_uid.get(uid)
        if node is None:
            return None
        own_iri = node.properties.get("iri")
        if isinstance(own_iri, str):
            return own_iri
        for edge in children.get(uid, ()):
            child_iri = first_iri(edge.target, seen)
            if child_iri is not None:
                return child_iri
        return None

    entries: list[_DiffEntry] = []
    for node in graph.nodes:
        if node.kind != "Ontology":
            continue
        raw_ontology_iri = node.properties.get("ontology_iri")
        ontology_iri = raw_ontology_iri if isinstance(raw_ontology_iri, str) else None
        for edge in children.get(node.uid, ()):
            child = nodes_by_uid.get(edge.target)
            if child is None:
                continue
            entries.append(
                _DiffEntry(
                    kind=child.kind,
                    iri=first_iri(child.uid, set()),
                    fingerprint=fingerprint(child.uid)[:_FINGERPRINT_DISPLAY_LENGTH],
                    ontology_iri=ontology_iri,
                )
            )
    return entries


def _digest(parts: list[str]) -> str:
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()


def _diff_rows(before_entries: list[_DiffEntry], after_entries: list[_DiffEntry]) -> list[DiffRow]:
    before_counts = Counter(before_entries)
    after_counts = Counter(after_entries)
    rows: list[DiffRow] = []
    for entry in sorted(
        set(before_counts) | set(after_counts),
        key=lambda e: (e.kind, e.iri or "", e.fingerprint),
    ):
        delta = after_counts[entry] - before_counts[entry]
        if delta == 0:
            continue
        rows.append(
            DiffRow(
                status="added" if delta > 0 else "removed",
                kind=entry.kind,
                iri=entry.iri or "",
                count=abs(delta),
                fingerprint=entry.fingerprint,
                ontology_iri=entry.ontology_iri,
            )
        )
    rows.sort(key=lambda row: (row.status, row.kind, row.iri, row.fingerprint))
    return rows
