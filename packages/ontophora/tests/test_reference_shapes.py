import pytest
from pydantic import TypeAdapter, ValidationError

from ontophora.constructs.data_property import DataProperty
from ontophora.constructs.declaration import Declaration
from ontophora.constructs.ontology_document import OntologyDocument
from ontophora.constructs.types import UID
from ontophora.reference_inspection import CollectionKind, field_collection_kind


def test_reference_module_is_importable_directly() -> None:
    from ontophora.reference import ReferenceValue

    value = ReferenceValue(uid="0x1234abcd")

    assert str(value) == "0x1234abcd"


def test_reference_value_identity_is_uid_only() -> None:
    from ontophora.reference import ReferenceValue

    ref_a = ReferenceValue(uid="0x1234abcd")
    ref_b = ReferenceValue(uid="0x1234abcd")

    assert ref_a == ref_b
    assert str(ref_a) == "0x1234abcd"
    assert len({ref_a, ref_b}) == 1


def test_reference_module_stays_narrow() -> None:
    import ontophora.reference as reference_module

    assert not hasattr(reference_module, "iter_construct_references")
    assert not hasattr(reference_module, "field_collection_kind")


def test_field_collection_kind_distinguishes_set_shapes() -> None:
    assert field_collection_kind(list[str]) is CollectionKind.ORDERED
    assert field_collection_kind(set[str]) is CollectionKind.UNORDERED_SET
    assert field_collection_kind(frozenset[str]) is CollectionKind.UNORDERED_FROZENSET
    assert field_collection_kind(str) is CollectionKind.SCALAR


def test_reference_uid_shape_validation() -> None:
    data_property = DataProperty(iri="https://example.com/p", uid="0x1234abcd")

    assert data_property.uid == "0x1234abcd"

    with pytest.raises(ValidationError, match="ontology"):
        _ = OntologyDocument(
            uid="0x1234abcd",
            ontology={"uid": "not-a-uid"},
        )


@pytest.mark.parametrize(
    ("value", "expected"),
    [("0x1234abcd", "0x1234abcd"), ("0X1234ABCD", "0x1234abcd"), ("0x0001", "0x1")],
)
def test_uid_normalizes_hex_strings(value: str, expected: str) -> None:
    assert TypeAdapter(UID).validate_python(value) == expected


@pytest.mark.parametrize("value", ["", "1234abcd", "0x", "0xnothex"])
def test_uid_rejects_invalid_hex_strings(value: str) -> None:
    with pytest.raises(ValidationError):
        TypeAdapter(UID).validate_python(value)


def test_reference_serialization_contains_uid_only() -> None:
    document = OntologyDocument(
        uid="0x9999aaaa",
        ontology="0x1234abcd",
    )

    assert document.model_dump(mode="json") == {
        "uid": "0x9999aaaa",
        "ontology": {"uid": "0x1234abcd"},
        "prefix_declarations": [],
        "kind": "OntologyDocument",
    }


def test_reference_validation_accepts_serialized_reference_object() -> None:
    document = OntologyDocument.model_validate(
        {
            "uid": "0x9999aaaa",
            "ontology": {"uid": "0x1234abcd"},
            "prefix_declarations": [],
            "kind": "OntologyDocument",
        }
    )

    assert str(document.ontology) == "0x1234abcd"
    assert document.model_dump(mode="json")["ontology"] == {"uid": "0x1234abcd"}


def test_reference_validation_accepts_legacy_expected_kind_in_input() -> None:
    document = OntologyDocument.model_validate(
        {
            "uid": "0x9999aaaa",
            "ontology": {"uid": "0x1234abcd", "expected_kind": "Ontology"},
            "prefix_declarations": [],
            "kind": "OntologyDocument",
        }
    )

    assert str(document.ontology) == "0x1234abcd"


def test_reference_schema_has_uid_only() -> None:
    schema = Declaration.model_json_schema()
    ref_value_schema = schema["$defs"]["ReferenceValue"]

    assert ref_value_schema["required"] == ["uid"]
    assert list(ref_value_schema["properties"]) == ["uid"]
