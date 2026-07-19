# Ontochoros

**Lint, test, diff, and CI for OWL ontologies — think dbt, for ontology
engineering.**

Ontochoros turns an OWL 2 ontology into an embedded, Cypher-queryable graph,
then puts a standard engineering workflow on top — build, query, lint, test,
diff, migrate:

```bash
ontopoiesis build pizza.owx -o pizza.lbug   # OWL/XML → queryable projection
ontopoiesis lint pizza.lbug                 # structural quality gates
ontopoiesis test pizza.lbug tests/          # your own Cypher checks, via pytest
ontopoiesis diff v1.lbug v2.lbug            # what actually changed, per axiom
ontopoiesis export pizza.lbug               # losslessly back to OWL/XML
```

Everything is pure Python: no JVM, no server, no specialized ontology API.
If you can write a graph query, you can interrogate, test, and author an
ontology. Run against widely used vocabularies — FoaF, the SNOMED CT
ontology, the Human Phenotype Ontology — the stock lint rules surface
structural defects in the released files that standard reports do not flag.
[Why this exists, and the evidence →](why.md)

## One graph, one query language

The build turns your ontology into a graph whose shape *is* OWL 2 — the
structural specification, not the RDF encoding, so there are no reified
axioms, `rdf:first`/`rdf:rest` chains, or blank nodes to reassemble — and
any question about the ontology can be asked directly. *Which live classes are
defined using a term the file itself marks obsolete?* is a single Cypher
query, and it answers in seconds on graphs of a million-plus nodes. Lint
rules, tests, diffs, and migrations all read that same graph: once you can
query an ontology, you can check it, change it, and gate it in CI.

## The packages

Three packages form one stack. Most people only need the CLI.

| I want to… | Reach for | Start at |
| --- | --- | --- |
| Lint, test, diff, and gate an ontology from the command line | **Ontopoiesis** | [Quickstart](ontopoiesis/quickstart.md) |
| Query an ontology with Cypher inside my own Python | **Ontoplexis** | [Quickstart](ontoplexis/quickstart.md) |
| Move typed OWL 2 records between systems as JSON | **Ontophora** | [Introduction](ontophora/index.md) |

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
- To see the lint findings first: the
  [case studies](ontopoiesis/case-studies.md) audit ten production ontologies
  and show every command.
- Embedding the graph in your own application? Start with the
  [Ontoplexis quickstart](ontoplexis/quickstart.md).
- Exchanging typed construct records between systems? See the
  [Ontophora introduction](ontophora/index.md).
