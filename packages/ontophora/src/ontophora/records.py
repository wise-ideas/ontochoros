"""Construct record coercion."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeAlias, cast

from ontophora._registry import construct
from ontophora.constructs.base import BaseConstruct

ConstructRecordPayload: TypeAlias = dict[str, object]
ConstructRecordInput: TypeAlias = BaseConstruct | ConstructRecordPayload


def coerce_construct(data: object) -> BaseConstruct:
    """Parse a construct object or flat record-shaped dict into a ``BaseConstruct``."""
    if isinstance(data, BaseConstruct):
        return data
    return construct(cast(dict[str, object], data))


def coerce_construct_records(
    items: Sequence[ConstructRecordInput],
) -> list[BaseConstruct]:
    """Validate record-shaped construct model items into construct records."""
    return [coerce_construct(item) for item in items]


__all__ = [
    "coerce_construct",
    "coerce_construct_records",
]
