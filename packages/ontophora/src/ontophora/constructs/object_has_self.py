from typing import Literal

from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class ObjectHasSelf(BaseConstruct):
    """Restricts individuals to those related to themselves by an object property.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Self-Restriction)
    """

    object_property_expression: Reference[Literal["ObjectPropertyExpression"]]
    kind: Literal["ObjectHasSelf"] = "ObjectHasSelf"
