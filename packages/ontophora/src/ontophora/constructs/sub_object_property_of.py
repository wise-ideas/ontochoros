from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.property_expression_chain import PropertyExpressionChain
from ontophora.reference import Reference


class SubObjectPropertyOf(BaseConstruct):
    """States that one object property expression is a subproperty of another.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Object_Subproperties)
    """

    sub_object_property_expression: (
        Reference[Literal["ObjectPropertyExpression"]] | Reference[PropertyExpressionChain]
    )
    super_object_property_expression: Reference[Literal["ObjectPropertyExpression"]]
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["SubObjectPropertyOf"] = "SubObjectPropertyOf"
