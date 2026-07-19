---
title: Public API
---

# Public API

Import these names from `ontophora`.

| Name | Description |
| --- | --- |
| `BaseConstruct` | Base Pydantic model. Every construct has `uid` and `kind`. |
| `UID` | Validated hexadecimal construct identifier annotation. |
| `coerce_construct(data)` | Returns `data` if it is a construct; otherwise validates a flat construct dictionary selected by `kind`. |
| `construct_types` | Ordered tuple of every registered concrete construct model. |
| `construct_json_schema(mode="validation", kind=None)` | Returns the JSON Schema for the discriminated construct union, or for the one construct named by `kind`. |
| `envelope_json_schema(mode="validation")` | Returns the JSON Schema for the package envelope (an array of `{uid, construct}` records). |
| `records_from_json(text)` | Decodes a JSON package envelope into construct records. |
| `records_to_json(records)` | Encodes construct records as a JSON package envelope. |
| `records_from_jsonl(text)` | Decodes JSONL (one envelope record per line) into construct records. |
| `records_to_jsonl(records)` | Encodes construct records as JSONL, one envelope record per line. |
| `EnvelopeError` | Raised when a JSON package has the wrong outer record shape. |

Every model in the [construct catalog](constructs.md) is also imported from
`ontophora`. For example:

```python
from ontophora import Klass, ObjectProperty, SubClassOf
```

## Supporting modules

These names are available from their modules for applications that need lower
level control.

| Import | Description |
| --- | --- |
| `ontophora._registry.construct_metadata` | Ordered metadata for registered constructs. |
| `ontophora._registry.construct_metadata_by_kind()` | Metadata indexed by fixed `kind`. |
| `ontophora._registry.construct_support_manifest()` | JSON-serializable catalog with fields, groups, and flags. |
| `ontophora._registry.is_kind_compatible(...)` | Tests a concrete kind against exact or abstract expected kinds. |
| `ontophora.fingerprint.fingerprint_construct(...)` | Produces one content-based SHA-256 digest. |
| `ontophora.fingerprint.fingerprint_constructs(...)` | Produces content-based digests for a record sequence. |
| `ontophora.reference.Reference` | Field annotation for a UID reference. |
| `ontophora.reference.ReferenceValue` | Runtime value for a validated reference. |
