---
title: Work with Other Formats
---

# Work with Other Formats

Ontoplexis reads and writes exactly one document format: OWL/XML, because it
is the OWL 2 structural specification serialized as XML. Everything else —
format conversion, reasoning, profile checking — is a pre- or post-processing
step with the OWLAPI-based tool you already use. This page shows the common
recipes.

## Convert to OWL/XML

With [ROBOT](http://robot.obolibrary.org/), the OBO community's OWLAPI CLI:

```bash
robot convert --input pizza.ttl --format owx --output pizza.owx
```

Or export from Protégé (*File → Save As…* → OWL/XML Syntax), or call OWLAPI
directly from Java/JPype. Then:

```python
from pathlib import Path
from ontoplexis import Ontology

ont = Ontology.from_owlxml(Path("pizza.owx").read_text())
```

## Convert from OWL/XML

The same in reverse — serialize, then convert:

```bash
robot convert --input out.owx --format ttl --output out.ttl
```

```python
Path("out.owx").write_text(ont.to_owlxml())
```

## Reason before loading

If you want inferred axioms in the graph, materialize them first:

```bash
robot reason --reasoner hermit --input pizza.owx \
      --axiom-generators "SubClass ClassAssertion" \
      convert --format owx --output pizza-inferred.owx
```

`robot reason` also fails on inconsistent ontologies, covering the
consistency-check use case; `robot validate-profile` reports OWL 2 profile
membership.

## Why no built-in converter?

Earlier versions bundled OWLAPI as a subprocess bridge. It made every install
carry a JVM dependency and a fat jar for what is a one-time preprocessing
step in most pipelines. The reference implementation still guards the walker
— the round-trip fidelity tests run OWLAPI as a development-only oracle — it
just no longer ships.
