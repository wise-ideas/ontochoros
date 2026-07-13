from typing import Literal

from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.iri import IRI
from ontophora.constructs.literal import LiteralUnion
from ontophora.reference import Reference


class FacetRestriction(BaseConstruct):
    """Constrains a datatype with a specific facet/value pair.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Datatype_Restrictions)
    """

    constraining_facet: IRI
    restriction_value: Reference[LiteralUnion]
    kind: Literal["FacetRestriction"] = "FacetRestriction"
