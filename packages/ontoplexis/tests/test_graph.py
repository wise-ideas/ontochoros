"""Ladybug projection tests (real database, no jar)."""

from __future__ import annotations

from pathlib import Path

import pytest

from ontoplexis import Ontology, Projection, ProjectionStorageError, WritableProjection
from ontoplexis.owlxml import OwlXmlStructureError, parse_owlxml


def test_projection_round_trips_the_graph(animals_owlxml: str) -> None:
    ontology = Ontology.from_owlxml(animals_owlxml)

    with ontology.project() as projection:
        loaded = projection.graph()

    assert set(loaded.nodes) == set(ontology.graph.nodes)
    assert set(loaded.edges) == set(ontology.graph.edges)


def test_projection_document_round_trips_through_the_database(animals_owlxml: str) -> None:
    ontology = Ontology.from_owlxml(animals_owlxml)

    with ontology.project() as projection:
        recovered = Ontology.from_projection(projection)

    assert parse_owlxml(recovered.to_owlxml()) == ontology.graph


def test_cypher_queries_subclass_pairs(animals_owlxml: str) -> None:
    with Ontology.from_owlxml(animals_owlxml).project() as projection:
        rows = projection.execute(
            "MATCH (a:N)<-[:E {role: 'sub'}]-(ax:N {kind: 'SubClassOf'})"
            "-[:E {role: 'super'}]->(b:N) "
            "WHERE a.iri IS NOT NULL AND b.iri IS NOT NULL "
            "RETURN a.iri AS sub_iri, b.iri AS super_iri ORDER BY sub_iri, super_iri"
        )

    assert [(row["sub_iri"], row["super_iri"]) for row in rows] == [
        ("http://example.org/animals#Dog", "http://example.org/animals#Pet"),
        ("http://example.org/animals#Pet", "http://example.org/animals#Animal"),
    ]


def test_cypher_transitive_traversal(animals_owlxml: str) -> None:
    with Ontology.from_owlxml(animals_owlxml).project() as projection:
        rows = projection.execute(
            "MATCH (a:N {iri: $start})<-[:E {role: 'sub'}]-(:N {kind: 'SubClassOf'})"
            "-[:E {role: 'super'}]->(b:N) WHERE b.iri IS NOT NULL "
            "RETURN b.iri AS super_iri",
            parameters={"start": "http://example.org/animals#Dog"},
        )

    assert [row["super_iri"] for row in rows] == ["http://example.org/animals#Pet"]


def test_counts(animals_owlxml: str) -> None:
    ontology = Ontology.from_owlxml(animals_owlxml)

    with ontology.project() as projection:
        assert projection.node_count == len(ontology.graph.nodes)
        assert projection.edge_count == len(ontology.graph.edges)


def test_save_and_open(animals_owlxml: str, tmp_path: Path) -> None:
    ontology = Ontology.from_owlxml(animals_owlxml)
    path = tmp_path / "animals.lbug"

    saved = ontology.save_projection(path)
    saved.close()

    with Projection.open(path) as projection:
        assert projection.node_count == len(ontology.graph.nodes)


def test_writable_projection_authors_a_valid_ontology(tmp_path: Path) -> None:
    writable = WritableProjection.open(tmp_path / "authored.lbug")
    writable.execute(
        "CREATE (o:N {uid: 'o', kind: 'Ontology', ontology_iri: 'http://example.org/authored'})"
    )
    writable.execute("CREATE (d:N {uid: 'd', kind: 'Declaration'})")
    writable.execute("CREATE (c:N {uid: 'c', kind: 'Class', iri: 'http://example.org/authored#A'})")
    writable.execute(
        "MATCH (o:N {uid: 'o'}), (d:N {uid: 'd'}) CREATE (o)-[:E {position: 0, role: 'axiom'}]->(d)"
    )
    writable.execute(
        "MATCH (d:N {uid: 'd'}), (c:N {uid: 'c'}) "
        "CREATE (d)-[:E {position: 0, role: 'entity'}]->(c)"
    )
    projection = writable.reopen_readonly()

    authored = Ontology.from_projection(projection)
    projection.close()
    xml = authored.to_owlxml()

    assert '<Class IRI="http://example.org/authored#A" />' in xml or (
        '<Class IRI="http://example.org/authored#A"/>' in xml
    )


def test_hostile_literal_content_round_trips_through_the_database() -> None:
    """Ingestion must not corrupt quotes, newlines, empty strings, or unicode."""
    from xml.sax.saxutils import escape

    values = [
        'He said "hi" and left',
        "line one\nline two",
        "a,b,c",
        "it's quoted, 'twice'",
        "tab\tseparated",
        "café ☕ Straße",
        "back\\slash \\n (not a newline)",
        "",
    ]
    assertions = "".join(
        "<AnnotationAssertion>"
        '<AnnotationProperty IRI="http://example.org/x#p"/>'
        "<IRI>http://example.org/x#A</IRI>"
        f"<Literal>{escape(value)}</Literal>"
        "</AnnotationAssertion>"
        for value in values
    )
    doc = (
        '<Ontology xmlns="http://www.w3.org/2002/07/owl#" '
        f'ontologyIRI="http://example.org/x">{assertions}</Ontology>'
    )
    ontology = Ontology.from_owlxml(doc)

    with ontology.project() as projection:
        loaded = projection.graph()

    assert {n.uid: n.properties for n in loaded.nodes} == {
        n.uid: n.properties for n in ontology.graph.nodes
    }
    recovered = {n.properties["text"] for n in loaded.nodes if n.kind == "Literal"}
    assert recovered == set(values)


def test_graph_rejects_authored_node_without_kind(tmp_path: Path) -> None:
    """Authoring mistakes must surface as errors, not vanish from the graph."""
    writable = WritableProjection.open(tmp_path / "bad.lbug")
    writable.execute("CREATE (:N {uid: 'o'})")

    with writable.reopen_readonly() as projection:
        with pytest.raises(OwlXmlStructureError, match="kind"):
            projection.graph()


def test_graph_rejects_authored_edge_without_position(tmp_path: Path) -> None:
    writable = WritableProjection.open(tmp_path / "bad.lbug")
    writable.execute("CREATE (:N {uid: 'o', kind: 'Ontology'})")
    writable.execute("CREATE (:N {uid: 'd', kind: 'Declaration'})")
    writable.execute(
        "MATCH (o:N {uid: 'o'}), (d:N {uid: 'd'}) CREATE (o)-[:E {role: 'axiom'}]->(d)"
    )

    with writable.reopen_readonly() as projection:
        with pytest.raises(OwlXmlStructureError, match="position"):
            projection.graph()


def test_closed_projection_rejects_queries(animals_owlxml: str) -> None:
    projection = Ontology.from_owlxml(animals_owlxml).project()
    projection.close()

    with pytest.raises(ProjectionStorageError, match="closed"):
        projection.execute("MATCH (n:N) RETURN count(n) AS count")
    with pytest.raises(ProjectionStorageError, match="closed"):
        projection.node_count


def test_open_missing_projection_requires_path() -> None:
    from ontoplexis.graph import _open_projection

    with pytest.raises(Exception, match="filesystem database path"):
        _open_projection(database_path=None, read_only=True, cls=Projection)


def test_save_projection_removes_temp_file_when_open_fails(
    animals_owlxml: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import ontoplexis.graph as graph_module

    def explode(*args: object, **kwargs: object) -> object:
        raise RuntimeError("database engine unavailable")

    monkeypatch.setattr(graph_module, "_create_writable", explode)
    with pytest.raises(RuntimeError, match="unavailable"):
        Ontology.from_owlxml(animals_owlxml).save_projection(tmp_path / "proj.lbug")

    assert list(tmp_path.iterdir()) == []
