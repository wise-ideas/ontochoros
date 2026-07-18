"""OWL 2 construct base model."""

import html
from typing import Any

from pydantic import BaseModel, ConfigDict, field_serializer

from ontophora._canonical import unordered_sort_key
from ontophora.display import (
    compact_display_label,
    construct_display_iri,
    construct_display_label,
)
from ontophora.uid import UID


class BaseConstruct(BaseModel):
    """Base type for all OWL 2 structural constructs in this package."""

    model_config = ConfigDict(extra="forbid")

    uid: UID
    kind: str

    @field_serializer("*", when_used="always", check_fields=False)
    def _serialize_unordered_fields(self, value: Any) -> Any:
        if isinstance(value, set | frozenset):
            return sorted(value, key=unordered_sort_key)
        return value

    def display_iri(self) -> str | None:
        """Return the first non-empty IRI-like string field, if any."""
        return construct_display_iri(self)

    def display_label(self) -> str | None:
        """Return the first non-empty identifying string field, if any."""
        return construct_display_label(self)

    def compact_label(self, *, limit: int | None = None) -> str | None:
        """Return a length-limited label with IRI fragment/path compaction."""
        if limit is None:
            return compact_display_label(self)
        return compact_display_label(self, limit=limit)

    def __rich__(self) -> str:
        # Duck-typed rich protocol: picked up by rich when installed, no
        # dependency taken here.
        label = self.compact_label()
        rendered = f"[bold]{self.kind}[/]"
        if label and label != self.kind:
            rendered += f" {label}"
        return f"{rendered} [dim]{self.uid}[/]"

    def _repr_html_(self) -> str:
        label = self.compact_label()
        heading = html.escape(
            self.kind if not label or label == self.kind else f"{self.kind} {label}"
        )
        rows = "".join(
            "<tr>"
            f"<td style='padding:0 8px 0 0;color:#888'>{html.escape(name)}</td>"
            f"<td>{html.escape(_display_field_value(getattr(self, name)))}</td>"
            "</tr>"
            for name in self.__class__.model_fields
            if name != "kind"
        )
        return (
            f"<div><strong>{heading}</strong>"
            f"<table style='border-collapse:collapse;font-size:90%'>{rows}</table></div>"
        )


def _display_field_value(value: Any) -> str:
    if isinstance(value, set | frozenset):
        return ", ".join(str(item) for item in sorted(value, key=unordered_sort_key))
    if isinstance(value, list | tuple):
        return ", ".join(str(item) for item in value)
    return str(value)


__all__ = ["BaseConstruct"]
