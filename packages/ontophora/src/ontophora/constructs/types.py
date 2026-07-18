# ruff: noqa: F401
import re
from typing import Annotated, TypeAlias

from language_tags import tags
from pydantic import AfterValidator, NonNegativeInt, StringConstraints

from ontophora.constructs.iri import (
    IRI,
    PN_CHARS,
    PN_CHARS_U,
    PN_PREFIX,
    AbbreviatedIRI,
    FullIRI,
)
from ontophora.uid import UID

_BLANK_NODE_LABEL = rf"_:[{PN_CHARS_U}0-9](?:[{PN_CHARS}.]*[{PN_CHARS}])?"


def _strip_leading_at(value: str) -> str:
    return value[1:]


def _validate_bcp47_tag(value: str) -> str:
    if not tags.check(value):
        raise ValueError(f"Invalid BCP 47 language tag: @{value}")
    return value


def _restore_leading_at(value: str) -> str:
    return f"@{value}"


LanguageTag = Annotated[
    str,
    StringConstraints(pattern=r"^@.*$"),
    AfterValidator(_strip_leading_at),
    AfterValidator(_validate_bcp47_tag),
    AfterValidator(_restore_leading_at),
]

_BLANK_NODE_LABEL_RE = re.compile(_BLANK_NODE_LABEL)


def _validate_node_id(value: str) -> str:
    if _BLANK_NODE_LABEL_RE.fullmatch(value) is None:
        raise ValueError(f"Invalid node ID: {value}")
    return value


NodeID = Annotated[
    str,
    AfterValidator(_validate_node_id),
]

NonNegativeInteger: TypeAlias = NonNegativeInt

_PREFIX_NAME_RE = re.compile(rf"(?:{PN_PREFIX})?:")


def _validate_prefix_name(value: str) -> str:
    if _PREFIX_NAME_RE.fullmatch(value) is None:
        raise ValueError(f"Invalid prefix name: {value}")
    return value


PrefixName = Annotated[
    str,
    AfterValidator(_validate_prefix_name),
]

_QUOTED_STRING_PATTERN = re.compile(
    r"""
        ^"
        (?:
        [^"\\]
        | \\\"
        | \\\\
        )*
        "$
    """,
    re.X,
)
QuotedString = Annotated[
    str,
    StringConstraints(pattern=_QUOTED_STRING_PATTERN),
]

__all__ = [
    "AbbreviatedIRI",
    "FullIRI",
    "IRI",
    "LanguageTag",
    "NodeID",
    "NonNegativeInteger",
    "PrefixName",
    "QuotedString",
    "UID",
]
