# Ontoplexis

Query [OWL 2](https://www.w3.org/TR/owl2-syntax/) ontologies with Cypher.

Ontoplexis loads an OWL/XML document into an embedded
[Ladybug](https://ladybugdb.com) graph whose shape is the OWL 2 structural
specification. It exposes raw Cypher over that graph and serializes the graph
losslessly back to OWL/XML.

## Scope

```
OWL/XML         ──(one generic walker)──▶  Ladybug graph
Ladybug graph   ──(the inverse walker)──▶  OWL/XML
```

Ontoplexis owns the OWL/XML-to-graph mapping, embedded graph storage, Cypher
access, and OWL/XML round trips. It does not provide typed Python classes for
OWL axioms, format conversion, reasoning, profile checking, or an RDF triple
view.

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
    rows = proj.execute(
        "MATCH (a:N)<-[:E {role: 'sub'}]-(:N {kind: 'SubClassOf'})"
        "-[:E {role: 'super'}]->(b:N) "
        "WHERE a.iri IS NOT NULL AND b.iri IS NOT NULL "
        "RETURN a.iri AS sub_iri, b.iri AS super_iri"
    )

print(ont.to_owlxml())   # lossless round trip
```

## Documentation

The [documentation](https://wise-ideas.github.io/ontotheke/ontoplexis/) covers the
quickstart, graph schema, edge roles, authoring with Cypher, document
conversion, and development setup.

## License

Ontoplexis is licensed under the [Apache License 2.0](https://github.com/wise-ideas/ontotheke/blob/main/packages/ontoplexis/LICENSE).
