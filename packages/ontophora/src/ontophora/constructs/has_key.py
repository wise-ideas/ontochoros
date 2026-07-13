from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class HasKey(BaseConstruct):
    """Defines a key for a class using object and/or data property expressions.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Keys)
    """

    class_expression: Reference[Literal["ClassExpression"]]
    object_property_expressions: set[Reference[Literal["ObjectPropertyExpression"]]]
    data_property_expressions: set[Reference[Literal["DataPropertyExpression"]]]
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["HasKey"] = "HasKey"
