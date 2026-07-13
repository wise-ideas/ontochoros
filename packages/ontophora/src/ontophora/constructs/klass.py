from typing import Literal

from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.iri import IRI


class Klass(BaseConstruct):
    """A named class entity.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Classes)
    """

    iri: IRI
    kind: Literal["Class"] = "Class"
