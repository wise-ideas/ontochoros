from typing import Literal

from pydantic import Field

from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class DataAllValuesFrom(BaseConstruct):
    """Restricts individuals to those whose data property values all belong to a data range.

    The property expressions are ordered: position i pairs with argument i of
    the data range, whose arity must equal the number of property expressions.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Universal_Quantification_2)
    """

    data_property_expressions: list[Reference[Literal["DataPropertyExpression"]]] = Field(
        min_length=1
    )
    data_range: Reference[Literal["DataRange"]]
    kind: Literal["DataAllValuesFrom"] = "DataAllValuesFrom"
