from typing import Literal

from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class ObjectComplementOf(BaseConstruct):
    """Defines a class expression as the complement of another class expression.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Complement_of_Class_Expressions)
    """

    class_expression: Reference[Literal["ClassExpression"]]
    kind: Literal["ObjectComplementOf"] = "ObjectComplementOf"
