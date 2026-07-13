---
title: "Working with a real ontology: GO Slim"
---

This guide applies the Ontopoiesis workflow to the
[GO generic slim](https://geneontology.org/docs/go-subset-guide/) — a curated subset of
the Gene Ontology that covers all three GO namespaces: biological process, molecular
function, and cellular component.

GO slim is a real, maintained ontology representative of biomedical practice. It uses
annotation properties, existential restrictions, property chains, and OBO conventions —
which makes it a practical test case for Ontopoiesis's full workflow.

This guide assumes you have completed the [Quickstart](quickstart.md) and already have
a working Ontopoiesis installation.

The GO generic slim is a curated subset of the full Gene Ontology, covering all three
GO namespaces while staying small enough to inspect interactively. It still uses
annotation properties, existential restrictions, and property chains, so it gives you a
representative slice of OWL 2 EL practice in biomedical ontologies.

This walkthrough takes about 15 minutes and requires network access to download the
slim from OBO Foundry.

The commands below assume you are running from the repository root.

## 1. Download and build the projection

Download the GO generic slim from OBO Foundry, then convert the RDF/XML download to
OWL/XML with ROBOT:

```bash
curl -L http://purl.obolibrary.org/obo/go/subsets/goslim_generic.owl \
  -o goslim_generic.owl
robot convert --input goslim_generic.owl --output goslim_generic.owlxml
```

Then build a Ladybug projection from it:

```bash
uv run ontopoiesis build goslim_generic.owlxml -o goslim_generic.lbug
```

```
Wrote goslim_generic.lbug
╭─ Build Complete ─╮
│ nodes  4,670     │
│ edges  7,923     │
╰──────────────────╯
```

4,670 nodes and 7,923 edges — one reusable artifact for every workflow that follows.

## 2. What is in the projection

Discover which OWL 2 construct kinds are present:

```bash
uv run ontopoiesis query goslim_generic.lbug \
  -q "MATCH (n:N) RETURN DISTINCT n.kind AS kind ORDER BY kind"
```

The GO slim uses classes, subclass axioms, annotation assertions, existential
restrictions (`ObjectSomeValuesFrom`), property chains, and transitive property
declarations — a representative cross-section of OWL 2 EL.

Count terms by GO namespace:

```bash
uv run ontopoiesis query goslim_generic.lbug -q "
MATCH (ax:N {kind: 'AnnotationAssertion'})
      -[:E {role: 'annotation_property'}]->(:N {iri: 'http://www.geneontology.org/formats/oboInOwl#hasOBONamespace'}),
      (ax)-[:E {role: 'annotation_value'}]->(val:N)
WHERE ax.annotation_subject IS NOT NULL
RETURN COALESCE(val.quoted_string, val.lexical_form) AS namespace,
       count(*) AS term_count
ORDER BY namespace"
```

```
  namespace               term_count
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  "biological_process"    72
  "cellular_component"    28
  "external"              11
  "molecular_function"    40
```

## 3. Labels, definitions, and synonyms

Retrieve labels and textual definitions (IAO:0000115) for GO terms:

```bash
uv run ontopoiesis query goslim_generic.lbug -q "
MATCH (label_ax:N {kind: 'AnnotationAssertion'})
      -[:E {role: 'annotation_property'}]->(:N {iri: 'http://www.w3.org/2000/01/rdf-schema#label'}),
      (label_ax)-[:E {role: 'annotation_value'}]->(label_val:N),
      (def_ax:N {kind: 'AnnotationAssertion'})
      -[:E {role: 'annotation_property'}]->(:N {iri: 'http://purl.obolibrary.org/obo/IAO_0000115'}),
      (def_ax)-[:E {role: 'annotation_value'}]->(def_val:N)
WHERE label_ax.annotation_subject = def_ax.annotation_subject
  AND label_ax.annotation_subject IS NOT NULL
RETURN label_ax.annotation_subject AS iri,
       COALESCE(label_val.quoted_string, label_val.lexical_form) AS label,
       COALESCE(def_val.quoted_string, def_val.lexical_form) AS definition
ORDER BY label
LIMIT 5"
```

Find terms with exact synonyms — common in biomedical ontologies:

```bash
uv run ontopoiesis query goslim_generic.lbug -q "
MATCH (label_ax:N {kind: 'AnnotationAssertion'})
      -[:E {role: 'annotation_property'}]->(:N {iri: 'http://www.w3.org/2000/01/rdf-schema#label'}),
      (label_ax)-[:E {role: 'annotation_value'}]->(label_val:N),
      (syn_ax:N {kind: 'AnnotationAssertion'})
      -[:E {role: 'annotation_property'}]->(:N {iri: 'http://www.geneontology.org/formats/oboInOwl#hasExactSynonym'}),
      (syn_ax)-[:E {role: 'annotation_value'}]->(syn_val:N)
WHERE label_ax.annotation_subject = syn_ax.annotation_subject
  AND label_ax.annotation_subject IS NOT NULL
RETURN COALESCE(label_val.quoted_string, label_val.lexical_form) AS label,
       COALESCE(syn_val.quoted_string, syn_val.lexical_form) AS synonym
ORDER BY label
LIMIT 8"
```

```
  label                            synonym
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  "ATP-dependent activity"         "ATPase activity"
  "ATP-dependent activity"         "ATPase activity, coupled"
  "ATP-dependent activity"         "ATP hydrolysis-dependent activity"
  "DNA-templated transcription"    "transcription, DNA-dependent"
  "DNA-templated transcription"    "DNA-dependent transcription"
  "Golgi apparatus"                "Golgi complex"
```

## 4. Subclass hierarchy and existential restrictions

Named subclass relationships in the slim:

```bash
uv run ontopoiesis query goslim_generic.lbug -q "
MATCH (ax:N {kind: 'SubClassOf'})
      -[:E {role: 'sub_class_expression'}]->(sub:N {kind: 'Class'}),
      (ax)-[:E {role: 'super_class_expression'}]->(sup:N {kind: 'Class'})
WHERE sub.iri IS NOT NULL AND sup.iri IS NOT NULL
RETURN sub.iri AS subclass, sup.iri AS superclass
ORDER BY superclass, subclass"
```

GO uses `part_of` (BFO_0000050) and `occurs_in` existential restrictions extensively.
Find which GO slim classes use them:

```bash
uv run ontopoiesis query goslim_generic.lbug -q "
MATCH (label_ax:N {kind: 'AnnotationAssertion'})
      -[:E {role: 'annotation_property'}]->(:N {iri: 'http://www.w3.org/2000/01/rdf-schema#label'}),
      (label_ax)-[:E {role: 'annotation_value'}]->(label_val:N),
      (ax:N {kind: 'SubClassOf'})
      -[:E {role: 'sub_class_expression'}]->(sub:N {kind: 'Class'}),
      (ax)-[:E {role: 'super_class_expression'}]->(restriction:N {kind: 'ObjectSomeValuesFrom'})
      -[:E {role: 'object_property_expression'}]->(prop:N)
WHERE sub.iri IS NOT NULL AND prop.iri IS NOT NULL
  AND label_ax.annotation_subject = sub.iri
RETURN COALESCE(label_val.quoted_string, label_val.lexical_form) AS class,
       prop.iri AS via_property
ORDER BY class"
```

## 5. Property chains

GO's relation ontology defines property chains — for example, that `part_of o part_of`
implies `part_of`, and `part_of o is_a` implies `part_of`. Query them directly:

```bash
uv run ontopoiesis query goslim_generic.lbug -q "
MATCH (ax:N {kind: 'SubObjectPropertyOf'})
      -[:E {role: 'super_object_property_expression'}]->(sup:N),
      (ax)-[:E {role: 'sub_object_property_expression'}]->(:N {kind: 'ObjectPropertyChain'})
      -[link:E {role: 'object_property_expressions'}]->(step:N)
WHERE sup.iri IS NOT NULL AND step.iri IS NOT NULL
RETURN sup.iri AS property, step.iri AS chain_step, link.endpoint_order AS position
ORDER BY property, position"
```

## 6. Lint

Run the default baseline across the full slim:

```bash
uv run ontopoiesis lint goslim_generic.lbug
```

The baseline passes cleanly. Add the editorial profile to check publication quality:

```bash
uv run ontopoiesis lint goslim_generic.lbug --profile editorial
```

```
WARN warn_missing_label.cypher
  query returned 40 violation row(s)

WARN warn_labeled_without_definition.cypher
  query returned 33 violation row(s)

WARN warn_ontology_no_metadata_annotations.cypher
  query returned 1 violation row(s)

========================= 25 passed, 3 warned in 3.40s =========================
```

40 entities in the slim do not have `rdfs:label` — these are predominantly imported
terms whose labels live in the parent ontology. 33 labeled terms lack a definition
(`IAO:0000115`). These are editorial warnings, not errors: the baseline remains clean.

## 7. Impact analysis

Trace which top-level axiom structure references a specific GO term — here, `GO:0006281`
(DNA repair):

```bash
uv run ontopoiesis impact upstream goslim_generic.lbug \
  --iri http://purl.obolibrary.org/obo/GO_0006281
```

The result shows every construct that references this term. On the GO slim, `GO:0006281`
appears directly in a `SubClassOf` axiom that itself connects back through the `Ontology`
and `OntologyDocument` wrappers:

```
  kind                   iri                                             uid    depth
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Class                  http://purl.obolibrary.org/obo/GO_0006281      ...    1
  SubClassOf             None                                            ...    2
  Ontology               http://purl.obolibrary.org/obo/go/subsets/…    ...    3
  OntologyDocument       None                                            ...    4
```

Depth 1 is the class node itself; depth 2 is the `SubClassOf` axiom that references it;
depth 3 and 4 are the document-level wrapper nodes reachable from that axiom. The
`OntologyDocument` row at the deepest level confirms that `GO:0006281` is referenced
through the ontology's axiom structure rather than being an isolated declaration.

On the full GO release, the same command returns more targeted results — specific
higher-level process terms that structurally depend on DNA repair through the class
hierarchy and existential restrictions.

## Troubleshooting

**`curl` fails with a certificate or network error.** The GO slim download requires
network access to `purl.obolibrary.org`. In restricted environments, download the file
through a browser or alternate tool and save it as `goslim_generic.owl` before
proceeding. The OBO Foundry also mirrors the file at the same PURL.

**`ontopoiesis build goslim_generic.owlxml` fails.** Confirm that the ROBOT conversion
completed and that the input is OWL/XML. The GO slim declares `owl:imports` to the Relations
Ontology (RO) and Basic Formal Ontology (BFO), but `ontopoiesis build` records those
declarations without resolving them.

**Query results include fewer terms than expected.** The projection covers only the GO
slim's directly stated axioms. GO terms whose labels and definitions live in the full GO
release (imported via `owl:imports`) appear in the projection as entity nodes without
annotation assertions. Merge imported content into the source document before building,
or accept that editorial lint rules flag those terms as missing labels.

## Scale note

The queries and lint runs above complete in a few seconds on a 4,670-node, 7,923-edge
projection. Ontopoiesis builds the projection once and reuses it across every command without
re-parsing the source OWL document.

For the full Gene Ontology (`go.owl`), the projection is proportionally larger. The same
commands apply without modification.

## Where To Go Next

The GO slim walkthrough covers the core read-only workflow: build, query, lint, and
impact. From here you can go in several directions:

- **[Tests](tests.md)** — write your own Cypher-based structural assertions and run
  them in CI with `ontopoiesis test`
- **[Diff](diff.md)** — compare GO slim releases semantically to see exactly which
  terms and axioms changed between versions
- **[Migrations](migrations.md)** — build ontology content incrementally from versioned
  Cypher scripts rather than editing a serialized file
- **[Queries reference](queries.md)** — the full set of Cypher patterns for classes,
  properties, individuals, annotations, and more

`goslim_generic.owlxml` fits the OWL 2 EL profile common in biomedical ontologies. The same
workflow applies to OWL/XML ontologies, including ontologies in full OWL 2 DL.
