"""Property-based tests: generated documents through the walker and database.

The walker's round-trip identity is asserted elsewhere on fixed fixtures;
these tests assert the same invariants over *generated* OWL/XML documents —
random axiom mixes over a small entity pool (so IRI merging is exercised)
and adversarial literal content — plus derivation idempotence.

No jar: the oracle proves semantic fidelity on real corpora; Hypothesis
probes structural identity on inputs nobody would write by hand.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from ontoplexis import Ontology, WritableProjection, derive_edges
from ontoplexis.owlxml import parse_owlxml, serialize_owlxml

_CLASSES = [f"http://ex.org/g#C{i}" for i in range(4)]
_OBJECT_PROPERTIES = [f"http://ex.org/g#p{i}" for i in range(2)]
_DATA_PROPERTIES = [f"http://ex.org/g#d{i}" for i in range(2)]
_INDIVIDUALS = [f"http://ex.org/g#i{i}" for i in range(3)]
_ANNOTATION_PROPERTY = "http://www.w3.org/2000/01/rdf-schema#label"

# Valid XML 1.0 text content, excluding carriage returns (the XML parser
# itself normalizes \r\n and \r to \n — that is XML semantics, not walker
# infidelity) and the two non-characters.
_XML_TEXT = st.text(
    alphabet=st.one_of(
        st.sampled_from("\t\n"),
        st.characters(min_codepoint=0x20, exclude_categories=("Cs",), exclude_characters="￾￿"),
    ),
    max_size=40,
)


def _cls(iri: str) -> str:
    return f'<Class IRI="{iri}"/>'


def _subclass_of(pair: tuple[str, str]) -> str:
    return f"<SubClassOf>{_cls(pair[0])}{_cls(pair[1])}</SubClassOf>"


def _operand_axiom(kind: str, iris: list[str]) -> str:
    return f"<{kind}>{''.join(_cls(iri) for iri in iris)}</{kind}>"


def _restriction_subclass(args: tuple[str, str, str, str]) -> str:
    sub, quantifier, prop, filler = args
    return (
        f"<SubClassOf>{_cls(sub)}"
        f'<{quantifier}><ObjectProperty IRI="{prop}"/>{_cls(filler)}</{quantifier}>'
        "</SubClassOf>"
    )


def _class_assertion(args: tuple[str, str]) -> str:
    return f'<ClassAssertion>{_cls(args[0])}<NamedIndividual IRI="{args[1]}"/></ClassAssertion>'


def _object_assertion(args: tuple[str, str, str]) -> str:
    prop, subject, target = args
    return (
        f'<ObjectPropertyAssertion><ObjectProperty IRI="{prop}"/>'
        f'<NamedIndividual IRI="{subject}"/><NamedIndividual IRI="{target}"/>'
        "</ObjectPropertyAssertion>"
    )


def _data_assertion(args: tuple[str, str, str]) -> str:
    prop, subject, text = args
    return (
        f'<DataPropertyAssertion><DataProperty IRI="{prop}"/>'
        f'<NamedIndividual IRI="{subject}"/><Literal>{escape(text)}</Literal>'
        "</DataPropertyAssertion>"
    )


def _annotation(args: tuple[str, str]) -> str:
    subject, text = args
    return (
        f'<AnnotationAssertion><AnnotationProperty IRI="{_ANNOTATION_PROPERTY}"/>'
        f"<IRI>{subject}</IRI><Literal>{escape(text)}</Literal></AnnotationAssertion>"
    )


def _characteristic(args: tuple[str, str]) -> str:
    kind, prop = args
    return f'<{kind}><ObjectProperty IRI="{prop}"/></{kind}>'


_AXIOMS = st.one_of(
    st.tuples(st.sampled_from(_CLASSES), st.sampled_from(_CLASSES)).map(_subclass_of),
    st.tuples(
        st.sampled_from(["EquivalentClasses", "DisjointClasses"]),
        st.lists(st.sampled_from(_CLASSES), min_size=2, max_size=3),
    ).map(lambda args: _operand_axiom(*args)),
    st.tuples(
        st.sampled_from(_CLASSES),
        st.sampled_from(["ObjectSomeValuesFrom", "ObjectAllValuesFrom"]),
        st.sampled_from(_OBJECT_PROPERTIES),
        st.sampled_from(_CLASSES),
    ).map(_restriction_subclass),
    st.tuples(st.sampled_from(_CLASSES), st.sampled_from(_INDIVIDUALS)).map(_class_assertion),
    st.tuples(
        st.sampled_from(_OBJECT_PROPERTIES),
        st.sampled_from(_INDIVIDUALS),
        st.sampled_from(_INDIVIDUALS),
    ).map(_object_assertion),
    st.tuples(st.sampled_from(_DATA_PROPERTIES), st.sampled_from(_INDIVIDUALS), _XML_TEXT).map(
        _data_assertion
    ),
    st.tuples(st.sampled_from(_CLASSES + _INDIVIDUALS), _XML_TEXT).map(_annotation),
    st.tuples(
        st.sampled_from(
            ["TransitiveObjectProperty", "SymmetricObjectProperty", "FunctionalObjectProperty"]
        ),
        st.sampled_from(_OBJECT_PROPERTIES),
    ).map(_characteristic),
)


@st.composite
def owlxml_documents(draw: st.DrawFn, max_axioms: int = 12) -> str:
    axioms = draw(st.lists(_AXIOMS, max_size=max_axioms))
    declarations = "".join(f"<Declaration>{_cls(iri)}</Declaration>" for iri in _CLASSES[:2])
    return (
        '<?xml version="1.0"?>'
        '<Ontology xmlns="http://www.w3.org/2002/07/owl#" ontologyIRI="http://ex.org/g">'
        f"{declarations}{''.join(axioms)}</Ontology>"
    )


@given(owlxml_documents())
@settings(max_examples=100, deadline=None)
def test_generated_documents_round_trip_structurally(document: str) -> None:
    graph = parse_owlxml(document)

    once = serialize_owlxml(graph)
    assert parse_owlxml(once) == graph
    # Serialization is stable from the first pass on.
    assert serialize_owlxml(parse_owlxml(once)) == once


@given(st.lists(_XML_TEXT, min_size=1, max_size=6, unique=True))
@settings(max_examples=8, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_generated_literal_content_round_trips_through_the_database(texts: list[str]) -> None:
    assertions = "".join(
        _data_assertion(("http://ex.org/g#d0", "http://ex.org/g#i0", text)) for text in texts
    )
    document = (
        '<Ontology xmlns="http://www.w3.org/2002/07/owl#" '
        f'ontologyIRI="http://ex.org/g">{assertions}</Ontology>'
    )
    ontology = Ontology.from_owlxml(document)

    with ontology.project() as projection:
        loaded = projection.graph()

    assert {n.uid: n.properties for n in loaded.nodes} == {
        n.uid: n.properties for n in ontology.graph.nodes
    }


@given(owlxml_documents(max_axioms=8))
@settings(max_examples=5, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_derivation_is_idempotent_for_generated_documents(document: str) -> None:
    with tempfile.TemporaryDirectory(prefix="ontoplexis-prop-") as tmp:
        target = Path(tmp) / "generated.lbug"
        Ontology.from_owlxml(document).save_projection(target).close()

        with WritableProjection.open(target) as writable:
            first = derive_edges(writable)
            second = derive_edges(writable)

    assert first == second
