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
