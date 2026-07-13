"""OWL 2 construct base model."""

from typing import Any

from pydantic import BaseModel, ConfigDict, field_serializer

from ontophora.reference import ReferenceValue
from ontophora.uid import UID


class BaseConstruct(BaseModel):
    """Base type for all OWL 2 structural constructs in this package."""

    model_config = ConfigDict(extra="forbid")

    uid: UID
    kind: str

    @field_serializer("*", when_used="always", check_fields=False)
    def _serialize_unordered_fields(self, value: Any) -> Any:
        if isinstance(value, set | frozenset):
            return sorted(value, key=_unordered_json_sort_key)
        return value


def _unordered_json_sort_key(value: Any) -> str:
    if isinstance(value, ReferenceValue):
        return f"ref:{value.uid}"
    if isinstance(value, BaseModel):
        return value.model_dump_json()
    return repr(value)


__all__ = ["BaseConstruct"]
