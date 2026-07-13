from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.iri import IRI
from ontophora.reference import Reference


class DataPropertyDomain(BaseConstruct):
    """Constrains the class of individuals a data property can apply to.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Data_Property_Domain)
    """

    data_property_expression: Reference[Literal["DataPropertyExpression"]]
    domain: Reference[Literal["ClassExpression"]]
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["DataPropertyDomain"] = "DataPropertyDomain"


class DataPropertyRange(BaseConstruct):
    """Constrains the datatype range of values for a data property.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Data_Property_Range)
    """

    data_property_expression: Reference[Literal["DataPropertyExpression"]]
    range: Reference[Literal["DataRange"]]
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["DataPropertyRange"] = "DataPropertyRange"


class DataProperty(BaseConstruct):
    """An entity that links individuals to literal values.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Data_Properties)
    """

    iri: IRI
    kind: Literal["DataProperty"] = "DataProperty"
