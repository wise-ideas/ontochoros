from __future__ import annotations

from ontoplexis import Edge, Graph, Node
from ontoplexis.graph import build_projection
from ontoplexis.owlxml import role_for

from ontopoiesis.lint import lint_dir

# Each fixture construct is one projection node plus its ordered children.
# Roles come from ontoplexis's own `role_for`, so fixtures can never drift
# from the walker's edge vocabulary.
Construct = tuple[Node, list[str]]


def _c(uid: str, kind: str, children: list[str] | None = None, **properties) -> Construct:
    return (Node(uid=uid, kind=kind, properties=properties), children or [])


def _graph(constructs: list[Construct]) -> Graph:
    nodes = tuple(node for node, _ in constructs)
    kind_by_uid = {node.uid: node.kind for node in nodes}
    edges = []
    for node, children in constructs:
        for index, child_uid in enumerate(children):
            edges.append(
                Edge(
                    source=node.uid,
                    target=child_uid,
                    position=index,
                    role=role_for(node.kind, kind_by_uid[child_uid], index),
                )
            )
    return Graph(nodes=nodes, edges=tuple(edges))


def _run_query(query_name: str, constructs: list[Construct]) -> list[dict[str, object]]:
    query_root = lint_dir().parent
    query_path = lint_dir() / query_name if "/" not in query_name else query_root / query_name
    query = query_path.read_text()
    with build_projection(_graph(constructs)) as projection:
        return projection.execute(query)


def test_negative_data_property_assertion_matches_equivalent_typed_literals() -> None:
    constructs = [
        _c("0x2", "DataProperty", iri="https://example.org#age"),
        _c("0x3", "NamedIndividual", iri="https://example.org#alice"),
        _c("0x4", "Literal", text="42", datatype_iri="http://www.w3.org/2001/XMLSchema#string"),
        _c("0x5", "Literal", text="42", datatype_iri="http://www.w3.org/2001/XMLSchema#string"),
        _c("0x6", "DataPropertyAssertion", ["0x2", "0x3", "0x4"]),
        _c("0x7", "NegativeDataPropertyAssertion", ["0x2", "0x3", "0x5"]),
    ]

    rows = _run_query("test_negative_data_property_assertion_contradiction.cypher", constructs)

    assert rows == [
        {
            "property_iri": "https://example.org#age",
            "source_iri": "https://example.org#alice",
            "target_literal": "42^^http://www.w3.org/2001/XMLSchema#string",
        }
    ]


def test_warn_annotation_assertion_unknown_subject_allows_known_entities_without_declaration() -> (
    None
):
    constructs = [
        _c("0x1", "Class", iri="https://example.org#Undeclared"),
        _c("0x2", "AnnotationProperty", iri="http://www.w3.org/2000/01/rdf-schema#label"),
        _c("0x3", "IRI", text="https://example.org#Undeclared"),
        _c("0x4", "Literal", text="Undeclared"),
        _c("0x5", "AnnotationAssertion", ["0x2", "0x3", "0x4"]),
    ]

    rows = _run_query(
        "lint_profiles/editorial/warn_annotation_assertion_unknown_subject.cypher", constructs
    )

    assert rows == []


def test_warn_annotation_assertion_unknown_subject_handles_non_http_iris() -> None:
    constructs = [
        _c("0x1", "AnnotationProperty", iri="https://example.org#note"),
        _c("0x2", "IRI", text="tag:example.org,2026:Undeclared"),
        _c("0x3", "Literal", text="Undeclared"),
        _c("0x4", "AnnotationAssertion", ["0x1", "0x2", "0x3"]),
    ]

    rows = _run_query(
        "lint_profiles/editorial/warn_annotation_assertion_unknown_subject.cypher", constructs
    )

    assert rows == [{"subject_iri": "tag:example.org,2026:Undeclared"}]


def test_warn_annotation_assertion_unknown_subject_exempts_xsd_builtins() -> None:
    constructs = [
        _c("0x1", "AnnotationProperty", iri="https://example.org#note"),
        _c("0x2", "IRI", text="http://www.w3.org/2001/XMLSchema#string"),
        _c("0x3", "Literal", text="builtin"),
        _c("0x4", "AnnotationAssertion", ["0x1", "0x2", "0x3"]),
    ]

    rows = _run_query(
        "lint_profiles/editorial/warn_annotation_assertion_unknown_subject.cypher", constructs
    )

    assert rows == []


def test_subclass_cycle_indirect_reports_one_row_per_member_set() -> None:
    constructs = [
        _c("0x1", "Class", iri="https://example.org#A"),
        _c("0x2", "Class", iri="https://example.org#B"),
        _c("0x3", "Class", iri="https://example.org#C"),
    ]
    for uid, sub_uid, sup_uid in [
        ("0x10", "0x1", "0x2"),
        ("0x11", "0x2", "0x1"),
        ("0x12", "0x1", "0x3"),
        ("0x13", "0x3", "0x1"),
        ("0x14", "0x2", "0x3"),
        ("0x15", "0x3", "0x2"),
    ]:
        constructs.append(_c(uid, "SubClassOf", [sub_uid, sup_uid]))

    rows = _run_query("lint_profiles/modeling_risk/warn_subclass_cycle_indirect.cypher", constructs)

    assert rows == [
        {
            "class_a": "https://example.org#A",
            "class_b": "https://example.org#B",
            "class_c": "https://example.org#C",
        }
    ]


def test_subclass_cycle_indirect_matches_non_sorted_cycle_orientation() -> None:
    constructs = [
        _c("0x1", "Class", iri="https://example.org#A"),
        _c("0x2", "Class", iri="https://example.org#B"),
        _c("0x3", "Class", iri="https://example.org#C"),
        _c("0x10", "SubClassOf", ["0x1", "0x3"]),
        _c("0x11", "SubClassOf", ["0x3", "0x2"]),
        _c("0x12", "SubClassOf", ["0x2", "0x1"]),
    ]

    rows = _run_query("lint_profiles/modeling_risk/warn_subclass_cycle_indirect.cypher", constructs)

    assert rows == [
        {
            "class_a": "https://example.org#A",
            "class_b": "https://example.org#B",
            "class_c": "https://example.org#C",
        }
    ]


def test_warn_duplicate_label_language_matches_untagged_duplicate_labels() -> None:
    constructs = [
        _c("0x1", "Class", iri="https://example.org#C"),
        _c("0x2", "AnnotationProperty", iri="http://www.w3.org/2000/01/rdf-schema#label"),
        _c("0x3", "IRI", text="https://example.org#C"),
        _c("0x4", "IRI", text="https://example.org#C"),
        _c("0x5", "Literal", text="C"),
        _c("0x6", "Literal", text="Class C"),
        _c("0x7", "AnnotationAssertion", ["0x2", "0x3", "0x5"]),
        _c("0x8", "AnnotationAssertion", ["0x2", "0x4", "0x6"]),
    ]

    rows = _run_query("lint_profiles/editorial/warn_duplicate_label_language.cypher", constructs)

    assert rows == [
        {
            "entity_iri": "https://example.org#C",
            "language_tag": "",
            "label_count": 2,
        }
    ]


def test_warn_duplicate_subclass_axiom_reports_each_pair_once() -> None:
    constructs = [
        _c("0x1", "Class", iri="https://example.org#A"),
        _c("0x2", "Class", iri="https://example.org#B"),
        _c("0x10", "SubClassOf", ["0x1", "0x2"]),
        _c("0x11", "SubClassOf", ["0x1", "0x2"]),
        _c("0x12", "SubClassOf", ["0x1", "0x2"]),
    ]

    rows = _run_query("warn_duplicate_subclass_axiom.cypher", constructs)

    assert rows == [
        {
            "sub_class": "https://example.org#A",
            "super_class": "https://example.org#B",
        }
    ]


def test_warn_ontology_no_metadata_annotations_requires_known_metadata_predicates() -> None:
    constructs = [
        _c("0x1", "Ontology", ["0x2"], ontology_iri="https://example.org/onto"),
        _c("0x2", "Annotation", ["0x3", "0x4"]),
        _c("0x3", "AnnotationProperty", iri="https://example.org#editorNote"),
        _c("0x4", "Literal", text="draft"),
    ]

    rows = _run_query(
        "lint_profiles/editorial/warn_ontology_no_metadata_annotations.cypher", constructs
    )

    assert rows == [{"ontology_iri": "https://example.org/onto"}]


def test_warn_missing_label_includes_named_datatypes() -> None:
    constructs = [
        _c("0x1", "Datatype", iri="https://example.org#AgeType"),
    ]

    rows = _run_query("lint_profiles/editorial/warn_missing_label.cypher", constructs)

    assert rows == [{"kind": "Datatype", "iri": "https://example.org#AgeType"}]


def test_warn_missing_label_excludes_builtin_terms() -> None:
    constructs = [
        _c("0x1", "Class", iri="http://www.w3.org/2002/07/owl#Thing"),
        _c("0x2", "Datatype", iri="http://www.w3.org/2001/XMLSchema#string"),
    ]

    rows = _run_query("lint_profiles/editorial/warn_missing_label.cypher", constructs)

    assert rows == []


def test_warn_labeled_without_definition_includes_named_datatypes() -> None:
    constructs = [
        _c("0x1", "Datatype", iri="https://example.org#AgeType"),
        _c("0x2", "AnnotationProperty", iri="http://www.w3.org/2000/01/rdf-schema#label"),
        _c("0x3", "IRI", text="https://example.org#AgeType"),
        _c("0x4", "Literal", text="Age type"),
        _c("0x5", "AnnotationAssertion", ["0x2", "0x3", "0x4"]),
    ]

    rows = _run_query("lint_profiles/editorial/warn_labeled_without_definition.cypher", constructs)

    assert rows == [{"kind": "Datatype", "iri": "https://example.org#AgeType"}]


def test_warn_object_property_no_domain_or_range_excludes_builtin_terms() -> None:
    constructs = [
        _c("0x1", "ObjectProperty", iri="http://www.w3.org/2002/07/owl#topObjectProperty"),
    ]

    rows = _run_query(
        "lint_profiles/modeling_risk/warn_object_property_no_domain_or_range.cypher", constructs
    )

    assert rows == []


def test_warn_functional_property_multiple_values_excludes_explicit_same_individual_targets() -> (
    None
):
    constructs = [
        _c("0x1", "ObjectProperty", iri="https://example.org#p"),
        _c("0x2", "NamedIndividual", iri="https://example.org#src"),
        _c("0x3", "NamedIndividual", iri="https://example.org#t1"),
        _c("0x4", "NamedIndividual", iri="https://example.org#t2"),
        _c("0x10", "FunctionalObjectProperty", ["0x1"]),
        _c("0x11", "ObjectPropertyAssertion", ["0x1", "0x2", "0x3"]),
        _c("0x12", "ObjectPropertyAssertion", ["0x1", "0x2", "0x4"]),
        _c("0x13", "SameIndividual", ["0x3", "0x4"]),
    ]

    rows = _run_query("warn_functional_property_multiple_values.cypher", constructs)

    assert rows == []


def test_warn_redundant_subclass_given_equivalence_reports_each_pair_once() -> None:
    constructs = [
        _c("0x1", "Class", iri="https://example.org#A"),
        _c("0x2", "Class", iri="https://example.org#B"),
        _c("0x10", "SubClassOf", ["0x1", "0x2"]),
        _c("0x11", "EquivalentClasses", ["0x1", "0x2"]),
        _c("0x12", "EquivalentClasses", ["0x1", "0x2"]),
    ]

    rows = _run_query("warn_redundant_subclass_given_equivalence.cypher", constructs)

    assert rows == [{"sub_class": "https://example.org#A", "super_class": "https://example.org#B"}]


def test_warn_disjoint_union_subclass_redundant_reports_each_pair_once() -> None:
    constructs = [
        _c("0x1", "Class", iri="https://example.org#Parent"),
        _c("0x2", "Class", iri="https://example.org#Child"),
        _c("0x3", "Class", iri="https://example.org#Sibling"),
        _c("0x10", "SubClassOf", ["0x2", "0x1"]),
        _c("0x11", "DisjointUnion", ["0x1", "0x2", "0x3"]),
        _c("0x12", "DisjointUnion", ["0x1", "0x2", "0x3"]),
    ]

    rows = _run_query("warn_disjoint_union_subclass_redundant.cypher", constructs)

    assert rows == [
        {
            "disjoint_union_parent": "https://example.org#Parent",
            "redundant_subclass_member": "https://example.org#Child",
        }
    ]


def test_class_assertion_nothing_reports_named_individual() -> None:
    constructs = [
        _c("0x1", "NamedIndividual", iri="https://example.org#alice"),
        _c("0x9", "Class", iri="http://www.w3.org/2002/07/owl#Nothing"),
        _c("0x2", "ClassAssertion", ["0x9", "0x1"]),
    ]

    rows = _run_query("test_class_assertion_nothing.cypher", constructs)

    assert rows == [{"iri": "https://example.org#alice"}]


def test_deprecated_entity_referenced_ignores_declaration_only() -> None:
    constructs = [
        _c("0x1", "Class", iri="https://example.org#Old"),
        _c("0x2", "Class", iri="https://example.org#Parent"),
        _c("0x3", "AnnotationProperty", iri="http://www.w3.org/2002/07/owl#deprecated"),
        _c("0x4", "IRI", text="https://example.org#Old"),
        _c("0x8", "Literal", text="true"),
        _c("0x5", "AnnotationAssertion", ["0x3", "0x4", "0x8"]),
        _c("0x6", "Declaration", ["0x1"]),
        _c("0x7", "SubClassOf", ["0x1", "0x2"]),
    ]

    rows = _run_query(
        "lint_profiles/editorial/warn_deprecated_entity_referenced.cypher", constructs
    )

    assert rows == [{"kind": "Class", "iri": "https://example.org#Old"}]


def test_disjoint_classes_shared_subclass_reports_unsatisfiable_child() -> None:
    constructs = [
        _c("0x1", "Class", iri="https://example.org#A"),
        _c("0x2", "Class", iri="https://example.org#B"),
        _c("0x3", "Class", iri="https://example.org#Child"),
        _c("0x10", "DisjointClasses", ["0x1", "0x2"]),
        _c("0x11", "SubClassOf", ["0x3", "0x1"]),
        _c("0x12", "SubClassOf", ["0x3", "0x2"]),
    ]

    rows = _run_query("test_disjoint_classes_shared_subclass.cypher", constructs)

    assert rows == [
        {
            "disjoint_a": "https://example.org#A",
            "disjoint_b": "https://example.org#B",
            "shared_subclass": "https://example.org#Child",
        }
    ]


def test_disjoint_classes_shared_individual_reports_contradictory_typing() -> None:
    constructs = [
        _c("0x1", "Class", iri="https://example.org#A"),
        _c("0x2", "Class", iri="https://example.org#B"),
        _c("0x3", "NamedIndividual", iri="https://example.org#alice"),
        _c("0x10", "DisjointClasses", ["0x1", "0x2"]),
        _c("0x11", "ClassAssertion", ["0x1", "0x3"]),
        _c("0x12", "ClassAssertion", ["0x2", "0x3"]),
    ]

    rows = _run_query("test_disjoint_classes_shared_individual.cypher", constructs)

    assert rows == [
        {
            "disjoint_a": "https://example.org#A",
            "disjoint_b": "https://example.org#B",
            "individual_iri": "https://example.org#alice",
        }
    ]


def test_disjoint_equivalent_classes_reports_pair() -> None:
    constructs = [
        _c("0x1", "Class", iri="https://example.org#A"),
        _c("0x2", "Class", iri="https://example.org#B"),
        _c("0x10", "EquivalentClasses", ["0x1", "0x2"]),
        _c("0x11", "DisjointClasses", ["0x1", "0x2"]),
    ]

    rows = _run_query("test_disjoint_equivalent_classes.cypher", constructs)

    assert rows == [{"class_a": "https://example.org#A", "class_b": "https://example.org#B"}]


def test_entity_iri_equals_ontology_iri_reports_collision() -> None:
    constructs = [
        _c("0x1", "Ontology", ontology_iri="https://example.org/onto"),
        _c("0x2", "Class", iri="https://example.org/onto"),
    ]

    rows = _run_query(
        "lint_profiles/editorial/warn_entity_iri_equals_ontology_iri.cypher", constructs
    )

    assert rows == [{"kind": "Class", "iri": "https://example.org/onto"}]


def test_negative_object_property_assertion_contradiction_reports_matching_target() -> None:
    constructs = [
        _c("0x1", "ObjectProperty", iri="https://example.org#p"),
        _c("0x2", "NamedIndividual", iri="https://example.org#alice"),
        _c("0x3", "NamedIndividual", iri="https://example.org#bob"),
        _c("0x10", "ObjectPropertyAssertion", ["0x1", "0x2", "0x3"]),
        _c("0x11", "NegativeObjectPropertyAssertion", ["0x1", "0x2", "0x3"]),
    ]

    rows = _run_query("test_negative_object_property_assertion_contradiction.cypher", constructs)

    assert rows == [
        {
            "property_iri": "https://example.org#p",
            "source_iri": "https://example.org#alice",
            "target_iri": "https://example.org#bob",
        }
    ]


def test_bottom_object_property_assertion_reports_impossible_edge() -> None:
    constructs = [
        _c("0x1", "ObjectProperty", iri="http://www.w3.org/2002/07/owl#bottomObjectProperty"),
        _c("0x2", "NamedIndividual", iri="https://example.org#alice"),
        _c("0x3", "NamedIndividual", iri="https://example.org#bob"),
        _c("0x10", "ObjectPropertyAssertion", ["0x1", "0x2", "0x3"]),
    ]

    rows = _run_query("test_bottom_object_property_assertion.cypher", constructs)

    assert rows == [
        {"source_iri": "https://example.org#alice", "target_iri": "https://example.org#bob"}
    ]


def test_bottom_data_property_assertion_reports_impossible_literal_edge() -> None:
    constructs = [
        _c("0x1", "DataProperty", iri="http://www.w3.org/2002/07/owl#bottomDataProperty"),
        _c("0x2", "NamedIndividual", iri="https://example.org#alice"),
        _c("0x4", "Literal", text="x", datatype_iri="http://www.w3.org/2001/XMLSchema#string"),
        _c("0x10", "DataPropertyAssertion", ["0x1", "0x2", "0x4"]),
    ]

    rows = _run_query("test_bottom_data_property_assertion.cypher", constructs)

    assert rows == [
        {
            "source_iri": "https://example.org#alice",
            "target_literal": "x^^http://www.w3.org/2001/XMLSchema#string",
        }
    ]


def test_property_contradictory_characteristics_reports_each_conflict() -> None:
    constructs = [
        _c("0x1", "ObjectProperty", iri="https://example.org#p"),
        _c("0x2", "ObjectProperty", iri="https://example.org#q"),
        _c("0x10", "ReflexiveObjectProperty", ["0x1"]),
        _c("0x11", "IrreflexiveObjectProperty", ["0x1"]),
        _c("0x12", "SymmetricObjectProperty", ["0x2"]),
        _c("0x13", "AsymmetricObjectProperty", ["0x2"]),
    ]

    rows = _run_query("test_property_contradictory_characteristics.cypher", constructs)

    assert sorted(rows, key=lambda row: (str(row["property_iri"]), str(row["contradiction"]))) == [
        {
            "property_iri": "https://example.org#p",
            "contradiction": "reflexive_and_irreflexive",
        },
        {
            "property_iri": "https://example.org#q",
            "contradiction": "symmetric_and_asymmetric",
        },
    ]


def test_irreflexive_property_self_assertion_reports_self_loop() -> None:
    constructs = [
        _c("0x1", "ObjectProperty", iri="https://example.org#parentOf"),
        _c("0x2", "NamedIndividual", iri="https://example.org#alice"),
        _c("0x10", "IrreflexiveObjectProperty", ["0x1"]),
        _c("0x11", "ObjectPropertyAssertion", ["0x1", "0x2", "0x2"]),
    ]

    rows = _run_query("test_irreflexive_property_self_assertion.cypher", constructs)

    assert rows == [
        {
            "property_iri": "https://example.org#parentOf",
            "individual_iri": "https://example.org#alice",
        }
    ]


def test_asymmetric_property_bidirectional_assertion_reports_reverse_pair_once() -> None:
    constructs = [
        _c("0x1", "ObjectProperty", iri="https://example.org#parentOf"),
        _c("0x2", "NamedIndividual", iri="https://example.org#alice"),
        _c("0x3", "NamedIndividual", iri="https://example.org#bob"),
        _c("0x10", "AsymmetricObjectProperty", ["0x1"]),
        _c("0x11", "ObjectPropertyAssertion", ["0x1", "0x2", "0x3"]),
        _c("0x12", "ObjectPropertyAssertion", ["0x1", "0x3", "0x2"]),
    ]

    rows = _run_query("test_asymmetric_property_bidirectional_assertion.cypher", constructs)

    assert rows == [
        {
            "property_iri": "https://example.org#parentOf",
            "individual_a": "https://example.org#alice",
            "individual_b": "https://example.org#bob",
        }
    ]


def test_disjoint_object_properties_shared_assertion_reports_same_edge_pair() -> None:
    constructs = [
        _c("0x1", "ObjectProperty", iri="https://example.org#hasParent"),
        _c("0x2", "ObjectProperty", iri="https://example.org#hasGuardian"),
        _c("0x3", "NamedIndividual", iri="https://example.org#alice"),
        _c("0x4", "NamedIndividual", iri="https://example.org#bob"),
        _c("0x10", "DisjointObjectProperties", ["0x1", "0x2"]),
        _c("0x11", "ObjectPropertyAssertion", ["0x1", "0x3", "0x4"]),
        _c("0x12", "ObjectPropertyAssertion", ["0x2", "0x3", "0x4"]),
    ]

    rows = _run_query("test_disjoint_object_properties_shared_assertion.cypher", constructs)

    assert rows == [
        {
            "property_a_iri": "https://example.org#hasGuardian",
            "property_b_iri": "https://example.org#hasParent",
            "source_iri": "https://example.org#alice",
            "target_iri": "https://example.org#bob",
        }
    ]


def test_disjoint_data_properties_shared_assertion_matches_equivalent_typed_literals() -> None:
    constructs = [
        _c("0x1", "DataProperty", iri="https://example.org#age"),
        _c("0x2", "DataProperty", iri="https://example.org#yearsOld"),
        _c("0x3", "NamedIndividual", iri="https://example.org#alice"),
        _c("0x5", "Literal", text="42", datatype_iri="http://www.w3.org/2001/XMLSchema#integer"),
        _c("0x6", "Literal", text="42", datatype_iri="http://www.w3.org/2001/XMLSchema#integer"),
        _c("0x10", "DisjointDataProperties", ["0x1", "0x2"]),
        _c("0x11", "DataPropertyAssertion", ["0x1", "0x3", "0x5"]),
        _c("0x12", "DataPropertyAssertion", ["0x2", "0x3", "0x6"]),
    ]

    rows = _run_query("test_disjoint_data_properties_shared_assertion.cypher", constructs)

    assert rows == [
        {
            "property_a_iri": "https://example.org#age",
            "property_b_iri": "https://example.org#yearsOld",
            "source_iri": "https://example.org#alice",
            "target_literal": "42^^http://www.w3.org/2001/XMLSchema#integer",
        }
    ]


def test_punning_queries_report_incompatible_entity_reuse() -> None:
    cases = [
        (
            "lint_profiles/description_logic/test_punning_class_individual.cypher",
            [
                _c("0x1", "Class", iri="https://example.org#X"),
                _c("0x2", "NamedIndividual", iri="https://example.org#X"),
            ],
        ),
        (
            "lint_profiles/description_logic/test_punning_class_datatype.cypher",
            [
                _c("0x1", "Class", iri="https://example.org#X"),
                _c("0x2", "Datatype", iri="https://example.org#X"),
            ],
        ),
        (
            "lint_profiles/description_logic/test_punning_object_data_property.cypher",
            [
                _c("0x1", "ObjectProperty", iri="https://example.org#X"),
                _c("0x2", "DataProperty", iri="https://example.org#X"),
            ],
        ),
    ]

    for query_name, constructs in cases:
        rows = _run_query(query_name, constructs)
        assert rows == [{"iri": "https://example.org#X"}]


def test_annotation_punning_queries_report_semantic_overlap() -> None:
    cases = [
        (
            "lint_profiles/modeling_risk/warn_annotation_punning_object_property.cypher",
            [
                _c("0x1", "ObjectProperty", iri="https://example.org#X"),
                _c("0x2", "AnnotationProperty", iri="https://example.org#X"),
            ],
        ),
        (
            "lint_profiles/modeling_risk/warn_annotation_punning_data_property.cypher",
            [
                _c("0x1", "DataProperty", iri="https://example.org#X"),
                _c("0x2", "AnnotationProperty", iri="https://example.org#X"),
            ],
        ),
    ]

    for query_name, constructs in cases:
        rows = _run_query(query_name, constructs)
        assert rows == [{"iri": "https://example.org#X"}]


def test_same_different_individual_reports_same_pair() -> None:
    constructs = [
        _c("0x1", "NamedIndividual", iri="https://example.org#alice"),
        _c("0x2", "NamedIndividual", iri="https://example.org#bob"),
        _c("0x10", "SameIndividual", ["0x1", "0x2"]),
        _c("0x11", "DifferentIndividuals", ["0x1", "0x2"]),
    ]

    rows = _run_query("test_same_different_individual.cypher", constructs)

    assert rows == [
        {
            "individual_a": "https://example.org#alice",
            "individual_b": "https://example.org#bob",
        }
    ]


def test_subclass_cycle_direct_reports_pair_once() -> None:
    constructs = [
        _c("0x1", "Class", iri="https://example.org#A"),
        _c("0x2", "Class", iri="https://example.org#B"),
        _c("0x10", "SubClassOf", ["0x1", "0x2"]),
        _c("0x11", "SubClassOf", ["0x2", "0x1"]),
    ]

    rows = _run_query("lint_profiles/modeling_risk/warn_subclass_cycle_direct.cypher", constructs)

    assert rows == [{"class_a": "https://example.org#A", "class_b": "https://example.org#B"}]


def test_subclass_nothing_reports_user_class() -> None:
    constructs = [
        _c("0x1", "Class", iri="https://example.org#Impossible"),
        _c("0x9", "Class", iri="http://www.w3.org/2002/07/owl#Nothing"),
        _c("0x10", "SubClassOf", ["0x1", "0x9"]),
    ]

    rows = _run_query("test_subclass_nothing.cypher", constructs)

    assert rows == [{"iri": "https://example.org#Impossible"}]


def test_subclass_reflexive_reports_tautology() -> None:
    constructs = [
        _c("0x1", "Class", iri="https://example.org#Self"),
        _c("0x10", "SubClassOf", ["0x1", "0x1"]),
    ]

    rows = _run_query("warn_subclass_reflexive.cypher", constructs)

    assert rows == [{"iri": "https://example.org#Self"}]


def test_undeclared_entities_reports_missing_declaration_and_user_datatype() -> None:
    constructs = [
        _c("0x1", "Class", iri="https://example.org#UndeclaredClass"),
        _c("0x2", "Datatype", iri="https://example.org#AgeType"),
        _c("0x3", "Datatype", iri="http://www.w3.org/2001/XMLSchema#integer"),
        _c("0x10", "DatatypeDefinition", ["0x2", "0x3"]),
    ]

    rows = _run_query("lint_profiles/description_logic/test_undeclared_entities.cypher", constructs)

    assert sorted(rows, key=lambda row: (str(row["kind"]), str(row["iri"]))) == [
        {"kind": "Class", "iri": "https://example.org#UndeclaredClass"},
        {"kind": "Datatype", "iri": "https://example.org#AgeType"},
    ]


def test_warn_datatype_property_no_domain_reports_missing_domain() -> None:
    constructs = [_c("0x1", "DataProperty", iri="https://example.org#age")]

    rows = _run_query(
        "lint_profiles/modeling_risk/warn_datatype_property_no_domain.cypher", constructs
    )

    assert rows == [{"iri": "https://example.org#age"}]


def test_warn_datatype_property_no_range_reports_missing_range() -> None:
    constructs = [_c("0x1", "DataProperty", iri="https://example.org#age")]

    rows = _run_query(
        "lint_profiles/modeling_risk/warn_datatype_property_no_range.cypher", constructs
    )

    assert rows == [{"iri": "https://example.org#age"}]


def test_warn_individual_no_type_reports_untyped_individual() -> None:
    constructs = [_c("0x1", "NamedIndividual", iri="https://example.org#orphan")]

    rows = _run_query("lint_profiles/modeling_risk/warn_individual_no_type.cypher", constructs)

    assert rows == [{"iri": "https://example.org#orphan"}]


def test_warn_property_dangerous_combination_reports_each_declared_combo() -> None:
    constructs = [
        _c("0x1", "ObjectProperty", iri="https://example.org#p"),
        _c("0x2", "ObjectProperty", iri="https://example.org#q"),
        _c("0x3", "ObjectProperty", iri="https://example.org#r"),
        _c("0x10", "TransitiveObjectProperty", ["0x1"]),
        _c("0x11", "FunctionalObjectProperty", ["0x1"]),
        _c("0x12", "TransitiveObjectProperty", ["0x2"]),
        _c("0x13", "InverseFunctionalObjectProperty", ["0x2"]),
        _c("0x14", "FunctionalObjectProperty", ["0x3"]),
        _c("0x15", "InverseFunctionalObjectProperty", ["0x3"]),
    ]

    rows = _run_query(
        "lint_profiles/modeling_risk/warn_property_dangerous_combination.cypher", constructs
    )

    assert sorted(rows, key=lambda row: (str(row["property_iri"]), str(row["combination"]))) == [
        {
            "property_iri": "https://example.org#p",
            "combination": "transitive_and_functional",
        },
        {
            "property_iri": "https://example.org#q",
            "combination": "transitive_and_inverse_functional",
        },
        {
            "property_iri": "https://example.org#r",
            "combination": "functional_and_inverse_functional",
        },
    ]


def test_warn_version_iri_missing_reports_unversioned_ontology() -> None:
    constructs = [
        _c("0x1", "Ontology", ontology_iri="https://example.org/onto"),
    ]

    rows = _run_query("lint_profiles/editorial/warn_version_iri_missing.cypher", constructs)

    assert rows == [{"ontology_iri": "https://example.org/onto"}]
