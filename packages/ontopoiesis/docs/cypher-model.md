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
- `uid` — a within-projection id, assigned in document order (`n0`, `n1`, …); not stable
  across rebuilds

Named entities (classes, properties, individuals, datatypes) also carry:

- `iri` — the expanded IRI of the entity

Axioms and anonymous constructs have no `iri`. You identify them by `kind` and navigate
to their participants via edges.

Literal values are a single node kind, `Literal`, carrying:

- `text` — the lexical value (`"Dog"`, `"42"`)
- `lang` — the language tag when present (`'en'`), otherwise null
- `datatype_iri` — the datatype IRI when the literal is typed

So the string value is just `val.text`, regardless of whether the literal is plain,
language-tagged, or typed.

Some construct types carry additional properties beyond `kind` and `uid`. See the
[constructs reference](constructs.md#node-and-edge-properties) for a complete listing.

## The E table

Every edge in `E` carries a `role` property that names the structural field it
represents. Roles are short, query-facing names assigned from the parent construct's
kind and the child's position among its arguments:

| Example role | What it represents                                     |
| ------------ | ------------------------------------------------------ |
| `sub`        | The subclass side of a `SubClassOf`                    |
| `super`      | The superclass side of a `SubClassOf`                  |
| `operand`    | Members of an `EquivalentClasses` or `DisjointClasses` |
| `property`   | The property in an `ObjectSomeValuesFrom` or assertion |
| `filler`     | The filler in an `ObjectSomeValuesFrom`                |
| `subject`    | The subject of an `AnnotationAssertion` or assertion   |
| `value`      | The value in an `AnnotationAssertion`                  |

The full role vocabulary — every construct and the roles it uses — is the
[Ontoplexis edge-roles reference](https://wise-ideas.github.io/ontotheke/ontoplexis/reference/roles/),
mirrored per construct in the [constructs reference](constructs.md#structural-edge-roles).
Roles are decoration; the property that actually round-trips is `position`.

Every edge also carries `position` — the child's zero-based index in document order
under its parent. It is what preserves ordered fields (property chain steps, ontology
axiom order) and what serialization uses to reconstruct the document. Query it to
recover the order of an ordered list.

## The D table

A third table, `D`, holds **derived edges**: the common binary relations
(`subclass_of`, `type`, `domain`, `range`, `annotation_value`, …) mechanically
collapsed from the structural graph so they are one hop instead of a walk
through an axiom node. Each edge carries a `relation` name, plus `property`
and `quantifier` where the relation needs them.

```cypher
MATCH (a:N)-[:D {relation: 'subclass_of'}]->(b:N)
RETURN a.iri AS sub_iri, b.iri AS super_iri
```

`D` is a refreshable cache over `N`/`E` — asserted structure only, no
reasoning — and is rebuilt by `ontopoiesis build` and `ontopoiesis migrate`.
Export and diff never read it. The relation vocabulary is documented in the
[Ontoplexis derived-relations reference](https://wise-ideas.github.io/ontotheke/ontoplexis/reference/derived/).

## Why this shape helps

The projection model has two practical consequences for query writing.

**Existential restrictions are directly navigable.** In SPARQL, you match blank-node
triples to recover a restriction. In Ontopoiesis, the restriction is a node:

```cypher
MATCH (ax:N {kind: 'SubClassOf'})
      -[:E {role: 'sub'}]->(sub:N {kind: 'Class'}),
      (ax)-[:E {role: 'super'}]->(restriction:N {kind: 'ObjectSomeValuesFrom'})
      -[:E {role: 'property'}]->(prop:N),
      (restriction)-[:E {role: 'filler'}]->(filler:N)
WHERE sub.iri IS NOT NULL AND prop.iri IS NOT NULL
RETURN sub.iri AS class, prop.iri AS property,
       COALESCE(filler.iri, filler.kind) AS filler
ORDER BY class, property
```

**N-ary axioms are flat fan-outs.** An `EquivalentClasses` axiom with three members has
three edges from the axiom node, all with role `operand`. An `ObjectIntersectionOf` with
four operands has four edges with role `operand`. No membership list structure to unwrap:

```cypher
MATCH (ax:N {kind: 'DisjointClasses'})
      -[:E {role: 'operand'}]->(cls:N)
WHERE cls.iri IS NOT NULL
RETURN ax.uid AS axiom, cls.iri AS class
ORDER BY axiom, class
```

**Queries compose across constructs.** Because axioms are nodes, a path that crosses
multiple axiom boundaries is just a graph traversal. Finding classes that appear both
as the subject of an existential restriction and as a disjoint class member is a single
connected match, not a join between SPARQL subqueries.

## The `uid`

Every node in the projection carries a `uid`. On a `build`, the parser assigns UIDs as
sequential ids in document order (`n0`, `n1`, and so on). Named entities and leaf values
are deduplicated: two axioms referencing the same class share one node and therefore one
`uid`. But the ids are positional, not content-derived, so **`uid` values are not stable
across rebuilds** — traversal order, and therefore the numbers, can differ from build to
build. Use `iri` for named entities as your durable identifier; treat `uid` as a
within-projection handle only.

Because uids are not stable, `ontopoiesis diff` does not compare them. It fingerprints
each construct structurally over the graph, so "changed" does not exist at the axiom
level: if `SubClassOf(:A :B)` becomes `SubClassOf(:A :C)`, the first fingerprint
disappears (removed) and a new one appears (added) — two genuinely distinct OWL axioms.

Migrations need the opposite property — a **deterministic** id so that re-running a script
`MERGE`s the existing node instead of duplicating it. They get it from the
`scalar_uid`/`axiom_uid` template helpers, which content-address a construct from its kind
and structure into a stable `0x`-prefixed digest. That is a separate, migration-only
scheme from the sequential build-time uids; see [Migrations](migrations.md).

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
