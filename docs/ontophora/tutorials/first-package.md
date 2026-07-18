---
title: Build an ontology package
---

# Build an ontology package

Create a small package that states `Dog` is a subclass of `Animal`, then write
it as JSON. This tutorial requires Python 3.11 or later.

## Install

```bash
pip install ontophora
```

## Create the entity records

Save the following as `animals.py`:

```python
from ontophora import Klass, SubClassOf, records_to_json

animal = Klass(uid="0x1", iri="https://example.org/animals#Animal")
dog = Klass(uid="0x2", iri="https://example.org/animals#Dog")

dog_is_an_animal = SubClassOf(
    uid="0x3",
    sub_class_expression=dog.uid,
    super_class_expression=animal.uid,
)

print(records_to_json([animal, dog, dog_is_an_animal]))
```

Each model supplies its own `kind`; you provide only the fields that identify
or connect the construct. Reference fields accept a bare UID and retain it as a
validated reference value.

## Run it

```bash
python animals.py
```

The program prints one JSON array. Its records use an envelope that separates
each record UID from its construct payload:

```json
[
  {"uid": "0x1", "construct": {"kind": "Class", "iri": "https://example.org/animals#Animal"}},
  {"uid": "0x2", "construct": {"kind": "Class", "iri": "https://example.org/animals#Dog"}},
  {"uid": "0x3", "construct": {"kind": "SubClassOf", "sub_class_expression": {"uid": "0x2"}, "super_class_expression": {"uid": "0x1"}, "axiom_annotations": []}}
]
```

## Read the package back

Replace the final `print` with this code:

```python
from ontophora import records_from_json

text = records_to_json([animal, dog, dog_is_an_animal])
records = records_from_json(text)

assert records[2].kind == "SubClassOf"
assert str(records[2].sub_class_expression) == "0x2"
```

Ontophora validates each payload using `kind` to select its concrete model.
Next, learn how to [read and write JSON](../how-to/json.md) at an application
boundary.
