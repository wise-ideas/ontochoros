from ontophora.constructs.klass import Klass
from ontophora.constructs.literal import StringLiteralNoLanguage
from ontophora.constructs.sub_class_of import SubClassOf
from ontophora.display import (
    CONSTRUCT_IRI_FIELDS,
    CONSTRUCT_LABEL_FIELDS,
    DEFAULT_COMPACT_DISPLAY_LIMIT,
    compact_display_value,
    first_display_field,
)


def test_display_helpers_use_construct_property_priority() -> None:
    props = {
        "version_iri": "https://example.org/version",
        "ontology_iri": "https://example.org/ontology",
        "iri": "https://example.org/entity#Pizza",
        "node_id": "_:b0",
    }

    assert first_display_field(props, CONSTRUCT_IRI_FIELDS) == "https://example.org/entity#Pizza"
    assert first_display_field(props, CONSTRUCT_LABEL_FIELDS) == "https://example.org/entity#Pizza"


def test_display_helpers_skip_missing_or_non_string_values() -> None:
    props = {
        "iri": None,
        "quoted_string": 7,
        "lexical_form": "Pizza",
    }

    assert first_display_field(props, CONSTRUCT_IRI_FIELDS) is None
    assert first_display_field(props, CONSTRUCT_LABEL_FIELDS) == "Pizza"


def test_compact_display_value_compacts_iri_tail() -> None:
    props = {"iri": "https://example.org/ontology#MargheritaPizza"}

    label = first_display_field(props, CONSTRUCT_LABEL_FIELDS)

    assert label == "https://example.org/ontology#MargheritaPizza"
    assert compact_display_value(label) == "MargheritaPizza"


def test_compact_display_value_falls_back_to_path_tail_and_survives_empty_tails() -> None:
    assert compact_display_value("https://example.org/ontology/Pizza") == "Pizza"
    # A trailing separator leaves an empty tail; the full value is kept.
    assert compact_display_value("https://example.org/ontology#") == "https://example.org/ontology#"
    assert compact_display_value('"quoted"') == "quoted"
    assert compact_display_value("plain") == "plain"


def test_compact_display_value_truncates_at_the_limit() -> None:
    at_limit = "x" * DEFAULT_COMPACT_DISPLAY_LIMIT

    assert compact_display_value(at_limit) == at_limit
    assert (
        compact_display_value(at_limit + "x") == "x" * (DEFAULT_COMPACT_DISPLAY_LIMIT - 3) + "..."
    )
    assert compact_display_value("abcdef", limit=5) == "ab..."


def test_construct_display_accessors_prefer_iri_fields() -> None:
    klass = Klass(uid="0x1", iri="https://example.org/pizza#Pizza")

    assert klass.display_iri() == "https://example.org/pizza#Pizza"
    assert klass.display_label() == "https://example.org/pizza#Pizza"
    assert klass.compact_label() == "Pizza"
    assert klass.compact_label(limit=4) == "P..."


def test_construct_without_identifying_fields_has_no_label() -> None:
    axiom = SubClassOf(
        uid="0x1",
        sub_class_expression="0x2",
        super_class_expression="0x3",
    )

    assert axiom.display_iri() is None
    assert axiom.display_label() is None
    assert axiom.compact_label() is None


def test_rich_rendering_shows_kind_label_and_uid() -> None:
    klass = Klass(uid="0x1", iri="https://example.org/pizza#Pizza")

    assert klass.__rich__() == "[bold]Class[/] Pizza [dim]0x1[/]"


def test_rich_rendering_omits_label_when_none_exists() -> None:
    axiom = SubClassOf(
        uid="0x1",
        sub_class_expression="0x2",
        super_class_expression="0x3",
    )

    assert axiom.__rich__() == "[bold]SubClassOf[/] [dim]0x1[/]"


def test_html_repr_lists_fields_and_escapes_markup() -> None:
    literal = StringLiteralNoLanguage(uid="0x1", quoted_string='"<b>&nasty</b>"')

    html = literal._repr_html_()

    assert "<strong>StringLiteralNoLanguage" in html
    assert "quoted_string" in html
    assert "&lt;b&gt;&amp;nasty&lt;/b&gt;" in html
    assert "<b>&nasty</b>" not in html


def test_html_repr_renders_unordered_fields_deterministically() -> None:
    axiom = SubClassOf(
        uid="0x1",
        sub_class_expression="0x2",
        super_class_expression="0x3",
        axiom_annotations={"0xb", "0xa"},
    )

    html = axiom._repr_html_()

    assert "0xa, 0xb" in html
