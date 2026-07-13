from typing import Literal

from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class DataSomeValuesFrom(BaseConstruct):
    """Restricts individuals to those with some data property value in a data range.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Existential_Quantification_2)
    """

    data_property_expression: Reference[Literal["DataPropertyExpression"]]
    data_range: Reference[Literal["DataRange"]]
    kind: Literal["DataSomeValuesFrom"] = "DataSomeValuesFrom"
