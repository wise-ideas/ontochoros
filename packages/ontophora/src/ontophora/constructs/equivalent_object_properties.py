from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class EquivalentObjectProperties(BaseConstruct):
    """States that listed object properties are semantically equivalent.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Equivalent_Object_Properties)
    """

    object_property_expressions: set[Reference[Literal["ObjectPropertyExpression"]]] = Field(
        min_length=2
    )
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["EquivalentObjectProperties"] = "EquivalentObjectProperties"
