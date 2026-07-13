from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class DifferentIndividuals(BaseConstruct):
    """States that listed individuals are pairwise different.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Individual_Inequality)
    """

    individuals: set[Reference[Literal["Individual"]]] = Field(min_length=2)
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["DifferentIndividuals"] = "DifferentIndividuals"
