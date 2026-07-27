---
title: "Case Studies"
---

Automated checks return observations. Calling one a defect requires more:
the ontology's import closure, intended OWL profile, and published modeling
commitments must support that conclusion. The examples below keep those steps
separate.

Ontopoiesis indexes an OWL document once, then supports stock lint rules and
case-specific Cypher analysis over the same graph. Each case says which kind
of check produced the result and what external evidence makes the result
meaningful. The claims apply only to the named releases, not every version of
the ontologies.

Each finding closes with **How existing tools fare**. Some overlap with
`robot report`; others do not. The value here is a repeatable
query/test/lint workflow and a graph that remains available for follow-up,
not a claim of exclusive detection.

These findings are projection findings. Resolve import closures before building
when a finding depends on declarations, labels, annotations, or hierarchy
axioms that may live in another ontology. Unresolved source-document
projections remain useful for local authoring checks, but they are not evidence
of an ontology-wide defect.

> **Try it yourself:** The commands below reproduce each finding. To run the same audit
> on your own ontology:
>
> ```bash
> ontopoiesis build your-ontology.owlxml -o your-ontology.lbug
> ontopoiesis lint --profile editorial --profile modeling_risk --profile description_logic your-ontology.lbug
> ontopoiesis query your-ontology.lbug -q "MATCH ... RETURN ..."
> ```
>
> If the ontology imports other documents, run `ontopoiesis resolve` first
> and build the resulting `.closure.owx` document.

## Scientific Model Checks

### SWEET — Semantic Web for Earth and Environmental Terminology

The bundled `sweetAll.owl` identifies itself as SWEET 3.6.0. It is an import
driver for a highly modular ontology suite, so the findings below apply to a
resolved import closure rather than the 22 KB source document by itself.

#### Angular momentum has two incompatible units, neither of them correct

The resolved ontology says that angular momentum is a kind of momentum and
assigns a default unit to each:

```text
AngularMomentum SubClassOf Momentum
AngularMomentum SubClassOf hasDefaultUnit value kilogramRadianPerSecond
Momentum        SubClassOf hasDefaultUnit value kilogramMeterPerSecond
```

SWEET constructs `kilogramRadianPerSecond` from kilogram, radian, and
per-second and gives it the notation `kg.rad/s`. Because radians are
dimensionless in SI, that unit has dimensions of mass per time. Angular
momentum instead has dimensions `kg m² s⁻¹`, also written `J s`.

The subclass axiom creates a second problem: `AngularMomentum` also inherits
`Momentum`'s `kg m s⁻¹` restriction. It therefore has two incompatible
default units, and both disagree with the standard dimension of angular
momentum.

This is present in the maintained SWEET
[rotation](https://github.com/ESIPFed/sweet/blob/master/src/propRotation.ttl),
[speed](https://github.com/ESIPFed/sweet/blob/master/src/propSpeed.ttl), and
[scientific-unit](https://github.com/ESIPFed/sweet/blob/master/src/reprSciUnits.ttl)
modules. The dimensional comparison is not a local naming preference:
the SI unit `J s` is `kg m² s⁻¹`; the
[BIPM SI Brochure](https://www.bipm.org/documents/20126/41483022/SI-Brochure-9-EN.pdf)
identifies action and angular momentum as quantities with that unit.

**How it was found:** this is an ad hoc analysis, not a stock lint rule. The
query compares a named class's direct default unit with the direct default
unit on its named superclass:

```cypher
MATCH (child:N {kind:'Class'})
      -[:D {relation:'subclass_of'}]->(parent:N {kind:'Class'}),
      (child_axiom:N {kind:'SubClassOf'})
      -[:E {role:'sub'}]->(child),
      (child_axiom)-[:E {role:'super'}]
      ->(child_restriction:N {kind:'ObjectHasValue'}),
      (child_restriction)-[:E {role:'property'}]
      ->(:N {iri:'http://sweetontology.net/relaSci/hasDefaultUnit'}),
      (child_restriction)-[:E {role:'filler'}]->(child_unit:N),
      (parent_axiom:N {kind:'SubClassOf'})
      -[:E {role:'sub'}]->(parent),
      (parent_axiom)-[:E {role:'super'}]
      ->(parent_restriction:N {kind:'ObjectHasValue'}),
      (parent_restriction)-[:E {role:'property'}]
      ->(:N {iri:'http://sweetontology.net/relaSci/hasDefaultUnit'}),
      (parent_restriction)-[:E {role:'filler'}]->(parent_unit:N)
WHERE child_unit.uid <> parent_unit.uid
RETURN child.iri AS child,
       child_unit.iri AS child_default_unit,
       parent.iri AS parent,
       parent_unit.iri AS parent_default_unit
```

The query also returns `Frequency` below `Rate`; hertz and per-second are
dimensionally compatible. It returns `Brightness` below `Luminance` too, but
that terminology needs domain interpretation. Neither result is presented as
a defect. This query finds candidates, not verdicts. A reusable check would
have to reduce each compound unit to a dimension vector first.

#### A subclass cycle conflates radiant flux with radiative forcing

The same resolved ontology asserts:

```text
RadiantFlux      SubClassOf RadiativeForcing
RadiativeForcing SubClassOf RadiantFlux
RadiativeForcing SubClassOf FluxDensity
FluxDensity      SubClassOf hasDefaultUnit value wattPerMeterSquared
```

The two subclass axioms make `RadiantFlux` and `RadiativeForcing` logically
equivalent. They also make radiant flux inherit `FluxDensity`'s `W/m²`
default unit. That erases a standard distinction: NIST gives radiant flux in
watts and irradiance in watts per square metre, while the IPCC defines
radiative forcing in watts per square metre
([NIST](https://www.nist.gov/publications/radiometry-and-photometry-review-vision-optics);
[IPCC](https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-1/)).

**How it was found:** the stock `M101` rule finds the cycle. A case-specific
follow-up query traces its dimensional consequence through the anonymous
`ObjectHasValue` restriction. `M101` alone does not claim that every subclass
cycle is wrong.

```cypher
MATCH (radiant:N {
         iri:'http://sweetontology.net/propEnergyFlux/RadiantFlux'
      })-[:D {relation:'subclass_of'}]->(forcing:N {
         iri:'http://sweetontology.net/propEnergyFlux/RadiativeForcing'
      }),
      (forcing)-[:D {relation:'subclass_of'}]->(density:N {
         iri:'http://sweetontology.net/propEnergyFlux/FluxDensity'
      }),
      (axiom:N {kind:'SubClassOf'})-[:E {role:'sub'}]->(density),
      (axiom)-[:E {role:'super'}]->(restriction:N {kind:'ObjectHasValue'}),
      (restriction)-[:E {role:'property'}]->(property:N),
      (restriction)-[:E {role:'filler'}]->(unit:N)
RETURN radiant.iri AS affected_class,
       forcing.iri AS via_class,
       density.iri AS inherited_superclass,
       property.iri AS restriction_property,
       unit.iri AS inherited_value
```

Neither finding makes the ontology inconsistent. `hasDefaultUnit` is not
functional, and the unit individuals are not logically disjoint. The defect
is scientific rather than logical: the entailed default-unit relationships
disagree with the standard dimensions of the quantities.

**How existing tools fare:** the default `robot report` run over the same
closure reports missing definitions for these classes but not the dimensional
problems. `robot reason` can detect the equivalence entailed by the cycle when
run with
[`--equivalent-classes-allowed asserted-only`](https://robot.obolibrary.org/reason.html#equivalent-class-axioms);
it does not establish that the equivalence is scientifically wrong or diagnose
the unit consequence. A custom SPARQL check is possible, but a general version
must reconstruct anonymous restrictions and recursively normalise compound
unit expressions before comparing dimensions.

Reproduce:

```bash
export ROBOT_JAR=/path/to/robot.jar
ontopoiesis resolve examples/sweetAll.owl -o sweet.closure.owx
ontopoiesis build sweet.closure.owx -o sweet.lbug
ontopoiesis lint --select M101 sweet.lbug
ontopoiesis query sweet.lbug -q "<paste either Cypher query above>"
```

---

## Modeling Risk

### SCTO — a research ontology based on SNOMED CT

The bundled SCTO is version 2.0 of the ontology published with the 2018 paper
[*SNOMED CT standard ontology based on the ontology for general medical
science*](https://pmc.ncbi.nlm.nih.gov/articles/PMC6119323/). It is a
third-party research artifact, not the official SNOMED CT distribution.

**A property pair restricts every participating concept to at most one
description**

```
ogms.owl#SCTO_0000006    (label: has_description)
ogms.owl#SCTO_00000012   (label: is_description_of)
```

The properties are inverses, and both are declared `Functional` and
`InverseFunctional`. Together those characteristics make the relation
one-to-one wherever it is asserted: a concept can have at most one description,
and a description can belong to at most one concept. They do not require either
individual to have a relationship, so this is a maximum-cardinality constraint,
not an exactly-one constraint.

That maximum conflicts with the
[SNOMED CT data model](https://support.nlm.nih.gov/knowledgebase/article/KA-04015/en-us)
the research ontology is representing. A SNOMED CT concept can have several
associated descriptions, including a fully specified name and synonyms selected
as preferred or acceptable in particular language reference sets.

**In plain terms:** if data asserts two description individuals for one
concept, OWL reasoning entails that the two individuals are the same. If the
data also states that they are different, the ontology becomes inconsistent.

**Caveat:** the bundled ontology is a 2017 schema snapshot with no
concept/description assertions that trigger the entailment. This is a modeling
risk in that research artifact, not a claim that SNOMED CT itself has the
constraint.

**How existing tools fare:** nothing here is illegal OWL, so a reasoner has no
inconsistency to report — and with no individuals loaded, it never triggers. `robot report`
does not flag this characteristic combination out of the box. You *can* find it
with a hand-written SPARQL query; the built-in `M107` rule makes the check
repeatable in the normal lint workflow.

Reproduce (the source uses a DOCTYPE declaration, so normalize it through ROBOT first):

```bash
ontopoiesis convert examples/SCTO.owl -o scto.owx    # requires ROBOT_JAR
ontopoiesis build scto.owx -o scto.lbug
ontopoiesis lint --profile modeling_risk scto.lbug
```

---

## OBO Policy Findings

### UBERON — Uber Anatomy Ontology

The bundled file identifies itself as the 2026-04-01 UBERON release.

**Obsolete `UBERON_0000000` retains a logical superclass axiom**

`UBERON_0000000` is marked `owl:deprecated true` and labelled `obsolete
processual entity`, but it still has a `SubClassOf BFO:0000003` axiom. This is
not an OWL contradiction. It is, however, a concrete violation of the
[OBO Foundry Term Stability policy](https://obofoundry.org/principles/fp-019-term-stability.html),
which requires all logical axioms to be removed from an obsolete term and
checks this condition as an error.

**How existing tools fare:** a reasoner need not report this because it is legal
OWL. `robot report` also checks references to deprecated entities, so this is a
parity example rather than an exclusive Ontopoiesis finding. `P105` exposes it
through the same graph used for project-specific follow-up queries.

Reproduce:

```bash
ontopoiesis lint --profile editorial --profile modeling_risk examples/uberon.lbug
```

---

### HPO — Human Phenotype Ontology

The bundled file identifies itself as the 2026-02-16 HPO release.

**`GO:0005623` (`obsolete cell`) is marked deprecated in HPO's own file, yet still
referenced by an active axiom**

HPO carries the `GO:0005623` class directly in its source, annotated `owl:deprecated
true` with the label `obsolete cell` and a comment that it is redundant with
`CL:0000000`. The deprecation is stated in the document itself — no import closure is
needed. Yet the same document still uses that obsolete term in the logical definition of a
live class: `HP:0006476` (`Abnormality of the pancreatic islet cells`) is defined, via an
`EquivalentClasses` axiom, against a restriction that references `GO:0005623`. The `P105`
editorial rule reports it against the plain projection.

This is a direct violation of the
[OBO Foundry Term Stability policy](https://obofoundry.org/principles/fp-019-term-stability.html),
which requires obsolete terms to be removed or replaced in logical axioms.
HPO's copied annotation says the GO class was obsoleted as redundant with
`CL:0000000`, but choosing the exact repair remains a curator decision rather
than something the lint result can establish.

**How existing tools fare:** `robot report` also has a deprecated-reference
check. The point is parity from the same surface: the built-in `P105` rule finds
it on a 767k-node projection, and the graph stays open so a follow-up query can
ask what else the obsolete class touches.

Reproduce (HPO ships as RDF/XML, so convert to OWL/XML first):

```bash
ontopoiesis convert examples/hp.owl -o hp.owx      # requires ROBOT_JAR
ontopoiesis build hp.owx -o hp.lbug
ontopoiesis lint --profile editorial hp.lbug
```

---

## Negative Controls

These examples show what the selected Ontopoiesis rules do *not* report. A
clean result means that none of those rules returned a row; it is not a complete
OWL profile validation or a general proof that the ontology is error-free.

### GO — Gene Ontology

The Gene Ontology is the de facto standard for annotating gene function across
databases and publications.

```bash
ontopoiesis lint --profile editorial --profile modeling_risk --profile description_logic examples/go.lbug
```

The bundled projection has 1,062,826 nodes and 2,021,126 edges.

The GO release passes the default baseline. The editorial profile produces
expected warnings for external terms whose labels and definitions are not copied
into the release document — the same projection-scope behaviour documented in the
[GO slim example](go-slim.md). No hard failures or modeling-risk flags were found.

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

The default baseline passes. The editorial profile flags 40 entities without
`rdfs:label` (predominantly external terms whose labels live in the parent GO
release) and 33 labeled terms without a definition (`IAO:0000115`). The release
does not declare formal imports, so these are source-document editorial findings
rather than demonstrated ontology defects. No errors or modeling-risk warnings
were found by the selected rules.

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

None of the selected rules returns a result for this source-document projection.
schema.org does not thereby gain an OWL 2 DL conformance claim; Ontopoiesis'
description-logic profile is a targeted rule set, not a complete profile
validator.

---

## Summary

| Ontology       | Result | Interpretation |
| -------------- | ------ | -------------- |
| **SWEET 3.6.0** | Angular-momentum unit mismatch; radiant-flux/radiative-forcing cycle propagates `W/m²` to radiant flux | Scientific-model defects established by combining graph results with published unit semantics; dimensional analysis is currently ad hoc, while `M101` finds the cycle |
| **SCTO 2.0**   | Functional and inverse-functional `has_description` | Modeling risk in a 2017 third-party research ontology; it does not describe an error in SNOMED CT itself |
| **UBERON 2026-04-01** | Obsolete term retains a logical axiom | Concrete OBO Term Stability policy violation; also covered by `robot report` |
| **HPO 2026-02-16** | Live definition references an obsolete GO class | Concrete OBO Term Stability policy violation; also covered by `robot report` |
| **GO**         | No baseline or modeling-risk result; expected editorial warnings | Negative control for the selected rules |
| **GO slim**    | No baseline or modeling-risk result; source-document editorial warnings | Negative control for the selected rules |
| **schema.org** | No result from the selected rules | Negative control, not a general conformance result |

---

## What this means for your ontology

The observations above are reproducible with stock lint rules or the shown
ad hoc Cypher query against a built projection. For import-heavy ontologies,
resolve the import closure before treating declaration-, annotation-, or
hierarchy-sensitive findings as ontology-wide evidence.

These structural checks are not exhaustive. Stock lint rules cover generally
applicable conditions such as type conflicts, undeclared references,
characteristic combinations, deprecation drift, and editorial hygiene.
Project tests and ad hoc queries can add domain contracts such as compatible
physical dimensions. Errors that require complete OWL inference still belong
with an external reasoner.

## Running the stock rule set

```bash
for f in examples/*.lbug; do
  ontopoiesis lint --profile editorial --profile modeling_risk --profile description_logic "$f"
done
```
