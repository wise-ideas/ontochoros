---
title: "The Projection Graph Model"
---

Ontopoiesis's Cypher surface is built on a projection of the OWL 2 structural specification
into a labelled property graph. Understanding that design makes the query patterns in
the [queries reference](queries.md) much easier to read and write.

## The central idea: axioms as nodes

In RDF/OWL, axioms are encoded as triples. A `SubClassOf` relationship is a triple:
subject → predicate → object. Complex axioms like existential restrictions require
blank nodes and multiple triples to encode. There is no single "axiom object" to address
directly — only a pattern of triples to match.

Ontopoiesis's projection takes a different approach: it stores every OWL 2 construct —
every axiom, every class expression, every property expression — as a **node** in a
single node table called `N`. Structural relationships between constructs become
**edges** in a single edge table called `E`.

This is not an arbitrary design. It mirrors the OWL 2 structural specification directly.
The specification defines OWL 2 syntax in terms of a grammar of nested constructs:
`SubClassOf` takes two class expressions; `EquivalentClasses` takes a set of class
expressions; `ObjectSomeValuesFrom` takes a property expression and a class expression.
The projection maps each construct in that grammar to a node, and each structural
relationship to a typed edge.

## The N table

Every node in `N` carries:

- `kind` — the OWL 2 construct name, taken directly from the structural specification
  (e.g., `SubClassOf`, `EquivalentClasses`, `ObjectSomeValuesFrom`)
- `uid` — a stable content-addressed identifier for this node within a projection

Named entities (classes, properties, individuals, datatypes) also carry:

- `iri` — the expanded IRI of the entity

Axioms and anonymous constructs have no `iri`. You identify them by `kind` and navigate
to their participants via edges.

Literal nodes (`StringLiteralNoLanguage`, `StringLiteralWithLanguage`, `TypedLiteral`)
carry additional properties depending on their form:

- `quoted_string` — the string value for `StringLiteralNoLanguage` and
  `StringLiteralWithLanguage`
- `language_tag` — the language tag for `StringLiteralWithLanguage` (e.g. `'en'`)
- `lexical_form` — the lexical value for `TypedLiteral`
- `datatype_iri` — the datatype IRI for `TypedLiteral`

Use `COALESCE(val.quoted_string, val.lexical_form)` when you want the string value
regardless of literal type.

Some construct types carry additional properties beyond `kind` and `uid`. See the
[constructs reference](constructs.md#node-and-edge-properties) for a complete listing.

## The E table

Every edge in `E` carries a `role` property that names the structural field it
represents. Role names come directly from the OWL 2 structural specification field
names:

| Example role                 | What it represents                                     |
| ---------------------------- | ------------------------------------------------------ |
| `sub_class_expression`       | The subclass side of a `SubClassOf`                    |
| `super_class_expression`     | The superclass side of a `SubClassOf`                  |
| `class_expressions`          | Members of an `EquivalentClasses` or `DisjointClasses` |
| `object_property_expression` | The property in an `ObjectSomeValuesFrom`              |
| `class_expression`           | The filler in an `ObjectSomeValuesFrom`                |
| `annotation_property`        | The property in an `AnnotationAssertion`               |
| `annotation_value`           | The value in an `AnnotationAssertion`                  |

If you know the OWL 2 structural specification field name for a construct, you already
know the `role` value to use in a query. The projection is not a re-encoding; it is a
direct graph representation of the same structure the spec defines.

Edges on ordered list fields also carry `endpoint_order` — a one-based integer giving
the position of this edge in the ordered list. Property chain steps, disjoint union
members, and ontology-level axiom sequences use `endpoint_order`.

## Why this shape helps

The projection model has two practical consequences for query writing.

**Existential restrictions are directly navigable.** In SPARQL, you match blank-node
triples to recover a restriction. In Ontopoiesis, the restriction is a node:

```cypher
MATCH (ax:N {kind: 'SubClassOf'})
      -[:E {role: 'sub_class_expression'}]->(sub:N {kind: 'Class'}),
      (ax)-[:E {role: 'super_class_expression'}]->(restriction:N {kind: 'ObjectSomeValuesFrom'})
      -[:E {role: 'object_property_expression'}]->(prop:N),
      (restriction)-[:E {role: 'class_expression'}]->(filler:N)
WHERE sub.iri IS NOT NULL AND prop.iri IS NOT NULL
RETURN sub.iri AS class, prop.iri AS property,
       COALESCE(filler.iri, filler.kind) AS filler
ORDER BY class, property
```

**N-ary axioms are flat fan-outs.** An `EquivalentClasses` axiom with three members has
three edges from the axiom node, all with role `class_expressions`. An
`ObjectIntersectionOf` with four operands has four edges with role `operands`. No
membership list structure to unwrap:

```cypher
MATCH (ax:N {kind: 'DisjointClasses'})
      -[:E {role: 'class_expressions'}]->(cls:N)
WHERE cls.iri IS NOT NULL
RETURN ax.uid AS axiom, cls.iri AS class
ORDER BY axiom, class
```

**Queries compose across constructs.** Because axioms are nodes, a path that crosses
multiple axiom boundaries is just a graph traversal. Finding classes that appear both
as the subject of an existential restriction and as a disjoint class member is a single
connected match, not a join between SPARQL subqueries.

## The `uid` and content-addressing

Every node in the projection carries a `uid` — a content-addressed key derived from the
structural identity of the construct.

Within a single ingestion run, the parser assigns UIDs as sequential integers in traversal
order (`0x1`, `0x2`, and so on). The projection deduplicates shared structure: two axioms
referencing the same class expression share a node and therefore the same UID. But the
same axiom deserialized from two different documents will carry different sequential UIDs,
because traversal order can differ.

This is why content-addressing matters: **the UID of a construct depends only on its
structural content**, not on traversal order. Rebuilding the same OWL/XML ontology assigns
the same `uid` to the same construct regardless of prefix declarations or element ordering.

`ontopoiesis diff` uses the same scheme for fingerprinting. At the axiom level, "changed"
does not exist as a concept:
if `SubClassOf(:A :B)` becomes `SubClassOf(:A :C)`, the first fingerprint disappears
(removed) and a new one appears (added). No in-place modification occurs — the two
are genuinely distinct OWL axioms, each with its own content-addressed key.

The `uid` is stable within a single projection run but recomputed on rebuild. Do not
store `uid` values as durable external identifiers; use `iri` for named entities instead.
The same content-addressing model underlies the migration workflow — see
[Migrations](migrations.md) for how it is used for `MERGE` idempotence in versioned
Cypher scripts.

## What is not in the projection

The projection represents the explicitly stated axioms in one OWL document. It does not
include:

- inferred axioms (entailments from a reasoner) unless the document contains them
  explicitly — use an external reasoner to materialize them in OWL/XML first
- SWRL rules — these are not part of the OWL 2 structural specification
- RDF-level constructs beyond OWL Full — the projection covers OWL 2 structural
  semantics, not arbitrary RDF graphs

### Import handling

`ontopoiesis build` records every `owl:imports` declaration in the source document as an
`Import` node in the projection. The imported IRI is stored as a node property, so you
can query the declarations directly:

```cypher
MATCH (n:N {kind: 'Import'}) RETURN n.iri AS imported_iri ORDER BY imported_iri
```

What Ontopoiesis does **not** do during `build` is fetch or merge the imported ontology
content. Queries, lint rules, rendering, and impact analysis therefore operate on the
source document's explicitly stated constructs only. Imported declarations, labels, and
annotations can be absent from the projection even when they exist in the full import
closure.

This matters most for checks that depend on declaration or annotation completeness. An
import-heavy ontology can produce projection-level findings such as "missing label" or
"undeclared entity" when the owning vocabulary lives in an imported module. Treat those
as source-document findings unless you first merge the import closure into one OWL
document before building.

If reasoning or import resolution is required, do it with an external tool and build from
the resulting OWL/XML document. Reasoning against an incomplete import closure would make
the result misleading.
