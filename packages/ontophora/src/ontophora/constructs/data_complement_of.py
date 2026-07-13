from typing import Literal

from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class DataComplementOf(BaseConstruct):
    """Defines a data range as the complement of another data range.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Complement_of_Data_Ranges)
    """

    data_range: Reference[Literal["DataRange"]]
    kind: Literal["DataComplementOf"] = "DataComplementOf"
