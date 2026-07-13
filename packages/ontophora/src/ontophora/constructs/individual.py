from typing import Literal

from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.iri import IRI
from ontophora.constructs.types import NodeID


class AnonymousIndividual(BaseConstruct):
    """An individual identified by a blank node-style local identifier.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Anonymous_Individuals)
    """

    node_id: NodeID
    kind: Literal["AnonymousIndividual"] = "AnonymousIndividual"


class NamedIndividual(BaseConstruct):
    """An individual identified by an IRI.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Named_Individuals)
    """

    iri: IRI
    kind: Literal["NamedIndividual"] = "NamedIndividual"
