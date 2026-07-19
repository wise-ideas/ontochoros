"""JSON wire envelope for transporting sets of construct records."""

from __future__ import annotations

import copy
import json
from collections.abc import Sequence
from typing import cast

from pydantic.json_schema import JsonSchemaMode

from ontophora._registry import construct_json_schema, construct_types
from ontophora.constructs.base import BaseConstruct
from ontophora.records import coerce_construct


class EnvelopeError(ValueError):
    """Raised when envelope JSON does not match the expected record shape."""


def records_from_json(text: str) -> list[BaseConstruct]:
    """Decode envelope JSON into construct records."""
    decoded = json.loads(text)
    if not isinstance(decoded, list):
        raise EnvelopeError("Envelope payload must decode to a JSON array of construct records")
    records: list[BaseConstruct] = []
    for index, item in enumerate(decoded, start=1):
        records.append(coerce_construct(_validate_record(item, index=index)))
    return records


def records_to_json(records: Sequence[BaseConstruct]) -> str:
    """Encode construct records into the JSON envelope."""
    for record in records:
        if record.__class__ not in construct_types:
            raise EnvelopeError(f"Cannot encode unregistered construct kind {record.kind!r}")
    return json.dumps([_record_payload(record) for record in records])


def records_from_jsonl(text: str) -> list[BaseConstruct]:
    """Decode JSONL (one envelope record per line) into construct records.

    Blank lines are skipped, so trailing newlines and spacing between records
    are harmless.
    """
    records: list[BaseConstruct] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            decoded = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EnvelopeError(f"Envelope line {line_number} is not valid JSON: {exc}") from exc
        records.append(coerce_construct(_validate_record(decoded, index=line_number)))
    return records


def records_to_jsonl(records: Sequence[BaseConstruct]) -> str:
    """Encode construct records as JSONL, one envelope record per line."""
    for record in records:
        if record.__class__ not in construct_types:
            raise EnvelopeError(f"Cannot encode unregistered construct kind {record.kind!r}")
    return "".join(json.dumps(_record_payload(record)) + "\n" for record in records)


def envelope_json_schema(*, mode: JsonSchemaMode = "validation") -> dict[str, object]:
    """Return the JSON Schema for the envelope: an array of ``{uid, construct}``.

    The construct payloads reuse the discriminated construct union, with each
    construct's ``uid`` field removed — the envelope hoists ``uid`` to the
    record level, so it must not appear inside ``construct``.
    """
    union = copy.deepcopy(construct_json_schema(mode=mode))
    definitions = union.pop("$defs", {})
    if isinstance(definitions, dict):
        for definition_obj in definitions.values():
            if not isinstance(definition_obj, dict):
                continue
            definition = cast(dict[str, object], definition_obj)
            properties = definition.get("properties")
            if isinstance(properties, dict):
                properties.pop("uid", None)
            required = definition.get("required")
            if isinstance(required, list):
                definition["required"] = [name for name in required if name != "uid"]
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "uid": {"type": "string"},
                "construct": union,
            },
            "required": ["uid", "construct"],
            "additionalProperties": False,
        },
        "$defs": definitions,
    }


def _validate_record(item: object, *, index: int) -> dict[str, object]:
    if not isinstance(item, dict):
        raise EnvelopeError(f"Envelope record {index} must be a JSON object")
    payload = cast(dict[str, object], item)
    if "uid" not in payload:
        raise EnvelopeError(f"Envelope record {index} is missing required field 'uid'")
    unknown_fields = sorted(set(payload) - {"uid", "construct"})
    if unknown_fields:
        raise EnvelopeError(
            f"Envelope record {index} has unexpected fields: {', '.join(unknown_fields)}"
        )
    construct_payload = payload.get("construct")
    if not isinstance(construct_payload, dict):
        raise EnvelopeError(f"Envelope record {index} field 'construct' must be a JSON object")
    if "uid" in construct_payload:
        raise EnvelopeError(f"Envelope record {index} construct must not contain field 'uid'")
    return {"uid": payload["uid"], **cast(dict[str, object], construct_payload)}


def _record_payload(record: BaseConstruct) -> dict[str, object]:
    construct_payload = record.model_dump(mode="json", by_alias=True)
    uid = construct_payload.pop("uid")
    return {
        "uid": str(uid),
        "construct": construct_payload,
    }


__all__ = [
    "EnvelopeError",
    "envelope_json_schema",
    "records_from_json",
    "records_from_jsonl",
    "records_to_json",
    "records_to_jsonl",
]
