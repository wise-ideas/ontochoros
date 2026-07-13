from typing import Literal

from pydantic import Field

from ontophora.constructs.annotation import Annotation
from ontophora.constructs.base import BaseConstruct
from ontophora.constructs.iri import IRI
from ontophora.reference import Reference


class ObjectPropertyDomain(BaseConstruct):
    """Constrains the class of individuals an object property can apply to.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Object_Property_Domain)
    """

    object_property_expression: Reference[Literal["ObjectPropertyExpression"]]
    domain: Reference[Literal["ClassExpression"]]
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["ObjectPropertyDomain"] = "ObjectPropertyDomain"


class ObjectPropertyRange(BaseConstruct):
    """Constrains the class of individuals reachable via an object property.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Object_Property_Range)
    """

    object_property_expression: Reference[Literal["ObjectPropertyExpression"]]
    range: Reference[Literal["ClassExpression"]]
    axiom_annotations: set[Reference[Annotation]] = Field(default_factory=set)
    kind: Literal["ObjectPropertyRange"] = "ObjectPropertyRange"


class ObjectProperty(BaseConstruct):
    """An entity that links individuals to individuals.

    See: [OWL 2 reference](https://www.w3.org/TR/owl2-syntax/#Object_Properties)
    """

    iri: IRI
    kind: Literal["ObjectProperty"] = "ObjectProperty"
