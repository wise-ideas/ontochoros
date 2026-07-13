from ontophora._registry import construct_metadata, construct_metadata_by_kind


def test_every_registered_construct_has_metadata() -> None:
    metadata_by_kind = construct_metadata_by_kind()

    assert set(metadata_by_kind) == {metadata.kind for metadata in construct_metadata}


def test_registered_constructs_use_single_metadata_table() -> None:
    for metadata in construct_metadata:
        looked_up = construct_metadata_by_kind()[metadata.kind]
        assert looked_up is metadata


def test_metadata_carries_abstract_group_information() -> None:
    assert "Entity" in construct_metadata_by_kind()["Class"].abstract_groups
    assert "ClassExpression" in construct_metadata_by_kind()["Class"].abstract_groups
    assert (
        "ObjectPropertyAxiom"
        in construct_metadata_by_kind()["FunctionalObjectProperty"].abstract_groups
    )
