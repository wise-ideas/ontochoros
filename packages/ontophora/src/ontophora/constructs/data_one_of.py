from typing import Literal

from pydantic import Field

from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.literal import LiteralUnion
from ontophora.reference import Reference


class DataOneOf(BaseConstruct):
    """Defines a data range by explicitly listing literal values.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Enumeration_of_Literals)
    """

    literals: set[Reference[LiteralUnion]] = Field(min_length=1)
    kind: Literal["DataOneOf"] = "DataOneOf"
