from typing import Literal

from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class ObjectHasValue(BaseConstruct):
    """Restricts individuals to those related by an object property to a specific individual.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Individual_Value_Restriction)
    """

    object_property_expression: Reference[Literal["ObjectPropertyExpression"]]
    individual: Reference[Literal["Individual"]]
    kind: Literal["ObjectHasValue"] = "ObjectHasValue"
