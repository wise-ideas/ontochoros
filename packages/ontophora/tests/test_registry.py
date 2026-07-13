from ontophora._registry import construct_metadata_by_kind


def test_construct_registry_exposes_known_kinds() -> None:
    kinds = construct_metadata_by_kind()

    assert "Class" in kinds
    assert "OntologyDocument" in kinds


def test_construct_registry_reports_document_metadata() -> None:
    metadata = construct_metadata_by_kind()["OntologyDocument"]

    assert metadata.is_document_construct is True
    assert "Entity" not in metadata.abstract_groups


def test_construct_registry_reports_abstract_groups() -> None:
    by_kind = construct_metadata_by_kind()

    assert "AnnotationAxiom" in by_kind["AnnotationAssertion"].abstract_groups
    assert "Assertion" in by_kind["ClassAssertion"].abstract_groups
    assert "Axiom" in by_kind["SubClassOf"].abstract_groups
    assert "ClassAxiom" in by_kind["EquivalentClasses"].abstract_groups
    assert "ClassExpression" in by_kind["Class"].abstract_groups
    assert "DataPropertyExpression" in by_kind["DataProperty"].abstract_groups
    assert "DataPropertyAxiom" in by_kind["FunctionalDataProperty"].abstract_groups
    assert "DataRange" in by_kind["Datatype"].abstract_groups
    assert "Individual" in by_kind["NamedIndividual"].abstract_groups
    assert "ObjectPropertyAxiom" in by_kind["FunctionalObjectProperty"].abstract_groups
    assert "ObjectPropertyExpression" in by_kind["ObjectInverseOf"].abstract_groups
