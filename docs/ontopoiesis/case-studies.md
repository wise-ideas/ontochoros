---
title: "Case Studies"
---

OWL ontologies accumulate structural errors silently. An ontology deployed for a
decade can carry undeclared entity references, dangerous characteristic
combinations, or deprecated terms still cited in live axioms — and no individual
reviewer is likely to notice any of them. The maintainers are not careless:
finding these errors requires systematic queries across the ontology's full
structure, and most tools make that hard.

Ontopoiesis indexes an OWL document into a queryable graph once, then runs
structural assertions against it repeatedly. Every finding below comes from
`ontopoiesis lint` — with the `editorial`, `modeling_risk`, and
`description_logic` profiles — run against ten real ontologies shipped in the
`examples/` directory, all of them in production use. The pattern is consistent:
even foundational vocabularies maintained for years contain structural issues
that only a graph-indexed view makes visible.

Each finding below closes with **How existing tools fare** — an honest account
of what a reasoner or `robot report` does with the same file. The recurring
lesson is not that these defects are impossible to find elsewhere, but *why the
usual tools stay quiet*: a reasoner checks logical consistency, so a legal-but-wrong
axiom raises nothing; `robot report` runs a fixed rule set that these issues fall
outside; and a bespoke SPARQL query only helps if you already suspect the problem.
A queryable projection plus a small built-in rule set turns "know to look" into
"run the baseline," and leaves the whole graph open for the follow-up question.

These findings are projection findings. Ontopoiesis records `owl:imports` declarations but
does not merge imported ontology content into the built graph. Where a finding depends
on declarations, labels, or annotations that may live in an imported ontology, the
examples below call that out explicitly.

> **Try it yourself:** The commands below reproduce each finding. To run the same audit
> on your own ontology:
>
> ```bash
> ontopoiesis build your-ontology.owlxml -o your-ontology.lbug
> ontopoiesis lint --profile editorial --profile modeling_risk --profile description_logic your-ontology.lbug
> ```

---

## Projection-Level Findings

### Dublin Core

Dublin Core is a foundational metadata vocabulary used in library systems, repositories,
and publishing workflows for over two decades.

**Five annotation properties used in axioms without declarations in the built
projection**

```
dc:isReferencedBy   dc:isRequiredBy   dc:issued
dc:modified         dc:hasVersion
```

These properties appear in the Dublin Core OWL export's own axioms, but the source file
also declares `owl:imports` for the Dublin Core Terms vocabulary. Ontopoiesis records those
imports without merging their content, so the built projection lacks the declarations
that may exist in the import closure. Treat this as a source-document projection
finding, not as a confirmed ontology-wide OWL 2 DL violation.

**How existing tools fare:** a strict OWL 2 DL parser reading the isolated document (as
opposed to the full import closure) can still reject or silently drop these axioms —
including the version metadata that references `dc:hasVersion` and `dc:modified`. Because
Ontopoiesis makes the projection scope explicit, you see exactly which declarations are
present in *this* file rather than assuming the import closure filled them in. Confirm
against a merged closure if the distinction matters to you.

Reproduce:

```bash
ontopoiesis lint --profile description_logic examples/dublincore.lbug
```

---

## OWL 2 DL Violations

### FoaF — Friend of a Friend

FoaF is one of the most widely deployed vocabularies on the web, describing people and
their relationships across social and linked-data systems.

**Six properties are declared as both data properties and inverse-functional — illegal in
OWL 2 DL**

```
foaf:aimChatID   foaf:icqChatID    foaf:jabberID
foaf:mbox_sha1sum   foaf:msnChatID   foaf:yahooChatID
```

Each of these is an `owl:DatatypeProperty` that is also declared
`owl:InverseFunctionalProperty`. Inverse-functional means "no two subjects share a value,"
which is how FoaF says a hashed mailbox or a chat ID uniquely identifies one person. But
OWL 2 restricts that characteristic to *object* properties, so declaring it on a data
property puns the same name across the object and data worlds — something the OWL 2 DL
profile forbids.

**In plain terms:** FoaF uses a value like a person's hashed email address as a unique
fingerprint. That is a reasonable thing to want, but the way FoaF declares it is off-limits
in the strict profile, so a DL reasoner will either refuse the file or silently discard the
uniqueness.

**Caveat:** this is not an oversight. FoaF's authors deliberately publish it in OWL Full,
the more permissive dialect, and accept that it falls outside OWL 2 DL. Treat this as a
compatibility fact to know before you feed FoaF to a DL reasoner — not a bug to file.

**How existing tools fare:** a DL reasoner reads the file without complaint, because a
profile violation is a syntactic matter, not a logical inconsistency — a consistency check
has nothing to report. `robot report` returns 93 findings, none of them this. The OWL API
*does* catch it, but only through its opt-in `OWL2DLProfile` checker, which is not on the
load/reason/report path curators normally run. Here it takes one baseline command instead
of a reasoner failing somewhere downstream.

Reproduce (FoaF ships as RDF/XML, so convert to OWL/XML first):

```bash
ontopoiesis convert examples/foaf.owl -o foaf.owx      # requires ROBOT_JAR
ontopoiesis build foaf.owx -o foaf.lbug
ontopoiesis lint --profile description_logic foaf.lbug
```

---

## Modeling Risk Warnings

### SCTO — SNOMED CT standard ontology

**A property pair forces an impossible one-to-one link between concepts and descriptions**

```
ogms.owl#SCTO_0000006    (label: has_description)
ogms.owl#SCTO_00000012   (label: is_description_of)
```

Both properties are declared `Functional` and `InverseFunctional`. A functional property
allows each subject at most one value; an inverse-functional property allows each value at
most one subject. A property that is both defines a *bijection* — a strict one-to-one
pairing. Here `has_description` runs from **SNOMED CT Concept** (its declared domain) to
**SNOMED CT Description** (its declared range), so the axioms assert that each concept has
exactly one description and each description belongs to exactly one concept.

That contradicts the standard the ontology exists to model. In SNOMED CT a single concept
carries several descriptions — a fully specified name, a preferred term, and any number of
synonyms. The one-to-one constraint is therefore wrong about its own subject matter.

**In plain terms:** the model claims a medical concept has exactly one name, when in
reality it has many. Under a reasoner, the consequence is not a warning but silent data
corruption: assert that a concept has two descriptions, and the reasoner concludes the two
descriptions are the *same thing* and merges them.

**Caveat:** the ontology as shipped is a schema (a TBox) with no concept/description data
in it yet, so nothing merges today. This is a latent trap that springs the moment someone
populates the ontology — which is precisely its stated purpose. It is worth reporting to
the maintainers rather than working around.

**How existing tools fare:** nothing here is illegal OWL, so a reasoner has no
inconsistency to report — and with no individuals loaded, it never triggers. `robot report`
does not flag this characteristic combination out of the box. You *can* find it with a
hand-written SPARQL query, but only if you already suspect it; the built-in `M107` rule
turns "know to look for it" into "run the baseline."

Additional findings:

- 4 object properties with no domain or range
- 6 annotation assertions targeting unknown subjects (annotations whose subject IRI does
  not resolve to any declared entity in the ontology)

Reproduce (the source uses a DOCTYPE declaration, so normalize it through ROBOT first):

```bash
ontopoiesis convert examples/SCTO.owl -o scto.owx    # requires ROBOT_JAR
ontopoiesis build scto.owx -o scto.lbug
ontopoiesis lint --profile modeling_risk scto.lbug
```

---

### UBERON — Uber Anatomy Ontology

**`UBERON_0000000` is deprecated but still referenced in active axioms**

A deprecated entity that still appears in a normative axiom causes downstream consumers
applying the deprecation to quietly lose that constraint.

**Seven entities carry duplicate `rdfs:label` values in the same language tag**

Affected entities include `GO:0110165`, `NCBITaxon:131567`, `GOREL:0002003`, and
`GOREL:0002004`. Any tool that relies on label uniqueness for lookup or display behaves
unpredictably against these entities.

**How existing tools fare:** a reasoner reports neither — both are legal OWL, not logical
contradictions. The deprecated-reference check is one `robot report` also covers, but the
duplicate-label and untyped-individual findings are not in its default set. Without a graph
index you would cross-reference every entity IRI against its deprecation and label
annotations by hand — impractical at UBERON's scale. The baseline surfaces all of them from
one projection, and the graph stays open to ask which axioms each affected entity sits in.

Additional findings:

- 18 named individuals with no type assertion (effectively unclassified)
- 216 object properties lacking domain or range declarations

Reproduce:

```bash
ontopoiesis lint --profile editorial --profile modeling_risk examples/uberon.lbug
```

---

### HPO — Human Phenotype Ontology

**`GO:0005623` (`obsolete cell`) is marked deprecated in HPO's own file, yet still
referenced by an active axiom**

HPO carries the `GO:0005623` class directly in its source, annotated `owl:deprecated
true` with the label `obsolete cell` and a comment that it is redundant with
`CL:0000000`. The deprecation is stated in the document itself — no import closure is
needed. Yet the same document still uses that obsolete term in the logical definition of a
live class: `HP:0006476` (`Abnormality of the pancreatic islet cells`) is defined, via an
`EquivalentClasses` axiom, against a restriction that references `GO:0005623`. The `P105`
editorial rule reports it against the plain projection.

**In plain terms:** a phenotype term doctors and researchers still use is built on top of a
component the ontology's own file marks "do not use — obsolete." Anyone who trusts the
deprecation flag and drops the obsolete class loses part of the phenotype's definition. The
fix is to repoint the definition at the current replacement, `CL:0000000`.

**How existing tools fare:** this is the one finding here that off-the-shelf tooling also
covers — `robot report` has a deprecated-reference check. The point is not exclusivity but
parity from the same surface: the built-in `P105` rule finds it on a 767k-node projection
in seconds with no bespoke SPARQL, and the graph stays open so the very next query can ask
"what else does this obsolete class touch?" without switching tools.

Additional editorial findings on the built projection:

- 137 entities without an `rdfs:label` (many imported terms whose labels live in the
  parent releases)
- 4,040 labeled terms without a textual definition (`IAO:0000115`)

Reproduce (HPO ships as RDF/XML, so convert to OWL/XML first):

```bash
ontopoiesis convert examples/hp.owl -o hp.owx      # requires ROBOT_JAR
ontopoiesis build hp.owx -o hp.lbug
ontopoiesis lint --profile editorial hp.lbug
```

---

## Clean Passes

The following ontologies ran the full `--profile editorial --profile modeling_risk
--profile description_logic` audit and produced no violations at any level.

### GO — Gene Ontology

The Gene Ontology is the de facto standard for annotating gene function across
databases and publications.

```bash
ontopoiesis lint --profile editorial --profile modeling_risk --profile description_logic examples/go.lbug
```

The bundled projection has 1,062,826 nodes and 2,021,126 edges.

The full GO release passes the baseline cleanly. The editorial profile produces
expected warnings for terms whose labels and definitions live in imported modules
rather than in the document itself — the same projection-scope behaviour documented
in the [GO slim example](go-slim.md). No hard failures or modeling-risk flags were
found in the source document's directly stated axioms.

Reproduce:

```bash
ontopoiesis lint --profile editorial --profile modeling_risk --profile description_logic examples/go.lbug
```

---

### GO Slim — Gene Ontology generic slim

The GO generic slim is a curated subset of the Gene Ontology covering all three GO
namespaces: biological process, molecular function, and cellular component.

The [GO slim example](go-slim.md) walks through the full Ontopoiesis workflow against this
ontology in detail. For the lint summary:

```bash
ontopoiesis lint --profile editorial examples/goslim_generic.lbug
```

The baseline passes cleanly. The editorial profile flags 40 entities without
`rdfs:label` (predominantly imported terms whose labels live in the parent GO
release) and 33 labeled terms without a definition (`IAO:0000115`). No errors or
modeling-risk warnings were found.

---

### SWEET — Semantic Web for Earth and Environmental Terminology

SWEET is a set of Earth and environmental science ontologies developed by NASA JPL.

```bash
ontopoiesis lint --profile editorial --profile modeling_risk --profile description_logic examples/sweetAll.lbug
```

The bundled projection has 2,337 nodes and 3,399 edges.

The full audit passes with no violations. SWEET uses a modular import structure;
as with GO, declaration- and annotation-sensitive editorial rules may flag terms
whose declarations live in imported modules not merged before build. No hard failures
or modeling-risk patterns were found in the directly stated axioms.

---

### schema.org

schema.org is a collaborative vocabulary for structured data markup, widely deployed
in HTML `<meta>` and JSON-LD annotations across the web.

```bash
robot convert --input examples/schemaorg.rdf --output /tmp/schemaorg.owlxml
ontopoiesis build /tmp/schemaorg.owlxml -o /tmp/schemaorg.lbug
ontopoiesis lint --profile editorial --profile modeling_risk --profile description_logic /tmp/schemaorg.lbug
```

A fresh projection built from the converted `examples/schemaorg.rdf` has 23,932 nodes and 40,092
edges.

The full audit passes with no violations. schema.org's property-heavy design and
liberal use of annotation properties produces no contradictions or dangerous
characteristic combinations. No hard failures, modeling-risk warnings, or OWL 2 DL
issues were found in the source document projection.

---

## Summary

| Ontology        | Hard failures                               | Notable warnings                                                                       |
| --------------- | ------------------------------------------- | -------------------------------------------------------------------------------------- |
| **FoaF**        | 6 object/data property punning violations (OWL 2 DL) | — (known OWL Full design; see caveat)                                          |
| **Dublin Core** | 1 projection-only undeclared-entity finding | Missing labels, missing version IRI                                                    |
| **SCTO**        | 0                                           | Impossible one-to-one concept↔description constraint (functional + inverse-functional), dangling annotations |
| **UBERON**      | 0                                           | Deprecated entity referenced, duplicate labels, untyped individuals                    |
| **HPO**         | 0                                           | Obsolete term (self-declared) still used in a live class definition                    |
| **GO**          | 0                                           | Projection-scope editorial warnings for imported terms (labels/definitions in imports) |
| **GO slim**     | 0                                           | 40 entities without label, 33 labeled without definition — both projection-scope       |
| **SWEET**       | 0                                           | None                                                                                   |
| **schema.org**  | 0                                           | None                                                                                   |

---

## What this means for your ontology

The findings above are all detectable with `ontopoiesis lint` against a single built
projection — a command that takes seconds on most ontologies. For import-heavy
ontologies such as Dublin Core and HPO, read declaration- and annotation-sensitive
findings as projection-level evidence first, then confirm them against a merged import
closure if the distinction matters.

These structural checks are not exhaustive. They cover errors expressible as Cypher
queries over the projection: type conflicts, undeclared references, characteristic
combinations, deprecation drift, and editorial hygiene. Errors that require a running
reasoner — unsatisfiable classes, property chain inconsistencies — fall outside this
scope. Use an external reasoner and inspect its inferred hierarchy.

## Running the full audit

```bash
for f in examples/*.lbug; do
  ontopoiesis lint --profile editorial --profile modeling_risk --profile description_logic "$f"
done
```
