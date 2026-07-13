---
title: "CI"
---

Ontopoiesis works best in CI when you build the projection once, then reuse that `.lbug`
artifact across lint and test steps. That keeps OWL parsing out of the hot path for
every quality gate and makes failures easier to reason about: one build step, many
read-only checks.

## Build Once, Reuse Everywhere

The projection is the shared artifact for graph-native checks:

- `ontopoiesis lint` reads the built projection
- `ontopoiesis test` reads the same projection
- `ontopoiesis diff` compares two projections when you need a release gate

## GitHub Actions Example

```yaml
name: ontology-ci

on:
  pull_request:
  push:
    branches: [main]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v6

      - name: Install workspace
        run: uv sync

      - name: Build projection
        run: uv run ontopoiesis build ontology.owlxml -o ontology.lbug

      - name: Lint (required)
        run: uv run ontopoiesis lint ontology.lbug

      - name: Tests (required)
        run: uv run ontopoiesis test ontology.lbug tests/

      - name: Editorial lint (advisory)
        run: uv run ontopoiesis lint ontology.lbug --profile editorial || true
```

## Release Gate Diff

When you want a release check that answers "what changed semantically," build two
projections and diff them:

```yaml
- name: Build previous release projection
  run: uv run ontopoiesis build ontology-prev.owlxml -o before.lbug

- name: Build candidate projection
  run: uv run ontopoiesis build ontology.owlxml -o after.lbug

- name: Semantic diff
  run: uv run ontopoiesis diff before.lbug after.lbug --format json --output diff.json
```

The diff command reports added and removed constructs by semantic fingerprint, not text
line changes. That makes it suitable for release review and artifact publication.

For the full exit code reference, see the [CLI reference](cli.md#exit-codes).

## Required vs Advisory Checks

Use normal command invocation for required gates and append `|| true` for advisory
checks whose output you still want to see in CI:

```yaml
- name: Required baseline
  run: uv run ontopoiesis lint ontology.lbug

- name: Advisory modeling-risk profile
  run: uv run ontopoiesis lint ontology.lbug --profile modeling_risk || true
```

That pattern keeps the build red only for gates you have decided should block merges.

## Related

- [CLI reference](cli.md) — command surface and flags
- [Lint](lint.md) — bundled structural checks
- [Tests](tests.md) — project-specific Cypher assertions
- [Diff](diff.md) — semantic change review between projections
