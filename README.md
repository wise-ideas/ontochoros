# Ontotheke

Ontotheke is the development monorepo for the OWL 2 tooling family. It contains
independently publishable Python packages that evolve together:

- `packages/ontophora`: typed OWL 2 construct records.
- `packages/ontoplexis`: lossless OWL/XML and Cypher-queryable graph mapping.
- `packages/ontopoiesis`: operator CLI and workflows over Ontoplexis projections.

## Why it matters

Building the bundled example ontologies into projections and querying them
surfaces concrete defects. Two, with an honest account of how existing tools fare:

**FoaF is not OWL 2 DL.** Six properties (`aimChatID`, `icqChatID`, `jabberID`,
`mbox_sha1sum`, `msnChatID`, `yahooChatID`) are declared both
`owl:DatatypeProperty` and `owl:InverseFunctionalProperty`. Inverse-functional is
object-property-only, so each IRI is punned across the object and data property
roles — illegal in OWL 2 DL.

- *Here:* `ontopoiesis lint --profile description_logic` reports it (`D104`), and
  one Cypher query pins all six to the exact source cause — a datatype property
  carrying an object-only characteristic.
- *Existing tooling:* a DL reasoner (HermiT via ROBOT) reasons the file without
  complaint, because punning is a syntactic profile violation, not a logical
  inconsistency — a consistency check has nothing to report. `robot report`
  returns 93 findings, none of them this. OWL API *does* catch it, but only
  through the opt-in `OWL2DLProfile` checker, which is not part of the
  load/reason/report path curators normally run.

**SCTO asserts an impossible cardinality.** `has_description` and its inverse
`is_description_of` are declared both `Functional` and `InverseFunctional` — a
one-to-one pairing of concepts and descriptions. But the domain is *SNOMED CT
Concept*, and a SNOMED concept has many descriptions (a fully-specified name plus
synonyms), so `Functional` (at most one) contradicts the intended model.
Separately, 148 of SCTO's 149 own `SCTO_*` terms are minted under a foreign
namespace (`…/obo/ogms.owl#`) with three different ID zero-padding widths.

- *Here:* the bijection is a built-in check (`M107`); the namespace and ID-width
  audit is a two-line Cypher over declared entities.
- *Existing tooling:* both are expressible in SPARQL, but a reasoner and
  `robot report` flag neither out of the box — you must know to write the query.

**HP ships a stale logical definition.** The Human Phenotype Ontology (~767k
projected nodes) has a class defined against `GO_0005623`, which its own file
marks `owl:deprecated true` — "obsolete cell", redundant with `CL:0000000`.

- *Here:* the built-in `P105` check finds it directly, and the same query surface
  scales to GO and Uberon (~1.3M and ~886k nodes) in seconds.
- *Existing tooling:* `robot report` covers deprecated-reference checks too; the
  point is parity on a large OBO ontology from the same queryable projection —
  no bespoke SPARQL, and the graph stays open for follow-up.

The claim is not that these are impossible to find elsewhere. It is that one
queryable projection plus a small set of built-in checks surfaces them in a
normal workflow, with the whole graph left open for ad-hoc follow-up.

## Development

Install every workspace package and its development dependencies:

```bash
uv sync --all-packages --all-groups
```

Run all checks, or the narrow check for one package, from the repository root:

```bash
make check
make check-ontoplexis
make test-ontophora
```

Each package remains separately versioned and publishable. The root `uv.lock`
locks the complete development workspace.

## Releases

Each package versions independently with CalVer (`YYYY.M.patch`) and publishes
to PyPI under its own name. Release tags identify both the package and its
version:

```text
ontophora-v2026.7.0
ontoplexis-v2026.7.10
ontopoiesis-v2026.7.0
```

Pushing a tag runs that package's checks, builds it, and publishes it to PyPI
via the release workflow. The tag version must match the version in the
package's `pyproject.toml`.
