from typing import Literal

from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.object_property import ObjectProperty
from ontophora.reference import Reference


class InverseObjectProperty(BaseConstruct):
    """References the inverse of a named object property.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Inverse_Object_Properties)
    """

    object_property: Reference[ObjectProperty]
    kind: Literal["ObjectInverseOf"] = "ObjectInverseOf"
