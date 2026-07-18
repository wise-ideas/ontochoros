---
title: Construct catalog
---

# Construct catalog

Ontophora registers the OWL 2 structural constructs below. Each concrete model
has `uid` and a fixed `kind`; fields follow the OWL 2 structural specification.
Use `construct_json_schema()` when code needs the complete field-level contract.

## Document constructs

`OntologyDocument`, `Ontology`, `Prefix`, `Import`

## Entities and literals

`AnnotationProperty`, `Class`, `DataProperty`, `Datatype`, `NamedIndividual`,
`ObjectProperty`, `AnonymousIndividual`, `StringLiteralNoLanguage`,
`StringLiteralWithLanguage`, `TypedLiteral`

## Annotations

`Annotation`, `AnnotationAssertion`, `AnnotationPropertyDomain`,
`AnnotationPropertyRange`, `SubAnnotationPropertyOf`

## Class expressions and data ranges

`ObjectAllValuesFrom`, `ObjectComplementOf`, `ObjectExactCardinality`,
`ObjectHasSelf`, `ObjectHasValue`, `ObjectIntersectionOf`,
`ObjectMaxCardinality`, `ObjectMinCardinality`, `ObjectOneOf`,
`ObjectSomeValuesFrom`, `ObjectUnionOf`, `DataAllValuesFrom`,
`DataComplementOf`, `DataExactCardinality`, `DataHasValue`,
`DataIntersectionOf`, `DataMaxCardinality`, `DataMinCardinality`, `DataOneOf`,
`DataSomeValuesFrom`, `DataUnionOf`, `DatatypeRestriction`, `FacetRestriction`,
`ObjectInverseOf`, `ObjectPropertyChain`

## Axioms

`AsymmetricObjectProperty`, `ClassAssertion`, `DataPropertyAssertion`,
`DataPropertyDomain`, `DataPropertyRange`, `DatatypeDefinition`, `Declaration`,
`DifferentIndividuals`, `DisjointClasses`, `DisjointDataProperties`,
`DisjointObjectProperties`, `DisjointUnion`, `EquivalentClasses`,
`EquivalentDataProperties`, `EquivalentObjectProperties`,
`FunctionalDataProperty`, `FunctionalObjectProperty`, `HasKey`,
`InverseFunctionalObjectProperty`, `InverseObjectProperties`,
`IrreflexiveObjectProperty`, `NegativeDataPropertyAssertion`,
`NegativeObjectPropertyAssertion`, `ObjectPropertyAssertion`,
`ObjectPropertyDomain`, `ObjectPropertyRange`, `ReflexiveObjectProperty`,
`SameIndividual`, `SubClassOf`, `SubDataPropertyOf`, `SubObjectPropertyOf`,
`SymmetricObjectProperty`, `TransitiveObjectProperty`

## Abstract groups

Reference fields can target an OWL abstract group rather than one concrete
model. The registry records group membership for `Axiom`, `AnnotationAxiom`,
`Assertion`, `ClassAxiom`, `ClassExpression`, `DataPropertyAxiom`,
`DataPropertyExpression`, `DataRange`, `Entity`, `Individual`,
`ObjectPropertyAxiom`, and `ObjectPropertyExpression`.

For example, `SubClassOf.sub_class_expression` expects `ClassExpression`, so a
reference may point to either a `Class` record or an anonymous class-expression
record such as `ObjectSomeValuesFrom`.
