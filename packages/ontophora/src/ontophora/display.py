"""Construct display helpers — canonical field priority for labels and IRIs."""

from __future__ import annotations

from collections.abc import Mapping

from ontophora.constructs.base import BaseConstruct

CONSTRUCT_IRI_FIELDS = ("iri", "ontology_iri", "version_iri")
CONSTRUCT_LABEL_FIELDS = (
    "iri",
    "ontology_iri",
    "node_id",
    "quoted_string",
    "lexical_form",
)

DEFAULT_COMPACT_DISPLAY_LIMIT = 48


def construct_display_iri(construct: BaseConstruct) -> str | None:
    """Return the first non-empty IRI-like string field from a construct."""
    return first_display_field(
        {field_name: getattr(construct, field_name, None) for field_name in CONSTRUCT_IRI_FIELDS},
        CONSTRUCT_IRI_FIELDS,
    )


def construct_display_label(construct: BaseConstruct) -> str | None:
    """Return the first non-empty identifying string field from a construct."""
    return first_display_field(
        {field_name: getattr(construct, field_name, None) for field_name in CONSTRUCT_LABEL_FIELDS},
        CONSTRUCT_LABEL_FIELDS,
    )


def compact_display_label(
    construct: BaseConstruct, *, limit: int = DEFAULT_COMPACT_DISPLAY_LIMIT
) -> str | None:
    """Return a length-limited display label with IRI fragment/path compaction.

    When the label is an IRI (the common fallback), strips the fragment identifier
    or last path component so renderers get `SubClassOf` rather than the full IRI.
    """
    raw = construct_display_label(construct)
    if not raw:
        return None
    return compact_display_value(raw, limit=limit)


def first_display_field(
    props: Mapping[str, object],
    field_names: tuple[str, ...],
) -> str | None:
    for field_name in field_names:
        value = props.get(field_name)
        if isinstance(value, str) and value:
            return value
    return None


def compact_display_value(value: str, *, limit: int = DEFAULT_COMPACT_DISPLAY_LIMIT) -> str:
    trimmed = value.strip('"')
    tail = trimmed.rsplit("#", 1)[-1]
    if tail == trimmed:
        tail = trimmed.rsplit("/", 1)[-1]
    if tail:
        trimmed = tail
    return trimmed if len(trimmed) <= limit else f"{trimmed[: limit - 1]}..."


__all__ = [
    "CONSTRUCT_IRI_FIELDS",
    "CONSTRUCT_LABEL_FIELDS",
    "DEFAULT_COMPACT_DISPLAY_LIMIT",
    "compact_display_label",
    "compact_display_value",
    "construct_display_iri",
    "construct_display_label",
    "first_display_field",
]
