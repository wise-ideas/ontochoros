"""Inspect validated constructs for embedded references."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from functools import singledispatch
from typing import Any, Final

from pydantic import BaseModel

from ontophora._field_encoding import (
    CollectionKind,
    field_shape,
)
from ontophora._field_encoding import (
    field_collection_kind as derive_field_collection_kind,
)
from ontophora.constructs.base import BaseConstruct
from ontophora.reference import (
    ExpectedKind,
    ReferenceValue,
    expected_kind_to_tuple,
)


@dataclass(frozen=True, slots=True)
class ReferenceEntry:
    edge_key: str
    endpoint_order: int | None
    target_uid: str
    expected_kinds: tuple[str, ...]


ENDPOINT_ORDER_ORIGIN: Final[int] = 1


def iter_construct_references(
    value: BaseModel,
    *,
    path: str | None = None,
) -> Iterable[ReferenceEntry]:
    """Yield direct reference entries embedded in one validated construct."""
    root_path = path or value.__class__.__name__
    yield from _iter_reference_values(
        value,
        expected_kind=None,
        path=root_path,
        endpoint_order=None,
    )


def field_collection_kind(annotation: object) -> CollectionKind:
    """Classify a field annotation as ordered, unordered, or scalar."""
    return derive_field_collection_kind(annotation)


@singledispatch
def _iter_reference_values(
    value: Any,
    *,
    expected_kind: ExpectedKind,
    path: str,
    endpoint_order: int | None,
) -> Iterable[ReferenceEntry]:
    return ()


@_iter_reference_values.register(ReferenceValue)
def _iter_reference_values_reference(
    value: ReferenceValue,
    *,
    expected_kind: ExpectedKind,
    path: str,
    endpoint_order: int | None,
) -> Iterable[ReferenceEntry]:
    yield ReferenceEntry(
        edge_key=_edge_key_from_path(path),
        endpoint_order=endpoint_order,
        target_uid=str(value.uid),
        expected_kinds=expected_kind_to_tuple(expected_kind),
    )


@_iter_reference_values.register(BaseModel)
def _iter_reference_values_model(
    value: BaseModel,
    *,
    expected_kind: ExpectedKind,
    path: str,
    endpoint_order: int | None,
) -> Iterable[ReferenceEntry]:
    for field_name, field in value.__class__.model_fields.items():
        expected_kind = _expected_kind_for_field(value, field_name, field)
        yield from _iter_reference_values(
            getattr(value, field_name),
            expected_kind=expected_kind,
            path=f"{path}.{field_name}" if path else field_name,
            endpoint_order=None,
        )


@_iter_reference_values.register(list)
@_iter_reference_values.register(tuple)
def _iter_reference_values_ordered(
    value: list[Any] | tuple[Any, ...],
    *,
    expected_kind: ExpectedKind,
    path: str,
    endpoint_order: int | None,
) -> Iterable[ReferenceEntry]:
    for index, item in enumerate(value):
        yield from _iter_reference_values(
            item,
            expected_kind=expected_kind,
            path=f"{path}[{index}]",
            endpoint_order=ENDPOINT_ORDER_ORIGIN + index,
        )


@_iter_reference_values.register(set)
@_iter_reference_values.register(frozenset)
def _iter_reference_values_unordered(
    value: set[Any] | frozenset[Any],
    *,
    expected_kind: ExpectedKind,
    path: str,
    endpoint_order: int | None,
) -> Iterable[ReferenceEntry]:
    for index, item in enumerate(sorted(value, key=_unordered_value_sort_key)):
        yield from _iter_reference_values(
            item,
            expected_kind=expected_kind,
            path=f"{path}{{{index}}}",
            endpoint_order=None,
        )


@_iter_reference_values.register(dict)
def _iter_reference_values_dict(
    value: dict[Any, Any],
    *,
    expected_kind: ExpectedKind,
    path: str,
    endpoint_order: int | None,
) -> Iterable[ReferenceEntry]:
    for key, item in value.items():
        yield from _iter_reference_values(
            item,
            expected_kind=expected_kind,
            path=f"{path}[{key!r}]",
            endpoint_order=None,
        )


def _expected_kind_for_field(model: BaseModel, field_name: str, field: Any) -> ExpectedKind:
    if isinstance(model, BaseConstruct):
        expected_kinds = field_shape(field).expected_kinds
        if expected_kinds:
            return expected_kind_to_tuple(expected_kinds)
    kinds: list[str] = []
    for item in getattr(field, "metadata", ()):
        raw = getattr(item, "expected_kind", None)
        values = raw if isinstance(raw, tuple) else (raw,)
        for value in values:
            if isinstance(value, str) and value not in kinds:
                kinds.append(value)
    return expected_kind_to_tuple(tuple(kinds)) or None


def _edge_key_from_path(path: str) -> str:
    field_path = path.rsplit(".", 1)[-1]
    return field_path.split("[", 1)[0].split("{", 1)[0]


@singledispatch
def _unordered_value_sort_key(value: Any) -> str:
    return repr(value)


@_unordered_value_sort_key.register(ReferenceValue)
def _unordered_value_sort_key_reference(value: ReferenceValue) -> str:
    return str(value.uid)


@_unordered_value_sort_key.register(BaseModel)
def _unordered_value_sort_key_model(value: BaseModel) -> str:
    return value.model_dump_json()


__all__ = [
    "CollectionKind",
    "ENDPOINT_ORDER_ORIGIN",
    "ReferenceEntry",
    "field_collection_kind",
    "iter_construct_references",
]
