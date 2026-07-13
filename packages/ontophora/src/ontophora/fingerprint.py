"""Canonical form and fingerprinting for construct records."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from functools import singledispatch

from pydantic import BaseModel

from ontophora.constructs.base import BaseConstruct
from ontophora.reference import ReferenceValue


@dataclass(slots=True)
class _FingerprintContext:
    cache: dict[str, str]
    in_progress: frozenset[str]

    @classmethod
    def new(cls) -> _FingerprintContext:
        return cls(cache={}, in_progress=frozenset())


def fingerprint_construct(
    record: BaseConstruct,
    record_index: dict[str, BaseConstruct],
) -> str:
    """Return a stable SHA-256 hex digest for a construct, resolving references by content."""
    return _fingerprint_construct(record, record_index, _FingerprintContext.new())


def fingerprint_constructs(
    records: Sequence[BaseConstruct],
    record_index: dict[str, BaseConstruct],
) -> dict[str, str]:
    """Return a fingerprint for each record, sharing one cache across all."""
    ctx = _FingerprintContext.new()
    return {
        str(record.uid): _fingerprint_construct(record, record_index, ctx) for record in records
    }


def _fingerprint_construct(
    record: BaseConstruct,
    record_index: dict[str, BaseConstruct],
    ctx: _FingerprintContext,
) -> str:
    uid = str(record.uid)
    if uid in ctx.cache:
        return ctx.cache[uid]
    if uid in ctx.in_progress:
        payload = json.dumps({"$cycle": uid}, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    inner_ctx = _FingerprintContext(cache=ctx.cache, in_progress=ctx.in_progress | {uid})
    # Exclude uid: fingerprints are content-addressed, not identity-addressed.
    fields = sorted(k for k in record.__class__.model_fields if k != "uid")
    normalized = {
        k: _canonical_value_form(getattr(record, k), record_index, inner_ctx) for k in fields
    }
    payload = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    ctx.cache[uid] = digest
    return digest


@singledispatch
def _canonical_value_form(
    value: object,
    record_index: dict[str, BaseConstruct],
    ctx: _FingerprintContext,
) -> object:
    return value


@_canonical_value_form.register(ReferenceValue)
def _normalize_reference_value(
    value: ReferenceValue,
    record_index: dict[str, BaseConstruct],
    ctx: _FingerprintContext,
) -> object:
    ref_uid = str(value.uid)
    if ref_uid in ctx.in_progress:
        return {"$cycle": ref_uid}
    if ref_uid in record_index:
        return {"$ref": _fingerprint_construct(record_index[ref_uid], record_index, ctx)}
    return {"$ref": ref_uid}


@_canonical_value_form.register(BaseModel)
def _normalize_model_value(
    value: BaseModel,
    record_index: dict[str, BaseConstruct],
    ctx: _FingerprintContext,
) -> object:
    return {
        key: _canonical_value_form(getattr(value, key), record_index, ctx)
        for key in sorted(value.__class__.model_fields)
    }


@_canonical_value_form.register(list)
def _normalize_list_value(
    value: list[object],
    record_index: dict[str, BaseConstruct],
    ctx: _FingerprintContext,
) -> object:
    return [_canonical_value_form(item, record_index, ctx) for item in value]


@_canonical_value_form.register(set)
@_canonical_value_form.register(frozenset)
def _normalize_unordered_value(
    value: set[object] | frozenset[object],
    record_index: dict[str, BaseConstruct],
    ctx: _FingerprintContext,
) -> object:
    normalized_items = [_canonical_value_form(item, record_index, ctx) for item in value]
    return sorted(normalized_items, key=lambda item: json.dumps(item, sort_keys=True))


@_canonical_value_form.register(dict)
def _normalize_dict_value(
    value: dict[object, object],
    record_index: dict[str, BaseConstruct],
    ctx: _FingerprintContext,
) -> object:
    return {key: _canonical_value_form(value[key], record_index, ctx) for key in sorted(value)}
