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
- [Content addressing](#content-addressing)
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

Literal values as nodes. All three literal forms from the OWL 2 structural
specification are represented.

| `kind`                      | OWL 2 form                                       |
| --------------------------- | ------------------------------------------------ |
| `StringLiteralNoLanguage`   | Plain string literal, no language tag            |
| `StringLiteralWithLanguage` | String literal with language tag (`"text"@en`)   |
| `TypedLiteral`              | Datatype-tagged literal (`"value"^^xsd:integer`) |

Literal node properties:

| `kind`                      | Property        | Description               |
| --------------------------- | --------------- | ------------------------- |
| `StringLiteralNoLanguage`   | `quoted_string` | String value              |
| `StringLiteralWithLanguage` | `quoted_string` | String value              |
| `StringLiteralWithLanguage` | `language_tag`  | Language tag such as `en` |
| `TypedLiteral`              | `lexical_form`  | Literal lexical value     |
| `TypedLiteral`              | `datatype_iri`  | Expanded datatype IRI     |

Use `COALESCE(val.quoted_string, val.lexical_form)` when you want the string value
regardless of literal kind.

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

Annotation axioms are full axiom nodes, not metadata attached to other nodes. Every
axiom type also carries an `axiom_annotations` field for axiom-level annotations.

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

| `kind`             | Description                                                                     |
| ------------------ | ------------------------------------------------------------------------------- |
| `Ontology`         | The ontology itself; carries `ontology_iri`, `version_iri`, and edges to axioms |
| `OntologyDocument` | The document wrapper; carries edges to prefix declarations and the ontology     |
| `Import`           | An `owl:imports` declaration; carries the imported IRI as a node property       |
| `Prefix`           | A prefix declaration (`@prefix`, `Prefix(...)`) from the source document        |
| `Declaration`      | Explicit entity declaration axiom                                               |

## Node and edge properties

Every node in the projection carries `kind` and `uid`. Named entities also carry `iri`.
Beyond those, several construct types carry additional properties:

### Named entities

| Property | Applies to                                                                                     | Description         |
| -------- | ---------------------------------------------------------------------------------------------- | ------------------- |
| `iri`    | `Class`, `ObjectProperty`, `DataProperty`, `AnnotationProperty`, `NamedIndividual`, `Datatype` | Expanded IRI string |

### Literals

| Property        | Applies to                                             | Description                          |
| --------------- | ------------------------------------------------------ | ------------------------------------ |
| `quoted_string` | `StringLiteralWithLanguage`, `StringLiteralNoLanguage` | The literal value as a quoted string |
| `lexical_form`  | `TypedLiteral`                                         | The raw lexical value                |
| `language_tag`  | `StringLiteralWithLanguage`                            | Language tag (`"en"`, `"de"`, etc.)  |
| `datatype_iri`  | `TypedLiteral`                                         | Expanded IRI of the datatype         |

### Annotation assertions

| Property             | Applies to            | Description                                                     |
| -------------------- | --------------------- | --------------------------------------------------------------- |
| `annotation_subject` | `AnnotationAssertion` | IRI of the annotated entity (stored as a property, not an edge) |

This is the property to filter on when querying annotations for a specific entity:
`WHERE ax.annotation_subject = 'http://example.org/MyClass'`.

### Ontology and document nodes

| Property       | Applies to         | Description                          |
| -------------- | ------------------ | ------------------------------------ |
| `ontology_iri` | `Ontology`         | The ontology IRI                     |
| `version_iri`  | `Ontology`         | The version IRI (may be null)        |
| `iri`          | `Import`, `Prefix` | Imported IRI or prefix namespace IRI |
| `prefix_name`  | `Prefix`           | Prefix name (e.g., `"owl"`, `"rdf"`) |

### Edges

| Property         | Applies to                   | Description                                                                                                      |
| ---------------- | ---------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `role`           | All edges                    | The OWL 2 field name this edge represents (e.g., `sub_class_expression`, `annotation_value`)                     |
| `endpoint_order` | Edges on ordered list fields | One-based position in an ordered sequence (e.g., steps in an `ObjectPropertyChain`, axioms in `Ontology.axioms`) |

`endpoint_order` is present on edges where the OWL 2 structural specification defines
an ordered list: property chain steps, disjoint union members, and ontology-level axiom
ordering. Query it to recover chain position:

```cypher
MATCH (:N {kind: 'ObjectPropertyChain'})
      -[link:E {role: 'object_property_expressions'}]->(step:N)
RETURN step.iri AS step, link.endpoint_order AS position
ORDER BY position
```

## Structural edge roles

The tables below make `constructs.md` the single lookup for which edge roles a construct
uses in the projection. Role names match the OWL 2 structural field names exactly.

### Common class and property axioms

| `kind`                       | Edge roles                                                                     |
| ---------------------------- | ------------------------------------------------------------------------------ |
| `SubClassOf`                 | `sub_class_expression`, `super_class_expression`                               |
| `EquivalentClasses`          | `class_expressions`                                                            |
| `DisjointClasses`            | `class_expressions`                                                            |
| `DisjointUnion`              | `class`, `class_expressions`                                                   |
| `SubObjectPropertyOf`        | `sub_object_property_expression`, `super_object_property_expression`           |
| `EquivalentObjectProperties` | `object_property_expressions`                                                  |
| `DisjointObjectProperties`   | `object_property_expressions`                                                  |
| `InverseObjectProperties`    | `first`, `second`                                                              |
| `ObjectPropertyDomain`       | `object_property_expression`, `class_expression`                               |
| `ObjectPropertyRange`        | `object_property_expression`, `class_expression`                               |
| `SubDataPropertyOf`          | `sub_data_property_expression`, `super_data_property_expression`               |
| `EquivalentDataProperties`   | `data_property_expressions`                                                    |
| `DisjointDataProperties`     | `data_property_expressions`                                                    |
| `DataPropertyDomain`         | `data_property_expression`, `class_expression`                                 |
| `DataPropertyRange`          | `data_property_expression`, `data_range`                                       |
| `HasKey`                     | `class_expression`, `object_property_expressions`, `data_property_expressions` |
| `DatatypeDefinition`         | `datatype`, `data_range`                                                       |
| `Declaration`                | `entity`                                                                       |

### Assertions and annotation axioms

| `kind`                            | Edge roles                                                             |
| --------------------------------- | ---------------------------------------------------------------------- |
| `ClassAssertion`                  | `class_expression`, `individual`                                       |
| `ObjectPropertyAssertion`         | `source_individual`, `object_property_expression`, `target_individual` |
| `NegativeObjectPropertyAssertion` | `source_individual`, `object_property_expression`, `target_individual` |
| `DataPropertyAssertion`           | `source_individual`, `data_property_expression`, `target_value`        |
| `NegativeDataPropertyAssertion`   | `source_individual`, `data_property_expression`, `target_value`        |
| `SameIndividual`                  | `individuals`                                                          |
| `DifferentIndividuals`            | `individuals`                                                          |
| `AnnotationAssertion`             | `annotation_property`, `annotation_value`                              |
| `SubAnnotationPropertyOf`         | `sub_annotation_property`, `super_annotation_property`                 |
| `AnnotationPropertyDomain`        | `annotation_property`, `domain`                                        |
| `AnnotationPropertyRange`         | `annotation_property`, `range`                                         |
| `Annotation`                      | `annotation_property`, `annotation_value`                              |

### Expressions and data ranges

| `kind`                   | Edge roles                                       |
| ------------------------ | ------------------------------------------------ |
| `ObjectIntersectionOf`   | `operands`                                       |
| `ObjectUnionOf`          | `operands`                                       |
| `ObjectComplementOf`     | `operand`                                        |
| `ObjectOneOf`            | `individuals`                                    |
| `ObjectSomeValuesFrom`   | `object_property_expression`, `class_expression` |
| `ObjectAllValuesFrom`    | `object_property_expression`, `class_expression` |
| `ObjectHasValue`         | `object_property_expression`, `individual`       |
| `ObjectHasSelf`          | `object_property_expression`                     |
| `ObjectMinCardinality`   | `object_property_expression`, `class_expression` |
| `ObjectMaxCardinality`   | `object_property_expression`, `class_expression` |
| `ObjectExactCardinality` | `object_property_expression`, `class_expression` |
| `DataSomeValuesFrom`     | `data_property_expressions`, `data_range`        |
| `DataAllValuesFrom`      | `data_property_expressions`, `data_range`        |
| `DataHasValue`           | `data_property_expression`, `literal`            |
| `DataMinCardinality`     | `data_property_expression`, `data_range`         |
| `DataMaxCardinality`     | `data_property_expression`, `data_range`         |
| `DataExactCardinality`   | `data_property_expression`, `data_range`         |
| `DataIntersectionOf`     | `operands`                                       |
| `DataUnionOf`            | `operands`                                       |
| `DataComplementOf`       | `operand`                                        |
| `DataOneOf`              | `literals`                                       |
| `DatatypeRestriction`    | `datatype`, `facet_restrictions`                 |
| `FacetRestriction`       | `facet_value`                                    |
| `ObjectInverseOf`        | `object_property`                                |
| `ObjectPropertyChain`    | `object_property_expressions`                    |

### Ontology structure

| `kind`             | Edge roles                                            |
| ------------------ | ----------------------------------------------------- |
| `Ontology`         | `axioms`, `annotations`, `directly_imports_documents` |
| `OntologyDocument` | `prefixes`, `ontology`                                |
| `Import`           | none                                                  |
| `Prefix`           | none                                                  |

## Content addressing

Every node in the projection carries a `uid`. For the content-addressing model behind
those UIDs, see [The Projection Graph Model](cypher-model.md#the-uid-and-content-addressing).
This reference page stays at the fact level: named entities carry stable `uid` values
derived from identity, and anonymous constructs carry stable `uid` values derived from
their structure.

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
MATCH (n:N {kind: 'SubClassOf'}) RETURN count(*) AS count
MATCH (n:N {kind: 'ObjectSomeValuesFrom'}) RETURN count(*) AS count
MATCH (n:N) WHERE n.kind IN ['ObjectMinCardinality', 'ObjectMaxCardinality', 'ObjectExactCardinality']
RETURN n.kind AS kind, count(*) AS count ORDER BY kind
```

To see every kind present in a given projection:

```cypher
MATCH (n:N) RETURN DISTINCT n.kind AS kind ORDER BY kind
```
