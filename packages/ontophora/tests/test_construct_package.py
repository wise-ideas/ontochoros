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
            "data_property_expression": "0x2",
            "data_range": "0x3",
        }
    )

    assert str(record.data_property_expression) == "0x2"


@pytest.mark.parametrize("kind", ["DataAllValuesFrom", "DataSomeValuesFrom"])
def test_data_value_restrictions_reject_multiple_data_property_expressions(kind: str) -> None:
    with pytest.raises(ValidationError, match="data_property_expression"):
        coerce_construct(
            {
                "uid": "0x1",
                "kind": kind,
                "data_property_expression": ["0x2", "0x3"],
                "data_range": "0x4",
            }
        )
