---
title: "Case Studies"
---

OWL ontologies accumulate structural errors silently. A well-known ontology in active
use for a decade can carry undeclared entity references, dangerous characteristic
combinations, or quietly deprecated terms still in active use — none of which any
individual reviewer is likely to notice. The reason is not carelessness: finding these
errors requires systematic querying across the full structure of the ontology, and most
tools make that difficult.

Ontopoiesis indexes an OWL document into a queryable graph once, then lets you run
structural assertions against it repeatedly. The findings below come from running
`ontopoiesis lint` — with the `editorial`, `modeling_risk`, and `description_logic` profiles — against
ten real ontologies shipped in the `examples/` directory. All ten are production
ontologies used in deployed systems. The pattern is consistent: even foundational
vocabularies maintained for years contain structural issues only visible from a
graph-indexed view.

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
finding, not as a confirmed ontology-wide OWL 2 DL violation. Tools doing strict OWL 2
DL parsing against the isolated document can still reject or silently drop these axioms
— including the version metadata statements, which reference `dc:hasVersion` and
`dc:modified`.

Reproduce:

```bash
ontopoiesis lint --profile description_logic examples/dublincore.lbug
```

---

## Modeling Risk Warnings

### SCTO — Standard Clinical Trials Ontology

**Two properties with a dangerous characteristic combination: functional + inverse-functional**

```
ogms.owl#SCTO_00000012
ogms.owl#SCTO_0000006
```

A functional property allows each subject at most one value; an inverse-functional
property allows each value at most one subject. A property that is both defines a
bijection between two classes. Under a reasoner, this causes unexpected individual
merging: any two individuals sharing a value for such a property are inferred to be
identical. In a clinical ontology this combination is rarely intentional, and the source
file gives no indication that it is there.

Additional findings:

- 4 object properties with no domain or range
- 6 annotation assertions targeting unknown subjects (annotations whose subject IRI does
  not resolve to any declared entity in the ontology)

Reproduce:

```bash
ontopoiesis lint --profile modeling_risk examples/SCTO.lbug
```

---

### UBERON — Uber Anatomy Ontology

**`UBERON_0000000` is deprecated but still referenced in active axioms**

A deprecated entity that still appears in a normative axiom causes downstream consumers
applying the deprecation to quietly lose that constraint. Without a graph index, the
only way to catch this is to manually cross-reference every entity IRI against the
deprecation annotations — impractical at UBERON's scale.

**Seven entities carry duplicate `rdfs:label` values in the same language tag**

Affected entities include `GO:0110165`, `NCBITaxon:131567`, `GOREL:0002003`, and
`GOREL:0002004`. Any tool that relies on label uniqueness for lookup or display behaves unpredictably
against these entities.

Additional findings:

- 18 named individuals with no type assertion (effectively unclassified)
- 216 object properties lacking domain or range declarations

Reproduce:

```bash
ontopoiesis lint --profile editorial --profile modeling_risk examples/uberon.lbug
```

---

### HPO — Human Phenotype Ontology

**`GO:0005623` (`cell`) is deprecated in the Gene Ontology but still referenced by HPO**

HPO imports terms from GO. `GO:0005623` has since been deprecated in GO, but HPO's axioms
still reference it. Detecting this requires checking the deprecation status of every
imported term. That requires a projection built from a pre-merged import closure until
Ontopoiesis has a graph-native import model.

Additional findings:

- 202 object properties lacking domain or range in the built projection; many are
  imported BFO/RO properties whose declarations may live outside the source document

Reproduce:

```bash
ontopoiesis lint --profile editorial examples/hp.lbug
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
| **Dublin Core** | 1 projection-only undeclared-entity finding | Missing labels, missing version IRI                                                    |
| **SCTO**        | 0                                           | Dangerous property combination (functional + inverse-functional), dangling annotations |
| **UBERON**      | 0                                           | Deprecated entity referenced, duplicate labels, untyped individuals                    |
| **HPO**         | 0                                           | Deprecated GO term referenced cross-ontology                                           |
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
