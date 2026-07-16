---
title: "Quickstart"
---

This walkthrough covers the core Ontopoiesis workflow using only bundled sample ontologies.
If you have not set up Ontopoiesis yet, start with the [installation guide](installation.md).

It focuses on one idea: build a Ladybug projection once, then reuse that graph across
multiple developer tasks without re-parsing the source ontology.

## Prerequisites

This quickstart assumes you are running from the repository root with the development
environment already set up. If you have not done that yet, start with the
[installation guide](installation.md).

You need:

- Python 3.11 or later and `uv`
- the Python workspace dependencies installed

From a fresh checkout:

```bash
make sync
```

## 1. Build A Projection

Start with the bundled family ontology:

```bash
uv run ontopoiesis build docs/family.owlxml -o /tmp/family.lbug
```

On the current sample this produces a small graph projection with 47 nodes and 63 edges.

What this gives you:

- a queryable `.lbug` graph
- one reusable artifact for querying, linting, tests, diffing, and impact analysis
- no need to re-parse the OWL document on each subsequent command

## 2. Interrogate The Graph With Cypher

Start by asking what kinds of OWL constructs are present:

```bash
uv run ontopoiesis query /tmp/family.lbug -q "MATCH (n:N) RETURN DISTINCT n.kind AS kind ORDER BY kind"
```

On the bundled sample, you should see kinds such as:

- `Class`
- `EquivalentClasses`
- `NegativeObjectPropertyAssertion`
- `ObjectSomeValuesFrom`
- `SubClassOf`

Then ask a more structural question:

```bash
uv run ontopoiesis query /tmp/family.lbug -q "
MATCH (ax:N {kind: 'EquivalentClasses'})
      -[:E {role: 'operand'}]->(cls:N {kind: 'Class'}),
      (ax)-[:E {role: 'operand'}]->(restriction:N {kind: 'ObjectSomeValuesFrom'})
      -[:E {role: 'property'}]->(:N {iri: 'http://example.org/hasChild'})
RETURN cls.iri AS class
ORDER BY class"
```

On the sample ontology, this returns `http://example.org/Parent`.

That is the core Ontopoiesis move: build the projection once, then interrogate it repeatedly
without re-parsing the source OWL document.

## 3. Run The Built-In Lint Baseline

Use the same projection as input to the bundled structural lint rules:

```bash
uv run ontopoiesis lint /tmp/family.lbug
```

On the current bundled sample, the baseline passes cleanly:

```
No lint violations found.
╭─ Lint Complete ─╮
│    rules  20    │
│ failures  0     │
│ warnings  0     │
╰─────────────────╯
```

What this shows:

- Ontopoiesis treats the built projection as a shared quality-control surface
- lint rules are just Cypher checks over the same graph you query directly
- teams can keep the default baseline conservative, then extend it with project-specific checks

## 4. Compare Ontology Versions Semantically

Now build two small pizza ontology versions:

```bash
uv run ontopoiesis build docs/pizza.owlxml -o /tmp/pizza_v1.lbug
uv run ontopoiesis build docs/pizza_v2.owlxml -o /tmp/pizza_v2.lbug
```

Then diff the two projections:

```bash
uv run ontopoiesis diff /tmp/pizza_v1.lbug /tmp/pizza_v2.lbug
```

The bundled `pizza_v2.owlxml` adds a new class, `SicilianPizza`, plus the related
declaration and subclass axiom. The diff reports semantic additions — not source-file
formatting differences:

```
  status   kind          iri             count   fingerprint    ontology_iri
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  added    Declaration   https://exam…   1       5ca795dc1e95   https://examp…
  added    SubClassOf    https://exam…   1       1a64b124791c   https://examp…
```

The two rows are the `Declaration` of the new `SicilianPizza` class (the added class
entity is represented by its declaration axiom) and the new `SubClassOf` axiom that
places it under `Pizza`. The diff fingerprints constructs structurally, so unchanged
axioms and the ontology wrapper produce no rows — only genuine additions and removals
appear. If the diff output is empty, the two projections were built from the same source
file.

This is useful because Ontopoiesis is diffing OWL constructs in the projection, not source
file formatting.

## 5. Trace Impact

Use impact analysis against the family projection:

```bash
uv run ontopoiesis impact upstream /tmp/family.lbug --iri http://example.org/hasChild
```

On this tiny sample, the upstream result walks from the constructs that reference
`hasChild` back to the `Ontology` root:

```
  uid   kind                   depth   iri
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  n23   Declaration            1       None
  n40   ObjectSomeValuesFrom   1       None
  n39   EquivalentClasses      2       None
  n0    Ontology               2       None
```

That confirms that `hasChild` appears in ontology content through semantic references,
not ad hoc text search: besides its own `Declaration`, it is used in the
`ObjectSomeValuesFrom` restriction that defines `Parent` (`Parent ≡ ∃ hasChild.Person`),
which the `EquivalentClasses` axiom and the `Ontology` root reach in turn. An entity used
only in its own `Declaration` would appear at depth 1 alone. (`uid` values are assigned in
document order and are not stable across rebuilds.)

On larger ontologies, this same command becomes much more informative, because it helps
answer “what statements mention this entity?”

## Where To Go Next

Once you have a projection, the workflow can branch in several directions:

- keep exploring with [`ontopoiesis query`](queries.md)
- add project-specific structural checks with [`ontopoiesis test`](tests.md)
- use the bundled baseline and optional rule groups with [`ontopoiesis lint`](lint.md)
- compare graph versions with [`ontopoiesis diff`](diff.md)
- trace references with [`ontopoiesis impact`](impact.md)
- serialize back to an OWL document with [`ontopoiesis export`](cli.md)

What matters is not the sequence. What matters is that one graph-native artifact — the
projection — supports all of them.

## Troubleshooting

**Step 2 returns empty results or unexpected kinds.** The projection may have been built
from a different file. Confirm the build command used `docs/family.owlxml` as the
source. To verify the projection directly, run:

```bash
uv run ontopoiesis query /tmp/family.lbug -q "MATCH (n:N) RETURN DISTINCT n.kind AS kind ORDER BY kind"
```

The output should match the kinds listed in step 2.

**Step 3 fails instead of passing.** The projection was not built cleanly. Rebuild it
from scratch: `ontopoiesis build docs/family.owlxml -o /tmp/family.lbug` and re-run
`ontopoiesis lint /tmp/family.lbug`.

**Step 4 shows no rows.** This is expected when the two projections are semantically
identical. If you are expecting substantive differences, confirm the two source files
differ:

```bash
diff docs/pizza.owlxml docs/pizza_v2.owlxml
```
