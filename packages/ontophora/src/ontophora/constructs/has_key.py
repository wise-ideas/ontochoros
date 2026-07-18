from typing import Literal, Self

from pydantic import Field, model_validator

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

    @model_validator(mode="after")
    def _require_key_property_expression(self) -> Self:
        # OWL 2 section 9.5: m or n (or both) MUST be larger than zero.
        if not self.object_property_expressions and not self.data_property_expressions:
            raise ValueError("HasKey requires at least one object or data property expression")
        return self
