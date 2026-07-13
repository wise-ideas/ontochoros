from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class InverseObjectProperties(BaseConstruct):
    """States that two object properties are inverses of each other.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Inverse_Object_Properties_2)
    """

    object_property_expression_1: Reference[Literal["ObjectPropertyExpression"]]
    object_property_expression_2: Reference[Literal["ObjectPropertyExpression"]]
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["InverseObjectProperties"] = "InverseObjectProperties"
