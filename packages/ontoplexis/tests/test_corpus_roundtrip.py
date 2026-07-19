"""Round-trip fidelity over the OWL 2 Primer corpus (requires the jar).

The sister package ontophora carries RDF/XML renderings of the OWL 2 Primer
and Structural Specification examples in its fixture corpus. Each is
normalized to OWL/XML by the reference implementation (ROBOT), walked into a
graph, serialized back, and compared semantically — the same oracle gate as
test_roundtrip.py, but over the whole spec-derived corpus instead of two
hand-written fixtures.

Cross-package coupling: the corpus lives in ontophora's test tree and is
reached by relative path below — ontophora's test_fixture_corpus.py gates
the pairing, and reorganizing that directory breaks this suite.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ontoplexis import Ontology
from ontoplexis.owlxml import parse_owlxml, serialize_owlxml
from tests.oracle import OracleConfig, convert_document

CASES = Path(__file__).resolve().parents[2] / "ontophora" / "tests" / "fixtures" / "cases"

# Cases the oracle itself cannot load: OWLAPI resolves owl:imports while
# parsing, and these documents import unresolvable example.org ontologies.
# Nothing here reaches the walker, so there is no fidelity to prove.
_ORACLE_CANNOT_LOAD = {
    "primer_8.2.3": "declares owl:imports of an unresolvable example.org ontology",
}


def _corpus() -> list[Path]:
    cases = sorted(CASES.glob("*.xml"))
    if not cases:
        raise AssertionError(f"No corpus documents found under {CASES}")
    return cases


@pytest.mark.parametrize("case", _corpus(), ids=lambda p: p.stem)
def test_corpus_document_round_trip_is_semantically_lossless(
    oracle_config: OracleConfig, case: Path
) -> None:
    if case.stem in _ORACLE_CANNOT_LOAD:
        pytest.skip(f"oracle cannot load this case: {_ORACLE_CANNOT_LOAD[case.stem]}")
    owlxml = convert_document(
        oracle_config,
        case.read_text(encoding="utf-8"),
        target_format="owlxml",
        source_format="rdfxml",
    )

    graph = parse_owlxml(owlxml)
    # Structural identity: the walker's serialization reparses to the same graph.
    assert parse_owlxml(serialize_owlxml(graph)) == graph
    # Semantic identity: the reference implementation sees the same axioms
    # before and after the walk.
    assert convert_document(
        oracle_config,
        Ontology(graph).to_owlxml(),
        target_format="functional",
        source_format="owlxml",
    ) == convert_document(oracle_config, owlxml, target_format="functional", source_format="owlxml")
