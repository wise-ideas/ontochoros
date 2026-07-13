from typing import Literal

from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class ObjectSomeValuesFrom(BaseConstruct):
    """Restricts individuals to those with some object property value in a class expression.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Existential_Quantification)
    """

    object_property_expression: Reference[Literal["ObjectPropertyExpression"]]
    class_expression: Reference[Literal["ClassExpression"]]
    kind: Literal["ObjectSomeValuesFrom"] = "ObjectSomeValuesFrom"
