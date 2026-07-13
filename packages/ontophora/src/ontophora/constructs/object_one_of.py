from typing import Literal

from pydantic import Field

from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class ObjectOneOf(BaseConstruct):
    """Defines a class expression by explicitly listing individuals.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Enumeration_of_Individuals)
    """

    individuals: set[Reference[Literal["Individual"]]] = Field(min_length=1)
    kind: Literal["ObjectOneOf"] = "ObjectOneOf"
