from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.klass import Klass
from ontophora.reference import Reference


class DisjointUnion(BaseConstruct):
    """Defines a class as the disjoint union of class expressions.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Disjoint_Union_of_Class_Expressions)
    """

    klass: Reference[Klass]
    disjoint_class_expressions: set[Reference[Literal["ClassExpression"]]] = Field(min_length=2)
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["DisjointUnion"] = "DisjointUnion"
