from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation, AnnotationProperty
from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class SubAnnotationPropertyOf(BaseConstruct):
    """States that one annotation property is a subproperty of another.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Annotation_Subproperties)
    """

    sub_annotation_property: Reference[AnnotationProperty]
    super_annotation_property: Reference[AnnotationProperty]
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["SubAnnotationPropertyOf"] = "SubAnnotationPropertyOf"
