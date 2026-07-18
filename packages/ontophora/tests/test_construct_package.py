import pytest
from pydantic import ValidationError

from ontophora import BaseConstruct
from ontophora.records import coerce_construct


def test_coerce_construct_accepts_flat_payload() -> None:
    record = coerce_construct(
        {
            "uid": "0xdeadbeef",
            "kind": "Ontology",
            "ontology_iri": "https://example.com/ontology",
        }
    )
    assert record.uid == "0xdeadbeef"


def test_coerce_construct_passes_through_base_construct() -> None:
    original = coerce_construct(
        {"uid": "0xaabb", "kind": "Ontology", "ontology_iri": "https://example.com/o"}
    )
    assert isinstance(original, BaseConstruct)
    assert coerce_construct(original) is original


@pytest.mark.parametrize("kind", ["DataAllValuesFrom", "DataSomeValuesFrom"])
def test_data_value_restrictions_accept_one_data_property_expression(kind: str) -> None:
    record = coerce_construct(
        {
            "uid": "0x1",
            "kind": kind,
            "data_property_expressions": ["0x2"],
            "data_range": "0x3",
        }
    )

    assert [str(expression) for expression in record.data_property_expressions] == ["0x2"]


@pytest.mark.parametrize("kind", ["DataAllValuesFrom", "DataSomeValuesFrom"])
def test_data_value_restrictions_accept_ordered_data_property_expressions(kind: str) -> None:
    # OWL 2 sections 8.4.1/8.4.2: one or more property expressions, ordered to
    # match the arity of the data range.
    record = coerce_construct(
        {
            "uid": "0x1",
            "kind": kind,
            "data_property_expressions": ["0x2", "0x3"],
            "data_range": "0x4",
        }
    )

    assert [str(expression) for expression in record.data_property_expressions] == ["0x2", "0x3"]


@pytest.mark.parametrize("kind", ["DataAllValuesFrom", "DataSomeValuesFrom"])
def test_data_value_restrictions_reject_zero_data_property_expressions(kind: str) -> None:
    with pytest.raises(ValidationError, match="data_property_expressions"):
        coerce_construct(
            {
                "uid": "0x1",
                "kind": kind,
                "data_property_expressions": [],
                "data_range": "0x4",
            }
        )


def test_has_key_requires_at_least_one_property_expression() -> None:
    # OWL 2 section 9.5: m or n (or both) MUST be larger than zero.
    with pytest.raises(ValidationError, match="at least one"):
        coerce_construct(
            {
                "uid": "0x1",
                "kind": "HasKey",
                "class_expression": "0x2",
                "object_property_expressions": [],
                "data_property_expressions": [],
            }
        )

    record = coerce_construct(
        {
            "uid": "0x1",
            "kind": "HasKey",
            "class_expression": "0x2",
            "object_property_expressions": ["0x3"],
            "data_property_expressions": [],
        }
    )
    assert [str(expression) for expression in record.object_property_expressions] == ["0x3"]
