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


def test_parse_rejects_non_integer_cardinality() -> None:
    doc = (
        '<Ontology xmlns="http://www.w3.org/2002/07/owl#" ontologyIRI="http://example.org/o">'
        '<SubClassOf><Class IRI="http://example.org/o#A"/>'
        '<ObjectMinCardinality cardinality="abc">'
        '<ObjectProperty IRI="http://example.org/o#p"/>'
        "</ObjectMinCardinality></SubClassOf></Ontology>"
    )
    with pytest.raises(OwlXmlStructureError, match="cardinality"):
        parse_owlxml(doc)


def test_parse_rejects_conflicting_iri_attributes() -> None:
    doc = (
        '<Ontology xmlns="http://www.w3.org/2002/07/owl#" ontologyIRI="http://example.org/o">'
        '<Prefix name="ex" IRI="http://example.org/o#"/>'
        '<Declaration><Class IRI="http://example.org/o#A" abbreviatedIRI="ex:B"/></Declaration>'
        "</Ontology>"
    )
    with pytest.raises(OwlXmlStructureError, match="both IRI and abbreviatedIRI"):
        parse_owlxml(doc)


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


def test_serialize_rejects_unreachable_nodes() -> None:
    """Authoring mistakes must surface as errors, not vanish from the document."""
    graph = Graph(
        nodes=(
            Node(uid="o", kind="Ontology"),
            Node(uid="c", kind="Class", properties={"iri": "http://example.org/o#A"}),
        ),
        edges=(),
    )
    with pytest.raises(OwlXmlStructureError, match="unreachable"):
        serialize_owlxml(graph)


def test_serialize_rejects_dangling_edge() -> None:
    graph = Graph(
        nodes=(Node(uid="o", kind="Ontology"),),
        edges=(Edge(source="o", target="ghost", position=0),),
    )
    with pytest.raises(OwlXmlStructureError, match="ghost"):
        serialize_owlxml(graph)


_ABBREVIATED_OWLXML = """<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#"
          ontologyIRI="http://example.org/o">
    <Prefix name="obo" IRI="http://purl.obolibrary.org/obo/"/>
    <Prefix name="rdfs" IRI="http://www.w3.org/2000/01/rdf-schema#"/>
    <Declaration><Class abbreviatedIRI="obo:GO_0000001"/></Declaration>
    <Declaration><Class IRI="http://purl.obolibrary.org/obo/GO_0000002"/></Declaration>
    <SubClassOf>
        <Class abbreviatedIRI="obo:GO_0000002"/>
        <Class IRI="http://purl.obolibrary.org/obo/GO_0000001"/>
    </SubClassOf>
    <AnnotationAssertion>
        <AnnotationProperty abbreviatedIRI="rdfs:label"/>
        <AbbreviatedIRI>obo:GO_0000001</AbbreviatedIRI>
        <Literal>first</Literal>
    </AnnotationAssertion>
</Ontology>
"""


def test_abbreviated_iri_attribute_resolves_to_full_iri() -> None:
    graph = parse_owlxml(_ABBREVIATED_OWLXML)

    classes = {n.iri for n in graph.nodes if n.kind == "Class"}
    assert classes == {
        "http://purl.obolibrary.org/obo/GO_0000001",
        "http://purl.obolibrary.org/obo/GO_0000002",
    }
    assert not any("abbreviated_iri" in n.properties for n in graph.nodes)


def test_abbreviated_and_full_reference_merge_to_one_entity() -> None:
    graph = parse_owlxml(_ABBREVIATED_OWLXML)

    # GO_0000002 is declared with a full IRI and referenced with an abbreviated
    # one; both must resolve to the same merged node.
    go2 = [
        n
        for n in graph.nodes
        if n.kind == "Class" and n.iri == "http://purl.obolibrary.org/obo/GO_0000002"
    ]
    assert len(go2) == 1


def test_abbreviated_iri_leaf_becomes_resolved_iri_value() -> None:
    graph = parse_owlxml(_ABBREVIATED_OWLXML)

    assert not any(n.kind == "AbbreviatedIRI" for n in graph.nodes)
    subjects = [
        n
        for n in graph.nodes
        if n.kind == "IRI"
        and n.properties.get("text") == "http://purl.obolibrary.org/obo/GO_0000001"
    ]
    assert len(subjects) == 1


def test_resolved_iris_survive_serialization_round_trip() -> None:
    once = serialize_owlxml(parse_owlxml(_ABBREVIATED_OWLXML))

    assert "abbreviatedIRI" not in once
    assert "http://purl.obolibrary.org/obo/GO_0000001" in once
    # Reparsing the resolved document is stable.
    assert serialize_owlxml(parse_owlxml(once)) == once


def test_undeclared_prefix_is_rejected() -> None:
    document = _ABBREVIATED_OWLXML.replace(
        'abbreviatedIRI="obo:GO_0000001"', 'abbreviatedIRI="zz:X"'
    )
    with pytest.raises(OwlXmlStructureError, match="undeclared prefix"):
        parse_owlxml(document)


def test_doctype_is_rejected() -> None:
    # OWL/XML never needs a DTD; rejecting DOCTYPE outright closes the
    # entity-expansion (billion-laughs) and external-entity (XXE) vectors.
    billion_laughs = (
        '<?xml version="1.0"?>\n'
        "<!DOCTYPE Ontology [\n"
        '  <!ENTITY a "aaaaaaaaaa">\n'
        '  <!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;">\n'
        '  <!ENTITY c "&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;">\n'
        "]>\n"
        '<Ontology xmlns="http://www.w3.org/2002/07/owl#">&c;</Ontology>'
    )
    with pytest.raises(OwlXmlStructureError, match="DOCTYPE"):
        parse_owlxml(billion_laughs)

    xxe = (
        '<?xml version="1.0"?>\n'
        '<!DOCTYPE Ontology [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>\n'
        '<Ontology xmlns="http://www.w3.org/2002/07/owl#">&xxe;</Ontology>'
    )
    with pytest.raises(OwlXmlStructureError, match="DOCTYPE"):
        parse_owlxml(xxe)


def test_malformed_xml_is_still_reported_as_such() -> None:
    with pytest.raises(OwlXmlStructureError, match="Not well-formed"):
        parse_owlxml("<Ontology")


_NARY_DATA_RESTRICTION_OWLXML = """<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#" ontologyIRI="http://example.org/nary">
    <SubClassOf>
        <Class IRI="http://example.org/Person"/>
        <DataSomeValuesFrom>
            <DataProperty IRI="http://example.org/hasGivenName"/>
            <DataProperty IRI="http://example.org/hasFamilyName"/>
            <Datatype IRI="http://www.w3.org/2001/XMLSchema#string"/>
        </DataSomeValuesFrom>
    </SubClassOf>
</Ontology>
"""


def test_nary_data_restriction_roles_discriminate_by_child_kind() -> None:
    # OWL 2 sections 8.4.1/8.4.2: DataSomeValuesFrom and DataAllValuesFrom
    # take one or more data property expressions followed by the data range,
    # so roles cannot be assigned positionally.
    graph = parse_owlxml(_NARY_DATA_RESTRICTION_OWLXML)
    nodes = _nodes_by_uid(graph)

    restriction = next(n for n in graph.nodes if n.kind == "DataSomeValuesFrom")
    children = sorted(
        (e for e in graph.edges if e.source == restriction.uid), key=lambda e: e.position
    )
    assert [e.role for e in children] == ["property", "property", "filler"]
    assert [nodes[e.target].kind for e in children] == ["DataProperty", "DataProperty", "Datatype"]


def test_nary_data_restriction_round_trips() -> None:
    once = serialize_owlxml(parse_owlxml(_NARY_DATA_RESTRICTION_OWLXML))
    assert serialize_owlxml(parse_owlxml(once)) == once


_RELATIVE_PREFIX_OWLXML = """<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#"
          xml:base="http://example.org/onto/"
          ontologyIRI="http://example.org/onto">
    <Prefix name="ex" IRI="terms#"/>
    <Declaration><Class abbreviatedIRI="ex:Foo"/></Declaration>
    <Declaration><Class IRI="terms#Foo"/></Declaration>
</Ontology>
"""


def test_prefix_namespaces_resolve_against_xml_base() -> None:
    # A term referenced via a CURIE and via a (relative) direct IRI must land
    # on the same absolute IRI and merge to one node; the trailing "#" of the
    # namespace must survive base resolution.
    graph = parse_owlxml(_RELATIVE_PREFIX_OWLXML)

    classes = [n for n in graph.nodes if n.kind == "Class"]
    assert len(classes) == 1
    assert classes[0].iri == "http://example.org/onto/terms#Foo"
    prefix = next(n for n in graph.nodes if n.kind == "Prefix")
    assert prefix.properties["iri"] == "http://example.org/onto/terms#"


def test_prefix_without_iri_attribute_is_rejected() -> None:
    document = _RELATIVE_PREFIX_OWLXML.replace('IRI="terms#"', "")
    with pytest.raises(OwlXmlStructureError, match="missing its IRI attribute"):
        parse_owlxml(document)


def test_duplicate_prefix_declaration_is_rejected() -> None:
    document = _RELATIVE_PREFIX_OWLXML.replace(
        '<Prefix name="ex" IRI="terms#"/>',
        '<Prefix name="ex" IRI="terms#"/><Prefix name="ex" IRI="other#"/>',
    )
    with pytest.raises(OwlXmlStructureError, match="declared more than once"):
        parse_owlxml(document)


def test_mixed_content_is_rejected() -> None:
    document = (
        '<?xml version="1.0"?>\n'
        '<Ontology xmlns="http://www.w3.org/2002/07/owl#">'
        '<Declaration>stray<Class IRI="http://example.org/A"/></Declaration>'
        "</Ontology>"
    )
    with pytest.raises(OwlXmlStructureError, match="mixes text content"):
        parse_owlxml(document)

    tail_document = document.replace(
        'stray<Class IRI="http://example.org/A"/>',
        '<Class IRI="http://example.org/A"/>stray',
    )
    with pytest.raises(OwlXmlStructureError, match="mixes text content"):
        parse_owlxml(tail_document)


def test_parse_rejects_elements_outside_the_owl_namespace() -> None:
    # Without this, a document in a foreign vocabulary that reuses OWL element
    # names would parse and round-trip rebranded into the OWL namespace.
    with pytest.raises(OwlXmlStructureError, match="namespace"):
        parse_owlxml(
            '<Ontology xmlns="http://evil.example/ns#">'
            '<Declaration><Class IRI="http://example.org/A"/></Declaration>'
            "</Ontology>"
        )
    with pytest.raises(OwlXmlStructureError, match="namespace"):
        parse_owlxml("<Ontology/>")


def test_serialize_rejects_text_alongside_children() -> None:
    # Mirrors the parser's mixed-content rejection: an authored node carrying
    # both text and child edges would serialize to a document parse refuses.
    graph = Graph(
        nodes=(
            Node(uid="o", kind="Ontology"),
            Node(uid="d", kind="Declaration", properties={"text": "stray"}),
            Node(uid="c", kind="Class", properties={"iri": "http://example.org/A"}),
        ),
        edges=(
            Edge(source="o", target="d", position=0, role="axiom"),
            Edge(source="d", target="c", position=0, role="entity"),
        ),
    )
    with pytest.raises(OwlXmlStructureError, match="mixes text content"):
        serialize_owlxml(graph)
