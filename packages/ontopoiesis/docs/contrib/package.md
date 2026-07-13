---
title: "Package Architecture"
---

This page covers `ontopoiesis` only.

`ontopoiesis` is the operator CLI and local workflow layer that sits on top of
`ontoplexus`. It should explain its own modules clearly, then stop at the
boundary of the reusable core package. If you need the internal architecture of
`ontoplexus`, read the companion package notes in that repository.

## The boundary

`ontopoiesis` owns operator workflows:

- CLI command entry points
- render-oriented graph presentation
- Cypher lint rule packaging and selection
- migration workflow and UID helpers
- pytest integration for `.cypher` graph checks

`ontoplexus` owns the reusable substrate underneath those workflows:

- OWL 2 construct models
- projection graph compilation and traversal
- Ladybug-backed projection storage and querying

That seam matters. `ontopoiesis` may orchestrate those capabilities for operators,
but it should not reimplement graph traversal, construct display priority,
fingerprinting, or document conversion logic.

## Ontopoiesis Modules

### `ontopoiesis.app`

The Typer entry point. This module wires subcommands together and owns global
CLI process concerns such as logging setup and dotenv loading.

### `ontopoiesis.commands`

Operator-facing command handlers. These modules may own light workflow
orchestration for a command, but they should stay close to the CLI boundary:
parse options, validate inputs, call `ontoplexus` or `ontopoiesis` workflow
helpers, and format operator output. They should not absorb reusable graph or
model logic.

### `ontopoiesis.render`

Presentation-oriented graph rendering. It accepts projection slices or related
render-ready inputs from `ontoplexus.graph` and produces SVG, PNG, DOT, and
related layout output. Rendering policy belongs here, not in `ontoplexus`.

### `ontopoiesis.lint`

Cypher-based structural lint packaging. This module owns built-in rule
registries, rule selection, and execution against an existing `.lbug`
projection. The rules are an operator workflow concern, so they belong here
rather than in `ontoplexus`.

### `ontopoiesis.cypher_test`

Pytest integration for running `.cypher` assertion files against a projection.
This is the operator-facing test harness layer over the projection query
surface; it is not part of the reusable graph core.

### `ontopoiesis.migrations`

Projection migration workflow and deterministic UID helpers for migration
templates. This module owns template rendering and migration bookkeeping around
the projection store, not the underlying graph storage implementation itself.

## What Does Not Belong Here

- New reusable graph traversal or query primitives
- OWL 2 structural model logic
- Construct display/IRI priority rules
- Construct canonicalization or fingerprinting
- Raw Ladybug schema ownership
- Hosted product concerns

If a new capability would be valuable without the CLI, it probably belongs in
`ontoplexus`, not here.
