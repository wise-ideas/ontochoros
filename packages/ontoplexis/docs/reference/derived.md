---
title: Derived Relations
---

# Derived Relations

The relation vocabulary of the derived-edge table `D`. Each relation is a
mechanical collapse of an OWL 2 construct whose RDF mapping is a single triple
(plus one marked convenience); derived edges connect the named entities (or
literals) the axiom relates, so the common queries are one hop. See
[The Graph Schema](../concepts/schema.md) for the table's columns and cache
semantics.

Only **named** participants are derived: rules require an `iri` on every
endpoint, so axioms over anonymous class expressions contribute nothing
(query them structurally through `N`/`E`).

## Class axioms

| `relation` | Source constructs | Notes |
|---|---|---|
| `subclass_of` | `SubClassOf`, `DisjointUnion` | `DisjointUnion` members are subclasses of the union class |
| `equivalent_class` | `EquivalentClasses` | Symmetric: both directions materialized |
| `disjoint_class` | `DisjointClasses`, `DisjointUnion` | Symmetric: both directions materialized |

## Property axioms

| `relation` | Source constructs | Notes |
|---|---|---|
| `subproperty_of` | `SubObjectPropertyOf`, `SubDataPropertyOf`, `SubAnnotationPropertyOf` | |
| `equivalent_property` | `EquivalentObjectProperties`, `EquivalentDataProperties` | Symmetric: both directions |
| `disjoint_property` | `DisjointObjectProperties`, `DisjointDataProperties` | Symmetric: both directions |
| `inverse_of` | `InverseObjectProperties` | Symmetric: both directions |
| `domain` | `ObjectPropertyDomain`, `DataPropertyDomain`, `AnnotationPropertyDomain` | Property → domain class |
| `range` | `ObjectPropertyRange`, `DataPropertyRange`, `AnnotationPropertyRange` | Property → range class/datatype |

## Property characteristics

Unary characteristic axioms are single `rdf:type` triples; with no node for
the OWL vocabulary class, each becomes a **self-loop on the property**:

| `relation` | Source constructs |
|---|---|
| `functional` | `FunctionalObjectProperty`, `FunctionalDataProperty` |
| `inverse_functional` | `InverseFunctionalObjectProperty` |
| `reflexive` | `ReflexiveObjectProperty` |
| `irreflexive` | `IrreflexiveObjectProperty` |
| `symmetric` | `SymmetricObjectProperty` |
| `asymmetric` | `AsymmetricObjectProperty` |
| `transitive` | `TransitiveObjectProperty` |

## Assertions

| `relation` | Source constructs | Notes |
|---|---|---|
| `type` | `ClassAssertion` | Individual → class |
| `asserts` | `ObjectPropertyAssertion` | Subject → object; `property` holds the property IRI |
| `data_value` | `DataPropertyAssertion` | Subject → `Literal` node; `property` holds the property IRI |
| `same_as` | `SameIndividual` | Symmetric: both directions |
| `different_from` | `DifferentIndividuals` | Symmetric: both directions |

## Annotations

| `relation` | Source constructs | Notes |
|---|---|---|
| `annotation` | `AnnotationAssertion` (IRI value) | Subject entity → value entity; `property` holds the annotation property IRI |
| `annotation_value` | `AnnotationAssertion` (literal value) | Subject entity → `Literal` node (labels, comments, …); `property` holds the annotation property IRI |

Annotation subjects (and IRI values) name **IRIs, not entities**, so the rules
attach an edge to every entity node carrying that IRI. Under punning — say a
`Class` and a `NamedIndividual` declared with the same IRI — one assertion
yields one edge per pun (a cross product when both ends are punned).

## Marked convenience

| `relation` | Source constructs | Notes |
|---|---|---|
| `restriction` | `SubClassOf` with an `ObjectSomeValuesFrom`/`ObjectAllValuesFrom` super | *Not* single-triple in RDF; makes the existential content graph one hop. `property` holds the restriction property IRI, `quantifier` is `some` or `only` |

## Traversal, not closure

No transitive closure is materialized — deliberately. Use bounded recursive
patterns instead:

```cypher
MATCH (c:N {iri: $iri})-[:D*1..20 {relation:'subclass_of'}]->(a:N)
RETURN DISTINCT a.iri AS ancestor
```
