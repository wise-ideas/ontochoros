---
title: "Queries"
---

`ontopoiesis query` runs Cypher against a `.lbug` projection and prints the results as a
table. Build the projection first with [`ontopoiesis build`](cli.md#build), then query it
repeatedly without re-parsing the source OWL document.

```bash
ontopoiesis query graph.lbug -q "MATCH (n:N) RETURN DISTINCT n.kind AS kind ORDER BY kind"
```

This page is a reference catalogue of Cypher patterns for querying a `.lbug`
projection by OWL 2 construct category. The sections are organized around common query
tasks: discovery, class hierarchy, property patterns, annotations, individuals, and
other structural lookups. For the graph shape those queries target, see
[The Projection Graph Model](cypher-model.md). For the canonical construct kind names
used in `kind` filters, see [OWL 2 Construct Coverage](constructs.md).

Jump to:

- [Discovery](#discovery)
- [Class hierarchy](#class-hierarchy)
- [Object properties](#object-properties)
- [Property characteristics](#property-characteristics)
- [Data properties](#data-properties)
- [Cardinality restrictions](#cardinality-restrictions)
- [Individuals and assertions](#individuals-and-assertions)
- [Ontology structure](#ontology-structure)
- [Annotation assertions](#annotation-assertions)
- [SPARQL comparison](#sparql-comparison)
- [Troubleshooting](#troubleshooting)

## Discovery

Discover what construct kinds are present in a projection:

```cypher
MATCH (n:N) RETURN DISTINCT n.kind AS kind ORDER BY kind
```

On the bundled family ontology:

```
  kind
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Class
  Declaration
  DisjointClasses
  EquivalentClasses
  NamedIndividual
  NegativeObjectPropertyAssertion
  ObjectHasSelf
  ObjectIntersectionOf
  ObjectProperty
  ObjectPropertyChain
  ObjectSomeValuesFrom
  Ontology
  Prefix
  SubClassOf
  SubObjectPropertyOf
```

List all named classes:

```cypher
MATCH (n:N {kind: 'Class'})
WHERE n.iri IS NOT NULL
RETURN n.iri AS iri ORDER BY iri
```

List all object properties:

```cypher
MATCH (n:N {kind: 'ObjectProperty'})
WHERE n.iri IS NOT NULL
RETURN n.iri AS iri ORDER BY iri
```

Count constructs by kind:

```cypher
MATCH (n:N)
RETURN n.kind AS kind, count(*) AS count
ORDER BY count DESC, kind
```

## Class hierarchy

Named subclass relationships:

```cypher
MATCH (ax:N {kind: 'SubClassOf'})
      -[:E {role: 'sub'}]->(sub:N {kind: 'Class'}),
      (ax)-[:E {role: 'super'}]->(sup:N {kind: 'Class'})
WHERE sub.iri IS NOT NULL AND sup.iri IS NOT NULL
RETURN sub.iri AS subclass, sup.iri AS superclass
ORDER BY subclass
```

Against the family sample ontology, which uses complex class expressions as superclasses,
this query returns no rows. On ontologies with direct named-class-to-named-class
subclass axioms — like the GO slim — this query returns a row per asserted relationship.
See the [GO slim example](go-slim.md#4-subclass-hierarchy-and-existential-restrictions)
for a worked demonstration.

Classes with no named superclass (root classes):

```cypher
MATCH (cls:N {kind: 'Class'})
WHERE cls.iri IS NOT NULL
  AND NOT EXISTS {
    MATCH (ax:N {kind: 'SubClassOf'})
          -[:E {role: 'sub'}]->(cls),
          (ax)-[:E {role: 'super'}]->(sup:N {kind: 'Class'})
    WHERE sup.iri IS NOT NULL
  }
RETURN cls.iri AS root_class
ORDER BY root_class
```

On the bundled family ontology:

```
  root_class
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  http://example.org/Father
  http://example.org/Man
  http://example.org/Mother
  http://example.org/NarcisticPerson
  http://example.org/Parent
  http://example.org/Person
  http://example.org/YoungChild
```

Named equivalence relationships:

```cypher
MATCH (ax:N {kind: 'EquivalentClasses'})
      -[:E {role: 'operand'}]->(cls:N {kind: 'Class'})
WHERE cls.iri IS NOT NULL
RETURN ax.uid AS axiom, cls.iri AS class
ORDER BY axiom, class
```

On the bundled family ontology:

```
  axiom   class
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  n37     http://example.org/NarcisticPerson
  n39     http://example.org/Parent
```

(`uid` values like `n37` are assigned in document order and are not stable across
rebuilds — filter and join on `iri`, not `uid`.)

Classes defined by existential restriction:

```cypher
MATCH (ax:N {kind: 'EquivalentClasses'})
      -[:E {role: 'operand'}]->(cls:N {kind: 'Class'}),
      (ax)-[:E {role: 'operand'}]->(restriction:N {kind: 'ObjectSomeValuesFrom'})
      -[:E {role: 'property'}]->(prop:N {kind: 'ObjectProperty'})
WHERE cls.iri IS NOT NULL AND prop.iri IS NOT NULL
RETURN cls.iri AS class, prop.iri AS via_property
ORDER BY class
```

## Object properties

Sub-property relationships:

```cypher
MATCH (ax:N {kind: 'SubObjectPropertyOf'})
      -[:E {role: 'sub'}]->(sub:N),
      (ax)-[:E {role: 'super'}]->(sup:N)
WHERE sub.iri IS NOT NULL AND sup.iri IS NOT NULL
RETURN sub.iri AS sub_property, sup.iri AS super_property
ORDER BY sub_property
```

Against the bundled family ontology, this query returns no rows because its
`SubObjectPropertyOf` axioms use property chains rather than named sub-property links.

Property chains — ordered links of a `SubObjectPropertyOf` chain clause:

```cypher
MATCH (ax:N {kind: 'SubObjectPropertyOf'})
      -[:E {role: 'super'}]->(sup:N),
      (ax)-[:E {role: 'sub'}]->(:N {kind: 'ObjectPropertyChain'})
      -[link:E {role: 'operand'}]->(step:N)
WHERE sup.iri IS NOT NULL AND step.iri IS NOT NULL
RETURN sup.iri AS property, step.iri AS chain_step, link.position AS position
ORDER BY property, position
```

On the bundled family ontology:

```
  property                      chain_step                      position
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  http://example.org/hasUncle   http://example.org/hasFather   0
  http://example.org/hasUncle   http://example.org/hasBrother  1
```

## Property characteristics

Transitive object properties:

```cypher
MATCH (n:N {kind: 'TransitiveObjectProperty'})
      -[:E {role: 'property'}]->(prop:N)
WHERE prop.iri IS NOT NULL
RETURN prop.iri AS property
ORDER BY property
```

Functional object properties:

```cypher
MATCH (n:N {kind: 'FunctionalObjectProperty'})
      -[:E {role: 'property'}]->(prop:N)
WHERE prop.iri IS NOT NULL
RETURN prop.iri AS property
ORDER BY property
```

Annotation property domains and ranges:

```cypher
MATCH (ax:N {kind: 'AnnotationPropertyDomain'})
      -[:E {role: 'property'}]->(prop:N),
      (ax)-[:E {role: 'domain'}]->(dom:N)
WHERE prop.iri IS NOT NULL
RETURN prop.iri AS property, COALESCE(dom.iri, dom.kind) AS domain
ORDER BY property
```

```cypher
MATCH (ax:N {kind: 'AnnotationPropertyRange'})
      -[:E {role: 'property'}]->(prop:N),
      (ax)-[:E {role: 'range'}]->(rng:N)
WHERE prop.iri IS NOT NULL
RETURN prop.iri AS property, COALESCE(rng.iri, rng.kind) AS range
ORDER BY property
```

## Data properties

List all data properties:

```cypher
MATCH (n:N {kind: 'DataProperty'})
WHERE n.iri IS NOT NULL
RETURN n.iri AS iri ORDER BY iri
```

Data property domain:

```cypher
MATCH (ax:N {kind: 'DataPropertyDomain'})
      -[:E {role: 'property'}]->(prop:N),
      (ax)-[:E {role: 'domain'}]->(cls:N)
WHERE prop.iri IS NOT NULL AND cls.iri IS NOT NULL
RETURN prop.iri AS property, cls.iri AS domain
ORDER BY property
```

Data property range:

```cypher
MATCH (ax:N {kind: 'DataPropertyRange'})
      -[:E {role: 'property'}]->(prop:N),
      (ax)-[:E {role: 'range'}]->(rng:N)
WHERE prop.iri IS NOT NULL
RETURN prop.iri AS property, COALESCE(rng.iri, rng.kind) AS range
ORDER BY property
```

Data property assertions:

```cypher
MATCH (ax:N {kind: 'DataPropertyAssertion'})
      -[:E {role: 'subject'}]->(src:N),
      (ax)-[:E {role: 'property'}]->(prop:N),
      (ax)-[:E {role: 'object'}]->(val:N)
WHERE src.iri IS NOT NULL AND prop.iri IS NOT NULL
RETURN src.iri AS source,
       prop.iri AS property,
       val.text AS value
ORDER BY source, property
```

## Cardinality restrictions

Minimum cardinality restrictions in subclass axioms:

```cypher
MATCH (ax:N {kind: 'SubClassOf'})
      -[:E {role: 'sub'}]->(cls:N {kind: 'Class'}),
      (ax)-[:E {role: 'super'}]->(card:N {kind: 'ObjectMinCardinality'})
      -[:E {role: 'property'}]->(prop:N)
WHERE cls.iri IS NOT NULL AND prop.iri IS NOT NULL
RETURN cls.iri AS class, prop.iri AS property, card.cardinality AS min_count
ORDER BY class, property
```

Maximum cardinality restrictions:

```cypher
MATCH (ax:N {kind: 'SubClassOf'})
      -[:E {role: 'sub'}]->(cls:N {kind: 'Class'}),
      (ax)-[:E {role: 'super'}]->(card:N {kind: 'ObjectMaxCardinality'})
      -[:E {role: 'property'}]->(prop:N)
WHERE cls.iri IS NOT NULL AND prop.iri IS NOT NULL
RETURN cls.iri AS class, prop.iri AS property, card.cardinality AS max_count
ORDER BY class, property
```

Exact cardinality restrictions:

```cypher
MATCH (ax:N {kind: 'SubClassOf'})
      -[:E {role: 'sub'}]->(cls:N {kind: 'Class'}),
      (ax)-[:E {role: 'super'}]->(card:N {kind: 'ObjectExactCardinality'})
      -[:E {role: 'property'}]->(prop:N)
WHERE cls.iri IS NOT NULL AND prop.iri IS NOT NULL
RETURN cls.iri AS class, prop.iri AS property, card.cardinality AS exact_count
ORDER BY class, property
```

Has-key axioms:

```cypher
MATCH (ax:N {kind: 'HasKey'})
      -[:E {role: 'class'}]->(cls:N {kind: 'Class'})
WHERE cls.iri IS NOT NULL
RETURN cls.iri AS class, ax.uid AS has_key_axiom
ORDER BY class
```

## Individuals and assertions

All named individuals and their explicitly asserted types:

```cypher
MATCH (ax:N {kind: 'ClassAssertion'})
      -[:E {role: 'class'}]->(cls:N {kind: 'Class'}),
      (ax)-[:E {role: 'individual'}]->(ind:N {kind: 'NamedIndividual'})
WHERE ind.iri IS NOT NULL AND cls.iri IS NOT NULL
RETURN ind.iri AS individual, cls.iri AS type
ORDER BY individual, type
```

Against the bundled family ontology, this query returns no rows because the sample
focuses on TBox patterns plus a negative assertion rather than positive type assertions.

Object property assertions between named individuals:

```cypher
MATCH (ax:N {kind: 'ObjectPropertyAssertion'})
      -[:E {role: 'subject'}]->(src:N),
      (ax)-[:E {role: 'property'}]->(prop:N),
      (ax)-[:E {role: 'object'}]->(tgt:N)
WHERE src.iri IS NOT NULL AND prop.iri IS NOT NULL AND tgt.iri IS NOT NULL
RETURN src.iri AS source, prop.iri AS property, tgt.iri AS target
ORDER BY source, property
```

Against the bundled family ontology, this query returns no rows because the bundled
sample contains only the negative form of the assertion.

Negative object property assertions:

```cypher
MATCH (ax:N {kind: 'NegativeObjectPropertyAssertion'})
      -[:E {role: 'subject'}]->(src:N),
      (ax)-[:E {role: 'property'}]->(prop:N),
      (ax)-[:E {role: 'object'}]->(tgt:N)
WHERE src.iri IS NOT NULL AND prop.iri IS NOT NULL AND tgt.iri IS NOT NULL
RETURN src.iri AS source, prop.iri AS property, tgt.iri AS target
ORDER BY source, property
```

On the bundled family ontology:

```
  source                    property                   target
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  http://example.org/Bill   http://example.org/hasD…   http://example.org/Sus…
```

## Ontology structure

Import declarations recorded in the projection:

```cypher
MATCH (n:N {kind: 'Import'})
RETURN n.text AS imported_iri
ORDER BY imported_iri
```

Prefix declarations from the source document:

```cypher
MATCH (n:N {kind: 'Prefix'})
RETURN n.prefix_name AS prefix, n.iri AS namespace
ORDER BY prefix
```

Ontology nodes and their version IRIs:

```cypher
MATCH (n:N {kind: 'Ontology'})
RETURN n.ontology_iri AS ontology_iri, n.version_iri AS version_iri
ORDER BY ontology_iri
```

## Annotation assertions

An `AnnotationAssertion` has three edges: `property` (the annotation property),
`subject` (an `IRI` node whose `text` is the annotated entity's IRI), and `value` (the
annotation value). A literal value is a `Literal` node — its string is `val.text`, its
language tag `val.lang`; an IRI-valued annotation points at an `IRI` node (also `text`).

All annotation assertions on a specific entity:

```cypher
MATCH (ax:N {kind: 'AnnotationAssertion'})
      -[:E {role: 'property'}]->(prop:N),
      (ax)-[:E {role: 'subject'}]->(subj:N),
      (ax)-[:E {role: 'value'}]->(val:N)
WHERE subj.text = 'http://example.org/YourClass'
RETURN prop.iri AS property,
       val.text AS value,
       val.lang AS lang
ORDER BY property
```

All `rdfs:label` annotations across the ontology:

```cypher
MATCH (ax:N {kind: 'AnnotationAssertion'})
      -[:E {role: 'property'}]->(:N {iri: 'http://www.w3.org/2000/01/rdf-schema#label'}),
      (ax)-[:E {role: 'subject'}]->(subj:N),
      (ax)-[:E {role: 'value'}]->(val:N)
RETURN subj.text AS entity,
       val.text AS label,
       val.lang AS lang
ORDER BY entity, lang
```

The derived `annotation_value` edge collapses this to one hop, joining the labelled
entity node straight to its literal — see the
[derived-relations reference](../ontoplexis/reference/derived.md).

Deprecated entities:

```cypher
MATCH (ax:N {kind: 'AnnotationAssertion'})
      -[:E {role: 'property'}]->(:N {iri: 'http://www.w3.org/2002/07/owl#deprecated'}),
      (ax)-[:E {role: 'subject'}]->(subj:N),
      (ax)-[:E {role: 'value'}]->(val:N)
WHERE val.text = 'true'
RETURN subj.text AS deprecated_entity
ORDER BY deprecated_entity
```

## SPARQL comparison

Ontopoiesis's Cypher surface queries the projection graph directly rather than RDF triples.
The comparison below shows the same structural question in both models.

### Named subclass relationships

```sparql
SELECT ?subClass ?superClass
WHERE {
  ?subClass rdfs:subClassOf ?superClass .
  FILTER(isIRI(?subClass) && isIRI(?superClass))
}
```

```cypher
MATCH (ax:N {kind: 'SubClassOf'})
      -[:E {role: 'sub'}]->(sub:N {kind: 'Class'}),
      (ax)-[:E {role: 'super'}]->(sup:N {kind: 'Class'})
WHERE sub.iri IS NOT NULL AND sup.iri IS NOT NULL
RETURN sub.iri AS subclass, sup.iri AS superclass
ORDER BY subclass
```

### Existential restrictions

```sparql
SELECT ?class ?property ?filler
WHERE {
  ?class rdfs:subClassOf ?restriction .
  ?restriction a owl:Restriction ;
               owl:onProperty ?property ;
               owl:someValuesFrom ?filler .
}
```

```cypher
MATCH (ax:N {kind: 'SubClassOf'})
      -[:E {role: 'sub'}]->(cls:N {kind: 'Class'}),
      (ax)-[:E {role: 'super'}]->(restriction:N {kind: 'ObjectSomeValuesFrom'})
      -[:E {role: 'property'}]->(prop:N),
      (restriction)-[:E {role: 'filler'}]->(filler:N)
WHERE cls.iri IS NOT NULL AND prop.iri IS NOT NULL
RETURN cls.iri AS class, prop.iri AS property,
       COALESCE(filler.iri, filler.kind) AS filler
ORDER BY class, property
```

### Property chains

```sparql
SELECT ?property ?step ?position
WHERE {
  ?property owl:propertyChainAxiom ?list .
  -- then walk rdf:first / rdf:rest by hand
}
```

```cypher
MATCH (ax:N {kind: 'SubObjectPropertyOf'})
      -[:E {role: 'super'}]->(sup:N),
      (ax)-[:E {role: 'sub'}]->(:N {kind: 'ObjectPropertyChain'})
      -[link:E {role: 'operand'}]->(step:N)
WHERE sup.iri IS NOT NULL AND step.iri IS NOT NULL
RETURN sup.iri AS property, step.iri AS chain_step, link.position AS position
ORDER BY property, position
```

### N-ary axioms

```sparql
SELECT ?axiom ?class
WHERE {
  ?axiom a owl:AllDisjointClasses ;
         owl:members ?list .
  ?list rdf:rest*/rdf:first ?class .
  FILTER(isIRI(?class))
}
ORDER BY ?axiom ?class
```

```cypher
MATCH (ax:N {kind: 'DisjointClasses'})
      -[:E {role: 'operand'}]->(cls:N)
WHERE cls.iri IS NOT NULL
RETURN ax.uid AS axiom, cls.iri AS class
ORDER BY axiom, class
```

### Multi-hop structural questions

```sparql
SELECT DISTINCT ?class ?superClass ?property ?filler
WHERE {
  ?class rdfs:subClassOf ?superClass .
  FILTER(isIRI(?class) && isIRI(?superClass))

  ?class rdfs:subClassOf ?restriction .
  ?restriction a owl:Restriction ;
               owl:onProperty ?property ;
               owl:someValuesFrom ?filler .
}
ORDER BY ?class ?superClass ?property
```

```cypher
MATCH (subAx:N {kind: 'SubClassOf'})
      -[:E {role: 'sub'}]->(cls:N {kind: 'Class'}),
      (subAx)-[:E {role: 'super'}]->(sup:N {kind: 'Class'}),
      (restrictionAx:N {kind: 'SubClassOf'})
      -[:E {role: 'sub'}]->(cls),
      (restrictionAx)-[:E {role: 'super'}]->(restriction:N {kind: 'ObjectSomeValuesFrom'})
      -[:E {role: 'property'}]->(prop:N),
      (restriction)-[:E {role: 'filler'}]->(filler:N)
WHERE cls.iri IS NOT NULL
  AND sup.iri IS NOT NULL
  AND prop.iri IS NOT NULL
RETURN cls.iri AS class,
       sup.iri AS superclass,
       prop.iri AS property,
       COALESCE(filler.iri, filler.kind) AS filler
ORDER BY class, superclass, property
```

## Troubleshooting

**Query returns no rows when rows are expected**

The most common cause is a `kind` string mismatch. Kind strings must exactly match the
OWL 2 structural specification names as used in the projection — for example,
`SubClassOf` not `subClassOf` or `subclass_of`. Run the discovery query first to see
the exact kind strings present in your projection:

```cypher
MATCH (n:N) RETURN DISTINCT n.kind AS kind ORDER BY kind
```

If the kind is present but the query still returns nothing, check whether the ontology
uses the pattern you expect. If all superclass expressions are anonymous intersections
or restrictions rather than named classes, a query for named-class-to-named-class
`SubClassOf` axioms will return no rows.

**Query returns rows but `iri` is `null`**

Anonymous constructs — axioms, class expressions, property expressions — have a `uid`
but no `iri`. Only named entities (`Class`, `ObjectProperty`, `NamedIndividual`, and so
on) carry an `iri` property. Add a `WHERE n.iri IS NOT NULL` clause to filter to named
entities, or use `n.uid` to identify anonymous nodes.

**`ontopoiesis query` exits with a non-zero status**

A syntax error in the Cypher string causes the command to exit non-zero and print the
error from the query engine. The most common source is unescaped quotes in an inline
`-q` string. Use a `.cypher` file with `--file` instead of `-q` for multi-line queries.

**Projection file not found or appears empty**

Run `ontopoiesis build` first to produce the `.lbug` file. If the file exists but queries
return nothing, the build may have failed partway through — rebuild with
`ontopoiesis build --force` to overwrite the existing projection.
