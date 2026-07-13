from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.reference import Reference


class AsymmetricObjectProperty(BaseConstruct):
    """States that an object property cannot hold in both directions for the same pair.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Asymmetric_Object_Properties)
    """

    object_property_expression: Reference[Literal["ObjectPropertyExpression"]]
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["AsymmetricObjectProperty"] = "AsymmetricObjectProperty"
