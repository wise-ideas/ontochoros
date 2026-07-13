from typing import Literal

from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.literal import LiteralUnion
from ontophora.reference import Reference


class DataHasValue(BaseConstruct):
    """Restricts individuals to those with a specific literal value for a data property.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Literal_Value_Restriction)
    """

    data_property_expression: Reference[Literal["DataPropertyExpression"]]
    literal: Reference[LiteralUnion]
    kind: Literal["DataHasValue"] = "DataHasValue"
