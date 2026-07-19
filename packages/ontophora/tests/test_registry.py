import pytest

from ontophora._registry import (
    CONSTRUCT_METADATA,
    construct_json_schema,
    construct_metadata_by_kind,
    construct_support_manifest,
    is_kind_compatible,
)


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


def test_construct_json_schema_rejects_unknown_kind() -> None:
    with pytest.raises(ValueError, match="Unknown construct kind"):
        construct_json_schema(kind="NotAConstruct")


def test_support_manifest_covers_every_registered_kind() -> None:
    # The manifest is the handoff for non-Python consumers (MCP tool
    # definitions, API schemas): every registered kind must appear, with a
    # schema ref that resolves into the construct union's $defs.
    manifest = construct_support_manifest()
    constructs = manifest["constructs"]
    assert isinstance(constructs, dict)

    assert manifest["schema_mode"] == "validation"
    assert manifest["construct_count"] == len(constructs)
    assert set(constructs) == {metadata.kind for metadata in CONSTRUCT_METADATA}

    schema = construct_json_schema()
    definitions = schema["$defs"]
    assert isinstance(definitions, dict)
    for kind, entry in constructs.items():
        assert isinstance(entry, dict)
        ref = entry["schema_ref"]
        assert isinstance(ref, str) and ref.startswith("#/$defs/"), kind
        assert ref.rsplit("/", 1)[-1] in definitions, kind


def test_support_manifest_field_names_match_the_models() -> None:
    manifest = construct_support_manifest()
    constructs = manifest["constructs"]
    assert isinstance(constructs, dict)
    by_kind = construct_metadata_by_kind()

    for kind, entry in constructs.items():
        assert isinstance(entry, dict)
        model_fields = set(by_kind[kind].model_type.model_fields) - {"uid", "kind"}
        field_names = entry["field_names"]
        assert isinstance(field_names, list)
        assert set(field_names) == model_fields, kind
        required = entry["required_fields"]
        assert isinstance(required, list)
        assert set(required) <= set(field_names), kind


def test_support_manifest_groups_agree_with_registry_metadata() -> None:
    manifest = construct_support_manifest()
    groups = manifest["groups"]
    assert isinstance(groups, dict)
    by_kind = construct_metadata_by_kind()

    class_expressions = groups["ClassExpression"]
    assert isinstance(class_expressions, list)
    assert class_expressions == sorted(class_expressions)
    assert set(class_expressions) == {
        metadata.kind
        for metadata in by_kind.values()
        if "ClassExpression" in metadata.abstract_groups
    }
    blank_nodes = groups["BlankNode"]
    assert isinstance(blank_nodes, list)
    assert set(blank_nodes) == {
        metadata.kind for metadata in by_kind.values() if metadata.is_blank_node
    }


def test_is_kind_compatible_accepts_exact_and_group_matches() -> None:
    assert is_kind_compatible(actual_kind="Class", expected_kinds=("Class",))
    assert is_kind_compatible(actual_kind="Class", expected_kinds=("ClassExpression",))
    assert is_kind_compatible(actual_kind="SubClassOf", expected_kinds=("Axiom",))
    # First match wins across several expected kinds.
    assert is_kind_compatible(actual_kind="Class", expected_kinds=("Datatype", "ClassExpression"))


def test_is_kind_compatible_rejects_mismatches_and_unknowns() -> None:
    assert not is_kind_compatible(actual_kind="Class", expected_kinds=("DataRange",))
    assert not is_kind_compatible(actual_kind="Class", expected_kinds=())
    # An unregistered kind can only match by exact name, never by group.
    assert is_kind_compatible(actual_kind="Mystery", expected_kinds=("Mystery",))
    assert not is_kind_compatible(actual_kind="Mystery", expected_kinds=("ClassExpression",))


def test_axioms_are_not_blank_nodes() -> None:
    # Blank nodes are anonymous expressions; axioms map to triples in RDF.
    by_kind = construct_metadata_by_kind()

    for metadata in by_kind.values():
        if "Axiom" in metadata.abstract_groups:
            assert not metadata.is_blank_node, metadata.kind
    assert by_kind["ObjectSomeValuesFrom"].is_blank_node
