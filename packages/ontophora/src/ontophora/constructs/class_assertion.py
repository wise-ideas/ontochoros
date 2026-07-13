from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class ClassAssertion(BaseConstruct):
    """States that an individual is an instance of a class expression.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Class_Assertions)
    """

    class_expression: Reference[Literal["ClassExpression"]]
    individual: Reference[Literal["Individual"]]
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["ClassAssertion"] = "ClassAssertion"
