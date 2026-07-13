---
title: The Design
---

# The Design

Ontoplexis is built on one idea: **OWL/XML is the OWL 2 structural
specification already serialized as a tree**, so a document-to-graph mapping
needs no vocabulary — just a generic walker.

## The problem it avoids

Making OWL queryable usually means choosing a model and writing per-construct
mapping code: one class (or table, or handler) for each of OWL 2's ~70 axiom
and expression types, on every side of every boundary. That code is the
system: it must be maintained in lockstep with itself, and every round-trip
guarantee is a promise kept by hand.

The other common shortcut — loading the ontology's RDF triples directly — gets
a graph cheaply but the *wrong* graph: OWL's RDF encoding reifies annotated
axioms, chains collections through `rdf:first`/`rdf:rest`, and scatters
restrictions across blank nodes. The query semantics you want are the
structural specification, not its RDF encoding.

## The mechanical mapping

In OWL/XML, the element name *is* the construct kind, attributes *are* its
scalar values, and child order *is* its argument order. So the mapping is:

| OWL/XML | Graph |
|---|---|
| Element occurrence | Node (`kind` = element name) |
| Attribute | Node property |
| Child element | Edge, with `position` = document order |
| Named entity (`Class`, `ObjectProperty`, …) | One node per kind and identifier, shared by every occurrence |
| `Literal` / `IRI` / `AbbreviatedIRI` | One node per distinct value |
| `AnonymousIndividual` | One node per `nodeID` |

Relative IRIs are resolved against `xml:base` at parse time, so the stored
graph is always absolute and base-free.

The only OWL-specific knowledge in the system is a small data table that
decorates edges with query-facing **roles** (`sub`, `super`, `property`,
`filler`, `operand`, `annotation`, …) so queries read naturally. Roles are
decoration; `position` is what round-trips. See [Edge Roles](../reference/roles.md).

## Where OWLAPI fits

Only in the test suite. The hard, format-specific work — parsing Turtle or
RDF/XML and executing the RDF-to-structural reverse mapping — belongs to
OWLAPI, the reference implementation, and the tools built on it (ROBOT,
Protégé). Ontoplexis does not wrap them: documents in other serializations
are pre-converted to OWL/XML with whichever of those tools you already use,
and reasoning (materializing inferred axioms) happens the same way, before
loading. The package itself is pure Python.

The test suite downloads [ROBOT](http://robot.obolibrary.org/), the OBO
community's OWLAPI CLI, as a **development-only test oracle**. It never
ships, and the repository contains no Java code at all.

## Round trips are proven, not promised

`parse_owlxml(serialize_owlxml(parse_owlxml(x)))` reproduces the same graph by
construction, and the test suite goes further: it converts documents to canonical functional syntax
through the OWLAPI oracle before and after both the document path and the
database path and requires byte equality. If the walker ever mishandles a
construct, the reference implementation fails the build.

## Non-goals

- **No typed axiom classes in Python.** The structural spec lives in the
  graph shape; typed models live in the sister package `ontophora`.
- **No runtime format conversion, reasoning, or profile checking.** OWLAPI
  is the test oracle, not a dependency.
- **No RDF triple view.** See above.
