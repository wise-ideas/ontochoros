from typing import Literal

from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class ObjectAllValuesFrom(BaseConstruct):
    """Restricts individuals to those whose object property values all satisfy a class expression.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Universal_Quantification)
    """

    object_property_expression: Reference[Literal["ObjectPropertyExpression"]]
    class_expression: Reference[Literal["ClassExpression"]]
    kind: Literal["ObjectAllValuesFrom"] = "ObjectAllValuesFrom"
