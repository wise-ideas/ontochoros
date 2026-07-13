from typing import Literal

from pydantic import Field

from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class DataIntersectionOf(BaseConstruct):
    """Defines a data range as the intersection of multiple data ranges.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Intersection_of_Data_Ranges)
    """

    data_ranges: set[Reference[Literal["DataRange"]]] = Field(min_length=2)
    kind: Literal["DataIntersectionOf"] = "DataIntersectionOf"
