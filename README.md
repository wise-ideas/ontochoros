# Ontotheke

Ontotheke is the development monorepo for the OWL 2 tooling family. It contains
independently publishable Python packages that evolve together:

- `packages/ontophora`: typed OWL 2 construct records.
- `packages/ontoplexis`: lossless OWL/XML and Cypher-queryable graph mapping.
- `packages/ontopoiesis`: operator CLI and workflows over Ontoplexis projections.

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

Each package versions independently with CalVer (`YYYY.M.patch`) and publishes
to PyPI under its own name. Release tags identify both the package and its
version:

```text
ontophora-v2026.7.0
ontoplexis-v2026.7.10
ontopoiesis-v2026.7.0
```

Pushing a tag runs that package's checks, builds it, and publishes it to PyPI
via the release workflow. The tag version must match the version in the
package's `pyproject.toml`.
