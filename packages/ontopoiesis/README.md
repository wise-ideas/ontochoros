# Ontopoiesis

The operator CLI for OWL 2 ontology projections.

Ontopoiesis builds an OWL/XML ontology into an
[Ontoplexis](https://github.com/wise-ideas/ontotheke/tree/main/packages/ontoplexis) projection, then runs
the day-to-day workflows around that projection: query, lint, test, diff,
impact analysis, render, migrate, and export.

## Scope

Ontopoiesis owns command-oriented workflows and their conventions. It does not
own the OWL/XML parser or graph projection model; those belong to Ontoplexis.
It also does not parse formats other than OWL/XML, reason over an ontology, or
provide typed OWL construct models.

## Relationship to the stack

```text
OWL/XML  -->  Ontoplexis projection  -->  Ontopoiesis workflows
```

Ontopoiesis depends on Ontoplexis. [Ontophora](https://github.com/wise-ideas/ontotheke/tree/main/packages/ontophora)
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

Read the [documentation](https://wise-ideas.github.io/ontotheke/ontopoiesis/)
for installation, the quickstart, command guides, and CLI reference.

## License

Ontopoiesis is licensed under the [Apache License 2.0](https://github.com/wise-ideas/ontotheke/blob/main/packages/ontopoiesis/LICENSE).
