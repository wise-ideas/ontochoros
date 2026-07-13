---
title: Ontophora
---

# Ontophora

Ontophora provides typed [Pydantic](https://docs.pydantic.dev/) models for the
[OWL 2 structural specification](https://www.w3.org/TR/owl2-syntax/). It gives
an OWL-aware application a compact, validated representation of entities,
expressions, axioms, and ontology documents without parsing or serializing an
OWL surface syntax.

Every construct is a record with a `uid` and a discriminating `kind`. Records
point to one another by UID, so a package can preserve the structural graph
without embedding the same construct repeatedly.

```python
from ontophora import Klass, SubClassOf

animal = Klass(uid="0x1", iri="https://example.org/animals#Animal")
dog = Klass(uid="0x2", iri="https://example.org/animals#Dog")
subclass = SubClassOf(
    uid="0x3",
    sub_class_expression=dog.uid,
    super_class_expression=animal.uid,
)
```

## What it provides

- Pydantic models for the OWL 2 structural construct catalog.
- A discriminated union and JSON Schema derived from that catalog.
- UID references that validate their wire shape while leaving graph resolution
  to the consumer.
- A small JSON envelope for moving sets of construct records between systems.
- Content-based fingerprints for comparing records independently of their UIDs.

## What it does not provide

Ontophora does not parse OWL/XML, Turtle, or RDF/XML; reason over ontologies;
or resolve references into an object graph. Those operations belong to the
application that owns the package. For an OWL/XML-to-graph workflow, see the
sibling project [Ontoplexis](https://wise-ideas.github.io/ontotheke/ontoplexis/).

## Start here

- [Build an ontology package](tutorials/first-package.md) creates and
  serializes a small connected record set.
- [Read and write JSON](how-to/json.md) shows the package envelope at a system
  boundary.
- [The model](explanation/model.md) explains records, references, and the
  registry.
- [Public API](reference/api.md) lists the supported entry points.
