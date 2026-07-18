"""Canonical ordering for members of unordered collections.

Set serialization (``BaseConstruct``) and reference traversal
(``reference_inspection``) must order unordered collections identically, so
both import this one key function.
"""

from __future__ import annotations

from pydantic import BaseModel

from ontophora.reference import ReferenceValue


def unordered_sort_key(value: object) -> str:
    if isinstance(value, ReferenceValue):
        return f"ref:{value.uid}"
    if isinstance(value, BaseModel):
        return value.model_dump_json()
    return repr(value)


__all__ = ["unordered_sort_key"]
