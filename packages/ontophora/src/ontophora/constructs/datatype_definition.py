from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.datatype import Datatype
from ontophora.reference import Reference


class DatatypeDefinition(BaseConstruct):
    """Defines a datatype as equivalent to a data range.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Datatype_Definitions)
    """

    datatype: Reference[Datatype]
    data_range: Reference[Literal["DataRange"]]
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["DatatypeDefinition"] = "DatatypeDefinition"
