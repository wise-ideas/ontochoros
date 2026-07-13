from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class FunctionalDataProperty(BaseConstruct):
    """States that a data property has at most one value per individual.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Functional_Data_Properties)
    """

    data_property_expression: Reference[Literal["DataPropertyExpression"]]
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["FunctionalDataProperty"] = "FunctionalDataProperty"
