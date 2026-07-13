from typing import Literal

from pydantic import Field

from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class PropertyExpressionChain(BaseConstruct):
    """Represents an ordered chain of object property expressions.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Object_Subproperties)
    """

    object_property_expressions: list[Reference[Literal["ObjectPropertyExpression"]]] = Field(
        min_length=2
    )
    kind: Literal["ObjectPropertyChain"] = "ObjectPropertyChain"
