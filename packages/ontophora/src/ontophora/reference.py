"""Runtime reference values and the ``Reference[T]`` field annotation."""

from types import UnionType
from typing import Annotated, Any, Generic, Literal, TypeVar, Union, get_args, get_origin

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
)

from ontophora._field_encoding import extract_expected_kinds
from ontophora.uid import UID

T = TypeVar("T")
ExpectedKind = str | tuple[str, ...] | None


# ---------------------------------------------------------------------------
# Runtime reference value
# ---------------------------------------------------------------------------


class ReferenceValue(BaseModel):
    """Validated in-memory representation of a construct reference.

    ``uid`` identifies the target construct. Reference identity is purely
    UID-based: two references to the same construct are equal regardless of
    which field annotation they came from.

    This does not mean the referenced construct has been resolved or checked.
    Referential integrity and kind validation are expected to happen in a later
    layer that has access to the full construct set.

    The compact JSONL wire form used in fixtures is usually just the bare UID
    string. ``Reference[...]`` expands that into this model during validation.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    uid: UID

    def __str__(self) -> str:
        return self.uid


# ---------------------------------------------------------------------------
# Reference[T] field annotation
# ---------------------------------------------------------------------------


class Reference(Generic[T]):
    """Type-level helper for fields that point at another construct.

    The validated runtime value is `ReferenceValue`. Input may be either a full
    object shape or the compact bare-UID wire form used in JSONL fixtures.

    The purpose of the generic parameter is to preserve the expected referenced
    kind for tooling and downstream validation, while keeping construct records
    themselves independent and UID-based.
    """

    def __new__(cls, *_, **__):
        raise TypeError("Reference is not instantiable")

    @classmethod
    def __class_getitem__(cls, type_: Any) -> Any:
        metadata = _ReferenceTypeMetadata(type_)
        # Returns a runtime Annotated special form; `Any` avoids false positives from static analysis here.
        return Annotated[
            ReferenceValue,
            metadata,
            BeforeValidator(metadata.prepare),
        ]


class _ReferenceTypeMetadata:
    """Pydantic-facing metadata derived from one ``Reference[...]`` annotation.

    Carries ``expected_kind`` for schema introspection. Does not embed the kind
    in the runtime value — ``expected_kind`` is field-position metadata derived
    from the annotation, not target-construct data.
    """

    def __init__(self, expected_type: Any):
        self.expected_type = expected_type
        self.expected_kind = _kind_for_reference_type_arg(expected_type)

    def prepare(self, value: Any) -> Any:
        """Normalize compact reference inputs into the full transport shape."""
        if isinstance(value, ReferenceValue):
            return value
        if isinstance(value, str):
            return {"uid": value}
        if isinstance(value, dict):
            # Strip legacy expected_kind; it is field-annotation metadata, not value data.
            return {k: v for k, v in value.items() if k != "expected_kind"}
        return value


def _kind_for_reference_type_arg(annotation: Any) -> str | tuple[str, ...]:
    """Resolve the expected-kind from the type argument inside ``Reference[...]``."""
    # This stays separate because it parses the narrower Reference[T] type-argument
    # domain, then delegates to the shared analyzer for general annotation forms.
    if isinstance(annotation, str):
        return annotation
    if hasattr(annotation, "__forward_arg__"):
        return annotation.__forward_arg__
    origin = get_origin(annotation)
    if origin in (Annotated,):
        value_type, *_ = get_args(annotation)
        return _kind_for_reference_type_arg(value_type)
    if origin is Literal:
        literal_args = get_args(annotation)
        if not literal_args or not all(isinstance(arg, str) for arg in literal_args):
            raise TypeError(f"Unsupported reference type annotation: {annotation!r}")
        if len(literal_args) == 1:
            return literal_args[0]
        return tuple(dict.fromkeys(literal_args))
    if origin in (UnionType, Union):
        rendered = []
        for arg in get_args(annotation):
            child = _kind_for_reference_type_arg(arg)
            if isinstance(child, tuple):
                for item in child:
                    if item not in rendered:
                        rendered.append(item)
            elif child not in rendered:
                rendered.append(child)
        if len(rendered) == 1:
            return rendered[0]
        return tuple(rendered)
    if _is_construct_type(annotation):
        return model_kind(annotation)
    expected_kinds = extract_expected_kinds(annotation)
    if not expected_kinds:
        raise TypeError(f"Unsupported reference type annotation: {annotation!r}")
    if len(expected_kinds) == 1:
        return expected_kinds[0]
    return expected_kinds


def _is_construct_type(annotation: Any) -> bool:
    return (
        isinstance(annotation, type)
        and issubclass(annotation, BaseModel)
        and hasattr(annotation, "model_fields")
    )


def model_kind(model: type[object]) -> str:
    """Return the construct kind declared by a model's ``kind`` field default."""
    kind_field = getattr(model, "model_fields", {}).get("kind")
    default = getattr(kind_field, "default", None)
    if isinstance(default, str):
        return default
    return model.__name__


def expected_kind_to_tuple(kind: ExpectedKind) -> tuple[str, ...]:
    """Normalize one expected-kind value into the tuple form used on edges."""
    if kind is None:
        return ()
    return kind if isinstance(kind, tuple) else (kind,)


__all__ = [
    "ExpectedKind",
    "Reference",
    "ReferenceValue",
    "expected_kind_to_tuple",
    "model_kind",
]
