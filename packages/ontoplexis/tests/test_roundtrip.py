"""The round-trip fidelity gate: the walker vs the reference implementation.

These tests compare functional-syntax renderings produced by OWLAPI (via
ROBOT, the dev-only test oracle) before and after passing a document through
the walker and the database. They require a Java runtime and the ROBOT jar;
run 'make fetch-robot'.
"""

from __future__ import annotations

from ontoplexis import Ontology
from ontoplexis.owlxml import parse_owlxml
from tests.oracle import OracleConfig, convert_document


def _functional(config: OracleConfig, document: str) -> str:
    return convert_document(config, document, target_format="functional", source_format="owlxml")


def test_document_round_trip_is_semantically_lossless(
    oracle_config: OracleConfig, complex_owlxml: str
) -> None:
    """The reference implementation sees identical axioms before and after."""
    ontology = Ontology.from_owlxml(complex_owlxml)

    assert _functional(oracle_config, ontology.to_owlxml()) == _functional(
        oracle_config, complex_owlxml
    )


def test_database_round_trip_is_semantically_lossless(
    oracle_config: OracleConfig, complex_owlxml: str
) -> None:
    ontology = Ontology.from_owlxml(complex_owlxml)

    with ontology.project() as projection:
        recovered = Ontology.from_projection(projection)

    assert _functional(oracle_config, recovered.to_owlxml()) == _functional(
        oracle_config, complex_owlxml
    )


def test_owlxml_output_reparses_with_owlapi(
    oracle_config: OracleConfig, animals_owlxml: str
) -> None:
    """The walker's serialization is valid OWL/XML by the reference parser."""
    ontology = Ontology.from_owlxml(animals_owlxml)

    functional = _functional(oracle_config, ontology.to_owlxml())

    assert "SubClassOf" in functional


def test_walker_parses_owlapi_normalized_foreign_formats(
    oracle_config: OracleConfig,
) -> None:
    """OWL/XML emitted by OWLAPI from another serialization walks cleanly."""
    turtle = """
        @prefix : <http://example.org/tiny#> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        <http://example.org/tiny> a owl:Ontology .
        :A a owl:Class .
        :B a owl:Class .
        :A rdfs:subClassOf :B .
    """
    xml = convert_document(oracle_config, turtle, target_format="owlxml", source_format="turtle")

    graph = parse_owlxml(xml)

    kinds = {node.kind for node in graph.nodes}
    assert "SubClassOf" in kinds
    class_iris = {node.iri for node in graph.nodes if node.kind == "Class"}
    assert class_iris == {"http://example.org/tiny#A", "http://example.org/tiny#B"}
