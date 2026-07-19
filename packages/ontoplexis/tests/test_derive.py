"""Derived-edge layer tests (no jar, no reasoner)."""

from __future__ import annotations

from ontoplexis import Ontology, WritableProjection, derive_edges

_OWLXML = """<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#" ontologyIRI="http://ex.org/o">
    <Prefix name="" IRI="http://ex.org/o#"/>
    <Declaration><Class abbreviatedIRI=":Animal"/></Declaration>
    <Declaration><Class abbreviatedIRI=":Dog"/></Declaration>
    <Declaration><Class abbreviatedIRI=":Cat"/></Declaration>
    <Declaration><Class abbreviatedIRI=":Pet"/></Declaration>
    <Declaration><NamedIndividual abbreviatedIRI=":rex"/></Declaration>
    <Declaration><ObjectProperty abbreviatedIRI=":cares_for"/></Declaration>
    <SubClassOf><Class abbreviatedIRI=":Dog"/><Class abbreviatedIRI=":Animal"/></SubClassOf>
    <SubClassOf><Class abbreviatedIRI=":Cat"/><Class abbreviatedIRI=":Animal"/></SubClassOf>
    <EquivalentClasses><Class abbreviatedIRI=":Pet"/><Class abbreviatedIRI=":Animal"/></EquivalentClasses>
    <DisjointClasses><Class abbreviatedIRI=":Dog"/><Class abbreviatedIRI=":Cat"/></DisjointClasses>
    <ClassAssertion><Class abbreviatedIRI=":Dog"/><NamedIndividual abbreviatedIRI=":rex"/></ClassAssertion>
    <ObjectPropertyDomain>
        <ObjectProperty abbreviatedIRI=":cares_for"/><Class abbreviatedIRI=":Pet"/>
    </ObjectPropertyDomain>
    <TransitiveObjectProperty><ObjectProperty abbreviatedIRI=":cares_for"/></TransitiveObjectProperty>
    <AnnotationAssertion>
        <AnnotationProperty IRI="http://www.w3.org/2000/01/rdf-schema#label"/>
        <IRI>http://ex.org/o#Dog</IRI>
        <Literal xml:lang="en">Dog</Literal>
    </AnnotationAssertion>
</Ontology>
"""


def _derived(path: str) -> dict[str, int]:
    with WritableProjection.open(path) as writable:
        return derive_edges(writable)


def test_derive_produces_expected_relations(tmp_path) -> None:
    out = str(tmp_path / "o.lbug")
    Ontology.from_owlxml(_OWLXML).save_projection(out).close()

    counts = _derived(out)

    assert counts["subclass_of"] == 2  # Dog->Animal, Cat->Animal
    assert counts["equivalent_class"] == 2  # symmetric: both directions
    assert counts["disjoint_class"] == 2  # symmetric: both directions
    assert counts["type"] == 1  # rex : Dog
    assert counts["domain"] == 1  # cares_for domain Pet
    assert counts["transitive"] == 1  # cares_for self-loop
    assert counts["annotation_value"] == 1  # Dog rdfs:label "Dog"@en


def test_save_projection_derives_by_construction(tmp_path) -> None:
    out = str(tmp_path / "o.lbug")

    projection = Ontology.from_owlxml(_OWLXML).save_projection(out)
    try:
        assert projection.derived_count > 0
    finally:
        projection.close()


def test_project_derives_by_construction() -> None:
    with Ontology.from_owlxml(_OWLXML).project() as projection:
        assert projection.derived_count > 0


def test_characteristic_axioms_become_self_loops(tmp_path) -> None:
    out = str(tmp_path / "o.lbug")
    Ontology.from_owlxml(_OWLXML).save_projection(out).close()

    with WritableProjection.open(out) as p:
        rows = p.execute("MATCH (p:N)-[:D {relation:'transitive'}]->(p) RETURN p.iri AS iri")
    assert [r["iri"] for r in rows] == ["http://ex.org/o#cares_for"]


def test_literal_annotations_are_one_hop(tmp_path) -> None:
    out = str(tmp_path / "o.lbug")
    Ontology.from_owlxml(_OWLXML).save_projection(out).close()

    with WritableProjection.open(out) as p:
        rows = p.execute(
            "MATCH (s:N)-[a:D {relation:'annotation_value'}]->(v:N) "
            "RETURN s.iri AS subject, a.property AS property, v.text AS value, v.lang AS lang"
        )
    assert rows == [
        {
            "subject": "http://ex.org/o#Dog",
            "property": "http://www.w3.org/2000/01/rdf-schema#label",
            "value": "Dog",
            "lang": "en",
        }
    ]


def test_subclass_edges_enable_transitive_traversal(tmp_path) -> None:
    out = str(tmp_path / "o.lbug")
    Ontology.from_owlxml(_OWLXML).save_projection(out).close()
    _derived(out)

    with WritableProjection.open(out) as p:
        rows = p.execute(
            "MATCH (d:N {iri:'http://ex.org/o#Dog'})"
            "-[:D*1..5 {relation:'subclass_of'}]->(a:N) "
            "RETURN DISTINCT a.iri AS ancestor ORDER BY ancestor"
        )
    assert [r["ancestor"] for r in rows] == ["http://ex.org/o#Animal"]


def test_derivation_is_idempotent(tmp_path) -> None:
    out = str(tmp_path / "o.lbug")
    Ontology.from_owlxml(_OWLXML).save_projection(out).close()

    first = _derived(out)
    second = _derived(out)  # drop-and-rebuild must not accumulate

    assert first == second


_PUNNED_OWLXML = """<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#" ontologyIRI="http://ex.org/o">
    <Prefix name="" IRI="http://ex.org/o#"/>
    <Declaration><Class abbreviatedIRI=":Dog"/></Declaration>
    <Declaration><NamedIndividual abbreviatedIRI=":Dog"/></Declaration>
    <AnnotationAssertion>
        <AnnotationProperty IRI="http://www.w3.org/2000/01/rdf-schema#label"/>
        <IRI>http://ex.org/o#Dog</IRI>
        <Literal xml:lang="en">Dog</Literal>
    </AnnotationAssertion>
</Ontology>
"""


def test_annotations_fan_out_across_puns() -> None:
    # Annotation subjects name IRIs, not entities: a punned Class and
    # NamedIndividual each receive the edge from a single assertion.
    with Ontology.from_owlxml(_PUNNED_OWLXML).project() as p:
        rows = p.execute(
            "MATCH (s:N)-[a:D {relation:'annotation_value'}]->(v:N) "
            "RETURN s.kind AS kind, s.iri AS iri, v.text AS value ORDER BY kind"
        )
    assert rows == [
        {"kind": "Class", "iri": "http://ex.org/o#Dog", "value": "Dog"},
        {"kind": "NamedIndividual", "iri": "http://ex.org/o#Dog", "value": "Dog"},
    ]


def test_derived_layer_is_invisible_to_round_trip(tmp_path) -> None:
    out = str(tmp_path / "o.lbug")
    ontology = Ontology.from_owlxml(_OWLXML)
    ontology.save_projection(out).close()

    with WritableProjection.open(out) as p:
        before = p.edge_count
        derive_edges(p)
        # graph() reconstructs from N/E only, so the structural edge set is unchanged
        recovered = p.graph()

    assert len(recovered.edges) == before
    assert not any(e.role == "subclass_of" for e in recovered.edges)
    # and the recovered structural graph still serializes
    assert "SubClassOf" in Ontology(recovered).to_owlxml()


_PREFIX_COLLISION_OWLXML = """<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#" ontologyIRI="http://ex.org/o">
    <Prefix name="ex" IRI="http://ex.org/o#Dog"/>
    <Declaration><Class IRI="http://ex.org/o#Dog"/></Declaration>
    <AnnotationAssertion>
        <AnnotationProperty IRI="http://www.w3.org/2000/01/rdf-schema#label"/>
        <IRI>http://ex.org/o#Dog</IRI>
        <Literal xml:lang="en">Dog</Literal>
    </AnnotationAssertion>
</Ontology>
"""


def test_annotation_fan_out_skips_non_entity_iri_carriers() -> None:
    # A Prefix node stores its namespace in the iri column; a namespace equal
    # to an annotated entity IRI must not pull the Prefix into the fan-out.
    with Ontology.from_owlxml(_PREFIX_COLLISION_OWLXML).project() as p:
        rows = p.execute(
            "MATCH (s:N)-[:D {relation:'annotation_value'}]->(:N) RETURN s.kind AS kind"
        )
    assert [r["kind"] for r in rows] == ["Class"]


_REPEATED_OPERAND_OWLXML = """<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#" ontologyIRI="http://ex.org/o">
    <EquivalentClasses>
        <Class IRI="http://ex.org/o#A"/>
        <Class IRI="http://ex.org/o#B"/>
        <Class IRI="http://ex.org/o#A"/>
    </EquivalentClasses>
</Ontology>
"""


def test_repeated_operands_do_not_duplicate_derived_edges() -> None:
    # EquivalentClasses(A B A) merges the repeated operand to one node with
    # parallel E edges. Each pair of distinct operands must still yield exactly
    # one derived edge per direction, not one per edge-instance combination.
    with Ontology.from_owlxml(_REPEATED_OPERAND_OWLXML).project() as p:
        rows = p.execute(
            "MATCH (a:N)-[:D {relation:'equivalent_class'}]->(b:N) "
            "RETURN a.iri AS a_iri, b.iri AS b_iri ORDER BY a_iri, b_iri"
        )
    assert [(r["a_iri"], r["b_iri"]) for r in rows] == [
        ("http://ex.org/o#A", "http://ex.org/o#B"),
        ("http://ex.org/o#B", "http://ex.org/o#A"),
    ]


_FULL_RELATION_OWLXML = """<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#" ontologyIRI="http://ex.org/r">
    <Prefix name="" IRI="http://ex.org/r#"/>
    <DisjointUnion>
        <Class abbreviatedIRI=":Parent"/>
        <Class abbreviatedIRI=":Left"/>
        <Class abbreviatedIRI=":Right"/>
    </DisjointUnion>
    <SubObjectPropertyOf>
        <ObjectProperty abbreviatedIRI=":hasDog"/><ObjectProperty abbreviatedIRI=":hasPet"/>
    </SubObjectPropertyOf>
    <SubDataPropertyOf>
        <DataProperty abbreviatedIRI=":shoeSize"/><DataProperty abbreviatedIRI=":size"/>
    </SubDataPropertyOf>
    <SubAnnotationPropertyOf>
        <AnnotationProperty abbreviatedIRI=":note"/><AnnotationProperty abbreviatedIRI=":remark"/>
    </SubAnnotationPropertyOf>
    <EquivalentObjectProperties>
        <ObjectProperty abbreviatedIRI=":hasPet"/><ObjectProperty abbreviatedIRI=":keeps"/>
    </EquivalentObjectProperties>
    <DisjointDataProperties>
        <DataProperty abbreviatedIRI=":size"/><DataProperty abbreviatedIRI=":age"/>
    </DisjointDataProperties>
    <InverseObjectProperties>
        <ObjectProperty abbreviatedIRI=":hasPet"/><ObjectProperty abbreviatedIRI=":petOf"/>
    </InverseObjectProperties>
    <FunctionalObjectProperty><ObjectProperty abbreviatedIRI=":hasDog"/></FunctionalObjectProperty>
    <FunctionalDataProperty><DataProperty abbreviatedIRI=":age"/></FunctionalDataProperty>
    <InverseFunctionalObjectProperty>
        <ObjectProperty abbreviatedIRI=":petOf"/>
    </InverseFunctionalObjectProperty>
    <ReflexiveObjectProperty><ObjectProperty abbreviatedIRI=":knows"/></ReflexiveObjectProperty>
    <IrreflexiveObjectProperty><ObjectProperty abbreviatedIRI=":petOf"/></IrreflexiveObjectProperty>
    <SymmetricObjectProperty><ObjectProperty abbreviatedIRI=":knows"/></SymmetricObjectProperty>
    <AsymmetricObjectProperty><ObjectProperty abbreviatedIRI=":hasDog"/></AsymmetricObjectProperty>
    <ObjectPropertyRange>
        <ObjectProperty abbreviatedIRI=":hasPet"/><Class abbreviatedIRI=":Left"/>
    </ObjectPropertyRange>
    <DataPropertyRange>
        <DataProperty abbreviatedIRI=":age"/>
        <Datatype IRI="http://www.w3.org/2001/XMLSchema#integer"/>
    </DataPropertyRange>
    <ObjectPropertyAssertion>
        <ObjectProperty abbreviatedIRI=":hasPet"/>
        <NamedIndividual abbreviatedIRI=":alice"/>
        <NamedIndividual abbreviatedIRI=":rex"/>
    </ObjectPropertyAssertion>
    <DataPropertyAssertion>
        <DataProperty abbreviatedIRI=":age"/>
        <NamedIndividual abbreviatedIRI=":alice"/>
        <Literal datatypeIRI="http://www.w3.org/2001/XMLSchema#integer">42</Literal>
    </DataPropertyAssertion>
    <SameIndividual>
        <NamedIndividual abbreviatedIRI=":alice"/><NamedIndividual abbreviatedIRI=":al"/>
    </SameIndividual>
    <DifferentIndividuals>
        <NamedIndividual abbreviatedIRI=":alice"/><NamedIndividual abbreviatedIRI=":rex"/>
    </DifferentIndividuals>
    <AnnotationAssertion>
        <AnnotationProperty IRI="http://www.w3.org/2000/01/rdf-schema#seeAlso"/>
        <IRI>http://ex.org/r#Left</IRI>
        <IRI>http://ex.org/r#Right</IRI>
    </AnnotationAssertion>
    <SubClassOf>
        <Class abbreviatedIRI=":Left"/>
        <ObjectSomeValuesFrom>
            <ObjectProperty abbreviatedIRI=":hasPet"/><Class abbreviatedIRI=":Right"/>
        </ObjectSomeValuesFrom>
    </SubClassOf>
    <SubClassOf>
        <Class abbreviatedIRI=":Right"/>
        <ObjectAllValuesFrom>
            <ObjectProperty abbreviatedIRI=":hasDog"/><Class abbreviatedIRI=":Left"/>
        </ObjectAllValuesFrom>
    </SubClassOf>
</Ontology>
"""


def _relation_pairs(relation: str) -> list[tuple[str, str]]:
    with Ontology.from_owlxml(_FULL_RELATION_OWLXML).project() as p:
        rows = p.execute(
            "MATCH (a:N)-[:D {relation: $relation}]->(b:N) "
            "RETURN a.iri AS a_iri, b.iri AS b_iri ORDER BY a_iri, b_iri",
            parameters={"relation": relation},
        )
    return [(r["a_iri"], r["b_iri"]) for r in rows]


def _r(name: str) -> str:
    return f"http://ex.org/r#{name}"


def test_disjoint_union_members_derive_subclass_and_disjointness() -> None:
    assert _relation_pairs("subclass_of") == [
        (_r("Left"), _r("Parent")),
        (_r("Right"), _r("Parent")),
    ]
    assert _relation_pairs("disjoint_class") == [
        (_r("Left"), _r("Right")),
        (_r("Right"), _r("Left")),
    ]


def test_subproperty_edges_derive_for_all_three_property_families() -> None:
    assert _relation_pairs("subproperty_of") == [
        (_r("hasDog"), _r("hasPet")),
        (_r("note"), _r("remark")),
        (_r("shoeSize"), _r("size")),
    ]


def test_property_equivalence_disjointness_and_inversion_are_symmetric() -> None:
    assert _relation_pairs("equivalent_property") == [
        (_r("hasPet"), _r("keeps")),
        (_r("keeps"), _r("hasPet")),
    ]
    assert _relation_pairs("disjoint_property") == [
        (_r("age"), _r("size")),
        (_r("size"), _r("age")),
    ]
    assert _relation_pairs("inverse_of") == [
        (_r("hasPet"), _r("petOf")),
        (_r("petOf"), _r("hasPet")),
    ]


def test_every_characteristic_axiom_derives_its_self_loop() -> None:
    # FunctionalObjectProperty and FunctionalDataProperty share 'functional',
    # mirroring the shared RDF vocabulary term.
    assert _relation_pairs("functional") == [
        (_r("age"), _r("age")),
        (_r("hasDog"), _r("hasDog")),
    ]
    assert _relation_pairs("inverse_functional") == [(_r("petOf"), _r("petOf"))]
    assert _relation_pairs("reflexive") == [(_r("knows"), _r("knows"))]
    assert _relation_pairs("irreflexive") == [(_r("petOf"), _r("petOf"))]
    assert _relation_pairs("symmetric") == [(_r("knows"), _r("knows"))]
    assert _relation_pairs("asymmetric") == [(_r("hasDog"), _r("hasDog"))]


def test_range_edges_derive_for_object_and_data_properties() -> None:
    assert _relation_pairs("range") == [
        (_r("age"), "http://www.w3.org/2001/XMLSchema#integer"),
        (_r("hasPet"), _r("Left")),
    ]


def test_individual_assertions_derive_one_hop_edges() -> None:
    with Ontology.from_owlxml(_FULL_RELATION_OWLXML).project() as p:
        asserts = p.execute(
            "MATCH (a:N)-[d:D {relation:'asserts'}]->(b:N) "
            "RETURN a.iri AS a_iri, d.property AS property, b.iri AS b_iri"
        )
        values = p.execute(
            "MATCH (a:N)-[d:D {relation:'data_value'}]->(v:N) "
            "RETURN a.iri AS a_iri, d.property AS property, v.text AS text"
        )
    assert asserts == [{"a_iri": _r("alice"), "property": _r("hasPet"), "b_iri": _r("rex")}]
    assert values == [{"a_iri": _r("alice"), "property": _r("age"), "text": "42"}]


def test_individual_identity_axioms_derive_symmetric_edges() -> None:
    assert _relation_pairs("same_as") == [
        (_r("al"), _r("alice")),
        (_r("alice"), _r("al")),
    ]
    assert _relation_pairs("different_from") == [
        (_r("alice"), _r("rex")),
        (_r("rex"), _r("alice")),
    ]


def test_iri_valued_annotations_derive_entity_to_entity_edges() -> None:
    with Ontology.from_owlxml(_FULL_RELATION_OWLXML).project() as p:
        rows = p.execute(
            "MATCH (a:N)-[d:D {relation:'annotation'}]->(b:N) "
            "RETURN a.iri AS a_iri, d.property AS property, b.iri AS b_iri"
        )
    assert rows == [
        {
            "a_iri": _r("Left"),
            "property": "http://www.w3.org/2000/01/rdf-schema#seeAlso",
            "b_iri": _r("Right"),
        }
    ]


def test_existential_and_universal_restrictions_derive_quantified_edges() -> None:
    with Ontology.from_owlxml(_FULL_RELATION_OWLXML).project() as p:
        rows = p.execute(
            "MATCH (a:N)-[d:D {relation:'restriction'}]->(b:N) "
            "RETURN a.iri AS a_iri, d.property AS property, d.quantifier AS quantifier, "
            "b.iri AS b_iri ORDER BY a_iri"
        )
    assert rows == [
        {
            "a_iri": _r("Left"),
            "property": _r("hasPet"),
            "quantifier": "some",
            "b_iri": _r("Right"),
        },
        {
            "a_iri": _r("Right"),
            "property": _r("hasDog"),
            "quantifier": "only",
            "b_iri": _r("Left"),
        },
    ]
