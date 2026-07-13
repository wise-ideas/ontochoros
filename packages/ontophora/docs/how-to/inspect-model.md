---
title: Inspect the supported model
---

# Inspect the supported model

Use the registry when tooling needs to discover the construct catalog rather
than maintaining a parallel list of OWL kinds.

## Get the catalog

```python
from ontophora import construct_types

for model in construct_types:
    print(model.__name__)
```

`construct_types` is the ordered collection of concrete Pydantic models that
the top-level package exports.

## Generate JSON Schema

```python
import json

from ontophora import construct_json_schema

schema = construct_json_schema()
print(json.dumps(schema, indent=2))
```

The schema is a discriminated union on `kind`. Use it to validate or generate
clients for a flat construct payload; use the envelope helpers when the payload
is a package of records.

## Look up construct metadata

The registry module also exposes metadata for applications that need to group
constructs:

```python
from ontophora._registry import construct_metadata_by_kind

metadata = construct_metadata_by_kind()["SubClassOf"]
assert "Axiom" in metadata.abstract_groups
assert metadata.is_blank_node
```

The metadata marks document constructs, blank-node constructs, IRI-identified
constructs, and OWL abstract groups. The [construct catalog](../reference/constructs.md)
describes these groups.
