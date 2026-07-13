from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class SubDataPropertyOf(BaseConstruct):
    """States that one data property is a subproperty of another.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Data_Subproperties)
    """

    sub_data_property_expression: Reference[Literal["DataPropertyExpression"]]
    super_data_property_expression: Reference[Literal["DataPropertyExpression"]]
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["SubDataPropertyOf"] = "SubDataPropertyOf"
