from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class SameIndividual(BaseConstruct):
    """States that listed individual references denote the same individual.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Individual_Equality)
    """

    individuals: set[Reference[Literal["Individual"]]] = Field(min_length=2)
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["SameIndividual"] = "SameIndividual"
