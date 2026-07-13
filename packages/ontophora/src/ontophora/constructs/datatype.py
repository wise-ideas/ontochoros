from typing import Literal

from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.iri import IRI


class Datatype(BaseConstruct):
    """An entity that denotes a datatype.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Datatypes)
    """

    iri: IRI
    kind: Literal["Datatype"] = "Datatype"
