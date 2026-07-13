from typing import Literal

from pydantic import Field

from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.datatype import Datatype
from ontophora.constructs.facet_restriction import FacetRestriction
from ontophora.reference import Reference


class DatatypeRestriction(BaseConstruct):
    """Defines a datatype-constrained data range via facet restrictions.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Datatype_Restrictions)
    """

    datatype: Reference[Datatype]
    restrictions: set[Reference[FacetRestriction]] = Field(min_length=1)
    kind: Literal["DatatypeRestriction"] = "DatatypeRestriction"
