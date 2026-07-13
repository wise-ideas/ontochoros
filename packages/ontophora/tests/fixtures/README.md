# Fixture Licensing Notes

This directory contains material copied from or derived from W3C OWL 2 documentation and W3C OWL 2 test materials.

Fixture layout:

- `cases/*.xml` contains expected RDF/XML for each test case.
- `cases/*.jsonl` contains construct model record payloads consumed by the OWL bridge's RDF/XML serializer tests.
- Numbered case IDs (`primer_4.*` through `primer_10.*`) are derived from OWL 2 Primer examples and section numbering.
- `spec_*` case IDs are derived from OWL 2 syntax, mapping, and quick-reference documents.
- `complete_test_ontology.*` is derived from OWL 2 Test/Conformance materials.

Primer case categories:

- `primer_4.*`: Classes, Properties, and Individuals
- `primer_5.*`: Advanced Class Relationships
- `primer_6.*`: Advanced Use of Properties
- `primer_7.*`: Advanced Use of Datatypes
- `primer_8.*`: Document Information and Annotations
- `primer_9.*`: OWL 2 DL and OWL 2 Full
- `primer_10.*`: OWL 2 Profiles

Distributed under both the W3C test suite license and the W3C 3-clause BSD license:

- https://www.w3.org/copyright/test-suite-license-2023/
- https://www.w3.org/copyright/3-clause-bsd-license-2008/

Primary source documents:

- https://www.w3.org/TR/owl2-primer/
- https://www.w3.org/TR/owl2-test/
- http://www.w3.org/2007/OWL/testOntology

Status for OWL 2 Primer and OWL 2 Test documents:

- W3C Recommendation, 11 December 2012

See `docs/third-party-notices.md` for the canonical notice text and file mapping.
