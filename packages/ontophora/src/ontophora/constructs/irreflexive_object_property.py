from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class IrreflexiveObjectProperty(BaseConstruct):
    """States that an object property cannot relate an individual to itself.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Irreflexive_Object_Properties)
    """

    object_property_expression: Reference[Literal["ObjectPropertyExpression"]]
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["IrreflexiveObjectProperty"] = "IrreflexiveObjectProperty"
