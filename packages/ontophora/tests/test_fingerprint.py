from ontophora.fingerprint import fingerprint_construct, fingerprint_constructs
from ontophora.records import coerce_construct


def test_fingerprint_construct_handles_self_reference_cycle() -> None:
    record = coerce_construct(
        {"uid": "0x1", "kind": "ObjectComplementOf", "class_expression": {"uid": "0x1"}}
    )

    digest = fingerprint_construct(record, {"0x1": record})

    assert len(digest) == 64


def test_fingerprint_construct_handles_mutual_reference_cycle() -> None:
    first = coerce_construct(
        {"uid": "0x1", "kind": "ObjectComplementOf", "class_expression": {"uid": "0x2"}}
    )
    second = coerce_construct(
        {"uid": "0x2", "kind": "ObjectComplementOf", "class_expression": {"uid": "0x1"}}
    )
    record_index = {"0x1": first, "0x2": second}
    digests_by_uid = fingerprint_constructs([first, second], record_index)
    digests = [digests_by_uid["0x1"], digests_by_uid["0x2"]]

    assert all(len(digest) == 64 for digest in digests)
    assert set(digests_by_uid) == {"0x1", "0x2"}


def test_fingerprint_cycles_are_order_independent_and_content_addressed() -> None:
    first = coerce_construct(
        {"uid": "0x1", "kind": "ObjectComplementOf", "class_expression": {"uid": "0x2"}}
    )
    second = coerce_construct(
        {"uid": "0x2", "kind": "ObjectComplementOf", "class_expression": {"uid": "0x1"}}
    )
    record_index = {"0x1": first, "0x2": second}

    forward = fingerprint_constructs([first, second], record_index)
    reverse = fingerprint_constructs([second, first], record_index)
    assert forward == reverse

    # Batch results agree with standalone computation.
    assert forward["0x2"] == fingerprint_construct(second, record_index)

    # Structurally identical cyclic records fingerprint identically despite
    # different uids, and mutually symmetric records share one fingerprint.
    third = coerce_construct(
        {"uid": "0xa", "kind": "ObjectComplementOf", "class_expression": {"uid": "0xb"}}
    )
    fourth = coerce_construct(
        {"uid": "0xb", "kind": "ObjectComplementOf", "class_expression": {"uid": "0xa"}}
    )
    other_index = {"0xa": third, "0xb": fourth}
    assert fingerprint_construct(third, other_index) == forward["0x1"]
    assert forward["0x1"] == forward["0x2"]
