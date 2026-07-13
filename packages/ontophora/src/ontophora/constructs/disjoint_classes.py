from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class DisjointClasses(BaseConstruct):
    """States that listed class expressions are pairwise disjoint.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Disjoint_Classes)
    """

    class_expressions: set[Reference[Literal["ClassExpression"]]] = Field(min_length=2)
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["DisjointClasses"] = "DisjointClasses"
