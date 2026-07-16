---
title: "OWL 2 Construct Coverage"
---

Ontopoiesis's projection covers the full [OWL 2 structural
specification](https://www.w3.org/TR/owl2-syntax/). Every axiom, class expression, data
range, property expression, and annotation construct from the specification has a
corresponding entry in the construct registry.

Each construct is stored as a node in the projection with a `kind` property you use to
query it. The kind strings match the OWL 2 specification names directly, so if you know
the OWL 2 name you already know the Cypher kind.

Jump to:

- [Entities](#entities)
- [Literals](#literals)
- [Class axioms](#class-axioms)
- [Object property axioms](#object-property-axioms)
- [Data property axioms](#data-property-axioms)
- [Keys and datatype definitions](#keys-and-datatype-definitions)
- [Assertion axioms](#assertion-axioms)
- [Annotation axioms](#annotation-axioms)
- [Class expressions](#class-expressions)
- [Data ranges](#data-ranges)
- [Property expressions](#property-expressions)
- [Ontology structure](#ontology-structure)
- [Node and edge properties](#node-and-edge-properties)
- [Structural edge roles](#structural-edge-roles)
- [Node identifiers](#node-identifiers)
- [What is out of scope](#what-is-out-of-scope)
- [Querying by construct kind](#querying-by-construct-kind)

## Entities

Named entities with IRI identity. Every entity also produces a `Declaration` axiom node.

| `kind`                | OWL 2 construct                                                                       |
| --------------------- | ------------------------------------------------------------------------------------- |
| `Class`               | Named class                                                                           |
| `ObjectProperty`      | Object property                                                                       |
| `DataProperty`        | Data property                                                                         |
| `AnnotationProperty`  | Annotation property                                                                   |
| `NamedIndividual`     | Named individual                                                                      |
| `Datatype`            | Named datatype                                                                        |
| `AnonymousIndividual` | Anonymous individual (blank node individual); has no `iri` — identified by `uid` only |

## Literals

Literal values are a single node kind. All three literal forms from the OWL 2 structural
specification share it, distinguished by which properties are set.

| `kind`    | OWL 2 forms represented                                                                                |
| --------- | ----------------------------------------------------------------------------------------------------- |
| `Literal` | Plain string, language-tagged string (`"text"@en`), and typed literal (`"value"^^xsd:integer`) |

Literal node properties:

| Property       | Description                                             |
| -------------- | ------------------------------------------------------ |
| `text`         | The lexical value (`"Dog"`, `"42"`)                    |
| `lang`         | Language tag such as `en`; null when untagged          |
| `datatype_iri` | Expanded datatype IRI; set on typed literals           |

The string value is `val.text` regardless of form — no `COALESCE` across kinds needed.

## Class axioms

| `kind`              | OWL 2 construct                                                   |
| ------------------- | ----------------------------------------------------------------- |
| `SubClassOf`        | Subclass relationship between two class expressions               |
| `EquivalentClasses` | Mutual subclass between two or more class expressions             |
| `DisjointClasses`   | No individual can be an instance of more than one                 |
| `DisjointUnion`     | Class defined as the disjoint union of a set of class expressions |

## Object property axioms

| `kind`                            | OWL 2 construct                                                             |
| --------------------------------- | --------------------------------------------------------------------------- |
| `SubObjectPropertyOf`             | Sub-property relationship (includes chain axioms via `ObjectPropertyChain`) |
| `EquivalentObjectProperties`      | Mutual sub-property                                                         |
| `DisjointObjectProperties`        | No individual pair can be related by more than one                          |
| `InverseObjectProperties`         | Two properties are inverses                                                 |
| `ObjectPropertyDomain`            | Domain class expression                                                     |
| `ObjectPropertyRange`             | Range class expression                                                      |
| `FunctionalObjectProperty`        | At most one value per subject                                               |
| `InverseFunctionalObjectProperty` | At most one subject per value                                               |
| `ReflexiveObjectProperty`         | Every individual relates to itself                                          |
| `IrreflexiveObjectProperty`       | No individual relates to itself                                             |
| `SymmetricObjectProperty`         | If `a P b` then `b P a`                                                     |
| `AsymmetricObjectProperty`        | If `a P b` then not `b P a`                                                 |
| `TransitiveObjectProperty`        | If `a P b` and `b P c` then `a P c`                                         |

## Data property axioms

| `kind`                     | OWL 2 construct                                            |
| -------------------------- | ---------------------------------------------------------- |
| `SubDataPropertyOf`        | Sub-property relationship                                  |
| `EquivalentDataProperties` | Mutual sub-property                                        |
| `DisjointDataProperties`   | No individual can have the same literal via two properties |
| `DataPropertyDomain`       | Domain class expression                                    |
| `DataPropertyRange`        | Data range                                                 |
| `FunctionalDataProperty`   | At most one value per subject                              |

## Keys and datatype definitions

| `kind`               | OWL 2 construct                                                             |
| -------------------- | --------------------------------------------------------------------------- |
| `HasKey`             | Identifies individuals uniquely via object and/or data property expressions |
| `DatatypeDefinition` | Defines a named datatype as equivalent to a data range                      |

## Assertion axioms

| `kind`                            | OWL 2 construct                                                   |
| --------------------------------- | ----------------------------------------------------------------- |
| `ClassAssertion`                  | States that an individual is an instance of a class expression    |
| `ObjectPropertyAssertion`         | States that two individuals are related by an object property     |
| `NegativeObjectPropertyAssertion` | Explicitly negates an object property assertion                   |
| `DataPropertyAssertion`           | States that an individual has a literal value via a data property |
| `NegativeDataPropertyAssertion`   | Explicitly negates a data property assertion                      |
| `SameIndividual`                  | Two or more individuals denote the same object                    |
| `DifferentIndividuals`            | Two or more individuals denote distinct objects                   |

## Annotation axioms

Annotation axioms are full axiom nodes, not metadata attached to other nodes. Axiom-level
annotations attach as `Annotation` children (edge role `annotation`) of any axiom node.

| `kind`                     | OWL 2 construct                                                              |
| -------------------------- | ---------------------------------------------------------------------------- |
| `AnnotationAssertion`      | Attaches an annotation property/value pair to an IRI or anonymous individual |
| `SubAnnotationPropertyOf`  | Sub-property relationship between annotation properties                      |
| `AnnotationPropertyDomain` | Domain IRI for an annotation property                                        |
| `AnnotationPropertyRange`  | Range IRI for an annotation property                                         |
| `Annotation`               | An annotation attached to an axiom (axiom-level annotation)                  |

## Class expressions

Object property class expressions:

| `kind`                   | OWL 2 construct                                                 |
| ------------------------ | --------------------------------------------------------------- |
| `ObjectIntersectionOf`   | Intersection of class expressions (`owl:intersectionOf`)        |
| `ObjectUnionOf`          | Union of class expressions (`owl:unionOf`)                      |
| `ObjectComplementOf`     | Complement of a class expression                                |
| `ObjectOneOf`            | Enumerated class: exactly these named individuals               |
| `ObjectSomeValuesFrom`   | Existential restriction (`∃ P.C`)                               |
| `ObjectAllValuesFrom`    | Universal restriction (`∀ P.C`)                                 |
| `ObjectHasValue`         | Value restriction: related to a specific individual (`∃ P.{a}`) |
| `ObjectHasSelf`          | Self restriction: related to itself (`∃ P.Self`)                |
| `ObjectMinCardinality`   | At least _n_ values                                             |
| `ObjectMaxCardinality`   | At most _n_ values                                              |
| `ObjectExactCardinality` | Exactly _n_ values                                              |

Data property class expressions:

| `kind`                 | OWL 2 construct                                |
| ---------------------- | ---------------------------------------------- |
| `DataSomeValuesFrom`   | Existential data restriction (`∃ P.D`)         |
| `DataAllValuesFrom`    | Universal data restriction (`∀ P.D`)           |
| `DataHasValue`         | Data value restriction: has a specific literal |
| `DataMinCardinality`   | At least _n_ data values                       |
| `DataMaxCardinality`   | At most _n_ data values                        |
| `DataExactCardinality` | Exactly _n_ data values                        |

## Data ranges

| `kind`                | OWL 2 construct                                          |
| --------------------- | -------------------------------------------------------- |
| `DataIntersectionOf`  | Intersection of data ranges                              |
| `DataUnionOf`         | Union of data ranges                                     |
| `DataComplementOf`    | Complement of a data range                               |
| `DataOneOf`           | Enumerated data range: exactly these literals            |
| `DatatypeRestriction` | Datatype restricted by facets                            |
| `FacetRestriction`    | A single facet/value pair within a `DatatypeRestriction` |

## Property expressions

| `kind`                | OWL 2 construct                                                |
| --------------------- | -------------------------------------------------------------- |
| `ObjectInverseOf`     | Anonymous inverse of an object property (`ObjectInverseOf(P)`) |
| `ObjectPropertyChain` | Ordered list of property expressions in a chain axiom          |

## Ontology structure

These construct kinds appear in every projection as document-level structure. They are
not axioms and have no standalone representation in OWL document round-trips.

| `kind`        | Description                                                                              |
| ------------- | ---------------------------------------------------------------------------------------- |
| `Ontology`    | The document root; carries `ontology_iri`, `version_iri`, and edges to prefixes, imports, annotations, and axioms |
| `Import`      | An `owl:imports` declaration; carries the imported IRI as a node property                |
| `Prefix`      | A prefix declaration (`Prefix(...)`) from the source document                            |
| `Declaration` | Explicit entity declaration axiom                                                        |

## Node and edge properties

Every node in the projection carries `kind` and `uid`. Named entities also carry `iri`.
Beyond those, several construct types carry additional properties:

### Named entities

| Property | Applies to                                                                                     | Description         |
| -------- | ---------------------------------------------------------------------------------------------- | ------------------- |
| `iri`    | `Class`, `ObjectProperty`, `DataProperty`, `AnnotationProperty`, `NamedIndividual`, `Datatype` | Expanded IRI string |

### Literals

| Property       | Applies to | Description                                    |
| -------------- | ---------- | ---------------------------------------------- |
| `text`         | `Literal`  | The lexical value                              |
| `lang`         | `Literal`  | Language tag (`"en"`, `"de"`, …); null if none |
| `datatype_iri` | `Literal`  | Expanded IRI of the datatype, on typed literals |

### Annotation assertions

An `AnnotationAssertion` has no subject property. Its subject is an edge (role `subject`)
to an `IRI` node whose `text` holds the annotated entity's IRI:

```cypher
MATCH (ax:N {kind: 'AnnotationAssertion'})-[:E {role: 'subject'}]->(s:N)
WHERE s.text = 'http://example.org/MyClass'
```

To join straight to the labelled entity instead, use the derived `annotation_value`
edge (see [derived relations](https://wise-ideas.github.io/ontotheke/ontoplexis/reference/derived/)),
which connects the entity node directly to the literal.

### Ontology and document nodes

| Property       | Applies to         | Description                          |
| -------------- | ------------------ | ------------------------------------ |
| `ontology_iri` | `Ontology`         | The ontology IRI                     |
| `version_iri`  | `Ontology`         | The version IRI (may be null)        |
| `iri`          | `Import`, `Prefix` | Imported IRI or prefix namespace IRI |
| `prefix_name`  | `Prefix`           | Prefix name (e.g., `"owl"`, `"rdf"`) |

### Edges

| Property   | Applies to | Description                                                                            |
| ---------- | ---------- | -------------------------------------------------------------------------------------- |
| `role`     | All edges  | The query-facing name this edge represents (e.g., `sub`, `super`, `operand`, `value`)  |
| `position` | All edges  | The child's zero-based index in document order under its parent                        |

`position` is present on every edge and is what serialization round-trips. Query it to
recover the order of an ordered field, such as property chain steps:

```cypher
MATCH (:N {kind: 'ObjectPropertyChain'})
      -[link:E {role: 'operand'}]->(step:N)
RETURN step.iri AS step, link.position AS position
ORDER BY position
```

## Structural edge roles

The tables below make `constructs.md` the single lookup for which edge roles a construct
uses in the projection. Roles are the short query-facing names assigned by the parent
kind and child position; the canonical source is the
[Ontoplexis edge-roles reference](https://wise-ideas.github.io/ontotheke/ontoplexis/reference/roles/).
Where a role appears more than once (n-ary operands, chain steps), the edges are
distinguished by `position`.

### Common class and property axioms

| `kind`                       | Edge roles          |
| ---------------------------- | ------------------- |
| `SubClassOf`                 | `sub`, `super`      |
| `EquivalentClasses`          | `operand`…          |
| `DisjointClasses`            | `operand`…          |
| `DisjointUnion`              | `class`, `operand`… |
| `SubObjectPropertyOf`        | `sub`, `super`      |
| `EquivalentObjectProperties` | `operand`…          |
| `DisjointObjectProperties`   | `operand`…          |
| `InverseObjectProperties`    | `property`, `property` |
| `ObjectPropertyDomain`       | `property`, `domain` |
| `ObjectPropertyRange`        | `property`, `range` |
| `SubDataPropertyOf`          | `sub`, `super`      |
| `EquivalentDataProperties`   | `operand`…          |
| `DisjointDataProperties`     | `operand`…          |
| `DataPropertyDomain`         | `property`, `domain` |
| `DataPropertyRange`          | `property`, `range` |
| `HasKey`                     | `class`, `property`… |
| `DatatypeDefinition`         | `datatype`, `range` |
| `Declaration`                | `entity`            |

### Assertions and annotation axioms

| `kind`                            | Edge roles                     |
| --------------------------------- | ------------------------------ |
| `ClassAssertion`                  | `class`, `individual`          |
| `ObjectPropertyAssertion`         | `property`, `subject`, `object` |
| `NegativeObjectPropertyAssertion` | `property`, `subject`, `object` |
| `DataPropertyAssertion`           | `property`, `subject`, `object` |
| `NegativeDataPropertyAssertion`   | `property`, `subject`, `object` |
| `SameIndividual`                  | `operand`…                     |
| `DifferentIndividuals`            | `operand`…                     |
| `AnnotationAssertion`             | `property`, `subject`, `value` |
| `SubAnnotationPropertyOf`         | `sub`, `super`                 |
| `AnnotationPropertyDomain`        | `property`, `domain`           |
| `AnnotationPropertyRange`         | `property`, `range`            |
| `Annotation`                      | `property`, `value`            |

### Expressions and data ranges

| `kind`                   | Edge roles           |
| ------------------------ | -------------------- |
| `ObjectIntersectionOf`   | `operand`…           |
| `ObjectUnionOf`          | `operand`…           |
| `ObjectComplementOf`     | `operand`            |
| `ObjectOneOf`            | `operand`…           |
| `ObjectSomeValuesFrom`   | `property`, `filler` |
| `ObjectAllValuesFrom`    | `property`, `filler` |
| `ObjectHasValue`         | `property`, `filler` |
| `ObjectHasSelf`          | `property`           |
| `ObjectMinCardinality`   | `property`, `filler` |
| `ObjectMaxCardinality`   | `property`, `filler` |
| `ObjectExactCardinality` | `property`, `filler` |
| `DataSomeValuesFrom`     | `property`, `filler` |
| `DataAllValuesFrom`      | `property`, `filler` |
| `DataHasValue`           | `property`, `filler` |
| `DataMinCardinality`     | `property`, `filler` |
| `DataMaxCardinality`     | `property`, `filler` |
| `DataExactCardinality`   | `property`, `filler` |
| `DataIntersectionOf`     | `operand`…           |
| `DataUnionOf`            | `operand`…           |
| `DataComplementOf`       | `operand`            |
| `DataOneOf`              | `operand`…           |
| `DatatypeRestriction`    | `datatype`, `facet`… |
| `FacetRestriction`       | `value`              |
| `ObjectInverseOf`        | `property`           |
| `ObjectPropertyChain`    | `operand`…           |

### Ontology structure

The `Ontology` node is the document root. Its children take a role by kind — `prefix`,
`import`, `annotation`, or `axiom` — rather than a single list role. There is no separate
`OntologyDocument` node in the projection.

| `kind`     | Edge roles                                 |
| ---------- | ------------------------------------------ |
| `Ontology` | `prefix`, `import`, `annotation`, `axiom`  |
| `Import`   | none                                       |
| `Prefix`   | none                                       |

## Node identifiers

Every node in the projection carries a `uid`, assigned in document order (`n0`, `n1`, …)
on each build. Named entities and leaf values are deduplicated to one node, but the ids
are positional and **not stable across rebuilds** — use `iri` as the durable identifier
for named entities. Migrations get a separate, deterministic id from the `scalar_uid` /
`axiom_uid` helpers. See [The Projection Graph Model](cypher-model.md#the-uid).

## What is out of scope

**SWRL rules.** SWRL (Semantic Web Rule Language) rules are not part of the OWL 2
structural specification. Ontopoiesis does not represent them. If an ontology document
contains SWRL rules, they are not represented in the projection.

**Import resolution.** `owl:imports` declarations are faithfully captured as `Import`
nodes, but `ontopoiesis build` does not fetch imported ontologies or merge their constructs
into the projection. Ontopoiesis also does not yet provide a graph-native import model that
preserves imported ontologies as distinct structural units with explicit cross-document
semantics inside one projection.

**OWL Full.** The OWL 2 structural specification — and therefore Ontopoiesis — does not cover
the RDF-level semantics of OWL Full. Constructs that exist only under OWL Full's RDF
semantics have no representation in the projection — this includes metamodeling beyond
standard punning and full RDF reification.

## Querying by construct kind

Every node in the projection carries a `kind` property. Use it to filter by construct
type:

```cypher
MATCH (n:N {kind: 'SubClassOf'}) RETURN count(*) AS count;
MATCH (n:N {kind: 'ObjectSomeValuesFrom'}) RETURN count(*) AS count;
MATCH (n:N) WHERE n.kind IN ['ObjectMinCardinality', 'ObjectMaxCardinality', 'ObjectExactCardinality']
RETURN n.kind AS kind, count(*) AS count ORDER BY kind;
```

To see every kind present in a given projection:

```cypher
MATCH (n:N) RETURN DISTINCT n.kind AS kind ORDER BY kind
```
