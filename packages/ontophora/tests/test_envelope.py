from __future__ import annotations

import json

import pytest

from ontophora.envelope import (
    EnvelopeError,
    records_from_json,
    records_to_json,
)


def test_records_from_json_decodes_construct_records() -> None:
    payload = json.dumps(
        [
            {
                "uid": "0x0",
                "construct": {
                    "kind": "Ontology",
                    "ontology_iri": None,
                    "version_iri": None,
                    "directly_imports_documents": [],
                    "ontology_annotations": [],
                    "axioms": [],
                },
            },
            {
                "uid": "0x1",
                "construct": {
                    "kind": "Class",
                    "iri": "https://example.org/A",
                },
            },
        ]
    )

    records = records_from_json(payload)

    assert [record.uid for record in records] == ["0x0", "0x1"]
    assert [record.kind for record in records] == ["Ontology", "Class"]


def test_records_from_json_rejects_non_array_payload() -> None:
    with pytest.raises(
        EnvelopeError,
        match="must decode to a JSON array of construct records",
    ):
        records_from_json('{"uid": "0x1"}')


def test_records_from_json_rejects_non_object_record() -> None:
    with pytest.raises(EnvelopeError, match="record 1 must be a JSON object"):
        records_from_json('["bad"]')


def test_records_from_json_rejects_missing_uid() -> None:
    with pytest.raises(EnvelopeError, match="missing required field 'uid'"):
        records_from_json('[{"construct": {"kind": "Class", "iri": "https://example.org/A"}}]')


def test_records_from_json_rejects_non_object_construct_payload() -> None:
    with pytest.raises(
        EnvelopeError,
        match="field 'construct' must be a JSON object",
    ):
        records_from_json('[{"uid": "0x1", "construct": "bad"}]')


def test_records_from_json_rejects_uid_in_construct_payload() -> None:
    with pytest.raises(EnvelopeError, match="construct must not contain field 'uid'"):
        records_from_json(
            '[{"uid": "0x1", "construct": {'
            '"uid": "0x2", "kind": "Class", "iri": "https://example.org/A"}}]'
        )


def test_records_from_json_rejects_unexpected_record_fields() -> None:
    with pytest.raises(EnvelopeError, match="record 1 has unexpected fields: extra"):
        records_from_json(
            '[{"uid": "0x1", "extra": true, '
            '"construct": {"kind": "Class", "iri": "https://example.org/A"}}]'
        )


def test_records_to_json_rejects_unregistered_construct() -> None:
    from ontophora import BaseConstruct

    with pytest.raises(EnvelopeError, match="unregistered construct kind 'Unknown'"):
        records_to_json([BaseConstruct(uid="0x1", kind="Unknown")])


def test_records_to_json_emits_construct_envelope() -> None:
    records = records_from_json(
        '[{"uid": "0x1", "construct": {"kind": "Class", "iri": "https://example.org/A"}}]'
    )

    encoded = records_to_json(records)

    assert json.loads(encoded) == [
        {
            "uid": "0x1",
            "construct": {
                "kind": "Class",
                "iri": "https://example.org/A",
            },
        }
    ]
