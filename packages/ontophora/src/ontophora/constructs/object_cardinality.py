from typing import Literal

from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.types import NonNegativeInteger
from ontophora.reference import Reference


class ObjectExactCardinality(BaseConstruct):
    """Restricts individuals to those with exactly N related individuals via an object property.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Exact_Cardinality)
    """

    cardinality: NonNegativeInteger
    object_property_expression: Reference[Literal["ObjectPropertyExpression"]]
    class_expression: Reference[Literal["ClassExpression"]] | None = None
    kind: Literal["ObjectExactCardinality"] = "ObjectExactCardinality"


class ObjectMaxCardinality(BaseConstruct):
    """Restricts individuals to those with at most N related individuals via an object property.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Maximum_Cardinality)
    """

    cardinality: NonNegativeInteger
    object_property_expression: Reference[Literal["ObjectPropertyExpression"]]
    class_expression: Reference[Literal["ClassExpression"]] | None = None
    kind: Literal["ObjectMaxCardinality"] = "ObjectMaxCardinality"


class ObjectMinCardinality(BaseConstruct):
    """Restricts individuals to those with at least N related individuals via an object property.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Minimum_Cardinality)
    """

    cardinality: NonNegativeInteger
    object_property_expression: Reference[Literal["ObjectPropertyExpression"]]
    class_expression: Reference[Literal["ClassExpression"]] | None = None
    kind: Literal["ObjectMinCardinality"] = "ObjectMinCardinality"
