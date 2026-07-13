from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class SubClassOf(BaseConstruct):
    """States that every instance of one class expression is also an instance of another.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Subclass_Axioms)
    """

    sub_class_expression: Reference[Literal["ClassExpression"]]
    super_class_expression: Reference[Literal["ClassExpression"]]
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["SubClassOf"] = "SubClassOf"
