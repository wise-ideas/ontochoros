# Ontochoros

**Lint, test, diff, and CI for OWL ontologies — think dbt, for ontology
engineering.**

Ontochoros turns an OWL 2 ontology into an embedded, Cypher-queryable graph,
then gives you the workflow you already trust for code and data — build,
query, lint, test, diff, migrate:

```bash
ontopoiesis build pizza.owx -o pizza.lbug   # OWL/XML → queryable projection
ontopoiesis lint pizza.lbug                 # structural quality gates
ontopoiesis test pizza.lbug tests/          # your own Cypher checks, via pytest
ontopoiesis diff v1.lbug v2.lbug            # what actually changed, per axiom
ontopoiesis export pizza.lbug               # losslessly back to OWL/XML
```

No JVM, no server, no ontologist's API to learn. If you can write a graph
query, you can interrogate, test, and author any ontology. And the payoff is
not hypothetical: point the stock lint rules at vocabularies the web runs
on — FoaF, the SNOMED CT ontology, the Human Phenotype Ontology — and they
surface real structural defects their maintainers never saw.
[Why this exists, and the evidence →](why.md)

## One graph, every question

Catching defects is only half of it. The build turns your ontology into a graph
whose shape *is* OWL 2, so you stop learning a bespoke ontology API and start
asking questions directly. *Which live classes are defined using a term the file
itself marks obsolete?* is one Cypher query, not a research project — and it
answers in seconds on graphs of a million-plus nodes. Lint rules, tests, diffs,
and migrations all read that same graph, so the moment you can query an ontology
you can check it, change it, and gate it in CI. One artifact, one query language,
every workflow.

## The packages

Three packages, one stack. Most people start — and stay — with the CLI.

| I want to… | Reach for | Start at |
| --- | --- | --- |
| Lint, test, diff, and gate an ontology from the command line | **Ontopoiesis** | [Quickstart](ontopoiesis/quickstart.md) |
| Query an ontology with Cypher inside my own Python | **Ontoplexis** | [Quickstart](ontoplexis/quickstart.md) |
| Move typed OWL 2 records between systems as JSON | **Ontophora** | [Introduction](ontophora/index.md) |

The cards below say what each package *is*; the table says which to reach for.

<div class="grid cards" markdown>

- **[Ontopoiesis](ontopoiesis/index.md)** — *the CLI you run*

    Build, query, lint, test, diff, migrate, and render ontologies, locally
    and in CI.

- **[Ontoplexis](ontoplexis/index.md)** — *the graph underneath*

    Lossless OWL/XML ⇄ property-graph mapping as a Python library, for when
    you want raw Cypher in your own code.

- **[Ontophora](ontophora/index.md)** — *the typed records*

    Standalone Pydantic models for OWL 2 constructs, with a stable JSON
    format for moving them between systems.

</div>

## Where to start

- New here? Read [why Ontochoros exists](why.md), then run the
  [Ontopoiesis quickstart](ontopoiesis/quickstart.md) — it builds, queries,
  lints, and diffs bundled sample ontologies in about ten minutes.
- Want proof first? The [case studies](ontopoiesis/case-studies.md) audit
  ten production ontologies and show every command.
- Embedding the graph in your own application? Start with the
  [Ontoplexis quickstart](ontoplexis/quickstart.md).
- Exchanging typed construct records between systems? See the
  [Ontophora introduction](ontophora/index.md).
