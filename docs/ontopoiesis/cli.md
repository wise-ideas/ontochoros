---
title: "Ontopoiesis CLI"
---

The `ontopoiesis` CLI is the local operator surface for ontology development and CI
workflows. It is not exposed to MCP clients.

The CLI is organized around one shared developer artifact: the Ladybug projection. In a
typical workflow you build a projection from an OWL/XML document, then choose the operations
that fit the task: query it, test it, lint it, diff it, analyze impact, edit it through
migrations, or serialize it back to an OWL document.

## Global options

| Option                 | Argument | Default | Description                                           |
| ---------------------- | -------- | ------- | ----------------------------------------------------- |
| `--log-level`          | `LEVEL`  | `INFO`  | Logging level: `DEBUG`, `INFO`, `WARNING`, or `ERROR` |
| `--install-completion` | none     | off     | Install shell completion for the current shell        |
| `--show-completion`    | none     | off     | Print the shell completion script                     |
| `--help`               | none     | off     | Show command help                                     |

## Graph operations

These commands work with the Ladybug graph projection — the primary queryable artifact.
The `.lbug` format is not an OWL serialization; it is a graph database built from an
OWL document with `ontopoiesis build` and then reused across multiple developer workflows.

### `build`

Build a Ladybug graph projection from an OWL document.

```bash
ontopoiesis build ontology.owlxml -o graph.lbug
```

`owl:imports` declarations in the source document are recorded as `Import` nodes in the
projection. The projection contains only the axioms stated in the source document
itself; use `resolve` before `build` when queries or checks require the full import
closure. See [The Projection Graph Model](cypher-model.md#import-handling) for details.

| Option           | Argument | Default                          | Description                        |
| ---------------- | -------- | -------------------------------- | ---------------------------------- |
| `--output`, `-o` | `PATH`   | `input_path` with `.lbug` suffix | Output projection path             |
| `--force`        | none     | off                              | Overwrite an existing `.lbug` file |

### `convert`

Convert an ontology document to OWL/XML via [ROBOT](https://robot.obolibrary.org/).
The input format is inferred from the file extension (`.ttl`, `.owl`, `.ofn`,
`.omn`, `.obo`, …).

```bash
export ROBOT_JAR=/path/to/robot.jar   # or a .env entry
ontopoiesis convert ontology.ttl && ontopoiesis build ontology.owx
```

This is the opt-in bridge for non-OWL/XML sources. It shells out to a
user-provided ROBOT jar and therefore requires a Java 17+ runtime; nothing is
bundled, and the rest of the toolchain stays pure Python. ROBOT's own errors
are reported verbatim — conversion can fail for RDF that is not valid OWL 2.

| Option           | Argument | Default                         | Description                  |
| ---------------- | -------- | ------------------------------- | ---------------------------- |
| `--output`, `-o` | `PATH`   | `input_path` with `.owx` suffix | Output OWL/XML path          |
| `--force`        | none     | off                             | Overwrite an existing output |

### `resolve`

Resolve an ontology's transitive import closure and merge it into one OWL/XML
document via [ROBOT](https://robot.obolibrary.org/merge.html). Build the
resulting document when lint, querying, rendering, or impact analysis must see
constructs supplied by imported ontologies.

```bash
export ROBOT_JAR=/path/to/robot.jar
ontopoiesis resolve ontology.owl -o ontology.closure.owx
ontopoiesis build ontology.closure.owx -o ontology.lbug
```

Import IRIs can move, disappear, or resolve differently over time. For
repeatable local and CI builds, map them to pinned local documents with an XML
catalog:

```bash
ontopoiesis resolve ontology.owl \
  --catalog catalog-v001.xml \
  -o ontology.closure.owx
```

The resolved document contains the axioms from the import closure and no longer
contains the collapsed `owl:imports` declarations. ROBOT reports retrieval,
catalog, parsing, and unresolved-import failures verbatim. Like `convert` and
`reason`, `resolve` is an opt-in JVM workflow over a user-provided ROBOT jar;
neither the jar nor a JVM is a runtime dependency of the rest of Ontopoiesis.

This distinction is observable in the bundled Dublin Core example. Linting its
source-document projection with `D101` reports five Dublin Core Terms annotation
properties whose declarations are absent locally. Resolving its two imports before
building supplies all five declarations, and `D101` passes. That is why Dublin Core
is an import-resolution example rather than a case-study violation.

| Option           | Argument | Default                                 | Description                         |
| ---------------- | -------- | --------------------------------------- | ----------------------------------- |
| `--output`, `-o` | `PATH`   | `input_path` with `.closure.owx` suffix | Resolved OWL/XML output path        |
| `--catalog`      | `PATH`   | none                                    | XML catalog for import IRI mappings |
| `--force`        | none     | off                                     | Overwrite an existing output        |

### `reason`

Materialize inferred axioms into a new OWL/XML document via ROBOT
(`robot reason`). Reasoning always stays outside the graph: the output is an
ordinary document containing the original axioms plus the reasoner's
inferences, each annotated `is_inferred true` by default. Build it like any
other document — entailed subsumptions are then one-hop derived edges like any
told axiom.

```bash
export ROBOT_JAR=/path/to/robot.jar
ontopoiesis reason ontology.owx --include-indirect
ontopoiesis build ontology.reasoned.owx
```

By default only direct, non-redundant inferences are asserted (ROBOT's
behaviour); `--include-indirect` asserts the full inferred hierarchy so *every*
entailed subsumption is a single edge. Requires `ROBOT_JAR` and a JVM, like
`convert`.

| Option               | Argument | Default                                  | Description                                        |
| -------------------- | -------- | ---------------------------------------- | -------------------------------------------------- |
| `--output`, `-o`     | `PATH`   | `input_path` with `.reasoned.owx` suffix | Output OWL/XML path                                |
| `--reasoner`         | `NAME`   | `ELK`                                    | `ELK`, `HermiT`, `whelk`, `JFact`, or `EMR`        |
| `--annotate`         | none     | on                                       | Annotate inferred axioms with `is_inferred true` (`--no-annotate` to disable) |
| `--include-indirect` | none     | off                                      | Also assert indirect inferred axioms               |
| `--force`            | none     | off                                      | Overwrite an existing output                       |

### `export`

Serialize a Ladybug graph projection back to an OWL/XML document. The inverse of `build`.

```bash
ontopoiesis export graph.lbug -o ontology.owlxml
ontopoiesis export graph.lbug
```

| Option           | Argument | Default                        | Description         |
| ---------------- | -------- | ------------------------------ | ------------------- |
| `--output`, `-o` | `PATH`   | input path with `.owx` suffix | Output OWL/XML path |

### `query`

Run a Cypher query against a `.lbug` projection and print the results as a table. See
the [Queries reference](queries.md) for starter patterns.

```bash
ontopoiesis query graph.lbug -q "MATCH (n:N) RETURN DISTINCT n.kind AS kind ORDER BY kind"
```

| Option          | Argument | Default  | Description         |
| --------------- | -------- | -------- | ------------------- |
| `--query`, `-q` | `TEXT`   | required | Cypher query string |

### `impact`

Trace semantic references to or from one named entity in a built projection.

```bash
ontopoiesis impact upstream graph.lbug --iri http://example.org/hasChild
ontopoiesis impact downstream graph.lbug --uid 0x42
```

`impact` has two subcommands: `upstream` and `downstream`.

| Option  | Argument | Default | Description           |
| ------- | -------- | ------- | --------------------- |
| `--iri` | `TEXT`   | none    | Seed entity by IRI    |
| `--uid` | `TEXT`   | none    | Seed construct by UID |

Pass exactly one of `--iri` or `--uid`.

### `diff`

Compute a semantic diff between two `.lbug` projections.

```bash
ontopoiesis diff before.lbug after.lbug
ontopoiesis diff before.lbug after.lbug --format json --output diff.json
```

| Option           | Argument | Default | Description                      |
| ---------------- | -------- | ------- | -------------------------------- |
| `--output`, `-o` | `PATH`   | stdout  | Write the diff report to a file  |
| `--format`       | `TEXT`   | `table` | Output format: `table` or `json` |

### `migrate`

Apply a directory of Cypher migration scripts in order and write or update a `.lbug`
projection. See [Migrations](migrations.md) for the script format.

```bash
ontopoiesis migrate migrations/
ontopoiesis migrate migrations/ --output result.lbug --force
```

| Option           | Argument | Default                                 | Description                                |
| ---------------- | -------- | --------------------------------------- | ------------------------------------------ |
| `--output`, `-o` | `PATH`   | `migrations.lbug` next to the directory | Output projection path                     |
| `--force`        | none     | off                                     | Rebuild the output projection from scratch |

### `test`

Run Cypher structural assertions against a `.lbug` projection file. See
[Tests](tests.md) for the test file format.

```bash
ontopoiesis test graph.lbug tests/
ontopoiesis test graph.lbug tests/check_labels.cypher -v
```

`ontopoiesis test` accepts extra pytest flags after the command because it forwards unknown
options to pytest. That is how `-v`, `-vv`, and `-x` work.

| Option            | Argument | Default | Description                                        |
| ----------------- | -------- | ------- | -------------------------------------------------- |
| extra pytest args | varies   | none    | Forwarded to pytest, for example `-v`, `-vv`, `-x` |

If no explicit test path is given, the command looks in `tests/`.

### `lint`

Run the bundled structural lint rules against a `.lbug` projection file. See
[Lint](lint.md) for rule groups and selection options.

```bash
ontopoiesis lint graph.lbug
ontopoiesis lint graph.lbug --profile editorial
```

| Option            | Argument | Default | Description                                               |
| ----------------- | -------- | ------- | --------------------------------------------------------- |
| `--profile`       | `TEXT`   | none    | Include a bundled supplemental profile                    |
| `--select`        | `TEXT`   | `E,W`   | Replace the default selection with rule codes or prefixes |
| `--extend-select` | `TEXT`   | none    | Add rule codes or prefixes to the default selection       |
| `--ignore`        | `TEXT`   | none    | Remove rule codes or prefixes from the final selection    |

### `render`

Render a construct graph from a `.lbug` projection to SVG, PNG, or DOT. See
[Rendering](rendering.md) for format and interpretation guidance.

```bash
ontopoiesis render graph.lbug -o graph.svg
ontopoiesis render graph.lbug http://example.org/Person -o person.svg
ontopoiesis render graph.lbug http://example.org/Person --include-external -o person.png
```

| Option               | Argument | Default                        | Description                                                                                                    |
| -------------------- | -------- | ------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| `--output`, `-o`     | `PATH`   | required                       | Output file path                                                                                               |
| `--format`, `-f`     | `TEXT`   | inferred from output extension | Output format: `svg`, `png`, or `dot`                                                                          |
| `--include-external` | none     | off                            | Extend the graph one hop beyond the focal entities, pulling in constructs referenced by the focal neighborhood |

With no IRIs, the entire projection is rendered. With one or more entity IRIs, the
graph is restricted to those constructs and their immediate references.

## Exit codes

- `0` — command completed successfully
- `1` — command-level failure such as `lint` finding error-level violations,
  `ontopoiesis diff` finding differences, or pytest reporting test failures
- `2` — usage or collection failure, for example `ontopoiesis test` finding no matching
  test files
- other non-zero codes — command execution failure such as parse errors, unresolved
  imports, invalid Cypher, missing files, or failed output writes

Command-specific notes:

- `lint`: `0` for clean or warning-only runs, `1` if any error-level rule fails
- `test`: pytest exit codes; warning-only files do not make the run fail
- `diff`: exits `1` when differences are found and `0` when the projections are identical
For the build-once-reuse CI pattern across `build`, `lint`, `test`, and `diff`, see
[CI](ci.md).
