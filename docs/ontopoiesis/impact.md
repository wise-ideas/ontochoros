---
title: "Impact analysis"
---

`ontopoiesis impact` traverses the semantic reference graph to answer two complementary
questions about a named entity in a built `.lbug` projection:

- **upstream** (`ontopoiesis impact upstream`): what constructs reference this entity,
  directly or transitively?
- **downstream** (`ontopoiesis impact downstream`): what constructs are reachable from this
  entity through semantic references?

Both directions print a table of constructs ordered by minimum traversal depth. The
`depth` column gives the shortest path between the reported construct and the seed entity;
depth 1 means a direct reference.

In the projection, every OWL construct is a node and structural relationships are
edges. An upstream traversal follows those edges in reverse — from the seed entity
back through the constructs that reference it. The result reports the full reachable
upstream path, including direct referring axioms, intermediate expressions, and the
`Ontology` root that ultimately contains them.

## Usage

Build the projection first:

```bash
ontopoiesis build family.owlxml -o family.lbug
```

Then run one of the two traversals:

```bash
ontopoiesis impact upstream family.lbug --iri http://example.org/hasChild
ontopoiesis impact downstream family.lbug --iri http://example.org/Father
ontopoiesis impact downstream family.lbug --uid n0
```

Pass exactly one seed selector: `--iri` for named entities, or `--uid` for any projected
construct.

## Upstream

Upstream reports every construct that can reach the seed through semantic reference
edges. The result answers "what statements and wrapper constructs mention this entity?"

On the bundled family ontology, `hasChild` is referenced by its `Declaration` and by the
`ObjectSomeValuesFrom` restriction that defines `Parent`, which the `EquivalentClasses`
axiom and the `Ontology` root reach in turn. The output is ordered by minimum traversal
depth:

```
  uid   kind                   depth   iri
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  n23   Declaration            1       None
  n40   ObjectSomeValuesFrom   1       None
  n39   EquivalentClasses      2       None
  n0    Ontology               2       None
```

(`uid` values are assigned in document order and are not stable across rebuilds.) On a
larger ontology the upstream result shows which class definitions, property axioms, and
annotation statements depend on the entity.

## Downstream

Downstream follows outgoing semantic reference edges from the seed node and reports
the reachable constructs.

In the projection, edges flow from axiom and expression nodes toward their constituent
named entities — not from entities outward. A `SubClassOf` axiom references its sub and
super class expressions via typed edges; those class expressions reference named classes.
Named classes, properties, and individuals are leaf nodes: they are destinations of edges
from axioms and expressions, but they have no outgoing edges of their own.

As a result, `ontopoiesis impact downstream` returns an empty result when the seed is a named
entity (class, property, or individual). On the bundled family ontology:

```bash
ontopoiesis impact downstream family.lbug --iri http://example.org/Father
```

```
No constructs found for http://example.org/Father.
```

This is expected behavior, not an error. For named entities, **upstream is the useful
direction**: it follows edges in reverse to find the axioms and wrapper constructs that
depend on the entity.

The downstream command becomes meaningful when the seed is a node that does have
outgoing edges — for example, an `Ontology` node with a resolvable IRI, or any
construct selected by `--uid`.

To see downstream in action, first retrieve the UID of the `Ontology` node:

```bash
ontopoiesis query family.lbug \
  -q "MATCH (n:N {kind: 'Ontology'}) RETURN n.uid AS uid, n.ontology_iri AS iri"
```

Then seed the downstream traversal with that UID:

```bash
ontopoiesis impact downstream family.lbug --uid <uid_from_above>
```

The result follows all outgoing semantic edges from the ontology node through its
axiom list, reaching every class, property, and individual that the ontology
directly or transitively contains:

```
  uid   kind                depth   iri
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  n7    Declaration         1       None
  n37   EquivalentClasses   1       None
  n41   SubClassOf          1       None
  n45   SubObjectPropertyOf 1       None
  n8    Class               2       http://example.org/Father
  n16   Class               2       http://example.org/Parent
  n36   Class               2       http://example.org/Person
  n40   ObjectSomeValuesFrom 2      None
  ...
```

On the bundled family ontology, this traversal reaches every projected construct —
because the `Ontology` node is the root from which all axioms are reachable.

On larger ontologies, seeding downstream from a specific axiom or expression node
(selected by `--uid`) produces a focused subgraph rather than the full projection,
which is more useful for understanding what a given structural pattern refers to.

## Troubleshooting

**`No constructs found for <iri>`.** The IRI was not found in the projection. Check
that the IRI is spelled and percent-encoded exactly as it appears in the ontology, and
that the projection was built from the correct source document. Use `ontopoiesis query` to
confirm:

```bash
ontopoiesis query graph.lbug -q "MATCH (n:N) WHERE n.iri = '<your-iri>' RETURN n.kind, n.uid"
```

If no row is returned, the entity is not in this projection. If the entity lives in an
imported ontology, merge the import closure into the source document before building
the projection.

**Upstream includes the `Ontology` root.** This is expected. Entities used in ontology
content are transitively reachable from the `Ontology` node that contains their axioms.
Read the lower-depth rows first when you want the direct axiom-level impact.

## Related

`ontopoiesis diff` compares construct sets across two projections rather than tracing
references within one. Use diff to find what changed between versions; use impact to
understand what else in the same projection depends on a given entity. See the
[Diff guide](diff.md) for the semantic fingerprint model and output format.
