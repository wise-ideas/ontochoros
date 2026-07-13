---
title: "Public Surface"
---

This page defines what currently counts as Ontopoiesis's public surface and what does not.

The point is not to freeze the entire internal layout. The point is to make future
documentation, packaging, and restructuring decisions more deliberate.

## Classification levels

Ontopoiesis currently uses three classifications:

- **Public and intended for external use**: safe to describe as part of the Ontopoiesis tool
  itself
- **Internal but stable enough to build on inside the repo**: important boundary, but
  not yet a promised external product surface
- **Internal and likely to be reorganized**: useful implementation unit today, but not
  something the docs should present as a long-term external surface

## Current public surface

These are the surfaces Ontopoiesis should currently present to outside reviewers:

- `src/ontopoiesis/`
  The operator CLI package is the clearest current external Ontopoiesis surface.
- `docs/`
  The Ontopoiesis docs are part of the public presentation layer.
- `docs/*.owlxml`, `docs/tests/*.cypher`
  Bundled sample ontologies and walkthrough fixtures are public support material for
  the operator experience.

This is the level Ontopoiesis should optimize first when trying to impress
ontology-focused reviewers.

## Internal but stable enough to build on

These submodules have meaningful architectural boundaries and should be treated as
stable internal layers, but they are not yet committed external distribution surfaces:

- `ontopoiesis.render`
  Render-oriented construct-graph formatting layer.
- `ontopoiesis.lint`
  Built-in Cypher lint rule packaging and selection layer.
- `ontopoiesis.migrations`
  Projection migration workflow and migration-template support.
- `ontopoiesis.cypher_test`
  Pytest integration for projection-backed `.cypher` assertions.

These are important architectural units. They deserve coherent boundaries and clean
internal APIs, but Ontopoiesis does not yet need to market them as independently consumable
packages.

## Internal and likely to be reorganized

These units are currently useful but should not be treated as durable external surface
area:

- `ontopoiesis.lint`
  Valuable as the current Cypher test/lint runtime, but still tightly coupled to the
  Ontopoiesis workflow story and a candidate for folding into a different layout later.
- `ontopoiesis.commands`
  A useful command layout today, but still an internal workflow-organizing slice rather
  than a separately marketable package.

## What this means for documentation

Current documentation effort should prioritize:

- the operator CLI
- the projection-centered developer workflow
- querying, linting, tests, diffing, impact analysis, authoring workflows, and rendering

Documentation should de-emphasize:

- package-by-package marketing
- treating every internal package as a separately sellable product
- implying that the current package boundaries are the final public install story

## What this means for restructuring

The current package layout is allowed to change.

In particular:

- Ontopoiesis does not yet commit to keeping every current package as a separately published
  or externally documented unit
- package names may collapse into a more consolidated module layout later
- external usefulness, licensing, and distribution strategy should drive that decision,
  not inertia from the current monorepo shape

Until then, Ontopoiesis should treat the CLI and documentation as the main public surface
and treat the package layer primarily as an internal architecture boundary.
