"""Lexically validated OWL 2 IRI syntax values."""

import re
from typing import Annotated, TypeAlias

from pydantic import AfterValidator, StringConstraints

# Character classes transcribed from the SPARQL 1.1 grammar
# (https://www.w3.org/TR/sparql11-query/#rPN_CHARS_BASE), which OWL 2
# Structural Specification section 2.1 references for abbreviated IRIs,
# prefix names, and node IDs. Shared with ontophora.constructs.types so the
# abbreviated-IRI grammar and the PrefixDeclaration grammar cannot drift.
PN_CHARS_BASE = "A-Za-zÀ-ÖØ-öø-˿Ͱ-ͽͿ-῿‌-‍⁰-↏Ⰰ-⿯、-퟿豈-﷏ﷰ-�\U00010000-\U000effff"
PN_CHARS_U = PN_CHARS_BASE + "_"
PN_CHARS = PN_CHARS_U + "\\-0-9·̀-ͯ‿-⁀"
PN_PREFIX = rf"[{PN_CHARS_BASE}](?:[{PN_CHARS}.]*[{PN_CHARS}])?"

_IRI_FORBIDDEN_CHARS = set(' <>"{}|^`\\')
_FULL_IRI_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:[^\s<>\"{}|^`\\]+$")
_PREFIX_NAME_BODY_RE = re.compile(rf"(?:{PN_PREFIX})?")
# SPARQL PN_LOCAL without the PLX escape forms (percent- and backslash-escapes),
# which this package does not support anywhere.
_PN_LOCAL_RE = re.compile(rf"[{PN_CHARS_U}0-9:](?:[{PN_CHARS}.:]*[{PN_CHARS}:])?")


def _unwrap_bracketed_full_iri(value: str) -> str:
    if value.startswith("<") or value.endswith(">"):
        if not (value.startswith("<") and value.endswith(">")):
            raise ValueError("Input should be a valid full IRI")
        return value[1:-1]
    return value


def _require_no_forbidden_iri_chars(value: str) -> str:
    if any(char in _IRI_FORBIDDEN_CHARS for char in value):
        raise ValueError("Input should be a valid IRI")
    return value


def _require_full_iri_shape(value: str) -> str:
    if not _FULL_IRI_RE.fullmatch(value):
        raise ValueError("Input should be a valid full IRI")
    return value


def _require_abbreviated_separator(value: str) -> str:
    prefix_name, separator, local_name = value.partition(":")
    if separator != ":" or not local_name:
        raise ValueError("Input should be a valid abbreviated IRI")
    return value


def _require_abbreviated_prefix_name(value: str) -> str:
    prefix_name, _, _ = value.partition(":")
    if not _PREFIX_NAME_BODY_RE.fullmatch(prefix_name):
        raise ValueError("Input should be a valid abbreviated IRI")
    return value


def _require_abbreviated_local_name(value: str) -> str:
    _, _, local_name = value.partition(":")
    if not _PN_LOCAL_RE.fullmatch(local_name):
        raise ValueError("Input should be a valid abbreviated IRI")
    return value


AbbreviatedIRI = Annotated[
    str,
    StringConstraints(min_length=2),
    AfterValidator(_require_abbreviated_separator),
    AfterValidator(_require_abbreviated_prefix_name),
    AfterValidator(_require_abbreviated_local_name),
]

FullIRI = Annotated[
    str,
    StringConstraints(min_length=1),
    AfterValidator(_unwrap_bracketed_full_iri),
    AfterValidator(_require_no_forbidden_iri_chars),
    AfterValidator(_require_full_iri_shape),
]

IRI: TypeAlias = FullIRI | AbbreviatedIRI
