from typing import Literal

from pydantic import Field

from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class ObjectUnionOf(BaseConstruct):
    """Defines a class expression as the union of class expressions.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Union_of_Class_Expressions)
    """

    class_expressions: set[Reference[Literal["ClassExpression"]]] = Field(min_length=2)
    kind: Literal["ObjectUnionOf"] = "ObjectUnionOf"
