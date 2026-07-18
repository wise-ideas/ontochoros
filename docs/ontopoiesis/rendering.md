---
title: "Rendering"
---

`ontopoiesis render` produces a visual graph from a built `.lbug` projection — SVG, PNG, or
DOT. Use it to inspect construct neighborhoods visually, generate documentation diagrams,
or explain ontology structure in a review or chat context.

Build a projection first with `ontopoiesis build`, then render from it as many times as needed
without re-parsing the source document.

## Output Formats

The format is inferred from the `--output` file extension when `--format` is omitted.

| Format | Extension | External dependency      | Notes                                                                |
| ------ | --------- | ------------------------ | -------------------------------------------------------------------- |
| SVG    | `.svg`    | None                     | Most portable; embeds in documentation, browsers, and chat clients   |
| PNG    | `.png`    | Graphviz `dot` on `PATH` | Raster image; good for screenshots and presentation slides           |
| DOT    | `.dot`    | None                     | Raw Graphviz source; useful for custom layouts or downstream tooling |

SVG is the recommended default. It renders without an external Graphviz dependency and
displays inline in most documentation platforms and chat clients.

## Render The Full Graph

With no entity IRIs, the entire projection is rendered:

```bash
uv run ontopoiesis build docs/ontopoiesis/family.owlxml -o /tmp/family.lbug
uv run ontopoiesis render /tmp/family.lbug -o /tmp/family.svg
```

The resulting SVG contains one node per construct in the projection — classes,
properties, axioms, class expressions — connected by labeled edges named after their
structural role (e.g., `sub`, `super`, `property`, `filler`). On the
bundled family ontology, the graph is small enough to be readable. On larger ontologies,
the full-graph render is too dense to be useful; entity-focused rendering is more
practical.

## Render A Focused Construct Neighborhood

Pass one or more entity IRIs to restrict the graph to those constructs and their
immediate structural references:

```bash
uv run ontopoiesis render /tmp/family.lbug http://example.org/Person -o /tmp/person.svg
uv run ontopoiesis render /tmp/family.lbug http://example.org/Person http://example.org/hasChild \
  -o /tmp/family_fragment.svg
```

The output includes the named entities and every construct they directly participate in —
their axioms, class expressions, and structural references.

## Include External References

By default, the render stops at the focal entities: it shows the constructs they
participate in, but nothing beyond the focal set. Pass `--include-external` to extend the graph one hop further, pulling in constructs
referenced by the focal neighborhood — for example, filler classes in existential
restrictions that sit one step outside the focal entity:

```bash
uv run ontopoiesis render /tmp/family.lbug http://example.org/Parent \
  --include-external -o /tmp/parent_full.svg
```

## Reading The Output

Each node in the graph represents one OWL 2 construct.

- **Selected nodes** use the strongest visual emphasis: the entity IRIs you passed to
  `ontopoiesis render`
- **Contextual nodes** show the axioms, class expressions, and structural references the
  selected entities participate in
- **External nodes** appear only with `--include-external`: constructs referenced just
  outside the focal neighborhood

Edge labels are the structural role names, such as `sub`, `super`, and `property`. These
match the `role` values used in Cypher queries; see the
[constructs reference](constructs.md#structural-edge-roles) for the full list.

## PNG Output

PNG output requires Graphviz `dot` on `PATH`. SVG and DOT do not. If Graphviz is not
installed and you need a raster image, render to SVG and convert with a browser or
image tool:

```bash
uv run ontopoiesis render /tmp/family.lbug -o /tmp/family.png  # requires dot on PATH
uv run ontopoiesis render /tmp/family.lbug -o /tmp/family.dot  # no external dependency
```

## Using SVG In Documentation And Chat

SVG output can be:

- embedded directly in HTML documentation
- opened in any modern browser
- displayed inline in chat clients and review tools that render image attachments
- included in Markdown documentation on platforms that preserve SVG attachments

## Troubleshooting

**PNG output fails with an error about `dot`.** PNG rendering requires Graphviz `dot` on
`PATH`. SVG and DOT output do not. Install Graphviz from your system package manager
(`apt install graphviz`, `brew install graphviz`) or render to SVG and convert with a
browser or image tool.

**The rendered SVG is blank or nearly empty.** The projection was built from a document
with no axioms, or the entity IRI passed to a focused render does not appear in the
projection. Confirm the projection is non-empty with:

```bash
ontopoiesis query graph.lbug -q "MATCH (n:N) RETURN count(*) AS nodes"
```

For a focused render, confirm the entity IRI matches exactly:

```bash
ontopoiesis query graph.lbug -q "MATCH (n:N) WHERE n.iri = '<your-iri>' RETURN n.kind"
```

**The SVG is too large to open or display.** Full-graph renders on large projections
produce very large SVG files. Use entity-focused rendering with one or more specific
IRIs instead of rendering the whole projection.

## Related

- [`ontopoiesis build`](cli.md#build) — build the projection to render from
- [Constructs reference](constructs.md) — the OWL 2 construct kinds that appear as nodes
- [Queries](queries.md) — inspect the same projection with Cypher
