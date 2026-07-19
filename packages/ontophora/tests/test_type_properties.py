"""Property-based tests for the lexical value types.

The IRI, node-ID, and UID grammars are defined by regular expressions
transcribed from the SPARQL 1.1 grammar. Generating inputs *from those same
expressions* proves the validator chains stay coherent with the grammar: no
validator in a chain rejects a value the grammar admits, and normalization
behaves as documented. (Acceptance of curated spec examples is pinned in
test_iri_types.py; these tests cover the space between the examples.)

The SPARQL name grammars are built here from the source character-class
strings rather than via ``st.from_regex``: Hypothesis pays a one-off cost of
tens of seconds per process to compile each regex whose classes span the
astral planes, which once dominated the whole suite's runtime. Each composed
value is asserted against the grammar regex before it is used, so generation
cannot drift from the grammar it claims to sample.
"""

from __future__ import annotations

import re

from hypothesis import given
from hypothesis import strategies as st
from pydantic import TypeAdapter

from ontophora.constructs.iri import (
    _FULL_IRI_RE,
    _PN_LOCAL_RE,
    _PREFIX_NAME_BODY_RE,
    PN_CHARS,
    PN_CHARS_BASE,
    PN_CHARS_U,
    AbbreviatedIRI,
    FullIRI,
)
from ontophora.constructs.types import _BLANK_NODE_LABEL_RE, NodeID, PrefixName
from ontophora.uid import UID

_FULL_IRI = TypeAdapter(FullIRI)
_ABBREVIATED_IRI = TypeAdapter(AbbreviatedIRI)
_NODE_ID = TypeAdapter(NodeID)
_PREFIX_NAME = TypeAdapter(PrefixName)
_UID = TypeAdapter(UID)


def _class_chars(char_class: str) -> st.SearchStrategy[str]:
    """Uniform codepoints over a regex character-class body, O(1) to build."""
    intervals: list[tuple[int, int]] = []
    i = 0
    while i < len(char_class):
        ch = char_class[i]
        if ch == "\\":
            ch = char_class[i + 1]
            i += 2
        else:
            i += 1
        if char_class[i : i + 1] == "-" and i + 1 < len(char_class):
            intervals.append((ord(ch), ord(char_class[i + 1])))
            i += 2
        else:
            intervals.append((ord(ch), ord(ch)))
    total = sum(hi - lo + 1 for lo, hi in intervals)

    def pick(index: int) -> str:
        for lo, hi in intervals:
            span = hi - lo + 1
            if index < span:
                return chr(lo + index)
            index -= span
        raise AssertionError("index out of range")

    return st.integers(min_value=0, max_value=total - 1).map(pick)


def _name(
    first: st.SearchStrategy[str],
    middle: st.SearchStrategy[str],
    last: st.SearchStrategy[str],
) -> st.SearchStrategy[str]:
    """``[first](?:[middle]*[last])?`` — the shared SPARQL name shape."""
    tail = st.one_of(
        st.just(""),
        st.tuples(st.text(middle, max_size=8), last).map("".join),
    )
    return st.tuples(first, tail).map("".join)


_PREFIX_BODIES = st.one_of(
    st.just(""),
    _name(_class_chars(PN_CHARS_BASE), _class_chars(PN_CHARS + "."), _class_chars(PN_CHARS)),
)
_PN_LOCALS = _name(
    _class_chars(PN_CHARS_U + "0-9:"),
    _class_chars(PN_CHARS + ".:"),
    _class_chars(PN_CHARS + ":"),
)
_NODE_IDS = _name(
    _class_chars(PN_CHARS_U + "0-9"),
    _class_chars(PN_CHARS + "."),
    _class_chars(PN_CHARS),
).map("_:".__add__)


def _grammatical(pattern: re.Pattern[str], value: str) -> str:
    # The guard that ties composed values back to the grammar: a generator
    # bug produces a loud failure here, never a false accusation below.
    assert pattern.fullmatch(value), f"generator drifted from the grammar: {value!r}"
    return value


@given(st.from_regex(_FULL_IRI_RE, fullmatch=True))
def test_every_grammatical_full_iri_is_accepted_verbatim(value: str) -> None:
    assert _FULL_IRI.validate_python(value) == value


@given(st.from_regex(_FULL_IRI_RE, fullmatch=True))
def test_bracketed_full_iris_unwrap_to_the_bare_form(value: str) -> None:
    assert _FULL_IRI.validate_python(f"<{value}>") == value


@given(_PREFIX_BODIES, _PN_LOCALS)
def test_every_grammatical_curie_is_accepted_by_the_abbreviated_iri_chain(
    prefix: str, local: str
) -> None:
    # AbbreviatedIRI is validated by three chained validators; composing the
    # grammar's own parts must never trip any link in the chain.
    value = f"{_grammatical(_PREFIX_NAME_BODY_RE, prefix)}:{_grammatical(_PN_LOCAL_RE, local)}"
    assert _ABBREVIATED_IRI.validate_python(value) == value


@given(_PREFIX_BODIES)
def test_every_grammatical_prefix_name_is_accepted(prefix: str) -> None:
    _grammatical(_PREFIX_NAME_BODY_RE, prefix)
    assert _PREFIX_NAME.validate_python(f"{prefix}:") == f"{prefix}:"


@given(_NODE_IDS)
def test_every_grammatical_node_id_is_accepted_verbatim(value: str) -> None:
    _grammatical(_BLANK_NODE_LABEL_RE, value)
    assert _NODE_ID.validate_python(value) == value


@given(st.integers(min_value=0), st.sampled_from(["0x", "0X"]), st.booleans())
def test_uid_normalization_is_case_and_padding_insensitive_and_idempotent(
    value: int, prefix: str, upper_digits: bool
) -> None:
    digits = format(value, "X" if upper_digits else "x")
    normalized = _UID.validate_python(f"{prefix}{digits}")

    assert normalized == hex(value)
    assert _UID.validate_python(f"{prefix}00{digits}") == normalized
    assert _UID.validate_python(normalized) == normalized
