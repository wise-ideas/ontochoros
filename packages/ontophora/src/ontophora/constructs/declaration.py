from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class Declaration(BaseConstruct):
    """Declares the type of an OWL entity.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Entity_Declarations_and_Typing)
    """

    entity: Reference[Literal["Entity"]]
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["Declaration"] = "Declaration"
