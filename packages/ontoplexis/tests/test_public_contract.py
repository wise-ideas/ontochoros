"""The public-surface ratchet: names may be removed, never silently added."""

import ontoplexis


def test_top_level_public_name_set() -> None:
    assert set(ontoplexis.__all__) == {
        "DERIVED_TABLE",
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
        "derive_edges",
    }


def test_headline_objects_resolve() -> None:
    assert ontoplexis.Ontology is not None
    assert ontoplexis.Projection is not None
    assert ontoplexis.WritableProjection is not None


def test_storage_backend_is_isolated_to_graph_module() -> None:
    """`real_ladybug` may be imported only by graph.py.

    The storage seam is the one place a backend swap would happen; every other
    module goes through the `Projection` handles. Keep it that way.
    """
    from pathlib import Path

    src = Path(ontoplexis.__file__).parent
    offenders = [
        str(path.relative_to(src))
        for path in src.rglob("*.py")
        if path.name != "graph.py" and "real_ladybug" in path.read_text(encoding="utf-8")
    ]
    assert offenders == []
