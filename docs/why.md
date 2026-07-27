---
title: "Why Ontochoros"
---

# Why Ontochoros exists

Software changes go through version control, a reviewable diff, automated
tests, and CI. Nothing ships because one expert eyeballed it and said it
looked fine.

Ontologies rarely get any of that. A curator edits the file in a GUI, a
reviewer scrolls a thousand-line XML diff, and a specialist runs a reasoner
that answers only one kind of question. Structural policy checks and
project-specific modeling constraints are then difficult to review and
repeat consistently.

Ontochoros closes that gap. It treats an ontology the way dbt treats a
warehouse: as typed data behind an engineering workflow — build, query,
lint, test, diff, migrate — with every step scriptable and CI-friendly.

## One idea: the ontology is a database

Everything in the toolchain follows from a single move. `ontopoiesis build`
loads an OWL/XML document into an embedded graph whose shape *is* the OWL 2
structural specification — one node per axiom, expression, or entity; one
ordered edge per parent–child slot. Build the projection once, and every
question about the ontology becomes a Cypher query:

- **Quality gates are queries.** A lint rule or test is a `.cypher` file
  that fails when it returns rows. You extend the rule set the way you write
  dbt tests, and you run it in CI the same way.
- **Diffs are structural.** `ontopoiesis diff` fingerprints every axiom, so
  a pull request shows which constructs changed — not which lines of XML
  moved.
- **Edits are migrations.** Cypher migration scripts, applied in order and
  recorded in the projection, replace hand-editing XML.
- **Nothing is lost.** The graph serializes back to OWL/XML byte-faithfully
  in structure, so the projection is a working surface, not a lossy export.

## Why not SPARQL over the triples?

An ontology is already a graph in RDF, so the obvious alternative is to load
the triples and query with SPARQL. For structural questions, though, the RDF
encoding is the wrong graph: the OWL-to-RDF mapping reifies annotated
axioms, chains every collection through `rdf:first`/`rdf:rest`, and scatters
class expressions across blank nodes. A question about one axiom becomes a
query about encoding artifacts. The projection here has the shape of the
OWL 2 structural specification instead — one node per axiom, expression, or
entity, with ordered edges for their slots — so the query you write names
the construct you mean. [The design](ontoplexis/concepts/design.md) works
through this in detail.

## Why not ROBOT?

For three of its jobs, do use it: reasoning, import resolution, and format
conversion stay with ROBOT, and `ontopoiesis reason`, `ontopoiesis resolve`,
and `ontopoiesis convert` are thin shims over a user-provided ROBOT jar.
What ROBOT does not provide is an open
query surface over ontology structure. `robot report` runs a fixed rule
set that overlaps some Ontopoiesis rules. Additional ROBOT checks can be
written as SPARQL for `robot verify`, which queries the RDF encoding with the
costs described above. Here, lint rules and tests are Cypher files over the
structural graph, and that same graph stays open for follow-up questions a
fixed report cannot anticipate. The toolchain is also pure Python — the JVM
enters only when you opt into the ROBOT shims.

## What the graph checks find

The [case studies](ontopoiesis/case-studies.md) separate four things: stock
lint results, case-specific analysis, the evidence needed to call a result a
defect, and overlap with existing tools.

**SWEET contains dimensionally incorrect quantity modeling.** In its resolved
3.6.0 closure, `AngularMomentum` has the unit `kg.rad/s` and inherits
`Momentum`'s `kg.m/s`; angular momentum should have dimensions `kg.m²/s`.
Elsewhere, a hierarchy cycle makes `RadiantFlux` equivalent to
`RadiativeForcing` and gives radiant flux a `W/m²` default unit instead of
watts. `M101` finds the cycle. A documented ad hoc query finds the inherited
unit candidates, which are then checked against published unit semantics.
That dimensional analysis is not a generic stock lint rule.

**SCTO contains a restrictive cardinality model.** Version 2.0 of this 2017
third-party research ontology—not the official SNOMED CT distribution—declares
`has_description` both `Functional` and `InverseFunctional`. If one concept is
asserted to have two description individuals, OWL reasoning entails that those
individuals are the same. That maximum-one constraint conflicts with the
SNOMED CT data model, in which a concept can have several descriptions. `M107`
reports the legal but consequential characteristic combination.

**UBERON and HPO contain policy-backed obsoletion findings.** In the bundled
2026 releases, an obsolete UBERON term retains a logical superclass axiom and
a live HPO definition references an obsolete GO class. Both conflict with the
OBO Foundry Term Stability policy. `robot report` covers this category too;
Ontopoiesis provides parity through `P105` and keeps the structural graph open
for follow-up queries.

These claims are deliberately narrow. Supplemental lint profiles encode
targeted checks, case-specific queries state their external assumptions, and
neither is complete ontology or OWL-profile validation. Clean results are
reported only relative to the selected checks.

## What stays with your existing tools

Ontochoros complements reasoners, SHACL, and triple stores; it replaces none
of them.

- **Reasoning** stays external. `ontopoiesis reason` wraps `robot reason`
  behind an opt-in, user-provided jar; inferred axioms then build like any
  told structure.
- **Import resolution** stays external. `ontopoiesis resolve` wraps `robot
  merge`, optionally with an XML catalog, and produces one closure-complete
  OWL/XML document for `build`.
- **Instance-data (ABox) validation** stays with pySHACL. The Cypher rules
  here validate ontology *structure*.
- **Other serializations** convert on the way in: OWL/XML is the one parsed
  format, and `ontopoiesis convert` shims Turtle, RDF/XML, and OBO through
  the same opt-in ROBOT jar.

Everything is pure Python with an embedded graph engine — no JVM at runtime,
no server to stand up, nothing hosted.

## Who this is for

Ontochoros is aimed at people who already work in lint–test–diff–CI loops:
a data engineer handed an ontology to maintain, a knowledge-graph engineer
who writes Cypher, or a curator who wants pull requests reviewed on
structure instead of XML. There is no ontologist's API to learn — if you can
write a graph query, you can interrogate, test, and author an ontology.

## Where to start

- Run the loop end to end: the
  [Ontopoiesis quickstart](ontopoiesis/quickstart.md).
- See the findings above reproduced:
  [case studies](ontopoiesis/case-studies.md).
- Understand the graph you are querying:
  [the design](ontoplexis/concepts/design.md).
