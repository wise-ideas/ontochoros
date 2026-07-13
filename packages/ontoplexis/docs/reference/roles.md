---
title: Edge Roles
---

# Edge Roles

Roles decorate edges so queries read naturally. They are derived from the
parent node's kind and the child's position among non-annotation children —
document `position` is what actually round-trips. The table below is the
complete role vocabulary. `_ROLES` defines non-root, non-annotation mappings;
`role_for` assigns annotation and `Ontology` roles directly.

`Annotation` children of any element take the role `annotation`. Children of
the `Ontology` root take `prefix`, `import`, `annotation`, or `axiom` by kind.

| Parent kind | Roles (by position) |
|---|---|
| `SubClassOf`, `Sub*PropertyOf` | `sub`, `super` |
| `Equivalent*`, `Disjoint*`, `SameIndividual`, `DifferentIndividuals` | `operand`… |
| `DisjointUnion` | `class`, then `operand`… |
| `Object/DataIntersectionOf`, `…UnionOf`, `…OneOf`, `ObjectPropertyChain` | `operand`… |
| `Object/DataComplementOf` | `operand` |
| `HasKey` | `class`, then `property`… |
| `Object/Data SomeValuesFrom`, `AllValuesFrom`, `HasValue`, cardinalities | `property`, `filler` |
| `ObjectHasSelf`, `ObjectInverseOf`, `Functional*Property`, `(In)Transitive/(A)Symmetric/(Ir)ReflexiveObjectProperty` | `property` |
| `InverseObjectProperties` | `property`, `property` |
| `Object/Data/Annotation PropertyDomain` | `property`, `domain` |
| `Object/Data/Annotation PropertyRange` | `property`, `range` |
| `ClassAssertion` | `class`, `individual` |
| `(Negative)Object/DataPropertyAssertion` | `property`, `subject`, `object` |
| `AnnotationAssertion` | `property`, `subject`, `value` |
| `Annotation` | `property`, `value` |
| `Declaration` | `entity` |
| `DatatypeDefinition` | `datatype`, `range` |
| `DatatypeRestriction` | `datatype`, then `facet`… |
| `FacetRestriction` | `value` |

Kinds not in the table produce edges with `role` null; query by `position`
instead.
