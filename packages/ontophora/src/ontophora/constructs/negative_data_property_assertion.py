from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.literal import LiteralUnion
from ontophora.reference import Reference


class NegativeDataPropertyAssertion(BaseConstruct):
    """States that an individual does not have a specific data property value.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Negative_Data_Property_Assertions)
    """

    data_property_expression: Reference[Literal["DataPropertyExpression"]]
    source_individual: Reference[Literal["Individual"]]
    target_value: Reference[LiteralUnion]
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["NegativeDataPropertyAssertion"] = "NegativeDataPropertyAssertion"
