---
title: Author with Cypher
---

# Author with Cypher

Projections are graphs all the way down, so Cypher writes are the editing
model — for migrations, bulk edits, or building ontologies from scratch.

## The contract

For a complete, serializable ontology, an authored graph should have:

- exactly one parentless node with `kind: 'Ontology'`
- every non-root node reachable from it through `:E` edges
- sibling edges carry distinct `position` values (child order)
- node properties match what the element kind allows (see
  [The Graph Schema](../concepts/schema.md))

`to_owlxml()` requires exactly one parentless `Ontology` node and rejects dangling edge
references, reachable cycles, and duplicate reachable sibling positions. It does not reject
unreachable nodes, multiply parented nodes, or property/kind mismatches, so authoring code
must avoid those conditions. `role` values on edges are optional decoration; only `position`
matters for serialization.

## Example: build a tiny ontology from nothing

```python
from ontoplexis import Ontology, WritableProjection

wp = WritableProjection.open("authored.lbug")
wp.execute("CREATE (:N {uid: 'o', kind: 'Ontology', ontology_iri: 'http://example.org/x'})")
wp.execute("CREATE (:N {uid: 'd', kind: 'Declaration'})")
wp.execute("CREATE (:N {uid: 'c', kind: 'Class', iri: 'http://example.org/x#A'})")
wp.execute(
    "MATCH (o:N {uid:'o'}), (d:N {uid:'d'}) "
    "CREATE (o)-[:E {position: 0, role: 'axiom'}]->(d)"
)
wp.execute(
    "MATCH (d:N {uid:'d'}), (c:N {uid:'c'}) "
    "CREATE (d)-[:E {position: 0, role: 'entity'}]->(c)"
)
proj = wp.reopen_readonly()

ont = Ontology.from_projection(proj)
print(ont.to_owlxml())
```

## Validation

Two layers catch mistakes:

1. **Structure** — `serialize_owlxml` (called by `to_owlxml`) rejects graphs
   with no root, multiple roots, reachable cycles, dangling edges, or duplicate
   reachable sibling positions, with a precise error.
2. **OWL/XML parsing** — parse the serialized document with an external
   OWLAPI-based tool such as `robot convert`.
3. **Reasoning** — use `robot reason` with an appropriate reasoner when you
   need a consistency or entailment check. Ontoplexis does not provide a
   separate semantic rule engine.

!!! tip "Refresh derived edges"
    Cypher writes touch only the structural tables, so the derived-edge cache
    `D` goes stale. Call `derive_edges(wp)` after authoring if you (or your
    lint rules) query derived relations.

!!! tip "Migrations"
    Because authoring is plain Cypher against a `.lbug` file, a migration
    system is just an ordered directory of `.cypher` files plus a bookkeeping
    table — no ontology-specific machinery required.
