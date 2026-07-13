---
title: The Graph Schema
---

# The Graph Schema

One node table `N`, one relationship table `E`. The schema is fixed — it does
not depend on which constructs an ontology uses.

## Node table `N`

| Column | Type | Meaning |
|---|---|---|
| `uid` | STRING (PK) | Synthetic id, assigned in document order (`n0`, `n1`, …) |
| `kind` | STRING | OWL/XML element name: `Class`, `SubClassOf`, `ObjectSomeValuesFrom`, `Literal`, … |
| `iri` | STRING | Entity IRI (also `Prefix` expansion and `Datatype` IRI) |
| `abbreviated_iri` | STRING | CURIE form (`rdfs:label`) when the document used one |
| `node_id` | STRING | `AnonymousIndividual` blank-node id |
| `datatype_iri` | STRING | `Literal` datatype |
| `lang` | STRING | `Literal` language tag |
| `facet` | STRING | `FacetRestriction` facet IRI |
| `prefix_name` | STRING | `Prefix` name |
| `ontology_iri`, `version_iri` | STRING | On the `Ontology` node |
| `text` | STRING | Element text: `Literal` value, `IRI` element content, `Import` target |
| `cardinality` | INT64 | On cardinality restrictions |

Unused columns are null. Named entities of the same kind and identifier are merged:
`<Class IRI="…#Dog"/>` is one node no matter how many axioms mention it, so entity nodes
are natural join points. Entities with different OWL kinds may use the same IRI.

## Relationship table `E`

| Column | Type | Meaning |
|---|---|---|
| `position` | INT64 | Child index in document order — this is what round-trips |
| `role` | STRING | Query-facing name; see [Edge Roles](../reference/roles.md) |

Every edge points from a parent element to a child element. An axiom node's
children are its arguments; the `Ontology` root's children are prefixes,
imports, annotations, and axioms.

## Reading the shape

A `SubClassOf` axiom with an annotation looks like:

```
(:N {kind:'SubClassOf'})
   -[:E {position:0, role:'annotation'}]-> (:N {kind:'Annotation'}) -> …
   -[:E {position:1, role:'sub'}]->        (:N {kind:'Class', iri:'…#Dog'})
   -[:E {position:2, role:'super'}]->      (:N {kind:'Class', iri:'…#Pet'})
```

Nested expressions nest as deeper trees: a qualified restriction is a node
whose `filler` child is another expression node, and so on. Entity nodes at
the leaves are shared across the whole graph.
