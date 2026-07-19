# Ontopoiesis

Lint, test, diff, and CI for OWL 2 ontologies, from a single command line.

Ontopoiesis builds an OWL/XML ontology into a Cypher-queryable
[Ontoplexis](https://github.com/wise-ideas/ontochoros/tree/main/packages/ontoplexis)
projection, then runs the day-to-day workflows around that one artifact:
query, lint, test, diff, impact analysis, render, migrate, and export.
Quality gates are plain `.cypher` files that fail when they return rows, so
teams extend the rule set the way they write dbt tests — and the stock
baseline alone finds shipping defects in production ontologies
([why this exists](https://wise-ideas.github.io/ontochoros/why/)).

## Scope

Ontopoiesis owns command-oriented workflows and their conventions. It does not
own the OWL/XML parser or graph projection model; those belong to Ontoplexis.
It also does not parse formats other than OWL/XML, reason over an ontology, or
provide typed OWL construct models.

## Relationship to the stack

```text
OWL/XML  -->  Ontoplexis projection  -->  Ontopoiesis workflows
```

Ontopoiesis depends on Ontoplexis. [Ontophora](https://github.com/wise-ideas/ontochoros/tree/main/packages/ontophora)
is a separate sister library that provides typed OWL 2 construct records; it is
not a dependency of this CLI.

## Install

```bash
pip install ontopoiesis
```

```bash
ontopoiesis build pizza.owlxml -o pizza.lbug
ontopoiesis lint pizza.lbug
ontopoiesis test pizza.lbug tests/
ontopoiesis export pizza.lbug
```

## Documentation

Read the [documentation](https://wise-ideas.github.io/ontochoros/ontopoiesis/)
for installation, the quickstart, command guides, and CLI reference.

## License

Ontopoiesis is licensed under the [Apache License 2.0](https://github.com/wise-ideas/ontochoros/blob/main/packages/ontopoiesis/LICENSE).
