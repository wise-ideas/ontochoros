---
title: Public API
---

# Public API

The supported top-level public API (`ontoplexis.__all__`). The set is pinned by
`tests/test_public_contract.py`; names may be removed, never silently added.

## `Ontology`

One ontology held as its OWL/XML structural graph.

| Member | Purpose |
|---|---|
| `Ontology.from_owlxml(text)` | Parse an OWL/XML document |
| `Ontology.from_projection(projection)` | Rebuild from a (possibly Cypher-authored) projection |
| `.graph` | The `Graph` (nodes + edges) |
| `.to_owlxml()` | Serialize to OWL/XML |
| `.project()` | In-memory queryable projection |
| `.save_projection(path)` | Materialize to a `.lbug` file |

Documents in other serializations are pre-converted to OWL/XML with an
external tool; see [Work with Other Formats](../howto/documents.md).

!!! warning "Untrusted input"
    `from_owlxml` hands the text straight to the stdlib XML parser, which is
    not hardened against entity-expansion attacks. For documents you do not
    control, normalize the input through an external OWLAPI-based tool first
    (a `robot convert` pass, for example) so the walker only ever sees that
    tool's own OWL/XML output.

## `Projection` and `WritableProjection`

Ladybug database handles. Both are context managers.

| Member | Purpose |
|---|---|
| `Projection.open(path)` | Open an existing `.lbug` read-only |
| `.execute(query, parameters=None)` | Raw Cypher → `list[dict]` |
| `.graph()` | Load the full `Graph` back |
| `.node_count` / `.edge_count` / `.derived_count` | Counts |
| `.database_path` | The backing file |
| `.close()` | Release the handle |
| `WritableProjection.open(path=None)` | Open or create writable; omit `path` for a temp projection |
| `.reopen_readonly()` | Finalize as a read-only `Projection` |

`NODE_TABLE` (`"N"`), `RELATIONSHIP_TABLE` (`"E"`), and `DERIVED_TABLE`
(`"D"`) are exported for query building.

## Derived edges

| Member | Purpose |
|---|---|
| `derive_edges(writable)` | Rebuild the derived-edge cache `D` from current `N`/`E`; returns per-relation counts |

`build_projection`/`save_projection` (and therefore `Ontology.project()` and
`Ontology.save_projection()`) derive automatically; call `derive_edges` only
after mutating `N`/`E` yourself. See
[Derived Relations](derived.md) for the relation vocabulary.

## Graph shapes

| Name | Fields |
|---|---|
| `Node` | `uid`, `kind`, `properties: dict` (plus `.iri` convenience) |
| `Edge` | `source`, `target`, `position`, `role` |
| `Graph` | `nodes: tuple[Node, ...]`, `edges: tuple[Edge, ...]` |

The walkers themselves are importable from `ontoplexis.owlxml`
(`parse_owlxml`, `serialize_owlxml`) for use without a database.

## Errors

| Name | Raised when |
|---|---|
| `OwlXmlStructureError` | A document or graph violates the OWL/XML mapping contract |
| `ProjectionStorageError` | A projection cannot be opened or is closed |
