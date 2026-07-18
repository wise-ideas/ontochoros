---
title: "Ontopoiesis"
---

# Ontopoiesis

Ontopoiesis is the command line you run to manage an ontology like code. It
builds an OWL/XML document into a Cypher-queryable
[Ontoplexis](../ontoplexis/index.md) projection, then gives you the
day-to-day workflows around that one artifact — query, lint, test, diff,
impact analysis, rendering, and Cypher migrations:

```bash
ontopoiesis build pizza.owx -o pizza.lbug   # OWL/XML → projection
ontopoiesis lint pizza.lbug                 # structural quality checks
ontopoiesis test pizza.lbug tests/          # your own Cypher tests, via pytest
ontopoiesis diff before.lbug after.lbug     # what changed, per axiom
ontopoiesis export pizza.lbug               # projection → OWL/XML
```

Every command reads the same projection, so you parse the source ontology
once and interrogate it as often as you like — locally or in CI. Quality
gates are plain `.cypher` files that fail when they return rows, which means
your team extends the rule set the way it writes dbt tests. On real
ontologies the bundled baseline alone finds shipping defects; the
[case studies](case-studies.md) reproduce them command by command, and
[Why Ontotheke](../why.md) explains the approach.

Ontopoiesis parses OWL/XML only, matching Ontoplexis. Other serializations
(Turtle, RDF/XML, functional syntax, OBO) are one `robot convert` or Protégé
export away; classify with an external reasoner before building if you want
inferred axioms in the graph.

Start with the [Quickstart](quickstart.md), then see the
[CLI reference](cli.md) and the [projection model](cypher-model.md).
