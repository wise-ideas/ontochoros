from __future__ import annotations

import json

import pytest

from ontophora.envelope import (
    EnvelopeError,
    envelope_json_schema,
    records_from_json,
    records_from_jsonl,
    records_to_json,
    records_to_jsonl,
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


def test_records_from_jsonl_decodes_one_record_per_line() -> None:
    payload = (
        '{"uid": "0x1", "construct": {"kind": "Class", "iri": "https://example.org/A"}}\n'
        "\n"
        '{"uid": "0x2", "construct": {"kind": "Class", "iri": "https://example.org/B"}}\n'
    )

    records = records_from_jsonl(payload)

    assert [record.uid for record in records] == ["0x1", "0x2"]


def test_records_from_jsonl_reports_the_failing_line_number() -> None:
    payload = (
        '{"uid": "0x1", "construct": {"kind": "Class", "iri": "https://example.org/A"}}\nnot json\n'
    )

    with pytest.raises(EnvelopeError, match="line 2 is not valid JSON"):
        records_from_jsonl(payload)


def test_records_from_jsonl_validates_record_shape() -> None:
    with pytest.raises(EnvelopeError, match="missing required field 'uid'"):
        records_from_jsonl('{"construct": {"kind": "Class", "iri": "https://example.org/A"}}')


def test_jsonl_round_trips_and_matches_the_json_envelope() -> None:
    records = records_from_json(
        '[{"uid": "0x1", "construct": {"kind": "Class", "iri": "https://example.org/A"}},'
        ' {"uid": "0x2", "construct": {"kind": "Class", "iri": "https://example.org/B"}}]'
    )

    encoded = records_to_jsonl(records)

    assert encoded.endswith("\n")
    assert [json.loads(line) for line in encoded.splitlines()] == json.loads(
        records_to_json(records)
    )
    assert records_from_jsonl(encoded) == records


def test_records_to_jsonl_rejects_unregistered_construct() -> None:
    from ontophora import BaseConstruct

    with pytest.raises(EnvelopeError, match="unregistered construct kind 'Unknown'"):
        records_to_jsonl([BaseConstruct(uid="0x1", kind="Unknown")])


def test_envelope_json_schema_describes_uid_construct_records() -> None:
    schema = envelope_json_schema()

    assert schema["type"] == "array"
    items = schema["items"]
    assert items["required"] == ["uid", "construct"]
    assert items["properties"]["uid"] == {"type": "string"}
    assert "oneOf" in items["properties"]["construct"]


def test_envelope_json_schema_strips_uid_from_construct_definitions() -> None:
    schema = envelope_json_schema()

    definitions = schema["$defs"]
    assert definitions
    for definition in definitions.values():
        assert "uid" not in definition.get("properties", {})
        assert "uid" not in definition.get("required", [])
