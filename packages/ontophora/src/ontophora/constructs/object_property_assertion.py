from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class ObjectPropertyAssertion(BaseConstruct):
    """States that an object property relates two individuals.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Positive_Object_Property_Assertions)
    """

    object_property_expression: Reference[Literal["ObjectPropertyExpression"]]
    source_individual: Reference[Literal["Individual"]]
    target_individual: Reference[Literal["Individual"]]
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["ObjectPropertyAssertion"] = "ObjectPropertyAssertion"
