---
title: JSON package format
---

# JSON package format

`records_to_json` and `records_from_json` exchange a JSON array of record
construct payload.

```json
[
  {
    "uid": "0x1",
    "construct": {
      "kind": "Class",
      "iri": "https://example.org/animals#Animal"
    }
  },
  {
    "uid": "0x2",
    "construct": {
      "kind": "SubClassOf",
      "sub_class_expression": {"uid": "0x1"},
      "super_class_expression": {"uid": "0x1"},
      "axiom_annotations": []
    }
  }
]
```

## Envelope rules

| Location | Required value |
| --- | --- |
| Root | A JSON array. |
| Record | A JSON object with `uid` and `construct`. |
| `uid` | A hexadecimal string beginning with `0x` or `0X`; validation normalizes its case and leading zeroes. |
| `construct` | A JSON object with a registered `kind` and fields valid for that kind. |
| Reference field | A `{"uid": "0x..."}` object. Input also accepts a bare UID string. |

The `uid` at the envelope level becomes the model's `uid` when the package is
decoded. The construct payload must not contain its own `uid`.

References are structural links only. Decoding validates their UID syntax but
does not require that the array contains a record with that UID or that the
target record has the expected kind.

## JSONL variant

`records_to_jsonl` and `records_from_jsonl` exchange the same records as
JSONL: one envelope record object per line, with blank lines ignored on
decode. Record shapes and validation match the array format exactly; only the
outer framing differs.

## Machine-readable schema

`envelope_json_schema()` returns a JSON Schema describing the array format:
each record requires `uid` and `construct`, and the construct payloads reuse
the discriminated construct union with the record-level `uid` removed. Use it
to validate envelopes from non-Python producers.
