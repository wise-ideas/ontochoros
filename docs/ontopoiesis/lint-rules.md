---
title: "Lint Rules"
---

This page is the full Ontopoiesis lint rule catalogue. For how to run lint, choose rules,
and wire it into CI, see the [Lint guide](lint.md).

## Rule Families

| Prefix                         | Profile             | Count | Description                        |
| ------------------------------ | ------------------- | ----- | ---------------------------------- |
| [`E1xx`](#contradictions)      | Default (errors)    | 15    | Contradiction checks               |
| [`W1xx`](#redundancy-warnings) | Default (warnings)  | 5     | Low-noise universal warnings       |
| [`P1xx`](#editorial-p)         | `editorial`         | 8     | Publication and editorial guidance |
| [`M1xx`](#modeling_risk-m)     | `modeling_risk`     | 8     | Modeling-risk guidance             |
| [`D1xx`](#description_logic-d) | `description_logic` | 5     | OWL 2 DL strictness                |

## Default Baseline

Rules are `.cypher` files. `test_*.cypher` rows fail the run. `warn_*.cypher` rows
appear separately without failing the run.

### Contradictions

These rules detect impossible axioms or direct semantic clashes without requiring a
classifier.

**`E101` `test_subclass_nothing`**

Named classes explicitly asserted under `owl:Nothing`.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint/test_subclass_nothing.cypher"
```

**`E102` `test_class_assertion_nothing`**

Individuals explicitly asserted as instances of `owl:Nothing`.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint/test_class_assertion_nothing.cypher"
```

**`E103` `test_disjoint_classes_shared_subclass`**

A named class directly asserted as a subclass of two disjoint named classes.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint/test_disjoint_classes_shared_subclass.cypher"
```

**`E104` `test_disjoint_classes_shared_individual`**

A named individual directly asserted into two disjoint named classes.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint/test_disjoint_classes_shared_individual.cypher"
```

**`E105` `test_disjoint_equivalent_classes`**

Two named classes that are asserted both equivalent and disjoint.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint/test_disjoint_equivalent_classes.cypher"
```

**`E106` `test_same_different_individual`**

The same pair of individuals asserted both same and different.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint/test_same_different_individual.cypher"
```

**`E107` `test_negative_object_property_assertion_contradiction`**

An object property assertion and its explicit negation on the same source, property,
and target.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint/test_negative_object_property_assertion_contradiction.cypher"
```

**`E108` `test_negative_data_property_assertion_contradiction`**

A data property assertion and its explicit negation on the same source, property, and
literal term. Literal matching is structural rather than value-normalized.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint/test_negative_data_property_assertion_contradiction.cypher"
```

**`E109` `test_property_contradictory_characteristics`**

Object properties declared with contradictory characteristics:

- reflexive and irreflexive
- symmetric and asymmetric

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint/test_property_contradictory_characteristics.cypher"
```

**`E110` `test_irreflexive_property_self_assertion`**

An irreflexive object property explicitly asserted from an individual to itself.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint/test_irreflexive_property_self_assertion.cypher"
```

**`E111` `test_asymmetric_property_bidirectional_assertion`**

An asymmetric object property asserted in both directions between the same pair, or as
a self-loop.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint/test_asymmetric_property_bidirectional_assertion.cypher"
```

**`E112` `test_disjoint_object_properties_shared_assertion`**

The same subject/target pair asserted through two disjoint object properties.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint/test_disjoint_object_properties_shared_assertion.cypher"
```

**`E113` `test_disjoint_data_properties_shared_assertion`**

The same subject/literal pair asserted through two disjoint data properties.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint/test_disjoint_data_properties_shared_assertion.cypher"
```

**`E114` `test_bottom_object_property_assertion`**

An assertion using `owl:bottomObjectProperty`, which can never have instances.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint/test_bottom_object_property_assertion.cypher"
```

**`E115` `test_bottom_data_property_assertion`**

An assertion using `owl:bottomDataProperty`, which can never have literal values.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint/test_bottom_data_property_assertion.cypher"
```

### Redundancy Warnings

These rules report low-noise structural cleanup opportunities.

**`W101` `warn_subclass_reflexive`**

`SubClassOf(A, A)` tautologies. Legal OWL, but always redundant. Also fires — deliberately —
when a `DisjointUnion` lists the union class among its own operands, which derives the same
self-loop and is the same authoring accident wearing a different axiom.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint/warn_subclass_reflexive.cypher"
```

**`W102` `warn_duplicate_subclass_axiom`**

Duplicate `SubClassOf(A, B)` pairs.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint/warn_duplicate_subclass_axiom.cypher"
```

**`W103` `warn_redundant_subclass_given_equivalence`**

`SubClassOf(A, B)` stated even though `EquivalentClasses` already entails it.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint/warn_redundant_subclass_given_equivalence.cypher"
```

**`W104` `warn_disjoint_union_subclass_redundant`**

`SubClassOf(Member, Parent)` restated even though a `DisjointUnion` axiom already
entails it.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint/warn_disjoint_union_subclass_redundant.cypher"
```

**`W105` `warn_functional_property_multiple_values`**

Functional object properties used with two distinct named targets from the same
source, excluding pairs already tied together with `SameIndividual`.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint/warn_functional_property_multiple_values.cypher"
```

## Supplemental Profiles

These rules still ship with Ontopoiesis, but they are not in the default baseline because
they depend on modeling style, publication policy, or a stricter profile target.

### `editorial` (`P...`)

Human-facing quality and publication guidance.

**`P101` `warn_missing_label`**

Named entities (classes, properties, individuals, datatypes) with no `rdfs:label`.
Without labels, entities are identified only by IRI in human-facing tools.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/editorial/warn_missing_label.cypher"
```

**`P102` `warn_duplicate_label_language`**

Multiple `rdfs:label` annotations in the same language on the same entity. Usually a
duplicate or accidental re-assertion rather than an intentional multilingual annotation.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/editorial/warn_duplicate_label_language.cypher"
```

**`P103` `warn_labeled_without_definition`**

Named entities that have an `rdfs:label` but no definition from common annotation
properties (`skos:definition`, `IAO:0000115`, `dc:description`, `dcterms:description`).
Labeled-but-undefined terms are a common gap in publication-ready ontologies.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/editorial/warn_labeled_without_definition.cypher"
```

**`P104` `warn_annotation_assertion_unknown_subject`**

`AnnotationAssertion` axioms whose subject IRI does not appear elsewhere in the
ontology as a declared entity or as the ontology IRI itself. These are genuinely
dangling annotations — not merely imported terms, which would appear at least as
references in other axioms.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/editorial/warn_annotation_assertion_unknown_subject.cypher"
```

**`P105` `warn_deprecated_entity_referenced`**

Entities marked `owl:deprecated` that still appear in structural axioms or class
expressions (excluding their own `Declaration`). Deprecated entities should be phased
out of active use; continued structural reference is usually an oversight.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/editorial/warn_deprecated_entity_referenced.cypher"
```

**`P106` `warn_entity_iri_equals_ontology_iri`**

Named entities whose IRI is identical to the ontology IRI itself. OWL 2 permits this
but it conflates the ontology document with a term in its own vocabulary, which causes
consistent confusion in tools and downstream consumers.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/editorial/warn_entity_iri_equals_ontology_iri.cypher"
```

**`P107` `warn_version_iri_missing`**

Ontologies that have an IRI but no version IRI. Without a version IRI, consumers
cannot distinguish between revisions when following the ontology IRI across releases.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/editorial/warn_version_iri_missing.cypher"
```

**`P108` `warn_ontology_no_metadata_annotations`**

Ontologies with no common metadata annotations (title, creator, description, license).
An ontology without provenance metadata is difficult to cite, attribute, or evaluate
for reuse.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/editorial/warn_ontology_no_metadata_annotations.cypher"
```

### `modeling_risk` (`M...`)

Valid OWL that often deserves explicit review.

**`M101` `warn_subclass_cycle`**

Subclass cycles: a chain of named classes `A ⊑ B ⊑ … ⊑ A`. Legal OWL 2 (it implies the
members are equivalent), but almost always an accidental hierarchy-maintenance error
rather than an intended equivalence. Reports each class that participates in a cycle.
Cycle length is bounded to 5 using fixed-length patterns over the derived `subclass_of`
edges: real accidental cycles are short, and unbounded recursive traversal of the whole
hierarchy is prohibitively slow on large ontologies.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/modeling_risk/warn_subclass_cycle.cypher"
```

**`M103` `warn_object_property_no_domain_or_range`**

Object properties with neither `ObjectPropertyDomain` nor `ObjectPropertyRange`.
Properties that declare only a domain or only a range are not flagged — this rule
targets properties with no semantic scope at all.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/modeling_risk/warn_object_property_no_domain_or_range.cypher"
```

**`M104` `warn_datatype_property_no_domain`**

Data properties with no `DataPropertyDomain` axiom. Without a domain, the property
can be asserted on any individual regardless of type, often an incomplete ABox
modeling decision.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/modeling_risk/warn_datatype_property_no_domain.cypher"
```

**`M105` `warn_datatype_property_no_range`**

Data properties with no `DataPropertyRange` axiom. Without a range, the property
accepts any literal value with no type constraint, which weakens data quality checks
downstream.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/modeling_risk/warn_datatype_property_no_range.cypher"
```

**`M106` `warn_individual_no_type`**

Named individuals with no `ClassAssertion`. A declared but untyped individual is a
common incomplete ABox pattern — the individual exists in the ontology but contributes
no classifiable information.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/modeling_risk/warn_individual_no_type.cypher"
```

**`M107` `warn_property_dangerous_combination`**

Object properties combining `Transitive` with `Functional` or `InverseFunctional`.
Transitivity collapses entire chains to a single filler, making a functional property
over a transitive chain almost always unsatisfiable or unexpectedly restrictive.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/modeling_risk/warn_property_dangerous_combination.cypher"
```

**`M108` `warn_annotation_punning_object_property`**

An IRI used simultaneously as both an `ObjectProperty` and an `AnnotationProperty`.
OWL 2 DL explicitly permits this (annotation punning), but axioms written against the
object property role are not visible to tools that traverse the same IRI as an
annotation property, and vice versa.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/modeling_risk/warn_annotation_punning_object_property.cypher"
```

**`M109` `warn_annotation_punning_data_property`**

An IRI used simultaneously as both a `DataProperty` and an `AnnotationProperty`.
OWL 2 DL explicitly permits this (annotation punning), but range constraints and
typing rules declared on the data property are not enforced when the same IRI is
accessed through annotation traversal.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/modeling_risk/warn_annotation_punning_data_property.cypher"
```

### `description_logic` (`D...`)

Checks that are useful when you specifically want a stricter OWL 2 DL-oriented
surface.

**`D101` `test_undeclared_entities`**

Named entities (other than built-in OWL 2 IRIs) used in axioms without a corresponding
`Declaration` axiom. OWL 2 DL requires all named entities to be explicitly declared;
undeclared use is a syntactic violation that some parsers silently accept. In Ontopoiesis's
current source-document projection model, this rule reports declarations missing from
the built projection. If the entity belongs to an imported ontology that was not merged
before build, treat the result as closure-dependent rather than as a confirmed
ontology-wide defect.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/description_logic/test_undeclared_entities.cypher"
```

**`D102` `test_punning_class_individual`**

An IRI used simultaneously as both a `Class` and a `NamedIndividual`. OWL 2 DL
disallows this form of punning; it almost always indicates a conflation of the class
taxonomy with its instance data.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/description_logic/test_punning_class_individual.cypher"
```

**`D103` `test_punning_class_datatype`**

An IRI used simultaneously as both a `Class` and a `Datatype`. These inhabit disjoint
domains in OWL 2; the combination is illegal in OWL 2 DL and will be rejected by
conformant reasoners.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/description_logic/test_punning_class_datatype.cypher"
```

**`D104` `test_punning_object_data_property`**

An IRI used simultaneously as both an `ObjectProperty` and a `DataProperty`. These
roles are disjoint in OWL 2; a property cannot relate individuals to individuals and
individuals to literals at the same time.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/description_logic/test_punning_object_data_property.cypher"
```

**`D105` `test_disjoint_classes_shared_subclass_transitive`**

A named class that is a subclass — at any depth — of two classes declared disjoint. Such a
class is unsatisfiable (equivalent to `owl:Nothing`), inheriting from two provably disjoint
parents. This generalizes the direct check [`E103`](#contradictions) through the derived
`subclass_of` closure, catching deep unsatisfiabilities a reasoner would flag but a one-hop
structural check misses. It also covers the degenerate case of a class that is disjoint
with one of its own ancestors, which the shared-subclass pattern alone cannot match. It
walks descendants from the (few) disjoint pairs to stay tractable, with depth capped at 20,
and lives in the opt-in `description_logic` profile
because the closure walk is heavier than the default baseline. It subsumes `E103`, so
direct cases also appear here when both are run.

```cypher
--8<-- "packages/ontopoiesis/src/ontopoiesis/lint/lint_profiles/description_logic/test_disjoint_classes_shared_subclass_transitive.cypher"
```
