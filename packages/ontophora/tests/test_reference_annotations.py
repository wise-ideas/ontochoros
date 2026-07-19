"""``Reference[...]`` annotation parsing: expected-kind resolution.

The expected kind attached to a reference field is what endpoint-kind
validation (see TODO.md) will check against, so every annotation form used
by the construct modules must resolve — and the whole catalog is swept to
prove no field slips through with an unresolvable or empty expectation.
"""

from __future__ import annotations

from typing import Annotated, Literal, get_args

import pytest
from pydantic import TypeAdapter

from ontophora._field_encoding import field_shape
from ontophora._registry import construct_metadata_by_kind
from ontophora.constructs.klass import Klass
from ontophora.reference import (
    Reference,
    ReferenceValue,
    expected_kind_to_tuple,
    model_kind,
)


def _expected_kind(annotation: object) -> str | tuple[str, ...]:
    _, metadata, _ = get_args(annotation)
    return metadata.expected_kind


def test_reference_is_not_instantiable() -> None:
    with pytest.raises(TypeError, match="not instantiable"):
        Reference()


def test_construct_type_argument_resolves_to_its_kind_default() -> None:
    # Klass's kind default is "Class", not the class name.
    assert _expected_kind(Reference[Klass]) == "Class"
    assert model_kind(Klass) == "Class"


def test_string_and_literal_arguments_resolve_verbatim() -> None:
    assert _expected_kind(Reference["ClassExpression"]) == "ClassExpression"
    assert _expected_kind(Reference[Literal["ClassExpression"]]) == "ClassExpression"


def test_multi_literal_argument_resolves_to_deduplicated_tuple() -> None:
    kind = _expected_kind(Reference[Literal["Class", "Datatype", "Class"]])

    assert kind == ("Class", "Datatype")


def test_union_argument_merges_arm_kinds() -> None:
    kind = _expected_kind(Reference[Literal["Class"] | Literal["Datatype"]])

    assert kind == ("Class", "Datatype")


def test_annotated_argument_unwraps_to_the_value_type() -> None:
    assert _expected_kind(Reference[Annotated[Klass, "ignored"]]) == "Class"


def test_unsupported_argument_is_rejected() -> None:
    with pytest.raises(TypeError, match="Unsupported reference type annotation"):
        Reference[int]

    with pytest.raises(TypeError, match="Unsupported reference type annotation"):
        Reference[Literal[1, 2]]


def test_reference_annotation_validates_bare_uid_and_object_forms() -> None:
    adapter = TypeAdapter(Reference[Klass])

    from_string = adapter.validate_python("0x1")
    from_object = adapter.validate_python({"uid": "0x1"})

    assert from_string == from_object == ReferenceValue(uid="0x1")


def test_expected_kind_to_tuple_normalizes_all_shapes() -> None:
    assert expected_kind_to_tuple(None) == ()
    assert expected_kind_to_tuple("Class") == ("Class",)
    assert expected_kind_to_tuple(("Class", "Datatype")) == ("Class", "Datatype")


def _is_reference_annotation(annotation: object) -> bool:
    if annotation is ReferenceValue:
        return True
    return any(_is_reference_annotation(arg) for arg in get_args(annotation))


def test_every_reference_field_in_the_catalog_resolves_expected_kinds() -> None:
    # The sweep: no construct field that carries references may have an
    # empty expected-kind set, or endpoint validation could never check it.
    checked = 0
    for metadata in construct_metadata_by_kind().values():
        for field_name, field in metadata.model_type.model_fields.items():
            if not _is_reference_annotation(field.annotation):
                continue
            shape = field_shape(field)
            assert shape.expected_kinds, (
                f"{metadata.kind}.{field_name} carries references but resolves no expected kinds"
            )
            checked += 1
    # Loud-failure guard: if field detection breaks, the sweep must not
    # silently pass by checking nothing.
    assert checked > 50
