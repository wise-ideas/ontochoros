---
title: "Ontopoiesis"
---

# Ontopoiesis

Ontopoiesis is the operator CLI for the
[ontoplexis](https://wise-ideas.github.io/ontotheke/ontoplexis/) stack: it turns OWL/XML
ontologies into Cypher-queryable Ladybug projections and gives you the
day-to-day workflows around them — query, lint, test, diff, impact analysis,
rendering, and Cypher migrations.

```bash
ontopoiesis build pizza.owx            # OWL/XML → pizza.lbug projection
ontopoiesis lint pizza.lbug            # structural quality checks
ontopoiesis test pizza.lbug tests/     # your own Cypher tests, via pytest
ontopoiesis diff before.lbug after.lbug
ontopoiesis export pizza.lbug          # projection → OWL/XML
```

OWL/XML is the only document format, matching ontoplexis. Other
serializations (Turtle, RDF/XML, functional syntax, OBO) are one
`robot convert` or Protégé export away; classify with an external reasoner
before building if you want inferred axioms in the graph.

Start with the [Quickstart](quickstart.md), then see the
[CLI reference](cli.md) and the [projection model](cypher-model.md).
