"""The public-surface ratchet: names may be removed, never silently added."""

import ontoplexis


def test_top_level_public_name_set() -> None:
    assert set(ontoplexis.__all__) == {
        "Edge",
        "Graph",
        "NODE_TABLE",
        "Node",
        "Ontology",
        "OwlXmlStructureError",
        "Projection",
        "ProjectionStorageError",
        "RELATIONSHIP_TABLE",
        "WritableProjection",
    }


def test_headline_objects_resolve() -> None:
    assert ontoplexis.Ontology is not None
    assert ontoplexis.Projection is not None
    assert ontoplexis.WritableProjection is not None
