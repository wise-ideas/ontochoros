# Ontochoros

**Lint, test, diff, and CI for OWL 2 ontologies — think dbt, for ontology
engineering.**

Ontochoros turns an ontology into an embedded, Cypher-queryable graph, then
puts an engineering workflow on top: author, lint, test, diff, analyze
impact, and gate in CI — all over the OWL 2 structural specification. It is
pure Python, needs no JVM at runtime, and round-trips losslessly to OWL/XML.

```bash
pip install ontopoiesis

ontopoiesis build pizza.owx -o pizza.lbug   # OWL/XML → queryable projection
ontopoiesis lint pizza.lbug                 # structural quality gates
ontopoiesis diff v1.lbug v2.lbug            # what changed, per axiom
ontopoiesis export pizza.lbug               # losslessly back to OWL/XML
```

**[Documentation](https://wise-ideas.github.io/ontochoros/)** ·
**[Why this exists](https://wise-ideas.github.io/ontochoros/why/)** ·
**[Quickstart](https://wise-ideas.github.io/ontochoros/ontopoiesis/quickstart/)**

This repository is the development monorepo for three independently published
packages that evolve together:

- [`packages/ontopoiesis`](packages/ontopoiesis): the operator CLI —
  build, query, lint, test, diff, migrate, render.
- [`packages/ontoplexis`](packages/ontoplexis): the graph core — lossless
  OWL/XML ⇄ Cypher-queryable graph mapping.
- [`packages/ontophora`](packages/ontophora): standalone typed Pydantic
  records for OWL 2 constructs.

## Positioning

Ontochoros complements reasoners, SHACL, and triple stores; it replaces none
of them. Non-goals, stated up front:

- **Reasoning.** Nothing here computes entailments. Materialize inference
  externally — `ontopoiesis reason` wraps `robot reason` (ELK/HermiT) behind
  an opt-in, user-provided jar — and build the output; inferred axioms then
  behave like any other told structure.
- **Instance-data (ABox) validation.** For SHACL over RDF data graphs, use
  pyshacl. The Cypher lint/test system here validates ontology *structure*.
- **Non-OWL/XML formats.** OWL/XML is the only document format the toolchain
  parses; `ontopoiesis convert` pre-converts Turtle/RDF-XML/OBO through the
  same opt-in ROBOT shim.
- **A hosted service.** These are libraries and a CLI, meant as components in
  a pipeline.

Running the bundled lint baseline against production ontologies surfaces real
defects — FoaF, the SNOMED CT standard ontology, and the Human Phenotype
Ontology among them — that off-the-shelf reasoners and reports miss. See
[Why Ontochoros](https://wise-ideas.github.io/ontochoros/why/) for the argument
and the [case studies](https://wise-ideas.github.io/ontochoros/ontopoiesis/case-studies/)
for each finding reproduced command by command.

## Stability

Pre-1.0 in spirit: packages version by CalVer and there is no compatibility
promise yet. Public APIs are pinned by contract tests and names are removed
deliberately, never silently — but they *are* removed. Built projections
(`.lbug`) are caches, not interchange artifacts: rebuild them after upgrading
rather than carrying them across versions.

## Development

Install every workspace package and its development dependencies:

```bash
uv sync --all-packages --all-groups
```

Run all checks, or the narrow check for one package, from the repository root:

```bash
make check
make check-ontoplexis
make test-ontophora
```

Each package remains separately versioned and publishable. The root `uv.lock`
locks the complete development workspace.

## Releases

Each package versions independently and publishes to PyPI under its own name.
Versions are the UTC release date (`YYYY.M.D`), with at most one release per
package per day.

To release a package, run the release workflow manually from the Actions tab
and select the package. The workflow runs that package's checks, stamps the
version, builds and publishes it to PyPI, then creates a tag and GitHub
release identifying the package and its version:

```text
ontophora-v2026.7.19
ontoplexis-v2026.7.19
ontopoiesis-v2026.7.19
```

No version bump or tag push is needed; the version in each package's
`pyproject.toml` is not used for releases.
