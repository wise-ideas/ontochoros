from ontophora.display import (
    CONSTRUCT_IRI_FIELDS,
    CONSTRUCT_LABEL_FIELDS,
    compact_display_value,
    first_display_field,
)


def test_display_helpers_use_construct_property_priority() -> None:
    props = {
        "version_iri": "https://example.org/version",
        "ontology_iri": "https://example.org/ontology",
        "iri": "https://example.org/entity#Pizza",
        "node_id": "_:b0",
    }

    assert first_display_field(props, CONSTRUCT_IRI_FIELDS) == "https://example.org/entity#Pizza"
    assert first_display_field(props, CONSTRUCT_LABEL_FIELDS) == "https://example.org/entity#Pizza"


def test_display_helpers_skip_missing_or_non_string_values() -> None:
    props = {
        "iri": None,
        "quoted_string": 7,
        "lexical_form": "Pizza",
    }

    assert first_display_field(props, CONSTRUCT_IRI_FIELDS) is None
    assert first_display_field(props, CONSTRUCT_LABEL_FIELDS) == "Pizza"


def test_compact_display_value_compacts_iri_tail() -> None:
    props = {"iri": "https://example.org/ontology#MargheritaPizza"}

    label = first_display_field(props, CONSTRUCT_LABEL_FIELDS)

    assert label == "https://example.org/ontology#MargheritaPizza"
    assert compact_display_value(label) == "MargheritaPizza"
