---
title: Read and write JSON
---

# Read and write JSON

Use the envelope helpers when a process needs to exchange a collection of
construct records.

## Decode a package

Pass the complete JSON document to `records_from_json`:

```python
from pathlib import Path

from ontophora import records_from_json

records = records_from_json(Path("ontology.json").read_text())
by_uid = {str(record.uid): record for record in records}
```

The helper requires a JSON array. Every item must contain a top-level `uid` and
a `construct` object with a recognized `kind`. Invalid JSON raises the standard
`json.JSONDecodeError`; an invalid envelope raises `EnvelopeError`; invalid
construct fields raise Pydantic validation errors.

## Encode records

Pass validated construct models to `records_to_json`:

```python
from pathlib import Path

from ontophora import records_to_json

Path("ontology.json").write_text(records_to_json(records))
```

The helper emits references as `{"uid": "0x..."}` and sorts unordered model
fields for deterministic model serialization. See the exact
[JSON package format](../reference/json-format.md).

## Validate one record-shaped payload

If an API sends one flat construct object rather than an envelope, use
`coerce_construct`:

```python
from ontophora import coerce_construct

record = coerce_construct(
    {
        "uid": "0xa",
        "kind": "Class",
        "iri": "https://example.org/animals#Animal",
    }
)
```

This is useful at a boundary that accepts either an already validated model or
a JSON-decoded dictionary.
