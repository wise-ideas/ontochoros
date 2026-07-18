import ontophora as model
import ontophora.records as records
from ontophora._registry import construct_types
from ontophora.records import coerce_construct_records


def test_coerce_construct_records_validates_record_payloads() -> None:
    records = coerce_construct_records(
        [
            {
                "uid": "0x1001",
                "kind": "Class",
                "iri": "https://example.org/pizza#Pizza",
            }
        ]
    )

    assert [record.uid for record in records] == ["0x1001"]
    assert [record.kind for record in records] == ["Class"]


def test_model_root_exports_only_curated_construct_surface() -> None:
    exported = set(model.__all__)

    # Internal helpers and speculative APIs stay out of the root surface.
    assert "first_display_field" not in exported
    assert "CollectionKind" not in exported
    assert "construct_support_manifest" not in exported
    assert "is_kind_compatible" not in exported
    assert "unordered_sort_key" not in exported
    assert exported >= {
        "BaseConstruct",
        "Construct",
        "ConstructMetadata",
        "Reference",
        "ReferenceEntry",
        "ReferenceValue",
        "UID",
        "coerce_construct",
        "compact_display_label",
        "construct_display_iri",
        "construct_display_label",
        "construct_json_schema",
        "construct_metadata",
        "construct_types",
        "fingerprint_construct",
        "fingerprint_constructs",
        "iter_construct_references",
    }
    assert {construct_type.__name__ for construct_type in construct_types}.issubset(exported)


def test_records_module_all_exports_supported_record_coercion_helpers() -> None:
    assert records.__all__ == [
        "coerce_construct",
        "coerce_construct_records",
    ]
