---
title: "Lint"
---

`ontopoiesis lint` runs the built-in OWL 2 baseline against a built `.lbug` projection.
Build the projection first with `ontopoiesis build`, then run lint against it as many times
as needed without rebuilding.

The default baseline is intentionally conservative: it focuses on direct contradictions,
impossible assertions, and low-noise structural redundancy that are useful across almost
any ontology. Use it when you want a broadly applicable structural check. Add the
supplemental profiles when you want stricter OWL 2 DL, editorial, or modeling-risk
feedback.

Lint rules are plain `.cypher` files using the same test runner as `ontopoiesis test`. The
selection layer maps rule codes and profiles to the underlying query files.

```bash
ontopoiesis lint family.lbug
ontopoiesis lint family.lbug --select E                   # all core errors
ontopoiesis lint family.lbug --extend-select M            # add modeling-risk rules
ontopoiesis lint family.lbug --select E101,W101
ontopoiesis lint family.lbug --ignore W101
ontopoiesis lint family.lbug --profile editorial
ontopoiesis lint family.lbug --profile modeling_risk --profile description_logic
```

## Rule Selection

The interface is intentionally Ruff-like:

- `--select`: replace the default selection with explicit codes or prefixes
- `--extend-select`: add codes or prefixes to the default selection
- `--ignore`: subtract codes or prefixes from the final selection
- `--profile`: convenience alias that extends selection with a bundled group

Selectors are comma-delimited and may be repeated. Selectors may be prefixes: `E` means all core error rules and `P10` means all
publication rules whose codes start with `P10`.

Running `ontopoiesis lint` with no selection flags runs the default baseline, which selects
`E,W`. The full code namespace:

- `E...`: universal contradiction checks (default)
- `W...`: low-noise universal warnings (default)
- `P...`: publication/editorial guidance (opt-in)
- `M...`: modeling-risk guidance (opt-in)
- `D...`: OWL 2 DL strictness checks (opt-in)

Bundled profiles map directly to those optional prefixes:

- `editorial` -> `P`
- `modeling_risk` -> `M`
- `description_logic` -> `D`

Examples:

```bash
ontopoiesis lint go.lbug --select E,W
ontopoiesis lint go.lbug --extend-select M
ontopoiesis lint go.lbug --select E,P101,P107
ontopoiesis lint go.lbug --extend-select M,D --ignore M103
ontopoiesis lint go.lbug --profile editorial --ignore P101
```

## Verbosity and output

`ontopoiesis lint` prints a compact summary of failing and warning rules, plus the
violation rows those rules returned. The current CLI surface does not expose separate
verbosity or fail-fast flags; the selector and profile options above are the supported
way to control what the command runs.

If the projection contains `Import` nodes, lint prints one warning that its import
closure is unresolved. This warning does not change rule severities or the exit code:
the rules still report exactly what is present in the projection, but
closure-sensitive findings may be false positives. Resolve the source document and
build the resulting closure before treating those findings as ontology-wide defects:

```bash
ontopoiesis resolve ontology.owl --catalog catalog-v001.xml
ontopoiesis build ontology.closure.owx
ontopoiesis lint ontology.closure.lbug --profile description_logic
```

## Output

### Passing run

A clean baseline run exits zero and prints a summary:

```
No lint violations found.
╭─ Lint Complete ─╮
│    rules  20    │
│ failures  0     │
│ warnings  0     │
╰─────────────────╯
```

### Warning output

Warnings are printed as rule-by-rule notices with their returned rows, followed by the
same summary block. Warning-only runs still exit zero.

### Failure output

Error-level rules (`E...`) that return violation rows are printed as `FAIL` notices with
their returned rows, and the command exits non-zero.

The columns in each violation row are the values returned by that rule's Cypher query.
They vary by rule rather than following one fixed schema. See
[lint-rules.md](lint-rules.md) for the meaning of the columns each rule returns.

The exit code is non-zero, making lint suitable as a CI gate without additional scripting.

## CI Integration

`ontopoiesis lint` exits non-zero on any error-level failure and zero on a clean run
(warnings do not affect the exit code). This makes it a drop-in CI gate without
additional scripting.

A minimal GitHub Actions step:

```yaml
- name: Build projection
  run: uv run ontopoiesis build ontology.owlxml -o ontology.lbug

- name: Lint
  run: uv run ontopoiesis lint ontology.lbug
```

To run supplemental profiles as a separate non-blocking check:

```yaml
- name: Lint (baseline, required)
  run: uv run ontopoiesis lint ontology.lbug

- name: Lint (editorial, advisory)
  run: uv run ontopoiesis lint ontology.lbug --profile editorial || true
```

The same pattern applies to `ontopoiesis test` — any CI system that checks exit codes
can use either command as a quality gate. Build the projection once and reuse it
across multiple lint and test steps without rebuilding. For a fuller build-once-reuse
workflow, see [CI](ci.md).

## Troubleshooting

**A rule code is not found.** Unknown selectors passed through `--select`,
`--extend-select`, or `--ignore` are rejected with a CLI error. For example,
`--select ZZ` fails with `Unknown lint selector(s)` and lists the supported rule codes.

**All rules pass but the CI step is red.** Warnings do not make `ontopoiesis lint` exit
non-zero; only error-level failures do. Re-run the baseline explicitly to isolate what
the CI job executed:

```bash
ontopoiesis lint ontology.lbug --select E,W
```

If that passes locally, check whether the CI step enabled extra profiles or selectors.

**A projection-level finding looks wrong.** The projection contains only constructs
stated in the source document. Imported ontology content is not merged during `build`,
so findings about missing labels or undeclared entities can be artifacts of an
incomplete import closure. Lint warns when the projection contains unresolved import
declarations; use `ontopoiesis resolve` on the source document before `build` to check
the full closure. See [The Projection Graph Model](cypher-model.md#import-handling).

**`--profile` has no effect.** Profile names must match exactly:
`editorial`, `modeling_risk`, or `description_logic`. Typos do not silently fall back;
they fail with `Unknown lint profile(s)`. If you want to verify the active rule family
explicitly, use selectors directly, for example:

```bash
ontopoiesis lint ontology.lbug --select E,W,P
```

## Rule Reference

The full catalogue of baseline rules and supplemental profiles now lives in the
[lint rule reference](lint-rules.md). Use that page when you need the complete E/W/P/M/D
inventory, rule descriptions, or the underlying `.cypher` source.
