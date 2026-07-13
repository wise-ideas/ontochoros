---
title: Quickstart
---

# Quickstart

Parse an ontology, query it with Cypher, and round-trip it back to a document.

## Prerequisites

- Python 3.11+ (the package is pure Python)

Install:

```bash
pip install ontoplexis
```

Save this as `animals.owlxml`:

```xml
<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#" ontologyIRI="http://example.org/animals">
    <Prefix name="rdfs" IRI="http://www.w3.org/2000/01/rdf-schema#"/>
    <Declaration><Class IRI="http://example.org/animals#Animal"/></Declaration>
    <Declaration><Class IRI="http://example.org/animals#Pet"/></Declaration>
    <Declaration><Class IRI="http://example.org/animals#Dog"/></Declaration>
    <SubClassOf>
        <Class IRI="http://example.org/animals#Pet"/>
        <Class IRI="http://example.org/animals#Animal"/>
    </SubClassOf>
    <SubClassOf>
        <Class IRI="http://example.org/animals#Dog"/>
        <Class IRI="http://example.org/animals#Pet"/>
    </SubClassOf>
    <AnnotationAssertion>
        <AnnotationProperty abbreviatedIRI="rdfs:label"/>
        <IRI>http://example.org/animals#Animal</IRI>
        <Literal xml:lang="en">Animal</Literal>
    </AnnotationAssertion>
</Ontology>
```

OWL/XML is the input format — it is also exactly what the graph maps to.
Ontologies in other serializations (Turtle, RDF/XML, functional syntax, OBO,
…) are one `robot convert`, Protégé export, or OWLAPI call away; see
[Work with Other Formats](howto/documents.md).

## Step 1: Parse

```python
from pathlib import Path
from ontoplexis import Ontology

ont = Ontology.from_owlxml(Path("animals.owlxml").read_text())
print(len(ont.graph.nodes), "nodes,", len(ont.graph.edges), "edges")
```

The document was walked into a graph. Every node has a `kind` — the OWL/XML
element name:

```python
from collections import Counter
print(Counter(n.kind for n in ont.graph.nodes))
```

## Step 2: Query

```python
with ont.project() as proj:
    rows = proj.execute(
        "MATCH (a:N)<-[:E {role: 'sub'}]-(:N {kind: 'SubClassOf'})"
        "-[:E {role: 'super'}]->(b:N) "
        "WHERE a.iri IS NOT NULL AND b.iri IS NOT NULL "
        "RETURN a.iri AS sub_iri, b.iri AS super_iri ORDER BY sub_iri"
    )
    for row in rows:
        print(row["sub_iri"], "⊑", row["super_iri"])
```

Expected output:

```
http://example.org/animals#Dog ⊑ http://example.org/animals#Pet
http://example.org/animals#Pet ⊑ http://example.org/animals#Animal
```

Labels are ordinary graph data — no special API:

```python
with ont.project() as proj:
    rows = proj.execute(
        "MATCH (aa:N {kind: 'AnnotationAssertion'})"
        "-[:E {role: 'subject'}]->(s:N), "
        "(aa)-[:E {role: 'value'}]->(v:N {kind: 'Literal'}) "
        "RETURN s.text AS subject, v.text AS label"
    )
```

## Step 3: Persist and reload

```python
from ontoplexis import Projection

ont.save_projection("animals.lbug").close()
proj = Projection.open("animals.lbug")
```

## Step 4: Round-trip

```python
print(ont.to_owlxml())
```

The graph serializes back to the same OWL/XML structural tree it was parsed
from — the round-trip fidelity tests prove this against OWLAPI, the reference
implementation. Convert onward to other formats with an external tool if you
need them.
