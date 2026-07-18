---
title: "Why Ontotheke"
---

# Why manage ontologies like code

Your team already knows how to keep software healthy. Every change goes
through version control, a reviewable diff, automated tests, and CI. Nothing
ships because one expert eyeballed it and said it looked fine.

Ontologies rarely get any of that. A curator edits the file in a GUI, a
reviewer scrolls a thousand-line XML diff, and a specialist runs a reasoner
that answers only one kind of question. The result is predictable: widely
used ontologies, maintained for decades by careful people, quietly accumulate
structural defects that no reviewer could have spotted by reading.

Ontotheke closes that gap. It treats an ontology the way dbt treats a
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

## The evidence: stock lint, real defects

Skepticism is fair — every tool promises to find problems. So here is what
the bundled lint baseline finds in production ontologies, with an honest
account of how existing tools fare:

**FoaF is not OWL 2 DL.** Six FoaF properties are declared both
`owl:DatatypeProperty` and `owl:InverseFunctionalProperty` — a characteristic
OWL 2 reserves for object properties, which makes the file illegal in the
OWL 2 DL profile. *In plain terms:* FoaF marks fields like `mbox_sha1sum` as
unique identifiers using a shortcut the strict profile forbids, so a DL
reasoner either rejects the file or quietly drops that uniqueness.
`ontopoiesis lint --profile description_logic` reports all six and one Cypher
query pins the exact cause; a DL reasoner and `robot report` (93 findings)
flag none of them. *Caveat:* FoaF's authors deliberately keep it in the more
permissive OWL Full, so read this as a compatibility gotcha to know about,
not a maintainer's mistake.

**SCTO asserts an impossible cardinality.** The SNOMED CT standard ontology
declares `has_description` both `Functional` and `InverseFunctional`, forcing
a one-to-one pairing of SNOMED concepts and descriptions. *In plain terms:*
the model says each medical concept has exactly one description and vice
versa — but in SNOMED every concept has several (a formal name, a preferred
term, synonyms), so once the ontology is filled with data, a reasoner
concludes those distinct descriptions must be the same thing and merges them.
A built-in check (`M107`) flags it; no off-the-shelf report does. *Caveat:*
the ontology as shipped has no such data yet, so this is a latent trap in the
schema, not a live contradiction in the file.

**HPO ships a stale logical definition.** The Human Phenotype Ontology
(~767k projected nodes) marks the class `GO:0005623` ("cell") as obsolete in
its own file, then still uses it to define a live term,
`HP:0006476` ("Abnormality of the pancreatic islet cells"). *In plain terms:*
a current medical term is built on a building block the same file says not to
use anymore. The built-in `P105` check finds it directly, and the same query
surface handles GO and Uberon (~1.3M and ~886k nodes) in seconds.

None of these defects is *impossible* to find with existing tools — most are
expressible in SPARQL if you know to write the query. The claim is
different: one queryable projection plus a small built-in rule set surfaces
them in a normal workflow, and the whole graph stays open for follow-up.
The [case studies](ontopoiesis/case-studies.md) reproduce every finding,
command by command.

## What stays with your existing tools

Ontotheke complements reasoners, SHACL, and triple stores; it replaces none
of them.

- **Reasoning** stays external. `ontopoiesis reason` wraps `robot reason`
  behind an opt-in, user-provided jar; inferred axioms then build like any
  told structure.
- **Instance-data (ABox) validation** stays with pySHACL. The Cypher rules
  here validate ontology *structure*.
- **Other serializations** convert on the way in: OWL/XML is the one parsed
  format, and `ontopoiesis convert` shims Turtle, RDF/XML, and OBO through
  the same opt-in ROBOT jar.

Everything is pure Python with an embedded graph engine — no JVM at runtime,
no server to stand up, nothing hosted.

## Who this is for

You will feel at home here if you already think in lint–test–diff–CI loops:
a data engineer handed an ontology to maintain, a knowledge-graph engineer
who writes Cypher, or a curator who wants pull requests reviewed on
structure instead of XML. You need no ontologist's API — if you can write a
graph query, you can interrogate, test, and author an ontology.

## Where to start

- Run the loop end to end: the
  [Ontopoiesis quickstart](ontopoiesis/quickstart.md).
- See the findings above reproduced:
  [case studies](ontopoiesis/case-studies.md).
- Understand the graph you are querying:
  [the design](ontoplexis/concepts/design.md).
