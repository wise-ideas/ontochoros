---
title: "Tests"
---

`ontopoiesis test` runs Cypher-based structural assertions against a built `.lbug`
projection. Use it to enforce structural constraints that should hold on every version of
the ontology — labeling coverage, deprecation hygiene, declared domains and ranges. These
checks integrate naturally into CI.

All queries run against the standard projection shape: construct nodes in `N`, semantic
reference edges in `E`, construct kind in `n.kind`.

## File Organization

Test files are collected from a directory you pass to `ontopoiesis test`. Keep project-specific
tests in a `tests/` directory alongside the ontology sources. Build the projection with
`ontopoiesis build` before running tests. The runner accepts either a directory (all matching
`.cypher` files are collected) or a single `.cypher` file.

## Error-level tests

Each error-level assertion lives in a `test_*.cypher` or `*_test.cypher` file. The
runner executes each query against the projection and fails the test if any rows are
returned. Violations are rows; an empty result is a pass. A single error-level failure
causes a non-zero exit code.

For this example, the rule prohibits negative object property assertions in the published
ontology. The example intentionally fails — the sample data contains one negative
`hasDaughter` assertion, from `Bill` to `Susan`.

```cypher
--8<-- "docs/tests/test_negative_property_assertions.cypher"
```

Store the query at `tests/test_negative_property_assertions.cypher`, build the
projection once, and run:

```bash
ontopoiesis build family.owlxml -o family.lbug
ontopoiesis test family.lbug tests/test_negative_property_assertions.cypher
```

Because `family.owlxml` contains one negative `hasDaughter` assertion, the test returns
a violation and exits non-zero:

```
=========================== short test summary info ============================
FAILED tests/test_negative_property_assertions.cypher::test_negative_property_assertions.cypher
============================== 1 failed in 1.00s ===============================
```

If you want this example to pass instead, remove the negative property assertion or
change the query to ignore it. A test that finds no violations prints:

```
============================== 1 passed in 0.XX s ==============================
```

## Warning-level tests

A `warn_*.cypher` or `*_warn.cypher` file works identically to an error-level test
except that violations do not fail the run. Violations appear in a dedicated
terminal summary section; the exit code remains zero. Use warning-level tests
for quality signals you want to track without blocking CI.

For example, self-referential object-property definitions may deserve review without
being outright errors. The Primer sample contains `NarcisticPerson`, defined with an
`ObjectHasSelf` restriction over `loves`:

```cypher
--8<-- "docs/tests/warn_self_referential_definitions.cypher"
```

```bash
ontopoiesis test family.lbug tests/warn_self_referential_definitions.cypher
```

`NarcisticPerson` matches the warning query, so the warning appears in the
Cypher warning summary, but the exit code remains zero:

```
============================= cypher warnings =============================
WARN warn_self_referential_definitions.cypher
query returned 1 violation row(s)
... run with -v to see a sample
```

Pass `-v` to see a sample of the violation rows:

```bash
ontopoiesis test family.lbug tests/ -v
```

## CI Integration

The common CI pattern is:

1. build the projection once
2. run `ontopoiesis lint` as the shared baseline gate
3. run `ontopoiesis test` for project-specific assertions

Example:

```bash
uv run ontopoiesis build ontology.owlxml -o ontology.lbug
uv run ontopoiesis lint ontology.lbug
uv run ontopoiesis test ontology.lbug tests/
```

`ontopoiesis test` forwards extra pytest flags, so `-v`, `-vv`, and `-x` can be passed
through when you want more detail or fail-fast behaviour during local debugging or CI:

```bash
uv run ontopoiesis test ontology.lbug tests/ -v
uv run ontopoiesis test ontology.lbug tests/ -vv
uv run ontopoiesis test ontology.lbug tests/ -x
```

For a full GitHub Actions example and gate/advisory split, see [CI](ci.md).

## Troubleshooting

**No test files collected.** The runner requires files named `test_*.cypher`,
`*_test.cypher`, `warn_*.cypher`, or `*_warn.cypher`. Files with other names are
silently ignored. Confirm the file names match one of these conventions.

**The test fails even though the query returns no rows when run manually.** The runner
and `ontopoiesis query` use the same projection file but different sessions. If the
projection file was modified between the two commands, results may differ. Rebuild the
projection and re-run both commands against the fresh file.

**Warning-level violations appear but the exit code is non-zero.** Warning-level
files (`warn_*.cypher`) never cause a non-zero exit on their own. If the exit
code is non-zero, at least one error-level test file returned violations or
pytest encountered a separate usage/collection failure. Check the short test
summary for `FAILED` entries.

## Related

`ontopoiesis lint` runs the same test runner against the built-in baseline rules rather than
your own `.cypher` files. If you want structural quality checks without writing your own
queries, start there. See the [Lint guide](lint.md) for running lint and the
[lint rule reference](lint-rules.md) for the full catalogue and
selection options.
