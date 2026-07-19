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


def _cls(uid: str, iri: str):
    return coerce_construct({"uid": uid, "kind": "Class", "iri": iri})


def test_acyclic_fingerprints_are_content_addressed() -> None:
    # The documented supported case: same content under a different uid
    # fingerprints identically, different content differs.
    same_a = _cls("0x1", "http://ex.org/A")
    same_b = _cls("0x2", "http://ex.org/A")
    other = _cls("0x3", "http://ex.org/B")
    index = {"0x1": same_a, "0x2": same_b, "0x3": other}

    assert fingerprint_construct(same_a, index) == fingerprint_construct(same_b, index)
    assert fingerprint_construct(same_a, index) != fingerprint_construct(other, index)


def test_acyclic_fingerprints_follow_references_by_content_and_direction() -> None:
    sub_a = _cls("0x1", "http://ex.org/A")
    sub_b = _cls("0x2", "http://ex.org/A")
    sup = _cls("0x3", "http://ex.org/B")
    forward_a = coerce_construct(
        {
            "uid": "0x10",
            "kind": "SubClassOf",
            "sub_class_expression": {"uid": "0x1"},
            "super_class_expression": {"uid": "0x3"},
        }
    )
    forward_b = coerce_construct(
        {
            "uid": "0x11",
            "kind": "SubClassOf",
            "sub_class_expression": {"uid": "0x2"},
            "super_class_expression": {"uid": "0x3"},
        }
    )
    reversed_axiom = coerce_construct(
        {
            "uid": "0x12",
            "kind": "SubClassOf",
            "sub_class_expression": {"uid": "0x3"},
            "super_class_expression": {"uid": "0x1"},
        }
    )
    index = {
        "0x1": sub_a,
        "0x2": sub_b,
        "0x3": sup,
        "0x10": forward_a,
        "0x11": forward_b,
        "0x12": reversed_axiom,
    }

    # References resolve by referenced *content*, not by uid...
    assert fingerprint_construct(forward_a, index) == fingerprint_construct(forward_b, index)
    # ...and swapping sub/super changes the fingerprint.
    assert fingerprint_construct(forward_a, index) != fingerprint_construct(reversed_axiom, index)


def test_unresolved_references_fall_back_to_identity() -> None:
    # A dangling reference cannot be resolved by content, so the raw uid
    # leaks into the digest: two records identical except for the dangling
    # target uid fingerprint differently. This is the documented trade-off,
    # not an accident — pin it.
    dangling_a = coerce_construct(
        {"uid": "0x1", "kind": "ObjectComplementOf", "class_expression": {"uid": "0xdead"}}
    )
    dangling_b = coerce_construct(
        {"uid": "0x2", "kind": "ObjectComplementOf", "class_expression": {"uid": "0xbeef"}}
    )
    index = {"0x1": dangling_a, "0x2": dangling_b}

    assert fingerprint_construct(dangling_a, index) != fingerprint_construct(dangling_b, index)
    # Same dangling target, different uid: still content-addressed.
    dangling_c = coerce_construct(
        {"uid": "0x3", "kind": "ObjectComplementOf", "class_expression": {"uid": "0xdead"}}
    )
    assert fingerprint_construct(dangling_c, {"0x3": dangling_c}) == fingerprint_construct(
        dangling_a, index
    )


def test_ordered_reference_lists_fingerprint_by_position() -> None:
    def chain(uid: str, first: str, second: str):
        return coerce_construct(
            {
                "uid": uid,
                "kind": "ObjectPropertyChain",
                "object_property_expressions": [{"uid": first}, {"uid": second}],
            }
        )

    prop_p = coerce_construct({"uid": "0x1", "kind": "ObjectProperty", "iri": "http://ex.org/p"})
    prop_q = coerce_construct({"uid": "0x2", "kind": "ObjectProperty", "iri": "http://ex.org/q"})
    index = {"0x1": prop_p, "0x2": prop_q}

    forward = fingerprint_construct(chain("0x10", "0x1", "0x2"), index)
    reordered = fingerprint_construct(chain("0x11", "0x2", "0x1"), index)

    # Lists are ordered content: reversing the chain changes the digest.
    assert forward != reordered


def test_asymmetric_cycle_fingerprints_are_order_and_uid_independent() -> None:
    # An asymmetric two-node cycle (complement -> someValuesFrom -> complement)
    # cannot pass by symmetry alone, unlike the mutual-complement cases above.
    # NOTE: full SCC canonicalization is still open (see TODO.md) — this pins
    # the strongest behavior the current implementation is known to provide.
    def build(u1: str, u2: str, u3: str):
        complement = coerce_construct(
            {"uid": u1, "kind": "ObjectComplementOf", "class_expression": {"uid": u2}}
        )
        restriction = coerce_construct(
            {
                "uid": u2,
                "kind": "ObjectSomeValuesFrom",
                "object_property_expression": {"uid": u3},
                "class_expression": {"uid": u1},
            }
        )
        prop = coerce_construct({"uid": u3, "kind": "ObjectProperty", "iri": "http://ex.org/p"})
        return [complement, restriction, prop], {u1: complement, u2: restriction, u3: prop}

    records, index = build("0x1", "0x2", "0x3")
    renamed_records, renamed_index = build("0xa", "0xb", "0xc")

    digests = fingerprint_constructs(records, index)
    assert digests == fingerprint_constructs(list(reversed(records)), index)

    renamed = fingerprint_constructs(renamed_records, renamed_index)
    assert digests["0x1"] == renamed["0xa"]
    assert digests["0x2"] == renamed["0xb"]
    # The two cycle members are distinguishable despite sharing the cycle.
    assert digests["0x1"] != digests["0x2"]
    # Standalone computation agrees with the batch.
    assert fingerprint_construct(records[0], index) == digests["0x1"]
