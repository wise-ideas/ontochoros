# Ontophora

Typed [Pydantic](https://docs.pydantic.dev/) models for the [OWL 2 structural
specification](https://www.w3.org/TR/owl2-syntax/).

Ontophora represents OWL entities, expressions, axioms, and ontology documents
as validated records. Each record has a UID and a fixed construct kind; records
refer to one another by UID rather than nesting an object graph.

## Scope

Ontophora owns:

- Typed models for the OWL 2 structural construct catalog.
- Construct validation, a registry-derived JSON Schema, and reference shapes.
- JSON envelopes for sets of construct records and content fingerprints.

It does not parse or serialize OWL document formats, store a graph, execute
queries, reason over an ontology, or resolve references. Applications that own
a complete record set perform those operations.

## Relationship to the stack

Ontophora is the typed-model library in the wider ontology tooling family. It
is independent of its sister projects:

- [Ontoplexis](https://github.com/wise-ideas/ontotheke/tree/main/packages/ontoplexis) maps OWL/XML to a
  Cypher-queryable graph and back.
- [Ontopoiesis](https://github.com/wise-ideas/ontotheke/tree/main/packages/ontopoiesis) provides operator
  workflows such as build, lint, test, diff, and render on Ontoplexis
  projections.

Neither project currently depends on Ontophora at runtime.

## Install

```bash
pip install ontophora
```

```python
from ontophora import Klass, SubClassOf, records_to_json

animal = Klass(uid="0x1", iri="https://example.org/animals#Animal")
dog = Klass(uid="0x2", iri="https://example.org/animals#Dog")
axiom = SubClassOf(
    uid="0x3",
    sub_class_expression=dog.uid,
    super_class_expression=animal.uid,
)

print(records_to_json([animal, dog, axiom]))
```

## Documentation

Read the [documentation](https://wise-ideas.github.io/ontotheke/ontophora/) for a
tutorial, JSON package guidance, the model rationale, and the API reference.

## License

Ontophora is licensed under the [Apache License 2.0](https://github.com/wise-ideas/ontotheke/blob/main/packages/ontophora/LICENSE).
