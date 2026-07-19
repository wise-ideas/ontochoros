from pathlib import Path

import pytest
from pydantic import TypeAdapter, ValidationError

from ontophora.constructs.individual import AnonymousIndividual, NamedIndividual
from ontophora.constructs.ontology_document import PrefixDeclaration
from ontophora.constructs.types import (
    IRI,
    AbbreviatedIRI,
    FullIRI,
    NodeID,
    PrefixName,
    QuotedString,
)


def _load_fixture(name: str) -> list:
    from ontophora.envelope import records_from_jsonl

    fixture_path = Path(__file__).parent / "fixtures" / "cases" / name
    return records_from_jsonl(fixture_path.read_text())


def test_full_iri_accepts_owl_2_primer_prefix_declaration_examples() -> None:
    # OWL 2 Primer section 8.2.2 fixture data uses plain absolute IRIs for Prefix declarations.
    records = _load_fixture("primer_8.2.2.jsonl")

    prefixes = [record for record in records if isinstance(record, PrefixDeclaration)]

    assert [prefix.full_iri for prefix in prefixes] == [
        "http://example.com/owl/families/",
        "http://example.org/otherOntologies/families/",
        "http://www.w3.org/2001/XMLSchema#",
        "http://www.w3.org/2002/07/owl#",
    ]


def test_full_iri_accepts_functional_syntax_bracketed_examples() -> None:
    # OWL 2 Structural Specification and Functional-Style Syntax documents FullIRI values in <...> form.
    adapter = TypeAdapter(FullIRI)

    assert adapter.validate_python("<http://example.org/otherOntologies/families/>") == (
        "http://example.org/otherOntologies/families/"
    )
    assert adapter.validate_python("<http://www.w3.org/2002/07/owl#>") == (
        "http://www.w3.org/2002/07/owl#"
    )


def test_full_iri_accepts_absolute_non_http_schemes() -> None:
    adapter = TypeAdapter(FullIRI)

    assert adapter.validate_python("urn:example:person") == "urn:example:person"
    assert adapter.validate_python("mailto:alice@example.org") == "mailto:alice@example.org"
    assert adapter.validate_python("otherOnt:Person") == "otherOnt:Person"


def test_iri_accepts_abbreviated_examples_from_owl_2_prefix_notation() -> None:
    adapter = TypeAdapter(IRI)

    assert adapter.validate_python(":Person") == ":Person"
    assert adapter.validate_python("otherOnt:Person") == "otherOnt:Person"
    assert TypeAdapter(AbbreviatedIRI).validate_python("owl:Thing") == "owl:Thing"
    assert TypeAdapter(AbbreviatedIRI).validate_python("ex:has_part") == "ex:has_part"


def test_iri_accepts_absolute_examples_used_in_owl_2_primer_fixtures() -> None:
    construct = NamedIndividual.model_validate(
        {"uid": "0x1", "kind": "NamedIndividual", "iri": "http://example.org/Mary"}
    )

    assert construct.iri == "http://example.org/Mary"


def test_prefix_name_accepts_owl_2_primer_prefix_examples() -> None:
    records = _load_fixture("primer_8.2.2.jsonl")

    prefixes = [record for record in records if isinstance(record, PrefixDeclaration)]

    assert [prefix.prefix_name for prefix in prefixes] == [":", "otherOnt:", "xsd:", "owl:"]


@pytest.mark.parametrize("value", ["é:", "a..b:"])
def test_prefix_name_accepts_sparql_pname_ns_examples(value: str) -> None:
    assert TypeAdapter(PrefixName).validate_python(value) == value


@pytest.mark.parametrize("value", ["é:x", "a..b:x", "ex:café", "ex:a:b"])
def test_abbreviated_iri_accepts_sparql_pname_ln_examples(value: str) -> None:
    # The abbreviated-IRI grammar must accept every prefix that PrefixName
    # accepts, plus SPARQL PN_LOCAL local names (which may contain ':').
    assert TypeAdapter(AbbreviatedIRI).validate_python(value) == value


def test_node_id_accepts_anonymous_individual_examples() -> None:
    # OWL 2 Structural Specification uses _: identifiers for anonymous individuals.
    construct = AnonymousIndividual.model_validate(
        {"uid": "0x1", "kind": "AnonymousIndividual", "node_id": "_:a.1-b"}
    )

    assert construct.node_id == "_:a.1-b"


@pytest.mark.parametrize("value", ["_:1", "_:a..b", "_:é", "_:a·b"])
def test_node_id_accepts_blank_node_labels_from_sparql_grammar(value: str) -> None:
    assert TypeAdapter(NodeID).validate_python(value) == value


@pytest.mark.parametrize("value", ['""', r'"a\"b"', r'"a\\b"'])
def test_quoted_string_accepts_owl_2_quoted_string_examples(value: str) -> None:
    assert TypeAdapter(QuotedString).validate_python(value) == value


@pytest.mark.parametrize(
    ("adapter", "value"),
    [
        (TypeAdapter(FullIRI), "http://example.org/space here"),
        (TypeAdapter(FullIRI), "<http://example.org/space here>"),
        (TypeAdapter(FullIRI), "://example.org/no-scheme"),
        (TypeAdapter(FullIRI), "<http://example.org/missing"),
        (TypeAdapter(FullIRI), ""),
        (TypeAdapter(AbbreviatedIRI), ":"),
        (TypeAdapter(AbbreviatedIRI), "otherOnt:"),
        (TypeAdapter(AbbreviatedIRI), "otherOnt:.Person"),
        (TypeAdapter(AbbreviatedIRI), "otherOnt:Person."),
        (TypeAdapter(PrefixName), "otherOnt.:"),
        (TypeAdapter(NodeID), "_:a."),
        (TypeAdapter(NodeID), "_:a:b"),
        (TypeAdapter(NodeID), "_:-a"),
        (TypeAdapter(QuotedString), r'"a\nb"'),
        (TypeAdapter(QuotedString), '"a\\"'),
        (TypeAdapter(IRI), "not an iri"),
    ],
)
def test_iri_types_reject_invalid_values(adapter: TypeAdapter[str], value: str) -> None:
    with pytest.raises(ValidationError):
        adapter.validate_python(value)
