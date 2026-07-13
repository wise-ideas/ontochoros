from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation, AnnotationProperty
from ontophora.constructs.annotation_value import AnnotationValue
from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.individual import AnonymousIndividual
from ontophora.constructs.iri import IRI
from ontophora.reference import Reference

AnnotationSubject = Reference[AnonymousIndividual] | IRI


class AnnotationAssertion(BaseConstruct):
    """Attaches an annotation property/value pair to an IRI, anonymous individual, or literal.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Annotation_Assertion)
    """

    annotation_property: Reference[AnnotationProperty]
    annotation_subject: AnnotationSubject
    annotation_value: AnnotationValue
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["AnnotationAssertion"] = "AnnotationAssertion"
