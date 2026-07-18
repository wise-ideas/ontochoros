# Ontoplexis

Query [OWL 2](https://www.w3.org/TR/owl2-syntax/) ontologies with Cypher.

Ontoplexis loads an OWL/XML document into an embedded
[Ladybug](https://ladybugdb.com) graph whose shape is the OWL 2 structural
specification, exposes raw Cypher over it, and serializes the graph
losslessly back to OWL/XML. If you can write a graph query, you can
introspect, test, diff, and author ontologies — no ontologist's API, no JVM.

## Scope

```
OWL/XML         ──(one generic walker)──▶  Ladybug graph
Ladybug graph   ──(the inverse walker)──▶  OWL/XML
```

Ontoplexis owns the OWL/XML-to-graph mapping, embedded graph storage, Cypher
access, and OWL/XML round trips. Alongside the structural graph it maintains a
derived-edge table that exposes the common binary relations (subsumption,
typing, labels, …) as one-hop edges — a refreshable cache over asserted
structure, not inference. It does not provide typed Python classes for OWL
axioms, format conversion, reasoning, or profile checking.

## Relationship to the stack

Ontoplexis is the graph core for the family:

- [Ontopoiesis](https://github.com/wise-ideas/ontotheke/tree/main/packages/ontopoiesis) depends on it for
  operator workflows: build, lint, test, diff, impact analysis, rendering, and
  migrations.
- [Ontophora](https://github.com/wise-ideas/ontotheke/tree/main/packages/ontophora) is the independent
  sister library for typed OWL 2 construct records. Ontoplexis deliberately
  keeps its structural model in the graph rather than depending on those
  models.

## Installation

```bash
pip install ontoplexis
```

Pure Python; requires Python 3.11+.

## Quickstart

```python
from pathlib import Path
from ontoplexis import Ontology

ont = Ontology.from_owlxml(Path("pizza.owx").read_text())

with ont.project() as proj:
    # Derived one-hop edges for the common relations …
    rows = proj.execute(
        "MATCH (a:N)-[:D {relation: 'subclass_of'}]->(b:N) "
        "RETURN a.iri AS sub_iri, b.iri AS super_iri"
    )
    # … and the full structural graph when you need every construct.
    axioms = proj.execute(
        "MATCH (ax:N)-[:E]->(:N {iri: 'https://example.org/pizza#Margherita'}) "
        "RETURN DISTINCT ax.kind AS kind"
    )

print(ont.to_owlxml())   # lossless round trip
```

## Documentation

The [documentation](https://wise-ideas.github.io/ontotheke/ontoplexis/) covers the
quickstart, graph schema, edge roles, authoring with Cypher, document
conversion, and development setup.

## License

Ontoplexis is licensed under the [Apache License 2.0](https://github.com/wise-ideas/ontotheke/blob/main/packages/ontoplexis/LICENSE).
