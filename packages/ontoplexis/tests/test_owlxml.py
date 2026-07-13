"""OWL/XML ⇄ graph mapping tests (no jar, no database)."""

from __future__ import annotations

import pytest

from ontoplexis.owlxml import (
    Edge,
    Graph,
    Node,
    OwlXmlStructureError,
    parse_owlxml,
    serialize_owlxml,
)


def _nodes_by_uid(graph: Graph) -> dict[str, Node]:
    return {node.uid: node for node in graph.nodes}


def _kinds(graph: Graph) -> set[str]:
    return {node.kind for node in graph.nodes}


def test_parse_maps_elements_to_kinds(animals_owlxml: str) -> None:
    graph = parse_owlxml(animals_owlxml)

    assert _kinds(graph) >= {
        "Ontology",
        "Prefix",
        "Declaration",
        "Class",
        "ObjectProperty",
        "NamedIndividual",
        "SubClassOf",
        "ObjectMinCardinality",
        "ClassAssertion",
        "AnnotationAssertion",
        "Annotation",
        "AnnotationProperty",
        "Literal",
        "IRI",
    }


def test_named_entities_merge_by_iri(animals_owlxml: str) -> None:
    graph = parse_owlxml(animals_owlxml)

    dogs = [
        n for n in graph.nodes if n.kind == "Class" and n.iri == "http://example.org/animals#Dog"
    ]
    assert len(dogs) == 1

    incoming = [e for e in graph.edges if e.target == dogs[0].uid]
    assert len(incoming) >= 3  # declaration + two subclass axioms + assertion


def test_axiom_occurrences_do_not_merge(animals_owlxml: str) -> None:
    graph = parse_owlxml(animals_owlxml)

    assert len([n for n in graph.nodes if n.kind == "SubClassOf"]) == 3
    assert len([n for n in graph.nodes if n.kind == "Declaration"]) == 5


def test_edges_carry_document_position_and_roles(animals_owlxml: str) -> None:
    graph = parse_owlxml(animals_owlxml)
    nodes = _nodes_by_uid(graph)

    annotated = [
        node.uid
        for node in graph.nodes
        if node.kind == "SubClassOf"
        and any(e.role == "annotation" for e in graph.edges if e.source == node.uid)
    ]
    assert len(annotated) == 1
    children = sorted(
        (e for e in graph.edges if e.source == annotated[0]), key=lambda e: e.position
    )
    assert [e.role for e in children] == ["annotation", "sub", "super"]
    assert [e.position for e in children] == [0, 1, 2]
    assert nodes[children[1].target].iri == "http://example.org/animals#Dog"
    assert nodes[children[2].target].iri == "http://example.org/animals#Pet"


def test_scalar_properties_are_captured(animals_owlxml: str) -> None:
    graph = parse_owlxml(animals_owlxml)

    ontology = next(n for n in graph.nodes if n.kind == "Ontology")
    assert ontology.properties["ontology_iri"] == "http://example.org/animals"

    cardinality = next(n for n in graph.nodes if n.kind == "ObjectMinCardinality")
    assert cardinality.properties["cardinality"] == 1

    labels = [
        n for n in graph.nodes if n.kind == "Literal" and n.properties.get("text") == "Animal"
    ]
    assert len(labels) == 1
    assert labels[0].properties["lang"] == "en"

    prefix = next(n for n in graph.nodes if n.kind == "Prefix")
    assert prefix.properties["prefix_name"] == "rdfs"
    assert prefix.properties["iri"] == "http://www.w3.org/2000/01/rdf-schema#"


def test_graph_round_trip_is_identity(animals_owlxml: str) -> None:
    graph = parse_owlxml(animals_owlxml)

    assert parse_owlxml(serialize_owlxml(graph)) == graph


def test_complex_constructs_round_trip(complex_owlxml: str) -> None:
    graph = parse_owlxml(complex_owlxml)

    assert _kinds(graph) >= {
        "EquivalentClasses",
        "ObjectIntersectionOf",
        "ObjectUnionOf",
        "ObjectOneOf",
        "ObjectSomeValuesFrom",
        "ObjectComplementOf",
        "DataSomeValuesFrom",
        "DatatypeRestriction",
        "FacetRestriction",
        "ObjectPropertyChain",
        "SubObjectPropertyOf",
        "InverseObjectProperties",
        "HasKey",
        "AnonymousIndividual",
    }
    assert parse_owlxml(serialize_owlxml(graph)) == graph


def test_anonymous_individuals_merge_by_node_id(complex_owlxml: str) -> None:
    graph = parse_owlxml(complex_owlxml)

    anonymous = [n for n in graph.nodes if n.kind == "AnonymousIndividual"]
    assert len(anonymous) == 1
    assert len([e for e in graph.edges if e.target == anonymous[0].uid]) == 2


def test_facet_restriction_keeps_facet_and_typed_literal(complex_owlxml: str) -> None:
    graph = parse_owlxml(complex_owlxml)

    facet = next(n for n in graph.nodes if n.kind == "FacetRestriction")
    assert facet.properties["facet"] == "http://www.w3.org/2001/XMLSchema#minInclusive"

    nodes = _nodes_by_uid(graph)
    (value_edge,) = [e for e in graph.edges if e.source == facet.uid]
    assert value_edge.role == "value"
    literal = nodes[value_edge.target]
    assert literal.properties["text"] == "100"
    assert literal.properties["datatype_iri"] == "http://www.w3.org/2001/XMLSchema#integer"


def test_nested_annotation_uses_annotation_roles(complex_owlxml: str) -> None:
    graph = parse_owlxml(complex_owlxml)
    nodes = _nodes_by_uid(graph)

    assertion = next(n for n in graph.nodes if n.kind == "AnnotationAssertion")
    roles = [
        e.role for e in sorted(graph.edges, key=lambda e: e.position) if e.source == assertion.uid
    ]
    assert roles == ["annotation", "property", "subject", "value"]

    nested = next(
        nodes[e.target] for e in graph.edges if e.source == assertion.uid and e.role == "annotation"
    )
    nested_roles = [e.role for e in graph.edges if e.source == nested.uid]
    assert sorted(nested_roles) == ["property", "value"]


def test_annotations_on_annotations_use_annotation_role() -> None:
    doc = """<?xml version="1.0"?>
    <Ontology xmlns="http://www.w3.org/2002/07/owl#" ontologyIRI="http://example.org/x">
        <AnnotationAssertion>
            <Annotation>
                <Annotation>
                    <AnnotationProperty IRI="http://example.org/x#meta"/>
                    <Literal>meta-comment</Literal>
                </Annotation>
                <AnnotationProperty IRI="http://example.org/x#source"/>
                <Literal>a source</Literal>
            </Annotation>
            <AnnotationProperty IRI="http://www.w3.org/2000/01/rdf-schema#comment"/>
            <IRI>http://example.org/x#A</IRI>
            <Literal>hello</Literal>
        </AnnotationAssertion>
    </Ontology>"""
    graph = parse_owlxml(doc)
    nodes = _nodes_by_uid(graph)

    assertion = next(n for n in graph.nodes if n.kind == "AnnotationAssertion")
    outer = next(
        e.target for e in graph.edges if e.source == assertion.uid and e.role == "annotation"
    )
    outer_children = sorted((e for e in graph.edges if e.source == outer), key=lambda e: e.position)
    assert [(nodes[e.target].kind, e.role) for e in outer_children] == [
        ("Annotation", "annotation"),
        ("AnnotationProperty", "property"),
        ("Literal", "value"),
    ]
    assert parse_owlxml(serialize_owlxml(graph)) == graph


def test_parse_rejects_non_ontology_root() -> None:
    with pytest.raises(OwlXmlStructureError, match="Ontology"):
        parse_owlxml("<Class IRI='http://example.org#A'/>")


def test_parse_rejects_unknown_attributes() -> None:
    with pytest.raises(OwlXmlStructureError, match="Unsupported attribute"):
        parse_owlxml('<Ontology xmlns="http://www.w3.org/2002/07/owl#" mystery="1"></Ontology>')


def test_serialize_rejects_cycles() -> None:
    graph = Graph(
        nodes=(
            Node(uid="o", kind="Ontology"),
            Node(uid="a", kind="SubClassOf"),
        ),
        edges=(
            Edge(source="o", target="a", position=0),
            Edge(source="a", target="a", position=0),
        ),
    )
    with pytest.raises(OwlXmlStructureError, match="Cycle"):
        serialize_owlxml(graph)


def test_serialize_rejects_missing_root() -> None:
    graph = Graph(nodes=(Node(uid="a", kind="Class"),), edges=())
    with pytest.raises(OwlXmlStructureError, match="exactly one parentless Ontology"):
        serialize_owlxml(graph)


def test_serialize_rejects_dangling_edge() -> None:
    graph = Graph(
        nodes=(Node(uid="o", kind="Ontology"),),
        edges=(Edge(source="o", target="ghost", position=0),),
    )
    with pytest.raises(OwlXmlStructureError, match="ghost"):
        serialize_owlxml(graph)
