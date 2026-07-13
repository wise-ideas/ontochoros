from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation_value import AnnotationValue
from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.iri import IRI
from ontophora.reference import Reference


class AnnotationProperty(BaseConstruct):
    """An entity used to annotate ontologies, axioms, and entities.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Annotation_Properties)
    """

    iri: IRI
    kind: Literal["AnnotationProperty"] = "AnnotationProperty"


class Annotation(BaseConstruct):
    """Attaches metadata to an ontology element.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Annotations_of_Ontologies.2C_Axioms.2C_and_other_Annotations)
    """

    annotation_property: Reference[AnnotationProperty]
    annotation_value: AnnotationValue
    annotation_annotations: set[Reference["Annotation"]] = Field(default_factory=set)
    kind: Literal["Annotation"] = "Annotation"


class AnnotationPropertyDomain(BaseConstruct):
    """Constrains the domain of an annotation property.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Annotation_Property_Domain)
    """

    annotation_property: Reference[AnnotationProperty]
    domain: IRI
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["AnnotationPropertyDomain"] = "AnnotationPropertyDomain"


class AnnotationPropertyRange(BaseConstruct):
    """Constrains the range of an annotation property.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Annotation_Property_Range)
    """

    annotation_property: Reference[AnnotationProperty]
    range: IRI
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["AnnotationPropertyRange"] = "AnnotationPropertyRange"
