"""A known-clean ontology yields zero findings across every rule.

Every other lint test proves a rule fires; nothing proved the rules stay
quiet. For a linter the reputation-killing regression is the false positive,
so this gate runs the complete rule set — every profile, errors and
warnings — against an ontology deliberately written to satisfy all of them.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from ontoplexis import Ontology

from ontopoiesis.lint import (
    available_lint_profiles,
    lint_rules,
    resolve_lint_rule_selection,
    run_lint_on_path,
)

_CLEAN_OWLXML = """<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#"
          ontologyIRI="http://ex.org/clean"
          versionIRI="http://ex.org/clean/2026-07-19">
    <Prefix name="" IRI="http://ex.org/clean#"/>
    <Prefix name="rdfs" IRI="http://www.w3.org/2000/01/rdf-schema#"/>
    <Prefix name="skos" IRI="http://www.w3.org/2004/02/skos/core#"/>
    <Prefix name="dcterms" IRI="http://purl.org/dc/terms/"/>
    <Prefix name="xsd" IRI="http://www.w3.org/2001/XMLSchema#"/>
    <Annotation>
        <AnnotationProperty abbreviatedIRI="dcterms:title"/>
        <Literal xml:lang="en">A deliberately lint-clean ontology</Literal>
    </Annotation>

    <Declaration><Class abbreviatedIRI=":Animal"/></Declaration>
    <Declaration><Class abbreviatedIRI=":Dog"/></Declaration>
    <Declaration><ObjectProperty abbreviatedIRI=":hasCompanion"/></Declaration>
    <Declaration><DataProperty abbreviatedIRI=":age"/></Declaration>
    <Declaration><NamedIndividual abbreviatedIRI=":rex"/></Declaration>
    <Declaration><AnnotationProperty abbreviatedIRI="skos:definition"/></Declaration>
    <Declaration><AnnotationProperty abbreviatedIRI="dcterms:title"/></Declaration>

    <SubClassOf><Class abbreviatedIRI=":Dog"/><Class abbreviatedIRI=":Animal"/></SubClassOf>
    <ObjectPropertyDomain>
        <ObjectProperty abbreviatedIRI=":hasCompanion"/><Class abbreviatedIRI=":Animal"/>
    </ObjectPropertyDomain>
    <ObjectPropertyRange>
        <ObjectProperty abbreviatedIRI=":hasCompanion"/><Class abbreviatedIRI=":Animal"/>
    </ObjectPropertyRange>
    <DataPropertyDomain>
        <DataProperty abbreviatedIRI=":age"/><Class abbreviatedIRI=":Animal"/>
    </DataPropertyDomain>
    <DataPropertyRange>
        <DataProperty abbreviatedIRI=":age"/><Datatype abbreviatedIRI="xsd:integer"/>
    </DataPropertyRange>
    <ClassAssertion><Class abbreviatedIRI=":Dog"/><NamedIndividual abbreviatedIRI=":rex"/></ClassAssertion>

    {annotations}
</Ontology>
"""

#: Every named non-builtin entity gets exactly one label and one definition.
_ANNOTATED_ENTITIES = [
    ("http://ex.org/clean#Animal", "Animal", "A living organism in the test domain."),
    ("http://ex.org/clean#Dog", "Dog", "A domesticated canine."),
    ("http://ex.org/clean#hasCompanion", "has companion", "Links an animal to a companion."),
    ("http://ex.org/clean#age", "age", "The age of an animal in years."),
    ("http://ex.org/clean#rex", "Rex", "A specific dog."),
    (
        "http://www.w3.org/2004/02/skos/core#definition",
        "definition",
        "A statement of the meaning of a concept.",
    ),
    ("http://purl.org/dc/terms/title", "title", "A name given to the resource."),
]


def _annotation_block() -> str:
    fragments = []
    for iri, label, definition in _ANNOTATED_ENTITIES:
        fragments.append(
            "<AnnotationAssertion>"
            '<AnnotationProperty abbreviatedIRI="rdfs:label"/>'
            f"<IRI>{iri}</IRI>"
            f'<Literal xml:lang="en">{label}</Literal>'
            "</AnnotationAssertion>"
            "<AnnotationAssertion>"
            '<AnnotationProperty abbreviatedIRI="skos:definition"/>'
            f"<IRI>{iri}</IRI>"
            f'<Literal xml:lang="en">{definition}</Literal>'
            "</AnnotationAssertion>"
        )
    return "\n    ".join(fragments)


@pytest.fixture(scope="module")
def clean_lbug(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("clean") / "clean.lbug"
    document = _CLEAN_OWLXML.format(annotations=_annotation_block())
    Ontology.from_owlxml(document).save_projection(path).close()
    return path


def test_full_rule_set_reports_nothing_on_a_clean_ontology(clean_lbug: Path) -> None:
    rules = resolve_lint_rule_selection(
        profiles=available_lint_profiles(), select=[], extend_select=[], ignore=[]
    )
    assert {str(rule.path) for rule in rules} == {str(rule.path) for rule in lint_rules()}, (
        "selecting every profile must cover the complete rule inventory"
    )

    results = run_lint_on_path(clean_lbug, rules=rules)

    findings = [
        f"{violation.path.name}: {violation.rows[:3]}"
        for violation in [*results.failures, *results.warnings]
    ]
    assert findings == []
