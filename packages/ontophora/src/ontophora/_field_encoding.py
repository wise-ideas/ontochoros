"""Internal construct-field encoding metadata shared across layers."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum, auto
from types import UnionType
from typing import Annotated, Any, Union, get_args, get_origin

from pydantic.fields import FieldInfo


class CollectionKind(Enum):
    ORDERED = auto()
    UNORDERED_SET = auto()
    UNORDERED_FROZENSET = auto()
    SCALAR = auto()


@dataclass(frozen=True, slots=True)
class FieldShape:
    collection: CollectionKind
    expected_kinds: tuple[str, ...]


def field_collection_kind(annotation: object) -> CollectionKind:
    return _analyze_annotation(annotation, metadata=()).collection


def extract_expected_kinds(annotation: object) -> tuple[str, ...]:
    return _analyze_annotation(annotation, metadata=()).expected_kinds


def field_shape(field: FieldInfo) -> FieldShape:
    return _analyze_annotation(field.annotation, metadata=field.metadata)


def _analyze_annotation(annotation: object, *, metadata: Sequence[object]) -> FieldShape:
    metadata_expected = metadata_expected_kinds(metadata)
    origin = get_origin(annotation)

    if origin is Annotated:
        value_type, *annotated_metadata = get_args(annotation)
        annotated_expected = metadata_expected_kinds(annotated_metadata)
        expected = _merge_kinds(metadata_expected, annotated_expected)
        if expected:
            return FieldShape(collection=CollectionKind.SCALAR, expected_kinds=expected)
        return _analyze_annotation(value_type, metadata=())

    if metadata_expected:
        return FieldShape(collection=CollectionKind.SCALAR, expected_kinds=metadata_expected)

    if origin in (list, tuple):
        child = _merge_child_encodings(get_args(annotation))
        return FieldShape(collection=CollectionKind.ORDERED, expected_kinds=child.expected_kinds)
    if origin is set:
        child = _merge_child_encodings(get_args(annotation))
        return FieldShape(
            collection=CollectionKind.UNORDERED_SET, expected_kinds=child.expected_kinds
        )
    if origin is frozenset:
        child = _merge_child_encodings(get_args(annotation))
        return FieldShape(
            collection=CollectionKind.UNORDERED_FROZENSET,
            expected_kinds=child.expected_kinds,
        )
    if origin is dict:
        args = get_args(annotation)
        child_args = args[1:] if len(args) == 2 else ()
        child = _merge_child_encodings(child_args)
        return FieldShape(collection=CollectionKind.SCALAR, expected_kinds=child.expected_kinds)
    if origin in (UnionType, Union):
        return _merge_child_encodings(arg for arg in get_args(annotation) if arg is not type(None))

    return FieldShape(collection=CollectionKind.SCALAR, expected_kinds=())


def _merge_child_encodings(annotations: Sequence[object] | Any) -> FieldShape:
    expected_kinds: list[str] = []
    collections: set[CollectionKind] = set()
    for annotation in annotations:
        analyzed = _analyze_annotation(annotation, metadata=())
        collections.add(analyzed.collection)
        for kind in analyzed.expected_kinds:
            if kind not in expected_kinds:
                expected_kinds.append(kind)
    collection = CollectionKind.SCALAR
    non_scalar = {kind for kind in collections if kind is not CollectionKind.SCALAR}
    if len(non_scalar) == 1:
        collection = next(iter(non_scalar))
    return FieldShape(collection=collection, expected_kinds=tuple(expected_kinds))


def metadata_expected_kinds(metadata: Sequence[object]) -> tuple[str, ...]:
    expected: list[str] = []
    for item in metadata:
        raw = getattr(item, "expected_kind", None)
        if raw is None:
            continue
        values = raw if isinstance(raw, tuple) else (raw,)
        for value in values:
            if isinstance(value, str) and value not in expected:
                expected.append(value)
    return tuple(expected)


def _merge_kinds(*values: tuple[str, ...]) -> tuple[str, ...]:
    merged: list[str] = []
    for value in values:
        for kind in value:
            if kind not in merged:
                merged.append(kind)
    return tuple(merged)
