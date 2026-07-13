---
title: Ontoplexis
---

# Ontoplexis

Ontoplexis makes OWL 2 ontologies queryable with Cypher.

It loads an OWL/XML document into an embedded [Ladybug](https://ladybugdb.com)
graph database whose shape *is* the OWL 2 structural specification — one node
per axiom, expression, or entity; one ordered edge per parent–child slot — and
gives you raw Cypher over it. The same graph serializes losslessly back to
OWL/XML.

## Who this is for

Ontoplexis is for developers and data engineers who want to work with OWL
ontologies using the tools they already know — graph queries — rather than an
ontologist's API. If you can write Cypher, you can introspect, test, diff, and
even author ontologies.

## The pipeline

```
OWL/XML         ──(one generic walker)──▶  Ladybug graph
Ladybug graph   ──(the inverse walker)──▶  OWL/XML
```

There is no hand-written vocabulary anywhere in the system. OWL/XML is the
OWL 2 structural specification serialized as XML, so the mapping to a graph is
mechanical, and round-trip fidelity is checked against the reference
implementation (OWLAPI, as a development-only test oracle) in the test suite
rather than maintained by hand. Ontologies in other serializations are one
external conversion away; see [Work with Other Formats](howto/documents.md).

## A one-minute example

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

## Where to go next

- [Quickstart](quickstart.md) — run the full pipeline against a small ontology
- [The Design](concepts/design.md) — why OWL/XML is the model and what that buys
- [The Graph Schema](concepts/schema.md) — the node and edge tables you query
- [Public API](reference/api.md) — every public name
