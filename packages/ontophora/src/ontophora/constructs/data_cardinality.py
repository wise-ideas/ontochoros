from typing import Literal

from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.types import NonNegativeInteger
from ontophora.reference import Reference


class DataExactCardinality(BaseConstruct):
    """Restricts individuals to those with exactly N values for a data property.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Exact_Cardinality_2)
    """

    cardinality: NonNegativeInteger
    data_property_expression: Reference[Literal["DataPropertyExpression"]]
    data_range: Reference[Literal["DataRange"]] | None = None
    kind: Literal["DataExactCardinality"] = "DataExactCardinality"


class DataMaxCardinality(BaseConstruct):
    """Restricts individuals to those with at most N values for a data property.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Maximum_Cardinality_2)
    """

    cardinality: NonNegativeInteger
    data_property_expression: Reference[Literal["DataPropertyExpression"]]
    data_range: Reference[Literal["DataRange"]] | None = None
    kind: Literal["DataMaxCardinality"] = "DataMaxCardinality"


class DataMinCardinality(BaseConstruct):
    """Restricts individuals to those with at least N values for a data property.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Minimum_Cardinality_2)
    """

    cardinality: NonNegativeInteger
    data_property_expression: Reference[Literal["DataPropertyExpression"]]
    data_range: Reference[Literal["DataRange"]] | None = None
    kind: Literal["DataMinCardinality"] = "DataMinCardinality"
