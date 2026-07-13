---
title: "Diff"
---

`ontopoiesis diff` computes the semantic difference between two `.lbug` projections and
reports which OWL constructs were added, removed, or modified.

This is not a text diff. It does not compare Turtle files, look for blank-node
reorderings, or flag prefix renames. It compares OWL constructs by semantic fingerprint — structural identity, not
serialization.

## Prerequisites

Build projections from both ontology versions first:

```bash
ontopoiesis build before.owlxml -o before.lbug
ontopoiesis build after.owlxml -o after.lbug
```

Both projections should be built from comparable source documents. `ontopoiesis build` records
`owl:imports` declarations but does not fetch or merge imported ontology content.

## Usage

```bash
ontopoiesis diff before.lbug after.lbug

# Write a diff report
ontopoiesis diff before.lbug after.lbug --output diff.txt
ontopoiesis diff before.lbug after.lbug --format json --output diff.json
```

Example output (diffing the bundled pizza v1 and v2 projections):

```
  status    kind               iri                  count   fingerprint
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  added     Class              https://example.o…   1       12b8fa4cb1…
  added     Declaration                             1       06687a17eb…
  added     Ontology           https://example.o…   1       a41528263…
  removed   Ontology           https://example.o…   1       acd30cd6e…
  added     OntologyDocument                        1       54cc71a614…
  removed   OntologyDocument                        1       f2753147d0…
  added     SubClassOf                              1       bebaa40a77…
```

## Output formats

### Table (default)

Printed to stdout. Columns:

- `status`
- `kind`
- `iri`
- `count`
- `fingerprint`
- `display_label`
- `ontology_uid`
- `ontology_iri`
- `context_iri`

### JSON (`--format json`)

An array of objects. Each object contains:

- `status`: `"added"`, `"removed"`, or `"modified"`
- `kind`: OWL 2 construct kind string such as `"SubClassOf"` or `"Class"`
- `iri`: IRI string for named entities, `null` for anonymous constructs
- `count`: number of constructs with this status/kind/iri combination
- `fingerprint`: semantic fingerprint
- `display_label`: nearest display label when available
- `ontology_uid`: containing ontology UID when available
- `ontology_iri`: containing ontology IRI when available
- `context_iri`: nearest named IRI that provides context for the row

## How the diff identifies constructs

`ontopoiesis diff` identifies constructs by **semantic fingerprint** — a content-addressed
key computed from record structure, not the storage UID. Entity nodes are fingerprinted
by `(kind, expanded_iri)`; axiom and expression nodes are fingerprinted recursively
from their structure, so `SubClassOf(:A :B)` always has the same fingerprint regardless
of which document it came from or which UID was assigned during build.

At the axiom level, "changed" does not exist as a diff concept: if `SubClassOf(:A :B)`
becomes `SubClassOf(:A :C)`, the first fingerprint disappears (removed) and a new one
appears (added). The two statements are genuinely distinct OWL axioms.

For the full content-addressing model, see
[The Projection Graph Model](cypher-model.md#the-uid-and-content-addressing).

### When modified rows appear

`modified` rows are for named constructs whose identity is stable by `(kind, iri)` but
whose semantic fingerprint changes between projections. The most common case is an
annotation attached to the same named entity with a different literal value.

A minimal example:

1. Start with an ontology containing an annotation assertion such as
   `rdfs:label(:Pizza "Pizza")`.
2. Change only the literal value to `rdfs:label(:Pizza "Pizza class")`.
3. Rebuild both versions and diff the projections.

The changed annotation assertion then appears as a `modified` row because it is still an
`AnnotationAssertion` about the same subject, but its fingerprint now reflects a
different literal node:

```text
  status    kind                   iri                         count   fingerprint
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  modified  AnnotationAssertion    https://example.org/Pizza   1       8f3d2d1c4e…
```

This is different from an axiom like `SubClassOf(:A :B)`, where changing either side
produces a removed row plus an added row because the axiom itself has no stable named
identity.

## What is compared

The diff operates on the full node set of each projection, comparing nodes by semantic
fingerprint rather than storage UID:

- **Added**: constructs present only in `after`
- **Removed**: constructs present only in `before`
- **Modified**: same `(kind, iri)` identity but different semantic fingerprint between
  `before` and `after`

Nodes that are present in both projections with the same fingerprint are not reported,
even if the source documents differ in whitespace, element ordering, blank-node names,
or prefix declarations.

## Scope and limitations

The current implementation is intentionally minimal:

- input must be two pre-built `.lbug` projections
- output formats are `table` and `json`
- output rows are aggregated as `added`, `removed`, or `modified`
- construct identity is based on semantic fingerprints, not storage UIDs
- `Ontology` and `OntologyDocument` wrapper constructs appear in the diff when the
  axiom list changes (their fingerprint is derived from the ordered axiom list, so any
  added or removed axiom changes both fingerprints)
- rename detection and migration generation are future work

The diff compares explicitly stated axioms in two built projections. Inferred axioms
(entailments from a reasoner) are included only if an external reasoner has materialized
them in the OWL/XML source before you build the projections.

Import declarations are included in the diff as `Ontology`-level node properties.
Constructs that enter an ontology via `owl:imports` are not included unless the
import closure has already been merged into the source document before build.

## Troubleshooting

**Every row shows as `added`, `removed`, or `modified`.** The two projections were
built from different source states. Confirm you are diffing the intended pair. As a
sanity check, diff a projection against itself — the result should be empty:

```bash
ontopoiesis diff before.lbug before.lbug
```

**`Ontology` and `OntologyDocument` nodes appear in every diff.** This is expected.
Their fingerprints are derived from the full ordered axiom list, so any change to any
axiom changes both fingerprints. They can be ignored when reading semantic diffs.

**A renamed entity appears as a full removal and full addition.** This is correct: a
renamed class is a genuinely different IRI. All axioms that referenced the old IRI
will appear as removed and their equivalents referencing the new IRI as added.
Rename detection is planned but not yet implemented.

## Related

`ontopoiesis impact` traces semantic references within a single projection rather than
comparing two. Use diff to find what changed between versions; use impact to understand
what else in the current projection depends on a given entity. See the [Impact
guide](impact.md) for usage and output format.

For scripted inspection of either projection, see the [Queries reference](queries.md).

For a full description of the semantic fingerprint model used by diff, see
[The Projection Graph Model](cypher-model.md#the-uid-and-content-addressing).
