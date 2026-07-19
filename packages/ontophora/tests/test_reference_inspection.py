"""Behavioral tests for ``iter_construct_references``.

This is the exported traversal API that the planned multi-construct
validation (see TODO.md) builds on: it must report, for one validated
construct, every embedded reference with a stable edge key, the ordinal
position for ordered collections, and the expected target kinds derived
from the field annotation.
"""

from __future__ import annotations

from ontophora.records import coerce_construct
from ontophora.reference_inspection import (
    ENDPOINT_ORDER_ORIGIN,
    ReferenceEntry,
    iter_construct_references,
)


def _entries(record) -> list[ReferenceEntry]:
    return list(iter_construct_references(record))


def test_scalar_reference_fields_yield_field_named_edges() -> None:
    record = coerce_construct(
        {
            "uid": "0x10",
            "kind": "SubClassOf",
            "sub_class_expression": "0x1",
            "super_class_expression": "0x2",
        }
    )

    entries = {entry.edge_key: entry for entry in _entries(record)}

    assert set(entries) == {"sub_class_expression", "super_class_expression"}
    assert entries["sub_class_expression"].target_uid == "0x1"
    assert entries["super_class_expression"].target_uid == "0x2"
    # Scalar fields carry no ordinal.
    assert entries["sub_class_expression"].endpoint_order is None
    # Expected kinds come from the Reference[...] annotation.
    assert entries["sub_class_expression"].expected_kinds == ("ClassExpression",)


def test_ordered_reference_lists_number_endpoints_from_origin() -> None:
    record = coerce_construct(
        {
            "uid": "0x10",
            "kind": "ObjectPropertyChain",
            "object_property_expressions": ["0x1", "0x2", "0x3"],
        }
    )

    entries = _entries(record)

    assert [entry.target_uid for entry in entries] == ["0x1", "0x2", "0x3"]
    assert [entry.endpoint_order for entry in entries] == [
        ENDPOINT_ORDER_ORIGIN,
        ENDPOINT_ORDER_ORIGIN + 1,
        ENDPOINT_ORDER_ORIGIN + 2,
    ]
    assert {entry.edge_key for entry in entries} == {"object_property_expressions"}
    assert entries[0].expected_kinds == ("ObjectPropertyExpression",)


def test_unordered_reference_sets_are_deterministic_and_unnumbered() -> None:
    record = coerce_construct(
        {
            "uid": "0x10",
            "kind": "ObjectIntersectionOf",
            "class_expressions": ["0x3", "0x1", "0x2"],
        }
    )

    entries = _entries(record)

    # Set fields iterate in canonical sorted order regardless of input order,
    # and never claim an ordinal.
    assert [entry.target_uid for entry in entries] == ["0x1", "0x2", "0x3"]
    assert all(entry.endpoint_order is None for entry in entries)
    assert {entry.edge_key for entry in entries} == {"class_expressions"}


def test_mixed_construct_reports_every_reference_with_its_field_key() -> None:
    record = coerce_construct(
        {
            "uid": "0x10",
            "kind": "OntologyDocument",
            "ontology": "0x1",
            "prefix_declarations": ["0x2", "0x3"],
        }
    )

    entries = _entries(record)

    assert [(entry.edge_key, entry.target_uid, entry.endpoint_order) for entry in entries] == [
        ("ontology", "0x1", None),
        ("prefix_declarations", "0x2", ENDPOINT_ORDER_ORIGIN),
        ("prefix_declarations", "0x3", ENDPOINT_ORDER_ORIGIN + 1),
    ]
    assert entries[0].expected_kinds == ("Ontology",)
    assert entries[1].expected_kinds == ("Prefix",)


def test_union_annotated_reference_field_reports_the_reference_arm() -> None:
    # AnnotationAssertion.annotation_subject is Reference[AnonymousIndividual] | IRI:
    # a reference input must surface as a reference entry with the arm's kind.
    record = coerce_construct(
        {
            "uid": "0x10",
            "kind": "AnnotationAssertion",
            "annotation_property": "0x1",
            "annotation_subject": {"uid": "0x2"},
            "annotation_value": "https://example.org/v",
        }
    )

    entries = {entry.edge_key: entry for entry in _entries(record)}

    assert entries["annotation_subject"].target_uid == "0x2"
    assert "AnonymousIndividual" in entries["annotation_subject"].expected_kinds


def test_non_reference_scalar_fields_yield_nothing() -> None:
    record = coerce_construct(
        {"uid": "0x10", "kind": "Class", "iri": "https://example.org/pizza#Pizza"}
    )

    assert _entries(record) == []


def test_every_entry_reports_expected_kinds() -> None:
    # Referential-integrity checking needs the expected kinds on every edge;
    # an empty tuple would make an edge unvalidatable.
    record = coerce_construct(
        {
            "uid": "0x10",
            "kind": "DisjointUnion",
            "klass": "0x1",
            "disjoint_class_expressions": ["0x2", "0x3"],
            "axiom_annotations": ["0x4"],
        }
    )

    entries = _entries(record)

    assert len(entries) == 4
    assert all(entry.expected_kinds for entry in entries)
