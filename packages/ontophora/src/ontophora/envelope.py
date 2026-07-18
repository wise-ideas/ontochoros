"""JSON wire envelope for transporting sets of construct records."""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import cast

from ontophora._registry import construct_types
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
    "records_from_json",
    "records_to_json",
]
