---
title: "Migrations"
---

The Ontopoiesis migration workflow treats an ontology as the _product_ of a sequence of
versioned, idempotent Cypher scripts rather than a serialized file to be edited in
place. Scripts are applied in order against a projection database — the same way
Alembic or Flyway manage database schema.

## The migration model

Each migration is a numbered `.cypher` file in a `migrations/` directory.
The runner applies them in lexicographic order and records each successful script in
the projection database. The runner skips scripts whose ids have already been applied,
so re-running against the same projection is safe. Each file runs as a single transaction: if any
statement fails, none of that migration's writes are committed and the runner exits
with a non-zero status. Fix the failing statement and re-run — already-applied
scripts are skipped, so only the failed migration is retried.

```
migrations/
  V0001__init_ontology.cypher
  V0002__class_hierarchy.cypher
  V0003__properties.cypher
  V0004__individuals.cypher
```

Each file is a `.cypher` script with an optional leading comment block and one or
more Cypher statements separated by semicolons. Migration identity comes from the
filename, so comments are just comments. The runner renders each file through the
Jinja environment before execution, so you can use template helpers and shared macros
directly inside migration scripts.

Relationships carry a `role` property naming the structural field
(e.g. `sub`, `super`, `individual`, `axiom`) and a `position` giving the child's
zero-based order under its parent. All constructs live in the single node table `N` and
all semantic references in the single relationship table `E`.

## Worked example: Margherita pizza

The four scripts below build the same ontology represented in `pizza.owlxml`,
arriving at it incrementally.

### V0001 — Declare the ontology

```cypher
--8<-- "docs/ontopoiesis/migrations/V0001__init_ontology.cypher"
```

### V0002 — Class hierarchy

> **Why `MERGE`, not `CREATE`:** Migration scripts are meant to be replay-safe. `MERGE`
> is idempotent: if you re-run the same migration, it matches the existing construct
> instead of creating a duplicate. Bare `CREATE` always inserts a fresh node or edge,
> which is why re-running a migration that uses `CREATE` can silently duplicate
> ontology structure.

```cypher
--8<-- "docs/ontopoiesis/migrations/V0002__class_hierarchy.cypher"
```

### V0003 — Object property

```cypher
--8<-- "docs/ontopoiesis/migrations/V0003__properties.cypher"
```

### V0004 — Individuals and assertions

```cypher
--8<-- "docs/ontopoiesis/migrations/V0004__individuals.cypher"
```

### Running the migrations

```bash
ontopoiesis migrate migrations/
```

By default this writes `migrations.lbug` next to the migration directory. Pass
`--output` to choose a different projection path:

```bash
ontopoiesis migrate migrations/ --output pizza.lbug
```

The runner reports each script it applies in order and prints a node/edge summary on
completion:

```
Applied V0001
Applied V0002
Applied V0003
Applied V0004
╭─ Migrate Complete ─╮
│ nodes  33          │
│ edges  55          │
╰────────────────────╯
```

Re-running the directory against the same projection is safe — the runner reads
applied migration ids from the projection and skips scripts it has already recorded.
Within one migration directory, every migration id must be unique. If two filenames
share the same id prefix, the runner rejects the directory before applying any scripts.
Pass `--force` to discard an existing output projection and rebuild it from scratch.

### Exporting the result

If you need an OWL document after running the migrations, export the `.lbug`
projection in a second step:

```bash
ontopoiesis migrate migrations/ --output pizza.lbug
ontopoiesis export pizza.lbug --output pizza_rebuilt.owlxml
```

This example makes the document root explicit by creating the `Ontology` node and its
`Prefix` constructs in `V0001`.

For the content-addressing model that makes migration `MERGE` operations idempotent,
see [The Projection Graph Model](cypher-model.md#the-uid).

## Extending the ontology

The normal workflow is incremental: keep the existing projection, add one new numbered
migration file, and re-run the directory. The runner records applied migration ids in
the projection and skips them on the next run, so only the new script is applied.

Add `V0005__pizza_toppings.cypher`:

```cypher
{%- set topping_uid = scalar_uid("Class", "https://example.org/PizzaTopping") -%}
{%- set pizza_uid = scalar_uid("Class", "https://example.org/Pizza") -%}
{%- set ax_uid = axiom_uid("SubClassOf", [
    ("sub", topping_uid),
    ("super", pizza_uid)
]) -%}

MERGE (topping:N {uid: "<< topping_uid >>"})
  SET topping.kind = "Class", topping.iri = "https://example.org/PizzaTopping";
MERGE (pizza:N {uid: "<< pizza_uid >>"})
  SET pizza.kind = "Class", pizza.iri = "https://example.org/Pizza";
MERGE (ax:N {uid: "<< ax_uid >>"})
  SET ax.kind = "SubClassOf";
MERGE (ax)-[:E {role: "sub"}]->(topping);
MERGE (ax)-[:E {role: "super"}]->(pizza);
```

Then re-run the directory against the existing projection:

```bash
ontopoiesis migrate migrations/ --output pizza.lbug
```

This applies `V0005` and leaves `V0001` through `V0004` untouched. Express corrections
as new forward migrations rather than by editing old files that may already have been
recorded in existing projections.

## Cypher template helpers

The migration runner processes `.cypher` files through a Jinja2 environment before
execution. Use template helpers to keep migration UIDs deterministic and to share
repeated OWL graph patterns across files.

### Template globals

The environment exposes two UID helpers as globals. Using them in templates makes
migrations replay-safe: the same inputs always produce the same UID, so `MERGE`
statements are idempotent across runs. The helpers use the existing migration UID
namespaces and a 128-bit SHA-256 digest prefix; scalar constructs and axiom-shaped
constructs intentionally live in separate namespaces.

| Function                 | Parameters                                                                 | Purpose                                     |
| ------------------------ | -------------------------------------------------------------------------- | ------------------------------------------- |
| `scalar_uid(kind, iri)`  | `kind`: OWL 2 construct kind string; `iri`: expanded IRI string            | Deterministic UID for a named entity        |
| `axiom_uid(kind, edges)` | `kind`: construct kind; `edges`: ordered list of `(role, child_uid)` pairs | Deterministic UID for an axiom by structure |

Both functions return a `0x`-prefixed UID with 32 lowercase hex digest characters.
The UID is stable for migration-authored constructs across re-runs and across machines.
To verify a UID matches an existing projection node, query with:

```cypher
MATCH (n:N {uid: "<< scalar_uid("Class", "http://example.org/Person") >>"}) RETURN n
```

**`scalar_uid`** computes the UID for a named entity from its kind and expanded IRI:

```cypher
{%- set person_uid = scalar_uid("Class", "http://example.org/Person") -%}
MERGE (n:N {uid: "<< person_uid >>"})
  SET n.kind = "Class", n.iri = "http://example.org/Person";
```

**`axiom_uid`** computes the UID for an axiom or anonymous expression from its kind and
the ordered list of `(role, child_uid)` pairs that describe its structure:

```cypher
{%- set person_uid = scalar_uid("Class", "http://example.org/Person") -%}
{%- set animal_uid = scalar_uid("Class", "http://example.org/Animal") -%}
{%- set ax_uid = axiom_uid("SubClassOf", [
    ("sub", person_uid),
    ("super", animal_uid)
]) -%}
MERGE (ax:N {uid: "<< ax_uid >>"}) SET ax.kind = "SubClassOf";
MERGE (p:N {uid: "<< person_uid >>"}) SET p.kind = "Class", p.iri = "http://example.org/Person";
MERGE (a:N {uid: "<< animal_uid >>"}) SET a.kind = "Class", a.iri = "http://example.org/Animal";
MERGE (ax)-[:E {role: "sub"}]->(p);
MERGE (ax)-[:E {role: "super"}]->(a);
```

The role names in `axiom_uid` must match the `role` values used on projection edges
(`sub`, `super`, `operand`, …). See the
[constructs reference](constructs.md#structural-edge-roles) for the full list.

### Constraints

**`iri` must be a fully expanded IRI string.** Do not pass a prefixed form such as
`foaf:Person`. A prefixed IRI produces a different UID than the one `ontopoiesis build`
assigned, so `MERGE` creates a duplicate node instead of targeting the existing one.

**Role names in `axiom_uid` must be in the correct order.** The UID derives from the
sequence of `(role, child_uid)` pairs in `edges`, so the order matters.

**`kind` must exactly match the projection kind string.** The kind strings are the OWL 2
structural specification construct names: `SubClassOf`, `ObjectProperty`, `Class`, and
so on.

### Macros

Jinja2 macros let repeated Cypher patterns be defined once and called by name.

#### Example — `subclass_axioms.cypher`

This template defines a `subclass` macro that generates an idempotent `SubClassOf`
axiom from two IRIs:

```cypher
--8<-- "docs/ontopoiesis/templates/subclass_axioms.cypher"
```

### Sharing macros across migrations

A simple project layout is:

```text
migrations/
  owl.cypher
  V0001__init.cypher
  V0002__classes.cypher
```

`owl.cypher` defines shared macros such as `subclass`. Individual migrations then
import them:

```cypher
{%- from 'owl.cypher' import subclass -%}
<< subclass("ex:Animal", "owl:Thing") >>;
<< subclass("ex:Person", "ex:Animal") >>;
```

The Jinja environment resolves imports relative to the migrations directory, so a
shared macro library can live beside the numbered migration files.

### Expression delimiters

Block tags use `{%  %}` and expressions use `<<  >>` — both are invalid in Cypher, so
no escaping is needed in query files.

## Troubleshooting

**A migration fails partway through.** Each migration file runs as a single transaction.
If any statement in the file fails, none of the file's writes are committed. The runner
exits non-zero and prints the failing statement. Fix the statement in the migration file
and re-run the directory — already-applied scripts are skipped by migration id, so only
the failed migration is retried.

**The projection has unexpected nodes after re-running.** All migration statements
should use `MERGE` rather than `CREATE` so that re-applying a script produces the same
graph state. If a script uses bare `CREATE`, re-running it will add duplicate nodes.
Replace `CREATE` with `MERGE` and add `ON MATCH SET` clauses if you need to update
properties on existing nodes.

**`MERGE` is not matching the expected node.** The `uid` used in a `MERGE` key must
be stable for the construct you intend to update. Use the `scalar_uid(kind, iri)` and
`axiom_uid(kind, edges)` template functions to compute deterministic migration UIDs
rather than hardcoding hash-like values. See [Cypher template helpers](#cypher-template-helpers)
for the UID helper reference and namespace contract.

**The runner reports a duplicate migration id.** Migration identity comes from the
filename prefix before `__`, so `V0002__classes.cypher` and
`V0002__properties.cypher` are the same migration id. Rename one file to the next
unused id before running the directory again.

## Where To Go Next

With a migration-built projection in hand, the rest of the Ontopoiesis workflow applies
without modification:

- **[Queries](queries.md)** — interrogate the projection with Cypher to verify the
  ontology structure is what you intended
- **[Tests](tests.md)** — write structural assertions as `.cypher` files and run them
  as CI gates
- **[Lint](lint.md)** — run the built-in baseline against the migration output to
  catch structural contradictions and redundancies
- **[Diff](diff.md)** — compare projections built from different migration checkpoints
  to see exactly which axioms changed between versions
- **[Rendering](rendering.md)** — produce SVG diagrams of construct neighborhoods for
  documentation or review
